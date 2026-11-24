"""
Step 1c: calculate the impact of each life cycle module (A1–A3, A4, A5, C1, C2, C3–C4) of 1 kg of each case.

How it works. Every LCI sheet is a chain of blocks: A1–A3 -> A4 -> A5 -> C1 -> C2 -> C3–C4, where each block's first
input is the output of the block before it. So the last activity of a block holds the impact of everything up to and
including that block ("cumulative impact"). The impact of one module is then the increase from the block before it:

    impact of module M = cumulative impact at the end of M - cumulative impact at the end of the module before M

The cumulative impact of an activity is found by going through its inputs: an ecoinvent input adds
amount x (impact per unit, from step 1b); an input from the same LCI sheet adds amount x (that activity's cumulative
impact), found the same way. Everything is per 1 unit of output (1 kg).

Note on losses: if installation (A5) needs 1.03 kg delivered per kg installed, A5 gets the impact of the extra 0.03 kg
(made and delivered), as in EN 15804, because the subtraction above takes 1 kg of the block before, not 1.03 kg.

Input:  01_data/02_processed/unit_lcia_steps/1a_lci_exchanges.csv
        01_data/02_processed/unit_lcia_steps/1b_background_impacts_<scenario>.csv
Output: 01_data/02_processed/unit_lcia_steps/1c_lcia_modules_<scenario>.csv
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


# %% Function: cumulative impact of one activity of one case
def cumulative_impact(case_exchanges, activity, background, memory):
    """Impact (a Series over the impact categories) of producing 1 unit of `activity`, upstream included.
    `memory` stores activities already calculated, so each is calculated once."""
    if activity in memory:
        return memory[activity]
    rows = case_exchanges[case_exchanges.activity == activity]
    produced = rows[rows.exchange_type == "production"].amount.iloc[0]
    total = pd.Series(0.0, index=categories)
    for _, row in rows[rows.exchange_type == "technosphere"].iterrows():
        if row.input_is == "foreground":
            per_unit = cumulative_impact(case_exchanges, row.input_name, background, memory)
        else:
            key = (row.input_name, row.input_reference_product, row.input_location)
            per_unit = background.loc[key, categories]
        total += row.amount * per_unit
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


# %% Calculate, scenario by scenario
for scenario in s.SCENARIOS:
    background = pd.read_csv(s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv")
    background = background.set_index(["name", "reference product", "location"])

    rows = []
    for case_id, case_exchanges in exchanges.groupby("case_id"):
        ends = end_of_each_module(case_exchanges)
        memory = {}
        previous = pd.Series(0.0, index=categories)          # cumulative impact before A1–A3: nothing
        for module in s.MODULES:
            cumulative = cumulative_impact(case_exchanges, ends[module], background, memory)
            rows.append({"case_id": case_id, "module": module, **(cumulative - previous).to_dict()})
            previous = cumulative
    modules = pd.DataFrame(rows)

    out = s.STEPS_FOLDER / f"1c_lcia_modules_{scenario}.csv"
    modules.to_csv(out, index=False)
    print(f"{scenario}: {modules.case_id.nunique()} cases x {len(s.MODULES)} modules. Saved {out}")


# %% Look at the result: climate change per module, today
today = pd.read_csv(s.STEPS_FOLDER / "1c_lcia_modules_today.csv")
today.pivot(index="case_id", columns="module", values="climate change")[s.MODULES].round(3)
