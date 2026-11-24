"""Merge the six batch runs (run_C1..run_C6) into one folder, merged_run_C/, for comparison and reading.

    python merge_batches.py
Concatenates decisions.csv, dataset_choices.csv, material_definitions.csv and epd_check.csv, copies every LCI_*.xlsx,
and joins the protocol_issues.md and summary.md files (headed by batch). Read-only on the batches.
"""
import csv, shutil
from pathlib import Path
here = Path(__file__).parent
out = here / "merged_run_C"; out.mkdir(exist_ok=True)
for name in ["decisions.csv", "dataset_choices.csv", "material_definitions.csv", "epd_check.csv"]:
    rows, header = [], None
    for b in range(1, 7):
        p = here / f"run_C{b}" / "runs" / f"run_C{b}" / name
        if p.exists():
            r = list(csv.reader(open(p, encoding="utf-8-sig")))
            header = header or r[0]; rows += r[1:]
        else:
            print("missing", p)
    if header:
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)
        print(name, len(rows), "rows")
for name in ["protocol_issues.md", "summary.md"]:
    with open(out / name, "w", encoding="utf-8") as f:
        for b in range(1, 7):
            p = here / f"run_C{b}" / "runs" / f"run_C{b}" / name
            if p.exists():
                f.write(f"\n\n# ===== batch run_C{b} =====\n\n" + p.read_text(encoding="utf-8"))
n = 0
for b in range(1, 7):
    for p in (here / f"run_C{b}" / "runs" / f"run_C{b}").glob("LCI_*.xlsx"):
        shutil.copy(p, out / p.name); n += 1
print(n, "LCI sheets copied to", out)
