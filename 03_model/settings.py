"""
Settings shared by all scripts of the model: folder paths, the Brightway project, the two scenarios and the impact
method. If something needs to change (a folder, a database name), change it here and nowhere else.
"""
from pathlib import Path

# ── Folders ─────────────────────────────────────────────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parents[1]           # the material_function_explorer folder

RAW_DATA = REPO / "01_data" / "01_raw"
LCI_FOLDER = RAW_DATA / "LCIs"                       # one Excel LCI sheet per case (27 baselines + 8 RAW cases)
CFF_AND_CARBON_FOLDER = RAW_DATA / "cff_and_carbon_inputs"
METHOD_CONSTANTS_FOLDER = RAW_DATA / "method_constants"

PROCESSED_DATA = REPO / "01_data" / "02_processed"
STEPS_FOLDER = PROCESSED_DATA / "unit_lcia_steps"    # intermediate tables of component 1, one per script

RESULTS_FOLDER = REPO / "04_results"

# ── Brightway ───────────────────────────────────────────────────────────────────────────────────────────────────────
# Only script 1b uses Brightway. The project holds ecoinvent 3.12 cut-off and the premise 2050 database.
BRIGHTWAY_PROJECT = "biobased_construction_impact_calculator"

# The database the LCI sheets point to for every background input.
LCI_BACKGROUND_DATABASE = "ecoinvent-3.12-cutoff"

# The two scenarios: name used in the file names -> Brightway database used as background.
# 2050 = premise, IMAGE SSP2-L, 2050 (the same scenario as in the bcic repo).
SCENARIOS = {
    "today": "ecoinvent-3.12-cutoff",
    "2050": "premise-image-ssp2-l-2050",
}

# Impact method: every Brightway method whose name starts with these two parts (25 EF 3.1 categories).
METHOD_FAMILY = ("ecoinvent-3.12", "EF v3.1")

# ── Life cycle modules (EN 15804), in the order of the chain in the LCI sheets ─────────────────────────────────────
MODULES = ["A1–A3", "A4", "A5", "C1", "C2", "C3–C4"]

# The two parts of the circular footprint formula (step 1d), reported as their own rows next to the modules:
# the correction of A1–A3 for recycled input, and module D.
CFF_RECYCLED_CONTENT = "A1–A3 recycled content (CFF)"
MODULE_D = "D"

# All rows of the unit impact tables, in the order they are shown.
ALL_MODULES = ["A1–A3", CFF_RECYCLED_CONTENT, "A4", "A5", "C1", "C2", "C3–C4", MODULE_D]
