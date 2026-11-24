"""
Step 1f: combine the results of steps 1c, 1d and 1e into the four unit impact tables of component 1.

Per scenario (today, 2050):

  unit_impacts_by_module_<scenario>.csv   long table, one row per case x module x impact category:
                                          A1–A3, A1–A3 recycled content (CFF), A4, A5, C1, C2, C3–C4 and D, plus one
                                          row per case with the biogenic CO2 stored in the product (module
                                          'in product', kg CO2)
  unit_impacts_total_<scenario>.csv       wide table, one row per case, one column per impact category:
                                          the sum of all these rows except the stored CO2, and a last column with the
                                          biogenic CO2 stored in the product

All values are per kg of product. Module B is not included: it depends on the function (component 2).
The stored biogenic CO2 is not inside 'climate change' (see step 1e).

Output: 01_data/02_processed/unit_impacts_by_module_<scenario>.csv
        01_data/02_processed/unit_impacts_total_<scenario>.csv
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

categories = pd.read_csv(s.STEPS_FOLDER / "1b_impact_categories.csv")
unit_of = dict(zip(categories.impact_category, categories.unit))
biogenic = pd.read_csv(s.STEPS_FOLDER / "1e_biogenic_carbon.csv")


def case_type(case_id):
    if case_id.startswith("baseline_"):
        return "baseline"
    return "RAW scaled-up" if case_id.endswith("_scaled_up") else "RAW prototype"


# %% Combine, scenario by scenario
for scenario in s.SCENARIOS:
    modules_a_to_c = pd.read_csv(s.STEPS_FOLDER / f"1c_lcia_modules_{scenario}.csv")
    cff = pd.read_csv(s.STEPS_FOLDER / f"1d_cff_{scenario}.csv")       # recycled content (CFF) and module D
    wide = pd.concat([modules_a_to_c, cff])

    # long table: one row per case x module x impact category
    long = wide.melt(id_vars=["case_id", "module"], var_name="impact_category", value_name="value")
    long["unit"] = long.impact_category.map(unit_of)
    stored = biogenic.rename(columns={"biogenic CO2 stored": "value"})
    stored = stored.assign(module="in product", impact_category="biogenic CO2 stored", unit="kg CO2")
    long = pd.concat([long, stored])
    long.insert(1, "case_type", long.case_id.map(case_type))
    module_order = {m: i for i, m in enumerate(s.ALL_MODULES + ["in product"])}
    long["module_order"] = long.module.map(module_order)
    long = long.sort_values(["case_id", "module_order", "impact_category"])
    long = long[["case_id", "case_type", "module", "impact_category", "unit", "value"]]

    # total table: sum of all modules, one column per impact category, with its unit in the column name
    total = wide.groupby("case_id")[list(categories.impact_category)].sum()
    total.columns = [f"{c} [{unit_of[c]}]" for c in total.columns]
    total["biogenic CO2 stored [kg CO2]"] = biogenic.set_index("case_id")["biogenic CO2 stored"]
    total.insert(0, "case_type", total.index.map(case_type))
    total = total.reset_index()

    long.to_csv(s.PROCESSED_DATA / f"unit_impacts_by_module_{scenario}.csv", index=False)
    total.to_csv(s.PROCESSED_DATA / f"unit_impacts_total_{scenario}.csv", index=False)
    print(f"{scenario}: saved unit_impacts_by_module_{scenario}.csv ({len(long)} rows) and "
          f"unit_impacts_total_{scenario}.csv ({len(total)} cases)")


# %% Look at the result: total climate change and stored CO2, today
today = pd.read_csv(s.PROCESSED_DATA / "unit_impacts_total_today.csv")
climate_change = [c for c in today.columns if c.startswith("climate change [")][0]
today[["case_id", "case_type", climate_change, "biogenic CO2 stored [kg CO2]"]].round(3)
