"""Compare two runs of the baseline LCI protocol.

    python compare_runs.py runs/run_A runs/run_B

Each run folder holds the outputs of one agent session. Prints agreement rates and writes, into the first run
folder's parent:
  comparison_decisions.csv   question by question (decisions.csv)
  comparison_datasets.csv    dataset by dataset (dataset_choices.csv), incl. the amount of each row
  comparison_machines.csv    P1 / P2 rows: machine used, power, throughput, mass, life, amount, ratio B/A
  comparison_archetypes.csv  CFF archetype per material and carbon archetype per constituent
  comparison_epd.csv         ÖKOBAUDAT checks side by side
"""
import sys
from pathlib import Path
import pandas as pd


def norm(x):
    return str(x).strip().lower() if pd.notna(x) else ""


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def read(d: Path, name: str):
    p = d / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def pair(a, b, key):
    return a.drop_duplicates(key).merge(b.drop_duplicates(key), on=key, how="outer",
                                        suffixes=("_A", "_B"), indicator=True)


def status(m, same):
    s = m["_merge"].astype(str).map({"both": "", "left_only": "only in A", "right_only": "only in B"})
    s[(m["_merge"] == "both") & same] = "same"
    s[(m["_merge"] == "both") & ~same] = "different"
    return s


def ratio(a, b):
    a, b = num(a), num(b)
    return round(b / a, 3) if a not in (None, 0) and b is not None else None


def compare(a_dir: Path, b_dir: Path):
    out = a_dir.parent

    # 1. decisions
    da, db = read(a_dir, "decisions.csv"), read(b_dir, "decisions.csv")
    key = ["material_id", "question_id"]
    for d in (da, db):
        d["question_id"] = d["question_id"].map(lambda x: str(x).strip())
        d["answer_n"] = d["answer"].map(norm)
        d["value_n"] = d["value"].map(norm) if "value" in d else ""
    m = pair(da, db, key)
    same = (m["answer_n_A"] == m["answer_n_B"]) & (m["value_n_A"] == m["value_n_B"])
    m["status"] = status(m, same)
    cols = key + ["status", "answer_A", "answer_B", "value_A", "value_B", "evidence_A", "evidence_B"]
    m[[c for c in cols if c in m]].sort_values(key).to_csv(out / "comparison_decisions.csv", index=False)
    both = m[m["_merge"] == "both"]
    print(f"Decisions: {int((both['status'] == 'same').sum())}/{len(both)} answered the same "
          f"({len(m) - len(both)} asked in only one run)")
    for mat, g in both.groupby("material_id"):
        print(f"  {mat}: {int((g['status'] == 'same').sum())}/{len(g)} same")

    # 2. datasets
    sa, sb = read(a_dir, "dataset_choices.csv"), read(b_dir, "dataset_choices.csv")
    key = ["material_id", "module", "row_purpose"]
    for d in (sa, sb):
        d["row_purpose"] = d["row_purpose"].map(norm)
        d["ds"] = d["chosen_activity"].map(norm) + " | " + d["location"].map(norm)
    n = pair(sa, sb, key)
    n["status"] = status(n, n["ds_A"] == n["ds_B"])
    if "amount_A" in n:
        n["amount_ratio_B_to_A"] = [ratio(a, b) for a, b in zip(n["amount_A"], n["amount_B"])]
    cols = key + ["status", "chosen_activity_A", "location_A", "amount_A", "rule_applied_A",
                  "chosen_activity_B", "location_B", "amount_B", "rule_applied_B", "amount_ratio_B_to_A"]
    n[[c for c in cols if c in n]].sort_values(key).to_csv(out / "comparison_datasets.csv", index=False)
    bothn = n[n["_merge"] == "both"]
    print(f"Datasets: {int((bothn['status'] == 'same').sum())}/{len(bothn)} rows with the same dataset and location "
          f"({len(n) - len(bothn)} rows in only one run; row_purpose must match to be compared)")

    # 3. machines (P1, P2): same dataset by design, so compare the values
    mach = n[n["row_purpose"].str.startswith(("processing:", "machine:")) & (n["_merge"] == "both")].copy()
    if len(mach):
        for c in ["power_kW", "throughput_kg_per_h", "machine_mass_kg", "machine_life_h", "amount"]:
            if f"{c}_A" in mach:
                mach[f"{c}_ratio_B_to_A"] = [ratio(a, b) for a, b in zip(mach[f"{c}_A"], mach[f"{c}_B"])]
        cols = key + [f"{c}_{s}" for c in ["machine_used", "power_kW", "throughput_kg_per_h", "machine_mass_kg",
                                           "machine_life_h", "amount"] for s in "AB"] + \
            [c for c in mach if c.endswith("_ratio_B_to_A")]
        mach[[c for c in cols if c in mach]].sort_values(key).to_csv(out / "comparison_machines.csv", index=False)
        r = mach["amount_ratio_B_to_A"].dropna() if "amount_ratio_B_to_A" in mach else pd.Series(dtype=float)
        within = int(((r >= 0.5) & (r <= 2)).sum())
        print(f"Machine rows: {len(mach)} in both runs; amount within a factor 2: {within}/{len(r)}")

    # 4. archetypes
    rows = []
    ca, cb = read(a_dir, "cff_inputs.csv"), read(b_dir, "cff_inputs.csv")
    if len(ca) or len(cb):
        c = pair(ca, cb, ["material_id"])
        for _, r in c.iterrows():
            rows.append(["CFF", r["material_id"], "", r.get("cff_archetype_A"), r.get("cff_archetype_B")])
    ba, bb = read(a_dir, "bioc_inputs.csv"), read(b_dir, "bioc_inputs.csv")
    if len(ba) or len(bb):
        for d in (ba, bb):
            d["constituent"] = d["constituent"].map(norm)
        c = pair(ba, bb, ["material_id", "constituent"])
        for _, r in c.iterrows():
            rows.append(["carbon", r["material_id"], r["constituent"],
                         r.get("carbon_archetype_A"), r.get("carbon_archetype_B")])
    if rows:
        ar = pd.DataFrame(rows, columns=["archetype", "material_id", "constituent", "A", "B"])
        ar["status"] = ["same" if norm(a) == norm(b) else "different" for a, b in zip(ar["A"], ar["B"])]
        ar.to_csv(out / "comparison_archetypes.csv", index=False)
        print(f"Archetypes: {int((ar['status'] == 'same').sum())}/{len(ar)} the same")

    # 5. ÖKOBAUDAT checks
    ea, eb = read(a_dir, "epd_check.csv"), read(b_dir, "epd_check.csv")
    if len(ea) or len(eb):
        e = pair(ea, eb, ["material_id", "check_id"])
        cols = ["material_id", "check_id"] + [f"{c}_{s}" for c in
                ["n_epds", "epd_median", "our_gwp_fossil_a1a3", "ratio_to_median", "result",
                 "wear_share_of_gwp_fossil_a1a3"] for s in "AB"]
        e[[c for c in cols if c in e]].to_csv(out / "comparison_epd.csv", index=False)
        for _, r in e.iterrows():
            print(f"  {r['material_id']} {r['check_id']}: A {r.get('our_gwp_fossil_a1a3_A')} ({r.get('result_A')}), "
                  f"B {r.get('our_gwp_fossil_a1a3_B')} ({r.get('result_B')})")
    print(f"Details: comparison_*.csv in {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    compare(Path(sys.argv[1]), Path(sys.argv[2]))
