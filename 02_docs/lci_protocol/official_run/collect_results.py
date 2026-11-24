#!/usr/bin/env python3
"""Collect the output of the official run.

    python collect_results.py              # copy finished LCIs, merge logs, write results/
    python collect_results.py --dry-run    # show what would happen
    python collect_results.py --force      # overwrite existing data/LCI/baseline_*.xlsx

For every batch in batches/batch_N/runs/batch_N/ it
  1. copies LCI_<material_id>.xlsx to <repo>/data/LCI/baseline_<material_id>.xlsx
     (an existing baseline file is kept unless --force),
  2. merges decisions.csv, dataset_choices.csv, epd_check.csv, cff_inputs.csv and bioc_inputs.csv into results/,
  3. joins protocol_issues.md and summary.md of all batches into results/,
  4. writes results/overview.csv: one row per material (LCI present, which route was kept, ÖKOBAUDAT ratio, flagged),
  5. prints the cost of each batch from logs/batch_N.json, if present.
"""
import argparse
import csv
import json
import shutil
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
LCI_DIR = HERE.parents[1] / "data" / "LCI"
RESULTS = HERE / "results"
CSVS = ["decisions.csv", "dataset_choices.csv", "epd_check.csv", "cff_inputs.csv", "bioc_inputs.csv"]
ROUTE_OF_CHECK = {"CHECK 1": "exact", "CHECK 2": "approximate", "CHECK 3": "built"}


def read_plan():
    with open(HERE / "batch_plan.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def overview_row(p, lci_state, epd):
    row = {"batch": p["batch"], "material_id": p["material_id"], "material": p["material"], "lci_file": lci_state,
           "outcome": "", "route_kept": "", "ratio_to_median": "", "flagged": ""}
    e = epd[epd["material_id"] == p["material_id"]] if len(epd) else epd
    if not len(e):
        row["outcome"] = "no epd_check rows"
        return row
    checks = e[e["check_id"].str.upper().str.startswith("CHECK")]
    passed = checks[checks["result"].str.lower().str.startswith("pass")]
    review = e[e["check_id"].str.upper().str.startswith("REVIEW")]
    nocheck = e[e["result"].str.lower().str.contains("no check")]
    if len(passed):
        r = passed.iloc[0]
        row.update(outcome="passed", route_kept=r.get("route") or ROUTE_OF_CHECK.get(r["check_id"].upper(), ""),
                   ratio_to_median=r.get("ratio_to_median", ""), flagged="no")
    elif len(review):
        r = review.iloc[-1]
        row.update(outcome="all checks failed, review", route_kept=r.get("lci_kept") or r.get("route", ""),
                   ratio_to_median=r.get("ratio_to_median", ""), flagged="yes")
    elif len(nocheck):
        row.update(outcome="no check possible", route_kept=nocheck.iloc[-1].get("route", ""), flagged="no")
    else:
        row["outcome"] = "unclear: see epd_check.csv"
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    plan = read_plan()
    ids = {p["material_id"] for p in plan}
    batches = sorted({p["batch"] for p in plan}, key=lambda b: int(b.split("_")[1]))
    RESULTS.mkdir(exist_ok=True)
    LCI_DIR.mkdir(parents=True, exist_ok=True)

    # 1. LCI sheets
    state = {}
    for b in batches:
        rd = HERE / "batches" / b / "runs" / b
        for f in sorted(rd.glob("LCI_*.xlsx")) if rd.exists() else []:
            mid = f.stem[len("LCI_"):]
            if mid not in ids:
                print(f"WARNING {f}: unknown material id, not copied")
                continue
            dest = LCI_DIR / f"baseline_{mid}.xlsx"
            if dest.exists() and not a.force:
                state[mid] = "kept existing (use --force)"
            else:
                if not a.dry_run:
                    shutil.copy2(f, dest)
                state[mid] = "copied"
    # 2. merged logs
    frames = {}
    for name in CSVS:
        parts = []
        for b in batches:
            p = HERE / "batches" / b / "runs" / b / name
            if p.exists():
                parts.append(pd.read_csv(p, dtype=str, keep_default_na=False))
        frames[name] = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if len(frames[name]) and not a.dry_run:
            frames[name].to_csv(RESULTS / name, index=False)
        print(f"{name}: {len(frames[name])} rows")
    # 3. notes
    for src, dst in [("protocol_issues.md", "protocol_issues_all.md"), ("summary.md", "summaries_all.md")]:
        text = ""
        for b in batches:
            p = HERE / "batches" / b / "runs" / b / src
            if p.exists():
                text += f"\n\n# {b}\n\n" + p.read_text()
        if text and not a.dry_run:
            (RESULTS / dst).write_text(text.lstrip())
    # 4. overview
    epd = frames["epd_check.csv"]
    rows = [overview_row(p, state.get(p["material_id"], "MISSING"), epd) for p in plan]
    if not a.dry_run:
        pd.DataFrame(rows).to_csv(RESULTS / "overview.csv", index=False)
    done = sum(r["lci_file"] != "MISSING" for r in rows)
    print(f"\n{done}/{len(rows)} materials have an LCI sheet. Missing: "
          + (", ".join(r["material_id"] for r in rows if r["lci_file"] == "MISSING") or "none"))
    print("Flagged: " + (", ".join(r["material_id"] for r in rows if r["flagged"] == "yes") or "none"))
    # 5. cost
    tot = 0.0
    for b in batches:
        p = HERE / "logs" / f"{b}.json"
        if not p.exists():
            continue
        try:
            j = json.loads(p.read_text())
            c = j.get("total_cost_usd")
            tot += c or 0
            models = ", ".join((j.get("modelUsage") or {}).keys()) or "not in log"
            print(f"{b}: cost estimate {c} USD, {j.get('num_turns')} turns, "
                  f"{round((j.get('duration_ms') or 0) / 60000)} min, error={j.get('is_error')}, models: {models}")
        except Exception as e:  # a log of an interrupted run may not be valid json
            print(f"{b}: log not readable ({e})")
    if tot:
        print(f"Total API-equivalent cost estimate: {tot:.2f} USD (client-side estimate, not a charge on a plan)")
    if a.dry_run:
        print("(dry run: nothing written)")


if __name__ == "__main__":
    main()
