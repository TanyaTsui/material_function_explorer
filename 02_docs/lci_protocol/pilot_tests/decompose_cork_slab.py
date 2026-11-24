"""Break the ecoinvent 'market for cork slab' (RER) result into its contributors (read-only).

Run it in the same conda environment the pipeline uses (brightway_env), from any folder:

    conda activate brightway_env
    python decompose_cork_slab.py                 # RER market, as both test runs used
    python decompose_cork_slab.py --depth 3       # follow the supply chain one level deeper

What it prints, per 1 kg of cork slab, for EF v3.1 'climate change: fossil':
  1. the total, and where the market's volume comes from (which production locations),
  2. every contributor in the cork slab production step (resin, electricity, heat, raw cork, transport, direct emissions),
  3. carbon intensity of 1 kWh of medium-voltage electricity in RER / PT / ES / DE, and what the cork slab
     result would be if the electricity input were swapped for Portuguese or German electricity,
  4. a closure check (sum of contributors vs total).
Results are also saved to cork_slab_decomposition.csv next to this script. Nothing in the database is changed.
"""
import argparse, csv, sys
from pathlib import Path
import bw2data as bd
import bw2calc as bc

PROJECT = "biobased_construction_impact_calculator"
EXPAND = ("market for cork slab", "market group for cork slab", "cork slab production")


def pick_db():
    names = [d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower()
             and "biosphere" not in d.lower()]
    if not names:
        sys.exit(f"No ecoinvent 3.12 cut-off database found: {list(bd.databases)}")
    return names[0]


def pick_method():
    cands = [m for m in bd.methods
             if "ef v3.1" in " ".join(m).lower() and "climate change: fossil" in " ".join(m).lower()]
    if not cands:
        sys.exit("No EF v3.1 'climate change: fossil' method found in this project.")
    cands.sort(key=lambda m: ("gwp100" not in " ".join(m).lower(), len(m)))
    return cands[0], cands


class Scorer:
    """score(id, amount) = kg CO2e (fossil) of `amount` units of activity `id`."""
    def __init__(self, method, first_id):
        self.method = method
        self.lca = bc.LCA({first_id: 1}, method)
        self.lca.lci(); self.lca.lcia()
        self.fast = True
        a = self._fast(first_id, 1.0)
        b = self._fresh(first_id, 1.0)
        if abs(a - b) > 1e-9 * max(1, abs(b)):
            print("# (re-using one LCA object gave a different score, so using a fresh LCA for each call: slower)")
            self.fast = False

    def _fast(self, i, amt):
        self.lca.redo_lci({i: amt})
        if hasattr(self.lca, "lcia_calculation"):
            self.lca.lcia_calculation()
        else:
            self.lca.redo_lcia()
        return float(self.lca.score)

    def _fresh(self, i, amt):
        l = bc.LCA({i: amt}, self.method)
        l.lci(); l.lcia()
        return float(l.score)

    def __call__(self, i, amt):
        try:
            return self._fast(i, amt) if self.fast else self._fresh(i, amt)
        except Exception:
            self.fast = False
            return self._fresh(i, amt)


