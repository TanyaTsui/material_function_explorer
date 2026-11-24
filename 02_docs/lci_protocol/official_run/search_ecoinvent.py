"""Search the ecoinvent 3.12 cut-off database in your Brightway project (read-only).

The agent runs this for every dataset search in the protocol (D1 to D4), e.g.

    python search_ecoinvent.py "oriented strand board"
    python search_ecoinvent.py "market for transport, freight, lorry" --location RER
    python search_ecoinvent.py "cork" --field product

Every word of the query must appear (case-insensitive) in the activity name, or in the reference product with
--field product, or in either with --field any (default). Prints one line per activity:
name | reference product | location | unit | code. Nothing in the database is changed.
"""
import argparse
import bw2data as bd

PROJECT = "biobased_construction_impact_calculator"


def ecoinvent_db():
    names = [d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower()
             and "biosphere" not in d.lower()]
    if not names:
        raise SystemExit(f"No ecoinvent 3.12 cut-off database in project {PROJECT}: {list(bd.databases)}")
    return names[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="words that must all appear")
    ap.add_argument("--field", choices=["name", "product", "any"], default="any")
    ap.add_argument("--location", help="keep only this location code, e.g. RER, GLO, RoW, DE")
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()

    if PROJECT not in bd.projects:
        raise SystemExit(f"No Brightway project '{PROJECT}' in {bd.projects.dir}. Projects there: "
                         f"{sorted(p.name for p in bd.projects)}. Activate the conda environment the pipeline uses "
                         f"(brightway_env) or edit PROJECT at the top of this script.")
    bd.projects.set_current(PROJECT)
    db_name = ecoinvent_db()
    words = a.query.lower().split()
    hits = []
    for act in bd.Database(db_name):
        name = act.get("name") or ""
        prod = act.get("reference product") or ""
        text = {"name": name, "product": prod, "any": name + " " + prod}[a.field].lower()
        if all(w in text for w in words) and (not a.location or act.get("location") == a.location):
            hits.append((name, prod, act.get("location"), act.get("unit"), act.get("code")))
    hits.sort()
    print(f"# {db_name}: {len(hits)} hits for '{a.query}' (field={a.field}"
          f"{', location=' + a.location if a.location else ''}); showing {min(len(hits), a.limit)}")
    for h in hits[: a.limit]:
        print(" | ".join(str(x) for x in h))


if __name__ == "__main__":
    main()
