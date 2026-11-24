import warnings; warnings.filterwarnings("ignore")
import bw2data as bd, bw2calc as bc
bd.projects.set_current("biobased_construction_impact_calculator")
DB=bd.Database("ecoinvent-3.12-cutoff")
METHOD=("ecoinvent-3.12","EF v3.1","climate change: fossil","global warming potential (GWP100)")
def find(name,loc=None,prod=None,exact=True):
    out=[]
    for a in DB:
        if (a["name"]==name if exact else name in a["name"]) and (loc is None or a["location"]==loc) and (prod is None or a["reference product"]==prod):
            out.append(a)
    return out
def one(name,loc,prod=None):
    r=find(name,loc,prod); assert len(r)==1,(name,loc,[x["reference product"] for x in r]); return r[0]
def show(a,n=40):
    print("##",a["name"],"|",a["reference product"],"|",a["location"],"|",a["unit"],a["code"])
    print("   doc:",str(a.get("comment",""))[:1200])
    for e in a.production(): print("   PROD",e["amount"],e["unit"],e.get("properties"))
    ex=sorted(a.technosphere(),key=lambda e:-abs(e["amount"]))
    for e in ex[:n]:
        i=e.input; print(f"   {e['amount']:.5g} {e['unit']} | {i['name']} | {i['reference product']} | {i['location']}")
def gwp(acts_amounts):
    """acts_amounts: list of (activity, amount). returns total and per-item gwp-fossil"""
    res=[]
    for a,amt in acts_amounts:
        lca=bc.LCA({a:1},METHOD); lca.lci(); lca.lcia(); res.append(lca.score*amt)
    return sum(res),res
