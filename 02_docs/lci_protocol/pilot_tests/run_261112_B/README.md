# Test kit: baseline LCI protocol

A pilot to see whether two independent AI runs of the protocol give the same LCI for the same material.

## Pilot materials

| Material | Function | What it tests |
|---|---|---|
| OSB/3 | F06 floor or roof deck panel (indoor) | finished product likely in ecoinvent (D1 yes); national transport; prefab |
| Hempcrete blocks | F07 interior partition wall (indoor) | probably not in ecoinvent, so built from constituents (D5); no product standard; end-of-life category by heaviest constituent |
| Cork board | F10 exterior rainscreen cladding (outdoor) | EU or global transport; outdoor maintenance (B2); bio-based end of life |

None of the three is used as a worked example in `protocol.md`, so a run cannot copy an answer from it.

## What's here

| File | What it is |
|---|---|
| `protocol.md` | The protocol, exported from the flowchart (12 Nov 2026) |
| `inputs.csv` | The four facts per material, plus the function (outdoor flag, service life) |
| `PROMPT.md` | The instructions to paste into the agent session |
| `templates/` | Empty output files with their columns, and the LCI sheet layout |
| `search_ecoinvent.py` | Read-only search of ecoinvent 3.12 cut-off in your Brightway project; the agent calls it for every dataset search |
| `compare_runs.py` | Compares two runs question by question and dataset by dataset |

## How to run the pilot

1. **Check the search works** in your conda environment with Brightway:
   `python search_ecoinvent.py "oriented strand board"` should list a few activities. Start Claude Code from a
   terminal where that environment is active, so the agent can run the script too.
2. **Copy this folder somewhere outside the repo**, e.g. `~/protocol_test/run_A/`, so the agent cannot read the
   repo's other files (the material list there has an `ecoinvent_candidate` column with dataset guesses).
3. **Open that folder in VS Code**, start Claude Code, and paste `PROMPT.md`.
4. **Repeat in a second copy** (`~/protocol_test/run_B/`) in a new session, with `run_id: run_B` at the bottom of
   the prompt. Optionally use a different model for this run.
5. **Compare:** put both `runs/` folders side by side and run
   `python compare_runs.py run_A/runs/run_A run_B/runs/run_B`.
6. **Read the differences** (`comparison_decisions.csv`, `comparison_datasets.csv`) and both
   `protocol_issues.md` files. Each difference points to a test in the flowchart that needs sharpening.

## Notes

- **Licence:** the agent reads your local ecoinvent copy through Brightway. Dataset names and any values it reads pass
  through the AI model. Check that this fits your ecoinvent licence.
- **EPD check (STEP 3):** this needs an LCA calculation of A1–A3 (GWP-fossil). If the agent cannot run Brightway, it
  writes "not computed" in `epd_check.csv`; the check can be run afterwards.
- **Time:** expect roughly 30–60 minutes of agent work per material, mostly web searches for EPDs.
