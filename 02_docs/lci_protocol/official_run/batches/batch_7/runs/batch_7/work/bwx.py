import bw2data as bd, sys
bd.projects.set_current("biobased_construction_impact_calculator")
DB=[d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower() and "biosphere" not in d.lower()][0]
def get(code): return bd.Database(DB).get(code)
def show(code, maxex=60):
    a=get(code)
    print("###",a["name"],"|",a["reference product"],"|",a["location"],"|",a["unit"])
    print("props:",{k:v for k,v in (a.get("properties") or {}).items()} if a.get("properties") else None)
    for e in a.production(): print(" PROD",e.get("properties"), e["amount"])
    n=0
    for e in a.technosphere():
        i=e.input; print("  %.5g %s | %s | %s | %s"%(e["amount"],e["unit"],i["name"],i["reference product"],i["location"])); n+=1
        if n>=maxex: break
    return a
if __name__=="__main__":
    for c in sys.argv[1:]: show(c)

M=('ecoinvent-3.12','EF v3.1','climate change: fossil','global warming potential (GWP100)')
def gwp(items):
    """items: list of (code, amount). returns total and per-item GWP-fossil (EF 3.1)"""
    import bw2calc as bc
    out=[]
    for code,amt in items:
        l=bc.LCA({get(code):amt},M); l.lci(); l.lcia(); out.append(l.score)
    return sum(out),out