def expand(act, amount, depth, max_depth, score, rows, path):
    """Split `amount` of `act` into its technosphere inputs; recurse into cork slab market/production nodes."""
    total = score(act.id, amount)
    kids = []
    for exc in act.technosphere():
        if exc["type"] != "technosphere":
            continue
        inp = exc.input
        amt = amount * exc["amount"]
        if inp.id == act.id:
            continue
        kids.append((inp, amt))
    child_sum = 0.0
    for inp, amt in kids:
        nm = inp["name"]
        if depth < max_depth and nm.startswith(EXPAND):
            child_sum += expand(inp, amt, depth + 1, max_depth, score, rows, path + [f'{act["name"]} [{act["location"]}]'])
        else:
            s = score(inp.id, amt)
            child_sum += s
            rows.append({"parent": f'{act["name"]} [{act["location"]}]', "input": nm,
                         "location": inp["location"], "unit": inp["unit"], "amount_per_kg_slab": amt,
                         "kgCO2e_fossil_per_kg_slab": s})
    direct = total - child_sum
    rows.append({"parent": f'{act["name"]} [{act["location"]}]', "input": "(direct emissions at this step)",
                 "location": act["location"], "unit": "", "amount_per_kg_slab": "",
                 "kgCO2e_fossil_per_kg_slab": direct})
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--location", default="RER", help="location of the 'market for cork slab' to use")
    ap.add_argument("--depth", type=int, default=2, help="how many market/production levels to expand")
    a = ap.parse_args()

    if PROJECT not in bd.projects:
        sys.exit(f"No project '{PROJECT}'. Projects: {sorted(p.name for p in bd.projects)}")
    bd.projects.set_current(PROJECT)
    db = bd.Database(pick_db())
    method, cands = pick_method()
    print(f"# database: {db.name}\n# method: {method}" + (f"  (other candidates: {cands[1:]})" if len(cands) > 1 else ""))

    root = [x for x in db if x["name"] == "market for cork slab" and x["location"] == a.location]
    if not root:
        sys.exit(f"No 'market for cork slab' at {a.location}")
    root = root[0]
    score = Scorer(method, root.id)
    total = score(root.id, 1.0)
    print(f"\n== {root['name']} [{root['location']}], per 1 {root['unit']}: {total:.4f} kg CO2e (fossil)")

    rows = []
    expand(root, 1.0, 0, a.depth, score, rows, [])

    print("\n== Contributors (kg CO2e fossil per kg cork slab), largest first")
    leaf = [r for r in rows]
    leaf.sort(key=lambda r: -abs(r["kgCO2e_fossil_per_kg_slab"]))
    for r in leaf:
        amt = f'{r["amount_per_kg_slab"]:.4g} {r["unit"]}' if r["amount_per_kg_slab"] != "" else ""
        print(f'{r["kgCO2e_fossil_per_kg_slab"]:8.4f}  {100*r["kgCO2e_fossil_per_kg_slab"]/total:5.1f}%  '
              f'{r["input"][:62]:62s} [{r["location"]}]  {amt}   <- {r["parent"][:40]}')
    # closure check: leaves of the deepest level + direct emissions of every expanded node = total
    closure = sum(r["kgCO2e_fossil_per_kg_slab"] for r in rows
                  if not str(r["input"]).startswith(EXPAND))
    print(f"\nClosure check: contributors sum to {closure:.4f} vs total {total:.4f} (difference {closure-total:+.2e})")

    # groups
    def grp(r):
        n = r["input"].lower()
        if "direct emissions" in n: return "direct emissions"
        if any(k in n for k in ("formaldehyde", "melamine", "urea", "phenol", "resin")): return "resin (UF/MF/PF)"
        if "electricity" in n: return "electricity"
        if any(k in n for k in ("heat", "steam", "wood chips", "natural gas", "light fuel oil", "heavy fuel")): return "heat / fuel"
        if "cork" in n and "slab" not in n: return "raw cork"
        if "transport" in n: return "transport"
        return "other"
    groups = {}
    for r in rows:
        if str(r["input"]).startswith(EXPAND):
            continue
        groups[grp(r)] = groups.get(grp(r), 0) + r["kgCO2e_fossil_per_kg_slab"]
    print("\n== Grouped")
    for k, v in sorted(groups.items(), key=lambda kv: -kv[1]):
        print(f"{v:8.4f}  {100*v/total:5.1f}%  {k}")

    # electricity sensitivity
    print("\n== Electricity: kg CO2e (fossil) per kWh, medium voltage")
    inten = {}
    for loc in ("RER", "PT", "ES", "DE", "FR"):
        m = [x for x in db if x["name"] == "market for electricity, medium voltage" and x["location"] == loc]
        if not m:
            m = [x for x in db if x["name"] == "market group for electricity, medium voltage" and x["location"] == loc]
        if m:
            inten[loc] = (m[0], score(m[0].id, 1.0))
            print(f"  {loc}: {inten[loc][1]:.3f}")
    el = [r for r in rows if "electricity" in str(r["input"]).lower() and r["amount_per_kg_slab"] != ""]
    if el:
        kwh = sum(r["amount_per_kg_slab"] for r in el if r["unit"] == "kilowatt hour")
        cur = sum(r["kgCO2e_fossil_per_kg_slab"] for r in el)
        print(f"\n  Electricity in the cork slab chain: {kwh:.3f} kWh per kg slab = {cur:.4f} kg CO2e as modelled")
        for loc, (_, ci) in inten.items():
            print(f"  if all of it were {loc} electricity: slab = {total - cur + kwh*ci:.4f} kg CO2e/kg "
                  f"(change {kwh*ci-cur:+.4f})")
        print("  (electricity inputs of other kinds, e.g. high voltage, are only partly captured here; check the table above)")

    out = Path(__file__).with_name("cork_slab_decomposition.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
