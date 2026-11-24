# Baseline LCI protocol: how the 27 baseline LCIs were made with AI agents

The LCIs of the baseline materials were written by AI agents (Claude Code sessions) that followed a fixed, written
protocol step by step, logging every decision. This folder documents the protocol, the tests that shaped it, and the
official run that produced the LCIs in `01_data/01_raw/LCIs/`.

The protocol itself was designed as a flowchart ("Baseline LCI Protocol" artifact on claude.ai) and exported to
`protocol.md` for each run.

## Timeline

| Date | Run | Folder | What it tested | Outcome (see the run's `runs/*/summary.md` and `protocol_issues.md`) |
|---|---|---|---|---|
| 12 Nov 2026 | pilot 1, runs A and B | `pilot_tests/run_261112_A`, `_B` | Do two independent runs give the same LCI? OSB/3, hempcrete blocks, cork board | 2 of 3 failed the ÖKOBAUDAT check; led to the 13 Nov changes |
| 13 Nov 2026 | pilot 2, runs A and B | `pilot_tests/run_261113_A`, `_B` | Simplified inputs (name and delivered state), S2 as a step, stricter D1 | led to the 17 Nov changes |
| 17 Nov 2026 | pilot 3, runs A and B | `pilot_tests/run_261117_A`, `_B` | Inputs prepared by hand (`material_definitions.csv`), predetermined values in a workbook, machine lookup (P1, P2) | led to the 19 Nov changes |
| 19 Nov 2026 | pilot 4, runs A, B and C | `pilot_tests/run_261119_A`, `_B`, `_C` | Approximate-match route (D1b), review when every check fails; run C: D1b without a mass threshold | protocol of 19 Nov fixed for the official run |
| 19 Nov 2026 | **official run** | `official_run/` | All 28 baseline materials, 7 batches of 4, protocol of 19 Nov (D1b without a mass threshold) | LCIs collected into `data/LCI/` of bcic, then checked by hand (`results/overview_copy_with_manual_checks.xlsx`). Straw bale and soft wood fibre board were later dropped; concrete is two LCIs in the model (non-structural, reinforced structural): 27 baselines |

Each pilot folder is a self-contained kit: `PROMPT.md` (what the agent was told), `protocol.md` (the protocol version it
followed), the inputs, `compare_runs.py` (compares two runs) and `runs/` with what the agent produced (LCI sheets,
`decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `protocol_issues.md`, `summary.md`).

## Files in this folder

| Path | What it is |
|---|---|
| `protocol_predetermined_values.xlsx` | the predetermined values the protocol points to (end-of-life defaults, transport, CFF and carbon archetypes, inputs per material); version of the official run |
| `templates/LCI_example_clay_brick_masonry.xlsx` | layout example of an LCI sheet (placeholder values) |
| `Part_C_Annex_II_V2.1_May2020.ods` | JRC list of default CFF parameters (Annex C of the EF method), source of the A values |
| `official_run/protocol.md` | the protocol as run (19 Nov 2026) |
| `official_run/README_official_run.md` | how the official run was launched (scripts, settings, model) |
| `official_run/PROMPT_template.md`, `make_batches.py`, `run_batches.sh`, `collect_results.py`, `search_ecoinvent.py`, `compare_runs.py` | the scripts of the run |
| `official_run/batch_plan.csv`, `logs/` | which material was in which batch; the agents' session logs (cost, model) |
| `official_run/batches/batch_N/` | each batch's prompt, inputs and output (`runs/batch_N/`), including the agents' own work scripts |
| `official_run/results/` | the merged records of all batches: decisions, dataset choices, EPD checks, CFF and carbon inputs, issues, summaries, overview |
| `pilot_tests/decompose_cork_slab.py`, `merge_batches.py`, `inputs_all30_review.csv` | helper files of the pilots |

## Not copied from bcic

- Duplicates that `make_batches.py` copied into every batch (`templates/`, `protocol.md`, the workbook,
  `search_ecoinvent.py`) and every pilot kit (`templates/`, `search_ecoinvent.py`): the copies in this folder are the same.
- Empty `lci_template.xlsx` copies in the run outputs, `cache/` folders and `__pycache__/`.
- Four agent scratch files nested too deep to copy (`batch_5/runs/batch_5/downloads/watlow/*`,
  `batch_5/runs/batch_5/work/summary.json`, `batch_7/runs/batch_7/work/results.json`); they are still in bcic.
- Downloaded documents in `downloads/` folders are kept locally but not in git (third-party PDFs).
