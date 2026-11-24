"""Read-only: list EN 15804+A2 EPDs in ÖKOBAUDAT release OBD_2024_III by class id or name; GWP-fossil A1-A3 per kg."""
import sys, json, urllib.request, urllib.parse, statistics
BASE="https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75"
def get(u):
    return json.load(urllib.request.urlopen(u, timeout=60))
def lst(**kw):
    q=urllib.parse.urlencode(dict(format="json",search="true",pageSize=200,**kw))
    return get(f"{BASE}/processes?{q}")["data"]
def detail(uuid):
    d=get(f"{BASE}/processes/{uuid}?format=json&view=extended")
    fossil=None
    for r in d["LCIAResults"]["LCIAResult"]:
        nm=r["referenceToLCIAMethodDataSet"]["shortDescription"][0]["value"]
        if "GWP-fossil" in nm:
            for a in r["other"]["anies"]:
                if a.get("module")=="A1-A3": fossil=float(a["value"])
    ex=[e for e in d["exchanges"]["exchange"] if e.get("referenceFlow")][0]
    unit=None; mass=None
    for p in ex.get("flowProperties",[]):
        nm=p["name"][0]["value"]
        if p.get("referenceFlowProperty"): unit=p.get("referenceUnit"); refname=nm
        if nm=="Mass": mass=p["meanValue"]
    dens=None
    for m in ex.get("materialProperties",[]):
        if m["name"] in("gross density","bulk density"): dens=m["value"]
    return fossil,unit,mass,dens,ex["referenceToFlowDataSet"]["shortDescription"][0]["value"]
if __name__=="__main__":
    kw={}
    for a in sys.argv[1:]:
        k,v=a.split("=",1); kw[k]=v
    rows=[]
    for p in lst(**kw):
        if not any("A2" in c["name"] for c in p.get("compliance",[])): continue
        try: f,u,m,dn,fl=detail(p["uuid"])
        except Exception as e: print("ERR",p["uuid"],e); continue
        print(p["uuid"],"|",p["name"],"|",p["geo"],p["refYear"],"|fossil A1-A3",f,"per",u,"| mass prop",m,"| density",dn,"| flow",fl)
