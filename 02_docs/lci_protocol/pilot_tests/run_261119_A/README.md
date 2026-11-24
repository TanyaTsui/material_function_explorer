# Test kit: baseline LCI protocol, 19 Nov version

A fourth pilot: do two independent AI runs of the 19 Nov protocol give the same LCI for the same material? The main new
thing to test is the approximate-match route in A1–A3 (D1b, check 2) and the final review when every check fails.

## What changed since the 17 Nov kit

| Change | Where |
|---|---|
| New route between "exact match" and "build from scratch": the finished product in its delivered state, with nearly the same constituents (same main constituent; differing constituents at most 10 % of the mass, our assumption) | D1b, YES · D2–D4 (approximate match), ROW (approximate match), CHECK 2 |
| Order of routes: D1 exact → CHECK 1 → D1b approximate → CHECK 2 → build from scratch → CHECK 3. Failing a check moves to the next route; the failed LCI is kept for the review | D1, CHECK 1, D1b, CHECK 2, BUILD FROM SCRATCH, CHECK 3 |
| If all routes fail their check, the old FLAG step becomes a review: compare the LCIs of every route tried, keep the one closest to the ÖKOBAUDAT median (distance \|value ÷ median − 1\|, tie: lower value) and flag it | REVIEW · FLAG |
| `epd_check.csv` has new columns `route`, `distance_to_median`, `lci_kept`; `check_id` is CHECK 1, CHECK 2, CHECK 3 or REVIEW | `templates/epd_check.csv`, `PROMPT.md` |

Unchanged from 17 Nov: the input, the workbook, P1/P2 machine lookup, A4 to C3–C4, module D.

## Materials

The same three as on 12 and 13 Nov, so results can be compared across protocol versions as well as between runs. Cork is the main test of the new route: its ecoinvent dataset has a resin binder, so it is not an exact match but may be an approximate one.

| Material | What it tests now |
|---|---|
| OSB/3 | D1 with a constituent match (strands + PMDI/MUF + paraffin wax) and CHECK 1. If D1 and D1b both fail, 6 machine steps: the heaviest P1/P2 test. One step tagged "no energy" |
| Hempcrete blocks | built from scratch: P1 for mixing and pressing, a "no energy" curing step; bio-C with a mixed constituent list (hemp shiv and lime); no ÖKOBAUDAT dataset listed in `material_overview` |
| Cork board | D1 no (resin binder in ecoinvent), then D1b: is the binder under 10 % of the mass? Then CHECK 2 or the build; P1 with a thermal machine (autoclave → heat row); input with 6 % loss (1.06 kg) |

## What's here

| File | What it is |
|---|---|
| `protocol.md` | The protocol, exported from the flowchart (19 Nov 2026) |
| `material_definitions.csv` | The input for the three materials, copied from sheet `input_definitions` |
| `protocol_predetermined_values.xlsx` | The workbook, copy of 17 Nov (unchanged) |
| `PROMPT.md` | The instructions to paste into the agent session (run_id already filled in) |
| `templates/` | Empty output files with their columns, and the LCI sheet layout |
| `search_ecoinvent.py` | Read-only search of ecoinvent 3.12 cut-off in your Brightway project |
| `compare_runs.py` | Compares two runs: decisions, datasets, machine values, archetypes and ÖKOBAUDAT checks |

## How to run

1. Open this folder in VS Code, start Claude Code from a terminal where `brightway_env` is active, and paste `PROMPT.md`.
2. Do the same in the other kit (`run_261119_B`) in a new session. Optionally use a different model there.
3. Compare: from `~/protocol_test`, run
   `python run_261119_A/compare_runs.py run_261119_A/runs/run_A run_261119_B/runs/run_B`.
4. Read the `comparison_*.csv` files (written to `run_261119_A/runs/`), both `epd_check.csv` and both
   `protocol_issues.md`. Each difference points to a step in the flowchart that needs sharpening.
   New this time: `comparison_machines.csv` shows, per step, the machine each run chose and how far its values differ. For the new route, compare in `comparison_decisions.csv` the D1b answers and the constituents each run counted as different, and in `comparison_epd.csv` which route each run kept.

## Notes

- **Licence:** the agent reads your local ecoinvent copy through Brightway; dataset names and values pass through the AI model.
- **Workbook:** the kit holds a copy. If you change the workbook in the repo before running, copy it in again.
- **Known open input:** the hempcrete shares are marked "to be sourced" in `material_overview` (they may be volume, not mass).
- **Time:** expect longer than on 13 Nov, because each machine step needs three datasheets. Roughly 45–90 minutes per material (estimate).
