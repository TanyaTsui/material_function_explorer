#!/usr/bin/env bash
# Launch the batches of the official baseline LCI run, a few at a time, each in its own non-interactive
# Claude Code session.
#
#   cd .../biobased_construction_impact_calculator/protocol/official_run
#   ./run_batches.sh --check              # test the setup only (ecoinvent search, claude, login); costs nothing
#   ./run_batches.sh 3 1                  # batch 1 only (3 = how many at a time)
#   ./run_batches.sh 3 2 3 4 5 6 7        # batches 2 to 7, 3 at a time
#   ./run_batches.sh                      # all batches, 3 at a time
#   MODEL=claude-sonnet-5-5 ./run_batches.sh
#   caffeinate -i ./run_batches.sh        # macOS: keep the computer awake
#
# Python: the script uses the brightway_env python by its full path (PYTHON=... overrides it), checks that it can
# search ecoinvent, and tells every agent to run Python with that full path. So it does not matter which conda
# environment is active in the terminal, or what the agent's own shell loads.
#
# A batch whose runs/<batch>/summary.md exists is finished and skipped. A batch that was interrupted (e.g. by a
# usage limit) is continued: the agent is told which materials are already done. Just run the script again.
# Per-batch logs: logs/batch_N.json (result, cost, models used) and logs/batch_N.err.
set -u
cd "$(dirname "$0")"

CHECK=0
if [ "${1:-}" = "--check" ]; then CHECK=1; shift; fi
PAR=${1:-3}; [ $# -gt 0 ] && shift
if [ $# -gt 0 ]; then BATCHES="$*"; else BATCHES=$(ls batches 2>/dev/null | sed 's/batch_//' | sort -n | tr '\n' ' '); fi
[ -z "$BATCHES" ] && { echo "No batches. Run: python make_batches.py"; exit 1; }

MODEL=${MODEL:-claude-sonnet-5-5}
TOOLS=${CLAUDE_TOOLS:-"Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"}
DEFAULT_PY="$HOME/miniconda3/envs/brightway_env/bin/python3"
if [ -n "${PYTHON:-}" ]; then :
elif [ -x "$DEFAULT_PY" ]; then PYTHON="$DEFAULT_PY"
else PYTHON=$(command -v python3 || command -v python); fi
export PYTHON MODEL TOOLS

fail() { echo "CHECK FAILED: $1"; exit 1; }

echo "Model:   $MODEL"
echo "Python:  $PYTHON"
command -v claude >/dev/null || fail "claude (Claude Code) not found on PATH"
echo "Claude:  $(claude --version 2>/dev/null | head -1)"
if [ -n "${ANTHROPIC_API_KEY:-}" ] && [ "${ALLOW_API_KEY:-0}" != "1" ]; then
  fail "ANTHROPIC_API_KEY is set: Claude Code would bill API rates instead of your plan. Run 'unset ANTHROPIC_API_KEY' (and remove it from ~/.zshrc if it is exported there), or set ALLOW_API_KEY=1."
fi
echo "API key: not set (the run uses your Claude plan login)"
"$PYTHON" -c "import bw2data" 2>/dev/null || fail "$PYTHON cannot import bw2data"
first=$(echo $BATCHES | awk '{print $1}')
test -d "batches/batch_$first" || fail "batches/batch_$first does not exist (python make_batches.py)"
out=$(cd "batches/batch_$first" && "$PYTHON" search_ecoinvent.py "cork slab" --limit 2 2>&1)
echo "$out" | grep -q "hits for" || fail "the ecoinvent search did not work. Output: $out"
echo "$out" | grep -q " 0 hits" && fail "ecoinvent search found nothing for 'cork slab': $out"
echo "ecoinvent search OK: $(echo "$out" | head -1)"
BWDIR=$("$PYTHON" -c "import bw2data as b; print(b.projects.dir)" 2>/dev/null)
echo "Brightway project folder: $BWDIR"
mkdir -p logs
if [ "$CHECK" = "1" ]; then echo "Setup OK. Nothing was run."; exit 0; fi

run_one() {
  n=$1; dir="batches/batch_$n"; run="batch_$n"
  [ -d "$dir" ] || { echo "batch_$n: no such batch"; return; }
  if [ -f "$dir/runs/$run/summary.md" ]; then echo "batch_$n: already finished, skipped"; return; fi
  prompt=$(cat "$dir/PROMPT.md")
  prompt="$prompt

ENVIRONMENT: run EVERY Python command with the full path $PYTHON (for example: $PYTHON search_ecoinvent.py \"cork\"), never with plain python or python3: those may not be the environment that has Brightway. Brightway project folder: $BWDIR. Your working folder is the folder you start in; work only there."
  if [ -d "$dir/runs/$run" ]; then
    prompt="$prompt

NOTE: this is a CONTINUATION. An earlier session was interrupted. runs/$run/ already exists. A material is finished if runs/$run/LCI_<material_id>.xlsx exists and decisions.csv has its rows. Do not redo finished materials and do not recreate the folder or the template files. Check the last material in decisions.csv: if it has no LCI sheet, redo that one from its start (remove its partial rows first). Continue with the remaining materials in the order of material_definitions.csv, appending to the existing files. At the end write summary.md for ALL materials of the batch."
    echo "batch_$n: continuing an interrupted run"
  else
    echo "batch_$n: started $(date +%H:%M)"
  fi
  ( cd "$dir" && claude -p "$prompt" --model "$MODEL" --allowedTools "$TOOLS" --output-format json \
      > "../../logs/batch_$n.json" 2> "../../logs/batch_$n.err" )
  rc=$?
  if [ -f "$dir/runs/$run/summary.md" ]; then echo "batch_$n: finished $(date +%H:%M)"
  else echo "batch_$n: stopped (exit $rc), no summary.md. See logs/batch_$n.err. Run again to continue."; fi
}
export -f run_one
export BWDIR

echo "Batches: $BATCHES| parallel: $PAR"
echo $BATCHES | tr ' ' '\n' | grep -v '^$' | xargs -P "$PAR" -I{} bash -c 'run_one {}'
echo
echo "Done. Next: python collect_results.py"
