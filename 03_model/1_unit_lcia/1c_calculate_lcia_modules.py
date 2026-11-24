"""
Step 1c: calculate the inventory and the impact of each life cycle module (A1–A3, A4, A5, C1, C2, C3–C4) of 1 kg of
each case.

How it works, in two parts.

1. Inventory per module. Every LCI sheet is a chain of blocks: A1–A3 -> A4 -> A5 -> C1 -> C2 -> C3–C4, where each
   block's first input is the output of the block before it. So the last activity of a block needs everything up to and
   including that block. Going back through its inputs gives the kg (or kWh, tkm, ...) of every ecoinvent dataset needed
   for 1 kg of that activity ("cumulative inventory"). The inventory of one module is the increase from the block before:

       inventory of module M = cumulative inventory at the end of M - cumulative inventory at the end of the module before M

2. Impact per module = Σ over the ecoinvent datasets of its inventory: amount x impact of 1 unit (from step 1b).

Note on losses: if installation (A5) needs 1.03 kg delivered per kg installed, A5 gets the inventory (and impact) of
the extra 0.03 kg (made and delivered), as in EN 15804, because the subtraction above takes 1 kg of the block before,
not 1.03 kg.

The inventory is the same in both scenarios; only the impact per unit of the datasets changes.

Input:  01_data/02_processed/unit_lcia_steps/1a_lci_exchanges.csv
        01_data/02_processed/unit_lcia_steps/1b_background_impacts_<scenario>.csv
Output: 01_data/02_processed/unit_lcia_steps/1c_inventory_by_module.csv
        (one row per case, module and ecoinvent dataset: the amount per kg of product; also read by step 1d)
        01_data/02_processed/unit_lcia_steps/1c_lcia_modules_<scenario>.csv
        (one row per case and module, one column per impact category)
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

exchanges = pd.read_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv")
categories = list(pd.read_csv(s.STEPS_FOLDER / "1b_impact_categories.csv").impact_category)
DATASET = ["name", "reference product", "location", "unit"]      # the columns that identify an ecoinvent dataset


# %% Function: cumulative inventory of one activity of one case
def cumulative_inventory(case_exchanges, activity, memory):
    """Amount of each ecoinvent dataset needed for 1 unit of `activity`, upstream included, as a Series indexed by
    (name, reference product, location, unit). `memory` stores activities already done, so each is done once."""
    if activity in memory:
        return memory[activity]
    rows = case_exchanges[case_exchanges.activity == activity]
    produced = rows[rows.exchange_type == "production"].amount.iloc[0]
    parts = []
    for _, row in rows[rows.exchange_type == "technosphere"].iterrows():
        if row.input_is == "foreground":           # an activity of the same LCI sheet: go back through its inputs
            parts.append(row.amount * cumulative_inventory(case_exchanges, row.input_name, memory))
        else:                                      # an ecoinvent dataset
            key = (row.input_name, row.input_reference_product, row.input_location, row.input_unit)
            parts.append(pd.Series({key: row.amount}))
    if parts:
        total = pd.concat(parts).groupby(level=[0, 1, 2, 3]).sum()
    else:                                          # an activity without inputs
        total = pd.Series(dtype=float, index=pd.MultiIndex.from_tuples([], names=DATASET))
    memory[activity] = total / produced
    return memory[activity]


# %% Function: the last activity of each module of one case
def end_of_each_module(case_exchanges):
    """For each module, the activity that the next module takes as its input (for the last module: the activity that
    no other activity uses)."""
    technosphere = case_exchanges[case_exchanges.input_is == "foreground"]
    module_of = dict(zip(case_exchanges.activity, case_exchanges.activity_module))
    ends = {}
    for module in s.MODULES:
        activities = {a for a, m in module_of.items() if m == module}
        used_by_other_module = {row.input_name for row in technosphere.itertuples()
                                if row.input_name in activities and module_of[row.activity] != module}
        used_at_all = set(technosphere.input_name)
        candidates = used_by_other_module if module != s.MODULES[-1] else activities - used_at_all
        if len(candidates) != 1:
            raise ValueError(f"{case_exchanges.case_id.iloc[0]}: cannot tell which activity ends module {module}: "
                             f"{sorted(candidates)}")
        ends[module] = candidates.pop()
    return ends


# %% Part 1: inventory per module, for every case
inventory_rows = []
for case_id, case_exchanges in exchanges.groupby("case_id"):
    ends = end_of_each_module(case_exchanges)
    memory = {}
    previous = None                                         # cumulative inventory before A1–A3: nothing
    for module in s.MODULES:
        cumulative = cumulative_inventory(case_exchanges, ends[module], memory)
        increase = cumulative if previous is None else cumulative.sub(previous, fill_value=0)
        for key, amount in increase.items():
            if abs(amount) > 1e-15:
                inventory_rows.append({"case_id": case_id, "module": module, **dict(zip(DATASET, key)),
                                       "amount": amount})
        previous = cumulative
inventory = pd.DataFrame(inventory_rows)
inventory.to_csv(s.STEPS_FOLDER / "1c_inventory_by_module.csv", index=False)
print(f"Inventory: {len(inventory)} rows (case x module x ecoinvent dataset). Saved 1c_inventory_by_module.csv")


# %% Look at one inventory: RAW timber, scaled-up, A1–A3
inventory[(inventory.case_id == "raw_timber_scaled_up") & (inventory.module == "A1–A3")]


# %% Part 2: impact per module = inventory x impact per unit, scenario by scenario
for scenario in s.SCENARIOS:
    background = pd.read_csv(s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv")
    table = inventory.merge(background[DATASET + categories], on=DATASET, how="left")
    if table[categories].isna().any().any():
        missing = table[table[categories].isna().any(axis=1)][DATASET].drop_duplicates()
        raise ValueError(f"{scenario}: no impact per unit for:\n{missing.to_string(index=False)}")
    for category in categories:
        table[category] = table["amount"] * table[category]
    modules = table.groupby(["case_id", "module"])[categories].sum()
    # every case gets all six modules, also those with no inventory (e.g. C1 without rows): 0
    every_module = pd.MultiIndex.from_product([sorted(exchanges.case_id.unique()), s.MODULES],
                                              names=["case_id", "module"])
    modules = modules.reindex(every_module, fill_value=0.0).reset_index()

    out = s.STEPS_FOLDER / f"1c_lcia_modules_{scenario}.csv"
    modules.to_csv(out, index=False)
    print(f"{scenario}: {modules.case_id.nunique()} cases x {modules.module.nunique()} modules. Saved {out}")


# %% Look at the result: climate change per module, today
today = pd.read_csv(s.STEPS_FOLDER / "1c_lcia_modules_today.csv")
today.pivot(index="case_id", columns="module", values="climate change").reindex(columns=s.MODULES).round(3)
