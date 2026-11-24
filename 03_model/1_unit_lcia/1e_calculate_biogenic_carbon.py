"""
Step 1e: calculate the biogenic CO2 stored in 1 kg of each case.

Per constituent of the product (losses excluded: only what ends up in the product):

    CO2 stored = kg per kg of product / (1 + moisture content) x carbon fraction of dry mass x 44/12

  moisture content   on a dry basis: from bioc_inputs.csv if given, else the default of the constituent's archetype
  carbon fraction    from the constituent's carbon archetype (0 for mineral, metal and fossil constituents)
  44/12              kg CO2 per kg C

The result is the CO2 held in the product, in kg CO2 per kg of product, the same in both scenarios. It is reported next
to the impact categories, not inside 'climate change': how much credit it gets depends on how long the carbon is stored
(the service life), which is only known per function, so the time-dependent credit (GWP_bio, dynamic characterisation)
is applied in component 2.

Input:  01_data/01_raw/cff_and_carbon_inputs/bioc_inputs.csv
        01_data/01_raw/method_constants/carbon_archetypes.csv
Output: 01_data/02_processed/unit_lcia_steps/1e_biogenic_carbon.csv              (one row per case)
        01_data/02_processed/unit_lcia_steps/1e_biogenic_carbon_by_constituent.csv  (the same, per constituent, to check)
"""
# %% Setup
import sys
from pathlib import Path

import pandas as pd

try:
    HERE = Path(__file__).resolve().parent
except NameError:
    HERE = Path.cwd()
sys.path.append(str(HERE.parent))
import settings as s

constituents = pd.read_csv(s.CFF_AND_CARBON_FOLDER / "bioc_inputs.csv")
archetypes = pd.read_csv(s.METHOD_CONSTANTS_FOLDER / "carbon_archetypes.csv")
archetypes = archetypes.set_index("archetype")[["carbon fraction of dry mass", "default moisture (dry basis)"]]

# every case of the LCIs needs rows in bioc_inputs.csv
cases = set(pd.read_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv").case_id)
missing = cases - set(constituents.case_id)
if missing:
    raise ValueError(f"No rows in bioc_inputs.csv for: {sorted(missing)}")


# %% Calculate per constituent
table = constituents.join(archetypes, on="carbon_archetype")
table["moisture used"] = table["moisture_content"].fillna(table["default moisture (dry basis)"]).fillna(0)
table["kg dry"] = table["kg_per_kg_product"] / (1 + table["moisture used"])
table["kg CO2 stored"] = table["kg dry"] * table["carbon fraction of dry mass"] * 44 / 12

table[["case_id", "constituent", "kg_per_kg_product", "carbon_archetype", "moisture used", "kg CO2 stored"]].round(3)


# %% Sum per case
per_case = table.groupby("case_id", as_index=False)["kg CO2 stored"].sum()
per_case = per_case.rename(columns={"kg CO2 stored": "biogenic CO2 stored"})
per_case.round(3)


# %% Save
table.to_csv(s.STEPS_FOLDER / "1e_biogenic_carbon_by_constituent.csv", index=False)
per_case.to_csv(s.STEPS_FOLDER / "1e_biogenic_carbon.csv", index=False)
print("Saved", s.STEPS_FOLDER / "1e_biogenic_carbon.csv")
