# Test kit: baseline LCI protocol, 19 Nov version, run C (D1b without a mass threshold)

A third kit for 19 Nov (run C), made after runs A and B. Same protocol as `run_261119_A` and `_B`, with one change: D1b no longer
has a mass threshold on the differing constituents. In runs A and B the cork slab in ecoinvent was rejected at D1b
because its resin binder was 14 % of the input mass (limit was 10 %), so no ecoinvent LCI reached CHECK 2 or the review.
This run tests whether cork now takes the approximate-match route, and what the review picks.

## What changed since runs A and B

| Change | Where |
|---|---|
| D1b test is now two conditions: same product and delivered state, and same main constituent. The share of other constituents that differ is not limited; each difference is logged, and CHECK 2 decides | D1b |
| `protocol.md` is the flowchart export of artifact version 1795095325-1875 | `protocol.md` |

Everything else is as in runs A and B: input, workbook, machine lookup, A4 to C3–C4, module D, the review and `epd_check.csv` columns.

## Background: what changed since the 17 Nov kit (as in runs A and B)

| Change | Where |
|---|---|
| New route between "exact match" and "build from scratch": the finished product in its delivered state, with nearly the same constituents (same main constituent; no limit on the share of differing constituents in run C) | D1b, YES · D2–D4 (approximate match), ROW (approximate match), CHECK 2 |
| Order of routes: D1 exact → CHECK 1 → D1b approximate → CHECK 2 → build from scratch → CHECK 3. Failing a check moves to the next route; the failed LCI is kept for the review | D1, CHECK 1, D1b, CHECK 2, BUILD FROM SCRATCH, CHECK 3 |
| If all routes fail their check, the old FLAG step becomes a review: compare the LCIs of every route tried, keep the one closest to the ÖKOBAUDAT median (distance \|value ÷ median − 1\|, tie: lower value) and flag it | REVIEW · FLAG |
| `epd_check.csv` has new columns `route`, `distance_to_median`, `lci_kept`; `check_id` is CHECK 1, CHECK 2, CHECK 3 or REVIEW | `templates/epd_check.csv`, `PROMPT.md` |

Unchanged from 17 Nov: the input, the workbook, P1/P2 machine lookup, A4 to C3–C4, module D.

## Materials

The same three as on 12 and 13 Nov, so results can be compared across protocol versions as well as between runs. Cork is the main test of the new route: its ecoinvent dataset has a resin binder, so it is not an exact match but should now be an approximate one.

| Material | What it tests now |
|---|---|
| OSB/3 | D1 with a constituent match (strands + PMDI/MUF + paraffin wax) and CHECK 1. If D1 and D1b both fail, 6 machine steps: the heaviest P1/P2 test. One step tagged "no energy" |
| Hempcrete blocks | built from scratch: P1 for mixing and pressing, a "no energy" curing step; bio-C with a mixed constituent list (hemp shiv and lime); no ÖKOBAUDAT dataset listed in `material_overview` |
| Cork board | D1 no (resin binder in ecoinvent), then D1b (the cork slab now qualifies: same main constituent), then CHECK 2 or the build; P1 with a thermal machine (autoclave → heat row); input with 6 % loss (1.06 kg) |

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
2. Run it in one session (run_id run_C). To compare with runs A and B, use `compare_runs.py` on any two runs.
3. Compare: from `~/protocol_test`, run
   `python run_261119_C/compare_runs.py run_261119_A/runs/run_A run_261119_C/runs/run_C`.
4. Read the `comparison_*.csv` files (written to `run_261119_A/runs/`), both `epd_check.csv` and both
   `protocol_issues.md`. Each difference points to a step in the flowchart that needs sharpening.
   New this time: `comparison_machines.csv` shows, per step, the machine each run chose and how far its values differ. For the new route, compare in `comparison_decisions.csv` the D1b answers and the constituents each run counted as different, and in `comparison_epd.csv` which route each run kept.

## Notes

- **Licence:** the agent reads your local ecoinvent copy through Brightway; dataset names and values pass through the AI model.
- **Workbook:** the kit holds a copy. If you change the workbook in the repo before running, copy it in again.
- **Known open input:** the hempcrete shares are marked "to be sourced" in `material_overview` (they may be volume, not mass).
- **Time:** expect longer than on 13 Nov, because each machine step needs three datasheets. Roughly 45–90 minutes per material (estimate).
