import bw2data as bd, bw2calc as bc
bd.projects.set_current("biobased_construction_impact_calculator")
DB=bd.Database("ecoinvent-3.12-cutoff")
M=('ecoinvent-3.12','EF v3.1','climate change: fossil','global warming potential (GWP100)')
def get(name,loc,prod=None):
    r=[a for a in DB if a['name']==name and a['location']==loc and (prod is None or a['reference product']==prod)]
    assert len(r)==1,(name,loc,len(r)); return r[0]
def show(a,n=40):
    print(f"## {a['name']} | {a['reference product']} | {a['location']} | {a['unit']}")
    for e in list(a.technosphere())[:n]:
        i=e.input; print(f"   {e['amount']:.4g} {i['unit']} {i['name']} [{i['location']}]")
def gwp(pairs):
    """pairs: list of (activity, amount) -> total and per-row"""
    out=[]
    for a,x in pairs:
        l=bc.LCA({a:1},M); l.lci(); l.lcia(); out.append(l.score*x)
    return sum(out),out
