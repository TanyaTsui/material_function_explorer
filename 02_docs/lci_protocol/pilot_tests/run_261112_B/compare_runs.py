"""Compare two runs of the baseline LCI protocol, question by question and dataset by dataset.

    python compare_runs.py runs/run_A runs/run_B

Each run folder holds the outputs of one agent session: decisions.csv, dataset_choices.csv (and the LCI sheets).
Prints agreement rates and writes comparison_decisions.csv and comparison_datasets.csv into the first run folder's
parent, listing every difference.
"""
import sys
from pathlib import Path
import pandas as pd


def norm(x):
    return str(x).strip().lower() if pd.notna(x) else ""


def compare(a_dir: Path, b_dir: Path):
    out_dir = a_dir.parent
    # decisions: one row per material and question id
    da = pd.read_csv(a_dir / "decisions.csv")
    db = pd.read_csv(b_dir / "decisions.csv")
    key = ["material_id", "question_id"]
    for d in (da, db):
        d["answer_n"] = d["answer"].map(norm)
        d["value_n"] = d["value"].map(norm) if "value" in d else ""
    m = da.drop_duplicates(key).merge(db.drop_duplicates(key), on=key, how="outer", suffixes=("_A", "_B"), indicator=True)
    m["same_answer"] = (m["answer_n_A"] == m["answer_n_B"]) & (m["value_n_A"] == m["value_n_B"])
    m["status"] = m["_merge"].astype(str).map({"both": "", "left_only": "only in A", "right_only": "only in B"})
    m.loc[(m["_merge"] == "both") & m["same_answer"], "status"] = "same"
    m.loc[(m["_merge"] == "both") & ~m["same_answer"], "status"] = "different"
    cols = key + ["status", "answer_A", "answer_B", "value_A", "value_B", "evidence_A", "evidence_B"]
    m[[c for c in cols if c in m]].sort_values(key).to_csv(out_dir / "comparison_decisions.csv", index=False)
    both = m[m["_merge"] == "both"]
    print(f"Decisions: {int(both['same_answer'].sum())}/{len(both)} questions answered the same "
          f"({len(m) - len(both)} asked in only one run)")
    for mat, g in both.groupby("material_id"):
        print(f"  {mat}: {int(g['same_answer'].sum())}/{len(g)} same")

    # datasets: one row per material, module and row purpose
    sa = pd.read_csv(a_dir / "dataset_choices.csv")
    sb = pd.read_csv(b_dir / "dataset_choices.csv")
    key = ["material_id", "module", "row_purpose"]
    for d in (sa, sb):
        d["row_purpose"] = d["row_purpose"].map(norm)
        d["ds"] = d["chosen_activity"].map(norm) + " | " + d["location"].map(norm)
    n = sa.drop_duplicates(key).merge(sb.drop_duplicates(key), on=key, how="outer", suffixes=("_A", "_B"), indicator=True)
    n["status"] = "different"
    n.loc[n["_merge"] == "left_only", "status"] = "only in A"
    n.loc[n["_merge"] == "right_only", "status"] = "only in B"
    n.loc[(n["_merge"] == "both") & (n["ds_A"] == n["ds_B"]), "status"] = "same"
    cols = key + ["status", "chosen_activity_A", "location_A", "rule_applied_A", "chosen_activity_B", "location_B", "rule_applied_B"]
    n[[c for c in cols if c in n]].sort_values(key).to_csv(out_dir / "comparison_datasets.csv", index=False)
    bothn = n[n["_merge"] == "both"]
    print(f"Datasets: {int((bothn['status'] == 'same').sum())}/{len(bothn)} rows with the same dataset and location "
          f"({len(n) - len(bothn)} rows in only one run; row_purpose must match to be compared)")
    print(f"Details: {out_dir / 'comparison_decisions.csv'} and {out_dir / 'comparison_datasets.csv'}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    compare(Path(sys.argv[1]), Path(sys.argv[2]))
