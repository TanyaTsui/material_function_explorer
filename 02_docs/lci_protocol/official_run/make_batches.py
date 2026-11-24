#!/usr/bin/env python3
"""Build the batch folders for the official baseline LCI run.

    python make_batches.py            # 7 batches of 4 materials
    python make_batches.py --batches 4

Reads  ../protocol_predetermined_values.xlsx  (sheets input_definitions and material_overview) and writes
  batch_plan.csv                       which material is in which batch
  batches/batch_N/                     one self-contained kit per batch:
      PROMPT.md, protocol.md, protocol_predetermined_values.xlsx, search_ecoinvent.py, templates/,
      material_definitions.csv       (only the materials of this batch)

Materials are spread over the batches so that each gets about the same workload (constituents + manufacturing
steps). A batch that already has agent output in runs/ is left alone unless you pass --force.
Rebuild any time the protocol.md, the workbook or the prompt changes.
"""
import argparse
import csv
import math
import re
import shutil
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
WORKBOOK = HERE.parent / "protocol_predetermined_values.xlsx"
SPECIAL_IDS = {"OSB/3": "osb3"}           # the id used in the pilot kits
COLS = ["material_id", "material", "delivered_state", "kind", "name", "amount", "unit", "source", "link", "note",
        "status"]


def material_id(name: str) -> str:
    return SPECIAL_IDS.get(name) or re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def table(ws, first_col):
    """Rows of a sheet as dicts, starting at the header row whose first cell is `first_col`."""
    rows = list(ws.iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows) if r and r[0] == first_col)
    head = [str(c).strip() if c is not None else "" for c in rows[h]]
    out = []
    for r in rows[h + 1:]:
        if not any(c is not None and str(c).strip() for c in r):
            continue
        out.append(dict(zip(head, r)))
    return out


def load():
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)
    states = {r["material"]: r["delivered state"] for r in table(wb["material_overview"], "#") if r.get("material")}
    mats, order = {}, []
    for r in table(wb["input_definitions"], "material"):
        m = r["material"]
        if not m:
            continue
        if m not in mats:
            mats[m] = []
            order.append(m)
        mats[m].append(r)
    missing = [m for m in order if m not in states]
    if missing:
        raise SystemExit(f"No delivered state in material_overview for: {missing}")
    return order, mats, states


def to_csv_rows(m, rows, states):
    out = []
    for r in rows:
        d = {"material_id": material_id(m), "material": m, "delivered_state": states[m]}
        for c in ["kind", "name", "amount", "unit", "source", "link", "note", "status"]:
            v = r.get(c)
            d[c] = "" if v is None else v
        out.append(d)
    return out


def assign(order, mats, n_batches):
    """Greedy: heaviest material first into the lightest batch that still has room (size cap = ceil(N / batches))."""
    cap = math.ceil(len(order) / n_batches)
    batches = [[] for _ in range(n_batches)]
    load_ = [0] * n_batches
    for m in sorted(order, key=lambda x: -len(mats[x])):
        k = min((i for i in range(n_batches) if len(batches[i]) < cap), key=lambda i: load_[i])
        batches[k].append(m)
        load_[k] += len(mats[m])
    return [sorted(b, key=order.index) for b in batches], load_


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batches", type=int, default=7)
    ap.add_argument("--force", action="store_true", help="rebuild batches that already have output in runs/")
    a = ap.parse_args()

    order, mats, states = load()
    ids = [material_id(m) for m in order]
    assert len(set(ids)) == len(ids), "duplicate material ids"
    batches, load_ = assign(order, mats, a.batches)
    prompt = (HERE / "PROMPT_template.md").read_text()
    out = HERE / "batches"
    plan = []
    for i, ms in enumerate(batches, 1):
        d = out / f"batch_{i}"
        if (d / "runs").exists() and any((d / "runs").iterdir()) and not a.force:
            print(f"batch_{i}: has output in runs/, left alone (use --force to rebuild)")
        else:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
            for f in ["protocol.md", "search_ecoinvent.py"]:
                shutil.copy(HERE / f, d / f)
            shutil.copy(WORKBOOK, d / "protocol_predetermined_values.xlsx")
            shutil.copytree(HERE / "templates", d / "templates")
            (d / "PROMPT.md").write_text(prompt.replace("{run_id}", f"batch_{i}"))
            with open(d / "material_definitions.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=COLS)
                w.writeheader()
                for m in ms:
                    w.writerows(to_csv_rows(m, mats[m], states))
            print(f"batch_{i}: {len(ms)} materials, {load_[i-1]} constituent+step rows: "
                  + ", ".join(material_id(m) for m in ms))
        for m in ms:
            plan.append({"batch": f"batch_{i}", "material_id": material_id(m), "material": m,
                         "constituents": sum(r["kind"] == "constituent" for r in mats[m]),
                         "steps": sum(r["kind"] == "step" for r in mats[m]),
                         "target_file": f"data/LCI/baseline_{material_id(m)}.xlsx"})
    with open(HERE / "batch_plan.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(plan[0]))
        w.writeheader()
        w.writerows(plan)
    print(f"\n{len(plan)} materials in {len(batches)} batches. Plan: batch_plan.csv")


if __name__ == "__main__":
    main()
