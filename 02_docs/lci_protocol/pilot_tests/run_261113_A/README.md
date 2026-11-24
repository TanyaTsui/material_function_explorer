# Test kit: baseline LCI protocol, 13 Nov version

A second pilot: do two independent AI runs of the simplified protocol give the same LCI for the same material, and
do the changes fix the problems found in the 12 Nov pilot?

## What changed since the 12 Nov kit

| Change | Where |
|---|---|
| Two inputs only: name and delivered state. No strength class, standard, element type or function | `inputs.csv`, INPUT |
| S2 is a step, not a decision: list the manufacturing steps from EPD › BREF › study › maker (no EN standards) | S2 |
| D1 matches only if the dataset has the same constituents as S1 (e.g. no extra resin binder) | D1 |
| D5 always builds; D6 proxy removed; a step with no dataset gets the closest processing dataset (TeR 4) | D5 |
| ÖKOBAUDAT check: within ±50 % of the EPD median; if not, one targeted check (units and mass, dataset state, indicator, composition), then recheck or flag | STEP 3, STEP 3 · RECHECK |
| Module B has no rows: B2 and B3 moved to the model, like B4. The sheet runs A1–A3 → A4 → A5 → C1 → C2 → C3–C4 | B1–B7, `lci_template.xlsx` |

## Materials

The same three as on 12 Nov, so results can be compared with the old protocol as well as between runs.

| Material | What it tests now |
|---|---|
| OSB/3 | finished product likely in ecoinvent (D1 yes); the dry-mass check in STEP 3 |
| Hempcrete blocks | built from constituents (D5); end-of-life category by heaviest constituent |
| Cork board | the new D1 constituent test: an ecoinvent dataset with a resin binder should not match a binder-free board |

## What's here

| File | What it is |
|---|---|
| `protocol.md` | The protocol, exported from the flowchart (13 Nov 2026) |
| `inputs.csv` | Name and delivered state per material |
| `PROMPT.md` | The instructions to paste into the agent session (run_id already filled in) |
| `templates/` | Empty output files with their columns, and the LCI sheet layout |
| `search_ecoinvent.py` | Read-only search of ecoinvent 3.12 cut-off in your Brightway project |
| `compare_runs.py` | Compares two runs question by question and dataset by dataset |

## How to run

1. Open this folder in VS Code, start Claude Code from a terminal where `brightway_env` is active, and paste `PROMPT.md`.
2. Do the same in the other kit (`run_261113_B`) in a new session. Optionally use a different model there.
3. Compare: from `~/protocol_test`, run
   `python run_261113_A/compare_runs.py run_261113_A/runs/run_A run_261113_B/runs/run_B`.
4. Read `comparison_decisions.csv`, `comparison_datasets.csv`, both `epd_check.csv` and both `protocol_issues.md`.
   Each difference points to a test in the flowchart that needs sharpening.

## Notes

- **Licence:** the agent reads your local ecoinvent copy through Brightway; dataset names and values pass through the AI model.
- **EPD check:** needs a Brightway calculation of GWP-fossil A1–A3; if the agent cannot run it, it writes "not computed".
- **Time:** roughly 30–60 minutes of agent work per material.
