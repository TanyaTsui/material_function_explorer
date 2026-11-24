"""
Step 1b: calculate the impact of one unit of every ecoinvent dataset the model uses (the only step that needs Brightway).

The model uses two kinds of ecoinvent datasets: the background inputs of the LCI sheets (from step 1a) and the avoided
products of module D (01_data/01_raw/method_constants/avoided_datasets.csv). For each of them, and for each scenario,
this script calculates the EF 3.1 impact of one unit (1 kg, 1 kWh, 1 tkm, ...) with Brightway. Steps 1c and 1d then only
multiply amounts by these numbers, without Brightway.

Needs: the conda environment brightway_env and the Brightway project in settings.py (ecoinvent 3.12 cut-off and the
premise 2050 database). Takes a few minutes per scenario.

Input:  01_data/02_processed/unit_lcia_steps/1a_lci_exchanges.csv
        01_data/01_raw/method_constants/avoided_datasets.csv
Output: 01_data/02_processed/unit_lcia_steps/1b_background_impacts_<scenario>.csv  (one row per dataset, one column per
        impact category)
        01_data/02_processed/unit_lcia_steps/1b_impact_categories.csv  (category names and units)
"""
# %% Setup
import sys
from pathlib import Path

import bw2calc as bc
import bw2data as bd
import pandas as pd

try:
    HERE = Path(__file__).resolve().parent
except NameError:
    HERE = Path.cwd()
sys.path.append(str(HERE.parent))
import settings as s

bd.projects.set_current(s.BRIGHTWAY_PROJECT)
print("Brightway project:", s.BRIGHTWAY_PROJECT, "| databases:", list(bd.databases))


# %% The impact categories: all EF 3.1 methods of ecoinvent 3.12
methods = sorted(m for m in bd.methods if m[:2] == s.METHOD_FAMILY)
categories = pd.DataFrame({
    "impact_category": [m[2] for m in methods],
    "unit": [bd.Method(m).metadata.get("unit", "") for m in methods],
})
categories.to_csv(s.STEPS_FOLDER / "1b_impact_categories.csv", index=False)
print(len(methods), "impact categories")
categories


# %% Check: how EF 3.1 characterises biogenic CO2 (the model reports stored biogenic carbon separately, in step 1e)
# If 'carbon dioxide, in air' (uptake) or 'carbon dioxide, non-fossil' (release) had a factor other than 0 in
# 'climate change', the stored carbon of step 1e would be counted twice. Expected: both 0.
climate_change = [m for m in methods if m[2] == "climate change"][0]
for flow_key, factor in bd.Method(climate_change).load():
    flow = bd.get_activity(flow_key)
    if flow["name"].lower() in ("carbon dioxide, in air", "carbon dioxide, non-fossil"):
        print(f"  {flow['name']} {flow.get('categories')}: {factor}")


# %% The list of datasets: background inputs of the LCIs + avoided products of module D
exchanges = pd.read_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv")
background = exchanges[exchanges.input_is == "background"]
from_lcis = background[["input_name", "input_reference_product", "input_location", "input_unit"]]
from_lcis.columns = ["name", "reference product", "location", "unit"]

avoided = pd.read_csv(s.METHOD_CONSTANTS_FOLDER / "avoided_datasets.csv")
from_module_d = avoided[["name", "reference product", "location", "unit"]]

datasets = pd.concat([from_lcis, from_module_d]).drop_duplicates().reset_index(drop=True)
print(len(datasets), "different datasets")


# %% Function: the impact of one unit of each dataset in one database
def impacts_per_unit(database_name, datasets):
    """One row per dataset, one column per impact category. Datasets not found get empty values."""
    index = {(a["name"], a.get("reference product"), a["location"]): a for a in bd.Database(database_name)}
    lca = None
    rows = []
    for _, d in datasets.iterrows():
        row = {"name": d["name"], "reference product": d["reference product"], "location": d["location"],
               "unit": d["unit"], "found": False}
        activity = index.get((d["name"], d["reference product"], d["location"]))
        if activity is not None:
            if activity["unit"] != d["unit"]:
                print(f"  WARNING unit differs for '{d['name']}' ({d['location']}): LCI says {d['unit']}, "
                      f"database says {activity['unit']}")
            if lca is None:                       # build the LCA once, then only change the demand
                lca = bc.LCA({activity.id: 1}, methods[0])
                lca.lci()
            else:
                lca.redo_lci({activity.id: 1})
            for m in methods:
                lca.switch_method(m)
                lca.lcia()
                row[m[2]] = lca.score
            row["found"] = True
        rows.append(row)
    return pd.DataFrame(rows)


# %% Calculate, scenario by scenario
results = {}
for scenario, database_name in s.SCENARIOS.items():
    print(f"\n{scenario}: {database_name}")
    results[scenario] = impacts_per_unit(database_name, datasets)
    missing = results[scenario][~results[scenario].found]
    print(f"  {len(datasets) - len(missing)} of {len(datasets)} datasets found")
    for _, d in missing.iterrows():
        print(f"  NOT FOUND: {d['name']} | {d['reference product']} | {d['location']}")


# %% Datasets missing in 2050: use today's value, and say so in the 'note' column
# premise rewrites the database, so a few datasets can be renamed or regionalised. A missing dataset today is an error.
if (~results["today"].found).any():
    raise ValueError("Some datasets are not in today's database (see the list above). Fix the LCI sheet or "
                     "avoided_datasets.csv, then run again.")
for scenario in s.SCENARIOS:
    table = results[scenario]
    table["note"] = ""
    if scenario != "today":
        missing = ~table.found
        table.loc[missing, categories.impact_category] = results["today"].loc[missing, categories.impact_category]
        table.loc[missing, "note"] = "not in the scenario database: today's value used"


# %% Save
for scenario, table in results.items():
    out = s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv"
    table.drop(columns="found").to_csv(out, index=False)
    print("Saved", out)
