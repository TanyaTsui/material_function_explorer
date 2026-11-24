import sys; sys.path.insert(0,'scripts')
import bwh, bw2data as bd, bw2calc as bc
M=('ecoinvent-3.12','EF v3.1','climate change: fossil','global warming potential (GWP100)')
def get(name,loc,prod=None):
    r=bwh.find(name,loc,prod)
    assert len(r)==1,(name,loc,len(r)); return r[0]
def gwp(demand):
    """demand: list of (activity, amount) -> total kg CO2e fossil, plus per-activity contribution (unit amount)"""
    d={a.id:amt for a,amt in demand}
    lca=bc.LCA(d,M); lca.lci(); lca.lcia()
    return lca.score
def per(a,amt=1.0):
    lca=bc.LCA({a.id:amt},M); lca.lci(); lca.lcia(); return lca.score
if __name__=="__main__":
    osb=get("market for oriented strand board","RER")
    print("OSB m3:",per(osb), "per kg:",per(osb)/607)
    for n,l in [("market for straw","Europe without Switzerland"),("market for polypropylene, granulate","RER"),("market for bamboo pole","RoW"),("market for melamine urea formaldehyde adhesive","GLO"),("market for decorticated fibre, hemp","FR"),("market for fibre, polyester","GLO"),("market for soda ash, light","RER"),("market group for electricity, medium voltage","RER"),("market for heat, district or industrial, natural gas","Europe without Switzerland"),("market for industrial machine, heavy, unspecified","RER"),("market for transport, freight, lorry, unspecified","RER"),("market for transport, freight, sea, container ship, heavy fuel oil","GLO"),("diesel, burned in building machine","GLO")]:
        print(n,l,per(get(n,l)))
