import sys, bw2data as bd
bd.projects.set_current("biobased_construction_impact_calculator")
DB = [d for d in bd.databases if d.lower().startswith("ecoinvent-3.12") and "cut" in d.lower() and "biosphere" not in d.lower()][0]
def find(name, loc=None, prod=None):
    r=[a for a in bd.Database(DB) if a['name']==name and (loc is None or a['location']==loc) and (prod is None or a['reference product']==prod)]
    return r
def show(name, loc=None, n=40):
    for a in find(name, loc):
        print("==", a['name'], "|", a['reference product'], "|", a['location'], "|", a['unit'])
        print("  DOC:", (a.get('comment') or '')[:1500].replace("\n"," "))
        for e in a.technosphere():
            print("   T", round(e['amount'],5), e['unit'], "|", e.input['name'], "|", e.input['reference product'], "|", e.input['location'])
if __name__=="__main__":
    show(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None)
