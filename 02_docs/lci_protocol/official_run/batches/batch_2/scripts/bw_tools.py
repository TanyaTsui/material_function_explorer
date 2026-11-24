import sys, bw2data as bd, bw2calc as bc
bd.projects.set_current("biobased_construction_impact_calculator")
DB=[d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower() and "biosphere" not in d.lower()][0]
def method():
    ms=[m for m in bd.methods if 'EF v3.1' in m[0] and m[1]=='climate change' and m[2]=='global warming potential (GWP100)' ] 
    return ms
def show(code):
    a=bd.get_activity((DB,code)); print(a['name'],a['reference product'],a['location'],a['unit'])
    for k,v in (a.get('properties') or {}).items() if hasattr(a,'get') else []: print(' prop',k,v)
    for e in a.technosphere(): print('  ',round(e['amount'],5),e.input['unit'],e.input['name'],'|',e.input['location'])
if __name__=="__main__":
    if sys.argv[1]=='m':
        for m in bd.methods:
            if 'EF v3.1' in m[0] and 'climate change' in m[1]: print(m)
    else: show(sys.argv[1])

M=('ecoinvent-3.12','EF v3.1','climate change: fossil','global warming potential (GWP100)')
def gwp(rows):
    """rows: list of (label, code, amount). returns total and per-row dict"""
    out={}
    for lab,code,amt in rows:
        a=bd.get_activity((DB,code)); lca=bc.LCA({a:amt},M); lca.lci(); lca.lcia(); out[lab]=lca.score
    return sum(out.values()),out
def prod_props(code):
    a=bd.get_activity((DB,code))
    for e in a.production(): print(e.as_dict().get('properties'), e['amount'])

def find(name, loc=None, exact=True):
    out=[]
    for a in bd.Database(DB):
        n=a['name']
        if (n==name if exact else name in n) and (loc is None or a['location']==loc): out.append((n,a['reference product'],a['location'],a['unit'],a['code']))
    return sorted(out)
