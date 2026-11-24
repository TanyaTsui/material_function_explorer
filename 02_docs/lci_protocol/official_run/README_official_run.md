# Official baseline LCI run (28 materials)

Runs the baseline LCI protocol (`protocol.md`, 19 Nov 2026, D1b without a mass threshold) for all 28 baseline
materials in `../protocol_predetermined_values.xlsx`, in 7 batches of 4 materials, and puts the finished sheets in
`data/LCI/baseline_<material_id>.xlsx`.

## How to start

1. Open a terminal, activate the environment (`conda activate brightway_env`) and go to this folder
   (full path under "How to run" below).
2. `./run_batches.sh --check` tests the setup (model, python, Claude Code login, a real ecoinvent search). It costs nothing.
3. `./run_batches.sh 3 1` runs batch 1 only (sawn softwood, cork, fibre cement, stone wool). The first number is how
   many batches run at the same time; the numbers after it are the batches to run. Check how far your usage meter
   moved: the full run is about 7× that.
4. Then `./run_batches.sh 3 2 3 4 5 6 7` runs the other six batches, 3 at a time. On a Mac, put `caffeinate -i` in
   front so the computer stays awake.
5. At the end, `python collect_results.py` copies the sheets to `data/LCI/` and merges the logs.

More detail (API key check, interruptions, environment, which model ran) is under "How to run".

| File | What it is |
|---|---|
| `protocol.md` | The protocol, exported from the flowchart (artifact version `1795095325-1875`). Re-export here if the flowchart changes, then run `make_batches.py` again |
| `PROMPT_template.md` | The agent prompt, same as the pilot kits; `{run_id}` becomes `batch_N` |
| `templates/` | Empty output files and `lci_template.xlsx` (copied into every batch) |
| `search_ecoinvent.py` | Read-only ecoinvent 3.12 cut-off search in the Brightway project |
| `make_batches.py` | Builds `batches/batch_1 … batch_7` (a self-contained kit each) and `batch_plan.csv` from the workbook |
| `run_batches.sh` | Launches the batches, a few at a time, each as its own non-interactive Claude Code session |
| `collect_results.py` | Copies the LCIs to `data/LCI/`, merges the logs into `results/`, writes `results/overview.csv`, prints costs |
| `compare_runs.py` | Compares two runs (as in the pilots), e.g. to rerun a few materials as a reproducibility check |
| `batch_plan.csv` | Which material is in which batch, with its number of constituents and steps |

`batches/` and `logs/` are generated and git-ignored. `results/` is not: commit it if you want the decision logs
in the repo.

## How to run

Everything runs in one terminal (Terminal, or the integrated terminal in VS Code: both work; the agents are
background sessions, not VS Code windows).

1. Go to this folder:
   `cd "/Users/tsuitpy/Library/CloudStorage/OneDrive-UniversiteitLeiden/01_Projects/RAW/biobased_construction_impact_calculator/protocol/official_run"`
2. Check the API key is not set: `echo "${ANTHROPIC_API_KEY:+SET}"`. Nothing printed = not set (good); `SET` = set,
   run `unset ANTHROPIC_API_KEY` (and remove its `export` line from `~/.zshrc` if it is there). The script also
   refuses to start if it is set. This key (Anthropic Console, pay as you go) is separate from your claude.ai plan
   and the usage credits you bought; Claude Code must use your plan login instead (`claude` then `/status` shows it).
3. Test the setup, free: `./run_batches.sh --check`. It prints the model, the python path, the Claude Code version,
   and runs a real ecoinvent search. If it says `Setup OK`, the agents will find ecoinvent too.
4. Run batch 1 alone to measure the cost: `./run_batches.sh 3 1`. Check how far your usage meter moved; the full run
   is about 7× that.
5. Then the rest, 2–3 at a time: `./run_batches.sh 3 2 3 4 5 6 7`. On macOS: `caffeinate -i ./run_batches.sh 3 2 3 4 5 6 7`
   so the computer stays awake.
6. If a usage limit stops a batch, wait for the reset (or let it continue on your usage credits) and run the same
   command again. Finished batches are skipped; an interrupted batch continues with its remaining materials.
7. `python collect_results.py` (any python with pandas). Existing `data/LCI/baseline_*.xlsx` are not overwritten
   unless you pass `--force`.
8. Read `results/overview.csv` (route used, flagged or not), `results/protocol_issues_all.md` and
   `results/summaries_all.md`.

Settings: model `claude-sonnet-5-5` (override with `MODEL=…`); tools Bash, Read, Write, Edit, Glob, Grep, WebSearch,
WebFetch (override with `CLAUDE_TOOLS=…`). The agent can run shell commands without asking inside its batch folder;
the prompt restricts it to the files there.

**Environment.** The launcher uses `~/miniconda3/envs/brightway_env/bin/python3` by its full path (override with
`PYTHON=…`), tests it with a real `search_ecoinvent.py` call, and tells every agent to run Python with that full path.
So it does not depend on which conda environment is active, or on what the agent's own shell loads. The Brightway
project folder is printed by `--check`.

**Which model ran.** `collect_results.py` prints the models listed in each batch's log. Expect `claude-sonnet-5-5`;
Claude Code may also use a smaller model for helper tasks such as summarising web pages.

## Notes

- Material ids are the workbook names in snake case (`sawn_hardwood_oak`, `pvc_u`, `clay_brick_masonry`); `OSB/3` is `osb3`
  as in the pilots.
- Output per batch: `batches/batch_N/runs/batch_N/` (LCI sheets, logs, `protocol_issues.md`, `summary.md`).
- Costs in `logs/batch_N.json` are Claude Code's client-side estimate at list prices; on a plan they are not a charge.
- The pilot run (A, B, C) ran in VS Code sessions; this launcher was tested with a stand-in agent only. The real
  `claude -p` call is not yet tested, so watch batch 1.
