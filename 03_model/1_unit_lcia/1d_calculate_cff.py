"""
Step 1d: apply the circular footprint formula (CFF) of the EU Environmental Footprint method, on both sides:

  - recycled material that goes INTO the product (correction of A1–A3), and
  - material and energy that come OUT of the product at end of life (module D).

Why both sides here. The LCI sheets hold only physical flows. ecoinvent's cut-off datasets give recycled material
without the burden of the product it came from (as if A = 1), while the CFF shares the benefit of recycling between the
user (share A) and the supplier (share 1 - A). Applying the CFF on one side only would count part of the benefit twice,
so this script applies it on both sides, with the same parameters (cff_archetypes.csv).

1. Recycled content, per kg of product (added to A1–A3, reported on its own row):

     correction = m_recycled x (1 - A) x (Qsin/Qp x E_virgin - E_recycled)

     m_recycled   kg of the archetype's recycled material in the A1–A3 inventory of the case (step 1c), e.g. the
                  reclaimed wood of RAW timber or the scrap-based steel of structural steel
     E_virgin     impact of 1 kg of the virgin material it stands in for (e.g. virgin sawnwood, converter steel)
     E_recycled   impact of 1 kg of the recycled material, as the LCI uses it

   With the correction, the recycled input costs A x E_recycled + (1 - A) x Qsin/Qp x E_virgin, as in the CFF.
   An archetype without a recycled material (empty in cff_archetypes.csv) gets no correction.

2. Module D, per kg of product at end of life (both negative = a benefit):

     material credit = -(1 - A) x (recycling share + reuse share) x (Qsout/Qp) x E_avoided product
     energy credit   = -(1 - B) x incineration share x LHV x (X_heat x E_heat + X_el x E_el / 3.6)

   A, Qsout/Qp, B, LHV (MJ/kg), X_heat, X_el and the avoided products come from the archetype; the shares from
   cff_inputs.csv; /3.6 turns MJ of electricity into kWh. Reuse is credited like recycling.

A case made of parts that belong to different archetypes (reinforced concrete: concrete and steel) has one row per part
in cff_inputs.csv, with its mass share; module D of the parts is weighted by mass share and added up.

Input:  01_data/01_raw/cff_and_carbon_inputs/cff_inputs.csv       (archetype, mass share, end-of-life shares)
        01_data/01_raw/method_constants/cff_archetypes.csv         (A, Q, B, LHV, efficiencies, the datasets used)
        01_data/01_raw/method_constants/cff_datasets.csv           (the ecoinvent dataset behind each name)
        01_data/02_processed/unit_lcia_steps/1c_inventory_by_module.csv
        01_data/02_processed/unit_lcia_steps/1b_background_impacts_<scenario>.csv
Output: 01_data/02_processed/unit_lcia_steps/1d_cff_<scenario>.csv
        (per case two rows, 'A1–A3 recycled content (CFF)' and 'D', one column per impact category)
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

categories = list(pd.read_csv(s.STEPS_FOLDER / "1b_impact_categories.csv").impact_category)
cff_inputs = pd.read_csv(s.CFF_AND_CARBON_FOLDER / "cff_inputs.csv")
archetypes = pd.read_csv(s.METHOD_CONSTANTS_FOLDER / "cff_archetypes.csv").set_index("archetype")
datasets = pd.read_csv(s.METHOD_CONSTANTS_FOLDER / "cff_datasets.csv").set_index("item")
inventory = pd.read_csv(s.STEPS_FOLDER / "1c_inventory_by_module.csv")
cases = sorted(inventory.case_id.unique())
DATASET = ["name", "reference product", "location", "unit"]


# %% Checks on cff_inputs.csv: one or more rows per case, mass shares and end-of-life shares add up to 1
missing = set(cases) - set(cff_inputs.case_id)
if missing:
    raise ValueError(f"No row in cff_inputs.csv for: {sorted(missing)}")

mass_shares = cff_inputs.groupby("case_id").mass_share.sum()
wrong = mass_shares[(mass_shares - 1).abs() > 1e-6]
if len(wrong):
    raise ValueError(f"Mass shares in cff_inputs.csv do not add up to 1 for: {wrong.to_dict()}")

route_total = cff_inputs[["recycling_share", "reuse_share", "incineration_share", "landfill_share"]].sum(axis=1)
wrong = cff_inputs[(route_total - 1).abs() > 1e-6]
if len(wrong):
    raise ValueError(f"End-of-life shares in cff_inputs.csv do not add up to 1 for: {list(wrong.case_id)}")


# %% Functions: look up a dataset named in the archetype table
def is_empty(value):
    return not isinstance(value, str) or value.strip() == ""


def dataset_key(item):
    """(name, reference product, location, unit) of a name in the archetype table."""
    d = datasets.loc[item]
    return tuple(d[c] for c in DATASET)


def impact_of(item, background):
    """Impact of 1 unit (Series over the impact categories) of the dataset behind a name; 0 if the name is empty."""
    if is_empty(item):
        return pd.Series(0.0, index=categories)
    return background.loc[dataset_key(item), categories].astype(float)


# %% How much recycled material each case uses in A1–A3 (from the inventory of step 1c)
a1_a3 = inventory[inventory.module == "A1–A3"].set_index(["case_id"] + DATASET).amount
recycled_items = {item for item in archetypes["recycled material"] if not is_empty(item)}


def kg_recycled(case_id, item):
    key = (case_id,) + dataset_key(item)
    return a1_a3.get(key, 0.0)


recycled_use = pd.DataFrame([{"case_id": c, "recycled material": i, "kg per kg of product": kg_recycled(c, i)}
                             for c in cases for i in recycled_items])
recycled_use = recycled_use[recycled_use["kg per kg of product"] != 0]
print("Cases with recycled material in A1–A3:")
recycled_use


# %% Check: every recycled material in an LCI belongs to one of the case's own archetypes (else it is not corrected)
for _, row in recycled_use.iterrows():
    own = set(archetypes.loc[cff_inputs[cff_inputs.case_id == row.case_id].cff_archetype, "recycled material"])
    if row["recycled material"] not in own:
        print(f"  WARNING {row.case_id} uses '{row['recycled material']}', which is not the recycled material of its "
              f"archetype(s): no CFF correction for it")


# %% Calculate, scenario by scenario
for scenario in s.SCENARIOS:
    background = pd.read_csv(s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv").set_index(DATASET)
    heat = impact_of("avoided heat", background)               # per MJ
    electricity = impact_of("avoided electricity", background)  # per kWh

    rows = []
    for _, part in cff_inputs.iterrows():                       # one row per case, or per part of a case
        a = archetypes.loc[part.cff_archetype]

        # 1. recycled content (A1–A3): only for the archetype's recycled material, in the kg the LCI uses
        if is_empty(a["recycled material"]):
            recycled_content = pd.Series(0.0, index=categories)
        else:
            m = kg_recycled(part.case_id, a["recycled material"])
            recycled_content = m * (1 - a["A"]) * (a["Qsin/Qp"] * impact_of(a["virgin material"], background)
                                                   - impact_of(a["recycled material"], background))
        rows.append({"case_id": part.case_id, "module": s.CFF_RECYCLED_CONTENT, **recycled_content.to_dict()})

        # 2. module D: material credit + energy credit, for the mass share of this part
        recycled_share = part.recycling_share + part.reuse_share
        material_credit = (-(1 - a["A"]) * recycled_share * a["Qsout/Qp"]
                           * impact_of(a["avoided primary material"], background))
        energy_credit = (-(1 - a["B"]) * part.incineration_share * a["LHV (MJ/kg)"]
                         * (a["X heat"] * heat + a["X electricity"] * electricity / 3.6))
        module_d = part.mass_share * (material_credit + energy_credit)
        rows.append({"case_id": part.case_id, "module": s.MODULE_D, **module_d.to_dict()})

    # add up the parts of each case
    cff = pd.DataFrame(rows).groupby(["case_id", "module"], as_index=False)[categories].sum()

    out = s.STEPS_FOLDER / f"1d_cff_{scenario}.csv"
    cff.to_csv(out, index=False)
    print(f"{scenario}: recycled content and module D of {cff.case_id.nunique()} cases. Saved {out}")


# %% Look at the result: climate change, today
today = pd.read_csv(s.STEPS_FOLDER / "1d_cff_today.csv")
today.pivot(index="case_id", columns="module", values="climate change").round(3)
