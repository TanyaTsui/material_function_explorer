"""Read-only ÖKOBAUDAT helper (release OBD_2024_III, 13.11.2026). Usage:
  okb.py index                       -> cache list of all processes
  okb.py cls <substr>                -> list EN 15804+A2 datasets whose classification contains substr (case-insens.)
  okb.py gwp <classsubstr> [namesub] -> fetch each, print GWP-fossil A1-A3 per kg
"""
import sys, json, os, urllib.request, urllib.parse, statistics
STOCK="bca3670a-8dcf-44d0-be1f-0633d9ba1a75"
BASE=f"https://www.oekobaudat.de/OEKOBAU.DAT/resource/datastocks/{STOCK}/processes"
CACHE=os.path.join(os.path.dirname(__file__),"..","cache")
def get(url):
    with urllib.request.urlopen(url,timeout=90) as r: return json.load(r)
def index():
    p=os.path.join(CACHE,"index.json")
    if os.path.exists(p): return json.load(open(p))
    out=[];i=0
    while True:
        d=get(f"{BASE}?format=json&lang=en&pageSize=500&startIndex={i}")
        out+=d["data"]; i+=500
        if i>=d["totalCount"]: break
    json.dump(out,open(p,"w")); return out
def is_a2(x): return any("15804+A2" in c.get("name","") for c in x.get("compliance",[]))
def detail(uuid):
    p=os.path.join(CACHE,uuid+".json")
    if os.path.exists(p): return json.load(open(p))
    d=get(f"{BASE}/{uuid}?format=json&view=extended"); json.dump(d,open(p,"w")); return d
def gwp_fossil_a1a3_per_kg(d):
    ex=d["exchanges"]["exchange"]; ref=[e for e in ex if e.get("referenceFlow")][0]
    unit=None;mass=None
    for fp in ref.get("flowProperties",[]):
        nm=[n["value"] for n in fp["name"] if n["lang"]=="en"]
        if fp.get("referenceFlowProperty"): unit=fp.get("referenceUnit")
        if nm and nm[0]=="Mass": mass=fp["meanValue"]
    if mass is None:
        for mp in ref.get("materialProperties",[]):
            if mp["name"] in("gross density","bulk density") and unit=="m3":
                try: mass=float(mp["value"])
                except: pass
            if mp["name"]=="grammage" and unit=="m2":
                try: mass=float(mp["value"])
                except: pass
    val=None
    for r in d["LCIAResults"]["LCIAResult"]:
        sd=" ".join(x["value"] for x in r["referenceToLCIAMethodDataSet"]["shortDescription"]).lower()
        if "fossil" in sd or "fossil" in sd.replace("fossil","fossil") or "fossil" in sd:
            if ("gwp" in sd or "climate" in sd or "erwärm" in sd) and "land" not in sd:
                for a in r["other"]["anies"]:
                    if a.get("module") in("A1-A3","A1-A3 "): val=float(a["value"])
    return val,unit,mass
if __name__=="__main__":
    c=sys.argv[1]
    if c=="index": print(len(index()))
    if c in("cls","gwp"):
        s=sys.argv[2].lower(); ns=sys.argv[3].lower() if len(sys.argv)>3 else ""
        sel=[x for x in index() if s in x.get("classific","").lower() and is_a2(x) and ns in x["name"].lower()]
        print(len(sel),"EN15804+A2 datasets")
        vals=[]
        for x in sel:
            if c=="cls": print(x["uuid"],x["geo"],x["type"],x["classific"],"|",x["name"][:90]); continue
            try:
                v,u,m=gwp_fossil_a1a3_per_kg(detail(x["uuid"]))
            except Exception as e: print("ERR",x["uuid"],e); continue
            pk=None
            if v is not None:
                if u=="kg": pk=v
                elif m: pk=v/m
            print(x["uuid"],x["geo"],x["type"],u,m,v,"-> per kg",pk,"|",x["name"][:80])
            if pk is not None: vals.append(pk)
        if vals: print("n",len(vals),"median",statistics.median(vals),"min",min(vals),"max",max(vals))
