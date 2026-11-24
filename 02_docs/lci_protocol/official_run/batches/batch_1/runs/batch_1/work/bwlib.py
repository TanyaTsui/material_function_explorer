import bw2data as bd
bd.projects.set_current("biobased_construction_impact_calculator")
DB=[d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower() and "biosphere" not in d.lower()][0]
db=bd.Database(DB)
def find(name,loc=None,exact=True):
    r=[a for a in db if (a['name']==name if exact else name in a['name']) and (loc is None or a['location']==loc)]
    return r
def show(a,n=40):
    print(a['name'],'|',a['reference product'],'|',a['location'],'|',a['unit'],'|',a['code'])
    print('props:',a.get('properties') or {k:v for k,v in a._data.items() if 'prop' in k})
    for i,e in enumerate(a.technosphere()):
        if i>=n: break
        i_=e.input
        print('  ',round(e['amount'],5),e['unit'],'|',i_['name'],'|',i_['reference product'],'|',i_['location'])

import bw2calc as bc
M=('ecoinvent-3.12','EF v3.1','climate change: fossil','global warming potential (GWP100)')
def gwp(demand):
    """demand: list of (activity, amount). returns GWP fossil kg CO2e (EF3.1)."""
    d={a:x for a,x in demand}
    lca=bc.LCA(d,M); lca.lci(); lca.lcia(); return lca.score
def gwp1(a): return gwp([(a,1)])

def ls(prefix,locs=None,contains=None):
    out=[]
    for a in db:
        n=a['name']
        if n.startswith(prefix) and (contains is None or contains in n):
            if locs is None or a['location'] in locs: out.append((n,a['reference product'],a['location'],a['unit']))
    for o in sorted(out): print(' | '.join(o))
