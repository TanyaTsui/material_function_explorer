"""
Step 1g: check the unit impact tables, and draw one figure to look at them.

Checks (the script stops with an error if one of the first three fails):
  1. Both scenarios have all cases, all modules and no empty values.
  2. The total table is the sum of the modules in the by-module table.
  3. The sum of modules A1–A3 to C3–C4 (step 1c, without the CFF rows of step 1d) equals an independent calculation:
     the whole foreground of each LCI solved as a system of linear equations (the usual matrix method of LCA) instead
     of block by block as in step 1c.
  4. For information: GWP-fossil of A1–A3 today compared with the value the protocol agents calculated for the same
     material during the official run (epd_check.csv). The two should be close; a large gap points to an LCI that
     was changed after the run, or to a different characterisation.

Output: 04_results/tables/check_gwp_fossil_a1a3_vs_protocol_run.csv
        04_results/figures/unit_climate_change_by_module_today.png
"""
# %% Setup
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    HERE = Path(__file__).resolve().parent
except NameError:
    HERE = Path.cwd()
sys.path.append(str(HERE.parent))
import settings as s

categories = list(pd.read_csv(s.STEPS_FOLDER / "1b_impact_categories.csv").impact_category)
exchanges = pd.read_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv")
cases = sorted(exchanges.case_id.unique())
(s.RESULTS_FOLDER / "tables").mkdir(parents=True, exist_ok=True)
(s.RESULTS_FOLDER / "figures").mkdir(parents=True, exist_ok=True)


# %% Check 1: all cases, all modules, no empty values
for scenario in s.SCENARIOS:
    by_module = pd.read_csv(s.PROCESSED_DATA / f"unit_impacts_by_module_{scenario}.csv")
    total = pd.read_csv(s.PROCESSED_DATA / f"unit_impacts_total_{scenario}.csv")
    assert sorted(total.case_id) == cases, f"{scenario}: the total table does not have all {len(cases)} cases"
    expected_rows = len(cases) * (len(s.ALL_MODULES) * len(categories) + 1)      # + 1: the stored CO2 row
    assert len(by_module) == expected_rows, f"{scenario}: {len(by_module)} rows in the by-module table, " \
                                            f"expected {expected_rows}"
    assert not by_module.value.isna().any(), f"{scenario}: empty values in the by-module table"
    assert not total.isna().any().any(), f"{scenario}: empty values in the total table"
print("Check 1 passed: all cases, modules and categories are there, no empty values.")


# %% Check 2: total = sum of the modules
for scenario in s.SCENARIOS:
    by_module = pd.read_csv(s.PROCESSED_DATA / f"unit_impacts_by_module_{scenario}.csv")
    total = pd.read_csv(s.PROCESSED_DATA / f"unit_impacts_total_{scenario}.csv").set_index("case_id")
    summed = (by_module[by_module.module != "in product"]
              .groupby(["case_id", "impact_category"]).value.sum().unstack())
    for category in categories:
        column = [c for c in total.columns if c.startswith(category + " [")][0]
        assert np.allclose(summed[category], total[column], rtol=1e-9, atol=1e-12), f"{scenario}: {category}"
print("Check 2 passed: the total table is the sum of the modules.")


# %% Check 3: modules A1–A3 to C3–C4 = the foreground solved as one system of equations
def solve_foreground(case_exchanges, background):
    """Cradle-to-grave impact of 1 kg, with the matrix method: technosphere matrix A of the foreground activities,
    demand f = 1 unit of the last activity, scaling vector x = A^-1 f, impact = background inputs x impacts."""
    activities = list(case_exchanges[case_exchanges.exchange_type == "production"].activity)
    position = {a: i for i, a in enumerate(activities)}
    A = np.zeros((len(activities), len(activities)))
    for row in case_exchanges.itertuples():
        if row.exchange_type == "production":
            A[position[row.activity], position[row.activity]] += row.amount
        elif row.input_is == "foreground":
            A[position[row.input_name], position[row.activity]] -= row.amount
    used = set(case_exchanges[case_exchanges.input_is == "foreground"].input_name)
    last = [a for a in activities if a not in used and
            case_exchanges[case_exchanges.activity == a].activity_module.iloc[0] == s.MODULES[-1]][0]
    f = np.zeros(len(activities))
    f[position[last]] = 1
    x = np.linalg.solve(A, f)
    impact = pd.Series(0.0, index=categories)
    for row in case_exchanges[case_exchanges.input_is == "background"].itertuples():
        key = (row.input_name, row.input_reference_product, row.input_location)
        impact += x[position[row.activity]] * row.amount * background.loc[key, categories].astype(float)
    return impact


