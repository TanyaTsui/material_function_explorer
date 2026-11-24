"""
Step 1d: calculate module D (benefits beyond the system boundary) of 1 kg of each case, with the circular footprint
formula (CFF) of the EU Environmental Footprint method.

Two credits, per kg of product at end of life (both negative = a benefit):

  material credit = -(1 - A) x (recycling share + reuse share) x (Qsout / Qp) x impact of 1 kg of avoided product
  energy credit   = -(1 - B) x incineration share x LHV x (X_heat x impact of 1 MJ heat + X_el x impact of 1 kWh el / 3.6)

  A          allocation factor between the supplier and the user of recycled material (archetype table)
  Qsout/Qp   quality of the recycled material relative to the primary material it replaces (archetype table)
  B          allocation factor of energy recovery, 0 in the EF method (archetype table)
  LHV        lower heating value of the material, MJ per kg (archetype table)
  X_heat, X_el  efficiencies of heat and electricity recovery in the incinerator (archetype table)
  /3.6       MJ of electricity to kWh

A case made of parts that belong to different archetypes (reinforced concrete: concrete and steel) has one row per part
in cff_inputs.csv, each with its mass share; the credits of the parts are weighted by mass share and added up. All
other cases have one row with mass share 1.

Reuse is credited like recycling, as in the RAW LCI sheets (cut-off). The recycled content (R1) term of the CFF is not
applied: the LCI datasets already contain the recycled content of the product (see 02_docs/methods_unit_lcia.md).

Input:  01_data/01_raw/cff_and_carbon_inputs/cff_inputs.csv       (archetype, mass share and end-of-life shares)
        01_data/01_raw/method_constants/cff_archetypes.csv         (A, Q, LHV, efficiencies, avoided products)
        01_data/01_raw/method_constants/avoided_datasets.csv       (the ecoinvent dataset of each avoided product)
        01_data/02_processed/unit_lcia_steps/1b_background_impacts_<scenario>.csv
Output: 01_data/02_processed/unit_lcia_steps/1d_module_d_<scenario>.csv
        (one row per case, one column per impact category)
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
avoided = pd.read_csv(s.METHOD_CONSTANTS_FOLDER / "avoided_datasets.csv").set_index("avoided_item")

# every case of the LCIs needs a row in cff_inputs.csv
cases = set(pd.read_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv").case_id)
missing = cases - set(cff_inputs.case_id)
if missing:
    raise ValueError(f"No row in cff_inputs.csv for: {sorted(missing)}")

# the mass shares of the rows of each case add up to 1
mass_shares = cff_inputs.groupby("case_id").mass_share.sum()
wrong = mass_shares[(mass_shares - 1).abs() > 1e-6]
if len(wrong):
    raise ValueError(f"Mass shares in cff_inputs.csv do not add up to 1 for: {wrong.to_dict()}")

# the four end-of-life shares of each row add up to 1 (fractions, not %)
route_total = cff_inputs[["recycling_share", "reuse_share", "incineration_share", "landfill_share"]].sum(axis=1)
wrong = cff_inputs[(route_total - 1).abs() > 1e-6]
if len(wrong):
    raise ValueError(f"End-of-life shares in cff_inputs.csv do not add up to 1 for: {list(wrong.case_id)}")


# %% Function: impact of 1 unit of an avoided product
def impact_of(avoided_item, background):
    """Impact per unit (Series over the impact categories) of the dataset behind an avoided product; 0 if none."""
    if not isinstance(avoided_item, str) or avoided_item == "":
        return pd.Series(0.0, index=categories)
    d = avoided.loc[avoided_item]
    return background.loc[(d["name"], d["reference product"], d["location"]), categories].astype(float)


# %% Calculate, scenario by scenario
for scenario in s.SCENARIOS:
    background = pd.read_csv(s.STEPS_FOLDER / f"1b_background_impacts_{scenario}.csv")
    background = background.set_index(["name", "reference product", "location"])
    heat = impact_of("avoided heat", background)               # per MJ
    electricity = impact_of("avoided electricity", background)  # per kWh

    rows = []
    for _, part in cff_inputs.iterrows():                       # one row per case, or per part of a case
        a = archetypes.loc[part.cff_archetype]

        recycled_share = part.recycling_share + part.reuse_share
        material_credit = (-(1 - a["A"]) * recycled_share * a["Qsout/Qp"]
                           * impact_of(a["avoided primary material"], background))

        energy_credit = (-(1 - a["B"]) * part.incineration_share * a["LHV (MJ/kg)"]
                         * (a["X heat"] * heat + a["X electricity"] * electricity / 3.6))

        credit_per_kg_of_case = part.mass_share * (material_credit + energy_credit)
        rows.append({"case_id": part.case_id, **credit_per_kg_of_case.to_dict()})

    # add up the parts of each case
    module_d = pd.DataFrame(rows).groupby("case_id", as_index=False)[categories].sum()
    module_d.insert(1, "module", "D")

    out = s.STEPS_FOLDER / f"1d_module_d_{scenario}.csv"
    module_d.to_csv(out, index=False)
    print(f"{scenario}: module D of {len(module_d)} cases. Saved {out}")


# %% Look at the result: climate change, today
pd.read_csv(s.STEPS_FOLDER / "1d_module_d_today.csv")[["case_id", "climate change"]].round(3)
