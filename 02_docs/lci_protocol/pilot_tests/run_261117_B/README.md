# Test kit: baseline LCI protocol, 17 Nov version

A third pilot: do two independent AI runs of the 17 Nov protocol give the same LCI for the same material? The main new
thing to test is the machine lookup in P1 (energy) and P2 (wear), which replaced the archetype library.

## What changed since the 13 Nov kit

| Change | Where |
|---|---|
| The input is prepared by hand: constituents (kg per kg) and manufacturing steps (kg processed per kg), with sources. The agent no longer researches the composition or the steps | `material_definitions.csv`, INPUT |
| Predetermined values live in the workbook only; the protocol says which sheet to read | `protocol_predetermined_values.xlsx` |
| D1 yes → CHECK 1; fail or D1 no → build from scratch; CHECK 2 fails → FLAG (no third route) | D1, CHECK 1, CHECK 2, FLAG |
| P1: machine power ÷ throughput = kWh per kg; median of three machines; fixed electricity and heat datasets | P1 · ENERGY |
| P2: machine mass × h per kg ÷ machine life = kg of machine per kg | P2 · WEAR |
| Steps tagged "no energy" in the input get no machine rows | P1, `material_definitions.csv` |
| End-of-life route from the NMD key; waste treatment W1, else the fallback sheet | C2 · ROUTE, W1, W2 |
| Module D: the agent only assigns the CFF archetype and the carbon archetype per constituent | `cff_inputs.csv`, `bioc_inputs.csv` |
| "Unclear" now takes the lower-impact branch | all |

## Materials

The same three as on 12 and 13 Nov, so results can be compared across protocol versions as well as between runs.

| Material | What it tests now |
|---|---|
| OSB/3 | D1 with a constituent match (strands + PMDI/MUF + paraffin wax) and CHECK 1. If D1 is no, 6 machine steps: the heaviest P1/P2 test. One step tagged "no energy" |
| Hempcrete blocks | built from scratch: P1 for mixing and pressing, a "no energy" curing step; bio-C with a mixed constituent list (hemp shiv and lime); no ÖKOBAUDAT dataset listed in `material_overview` |
| Cork board | D1 no (resin binder in ecoinvent); P1 with a thermal machine (autoclave → heat row); input with 6 % loss (1.06 kg) |

## What's here

| File | What it is |
|---|---|
| `protocol.md` | The protocol, exported from the flowchart (17 Nov 2026) |
| `material_definitions.csv` | The input for the three materials, copied from sheet `input_definitions` |
| `protocol_predetermined_values.xlsx` | The workbook, copy of 17 Nov |
| `PROMPT.md` | The instructions to paste into the agent session (run_id already filled in) |
| `templates/` | Empty output files with their columns, and the LCI sheet layout |
| `search_ecoinvent.py` | Read-only search of ecoinvent 3.12 cut-off in your Brightway project |
| `compare_runs.py` | Compares two runs: decisions, datasets, machine values, archetypes and ÖKOBAUDAT checks |

## How to run

1. Open this folder in VS Code, start Claude Code from a terminal where `brightway_env` is active, and paste `PROMPT.md`.
2. Do the same in the other kit (`run_261117_B`) in a new session. Optionally use a different model there.
3. Compare: from `~/protocol_test`, run
   `python run_261117_A/compare_runs.py run_261117_A/runs/run_A run_261117_B/runs/run_B`.
4. Read the `comparison_*.csv` files (written to `run_261117_A/runs/`), both `epd_check.csv` and both
   `protocol_issues.md`. Each difference points to a step in the flowchart that needs sharpening.
   New this time: `comparison_machines.csv` shows, per step, the machine each run chose and how far its values differ.

## Notes

- **Licence:** the agent reads your local ecoinvent copy through Brightway; dataset names and values pass through the AI model.
- **Workbook:** the kit holds a copy. If you change the workbook in the repo before running, copy it in again.
- **Known open input:** the hempcrete shares are marked "to be sourced" in `material_overview` (they may be volume, not mass).
- **Time:** expect longer than on 13 Nov, because each machine step needs three datasheets. Roughly 45–90 minutes per material (estimate).