for scenario in s.SCENARIOS:
    background = pd.read_csv(s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv")
    background = background.set_index(["name", "reference product", "location"])
    modules = pd.read_csv(s.STEPS_FOLDER / f"1c_lcia_modules_{scenario}.csv")
    block_by_block = modules.groupby("case_id")[categories].sum()
    for case_id, case_exchanges in exchanges.groupby("case_id"):
        matrix = solve_foreground(case_exchanges, background)
        assert np.allclose(block_by_block.loc[case_id], matrix, rtol=1e-6, atol=1e-12), f"{scenario}: {case_id}"
print("Check 3 passed: block by block (step 1c) and the matrix method give the same cradle-to-grave impact.")


# %% Check 4 (information): GWP-fossil A1–A3 today vs the value of the protocol run
fossil = [c for c in categories if c.startswith("climate change") and "fossil" in c][0]
modules_today = pd.read_csv(s.STEPS_FOLDER / "1c_lcia_modules_today.csv")
ours = modules_today[modules_today.module == "A1–A3"].set_index("case_id")[fossil]

protocol = pd.read_csv(s.REPO / "02_docs/lci_protocol/official_run/results/epd_check.csv")
for column in ["our_gwp_fossil_a1a3", "epd_median"]:                    # a few cells hold text, e.g. "n/a"
    protocol[column] = pd.to_numeric(protocol[column], errors="coerce")
protocol = protocol.dropna(subset=["our_gwp_fossil_a1a3"]).groupby("material_id").last()   # last check of each material
protocol.index = "baseline_" + protocol.index

comparison = pd.DataFrame({
    "this model (today)": ours,
    "protocol run": protocol["our_gwp_fossil_a1a3"],
    "EPD median (ÖKOBAUDAT)": protocol["epd_median"],
}).loc[lambda d: d.index.str.startswith("baseline_")]
comparison["ratio model / protocol run"] = comparison["this model (today)"] / comparison["protocol run"]
comparison.to_csv(s.RESULTS_FOLDER / "tables" / "check_gwp_fossil_a1a3_vs_protocol_run.csv")
print(f"Check 4: GWP-fossil A1–A3 ({fossil}), kg CO2-eq per kg")
comparison.round(3)


# %% Figure: climate change per module, today
by_module = pd.read_csv(s.PROCESSED_DATA / "unit_impacts_by_module_today.csv")
cc = by_module[by_module.impact_category == "climate change"].pivot(index="case_id", columns="module", values="value")
cc = cc[s.ALL_MODULES]
cc = cc.loc[cc.sum(axis=1).sort_values().index]

fig, ax = plt.subplots(figsize=(8, 10))
left_pos = np.zeros(len(cc))
left_neg = np.zeros(len(cc))
colors = plt.cm.tab10.colors
for i, module in enumerate(cc.columns):
    values = cc[module].values
    left = np.where(values >= 0, left_pos, left_neg)
    ax.barh(cc.index, values, left=left, color=colors[i], label=module)
    left_pos += np.where(values >= 0, values, 0)
    left_neg += np.where(values < 0, values, 0)
ax.plot(cc.sum(axis=1).values, range(len(cc)), "k|", markersize=10, label="net")
ax.axvline(0, color="grey", linewidth=0.5)
ax.set_xlabel("climate change, kg CO2-eq per kg of product (today)")
ax.legend(loc="lower right", fontsize=8)
ax.set_title("Unit impact per module (biogenic CO2 stored not included)")
fig.tight_layout()
fig.savefig(s.RESULTS_FOLDER / "figures" / "unit_climate_change_by_module_today.png", dpi=200)
plt.show()
