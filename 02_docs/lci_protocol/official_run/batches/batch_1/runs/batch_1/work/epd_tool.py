"""Read-only ÖKOBAUDAT API helper: GWP-fossil A1-A3 per kg for EN 15804+A2 datasets."""
import sys, json, re, statistics, subprocess, urllib.parse
import xml.etree.ElementTree as ET
R="https://oekobaudat.de/OEKOBAU.DAT/resource"
S=R+"/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75"
def get(url):
    return subprocess.run(["curl","-sS","-m","60","-A","Mozilla/5.0",url],capture_output=True,text=True).stdout
def listing(**kw):
    q=urllib.parse.urlencode(dict(search="true",format="json",pageSize=500,**kw))
    return json.loads(get(S+"/processes?"+q))["data"]
def local(t): return t.split('}')[-1]
def process(uuid):
    x=get(f"{S}/processes/{uuid}?format=xml&view=extended")
    root=ET.fromstring(x)
    out={"uuid":uuid}
    # reference flow
    ref=None
    rid=[t.text for t in root.iter() if local(t.tag)=="referenceToReferenceFlow"][0].strip()
    for e in root.iter():
        if local(e.tag)=="exchange" and e.get("dataSetInternalID")==rid:
            ref=e; break
    refuuid=None; refamt=1.0
    for c in ref.iter():
        if local(c.tag)=="referenceToFlowDataSet": refuuid=c.get("refObjectId")
        if local(c.tag)=="meanAmount": refamt=float(c.text)
    out["ref_amount"]=refamt
    # GWP-fossil
    gw=None
    for r in root.iter():
        if local(r.tag)=="LCIAResult":
            d=" ".join(t.text or "" for t in r.iter() if local(t.tag)=="shortDescription")
            if "GWP-fossil" in d:
                gw={}
                for a in r.iter():
                    if local(a.tag)=="amount":
                        m=[v for k,v in a.attrib.items() if k.endswith("module")][0]
                        sc=[v for k,v in a.attrib.items() if k.endswith("scenario")]
                        if not sc: gw[m]=float(a.text)
    out["gwp_fossil"]=gw
    # flow properties
    f=ET.fromstring(get(f"{R}/flows/{refuuid}?format=xml"))
    props=[]; 
    for fp in f.iter():
        if local(fp.tag)=="flowProperty":
            nm=[t.text for t in fp.iter() if local(t.tag)=="shortDescription" and t.get("{http://www.w3.org/XML/1998/namespace}lang")=="en"]
            mv=[t.text for t in fp.iter() if local(t.tag)=="meanValue"]
            props.append((nm[0] if nm else "?",float(mv[0]) if mv else None))
    names={}; vals={}
    for e in f.iter():
        if local(e.tag)=="PropertyDetails":
            nm=[c.text for c in e.iter() if local(c.tag)=="Name"]
            names[e.get("id")]=nm[0] if nm else "?"
        if local(e.tag)=="PropertyData":
            d=[c.text for c in e.iter() if local(c.tag)=="Data"]
            vals[e.get("property")]=d[0] if d else None
    out["matml"]={names.get(k,k):v for k,v in vals.items()}
    refprop=[t.text for t in f.iter() if local(t.tag)=="referenceToReferenceFlowProperty"]
    out["props"]=props; out["refprop"]=int(refprop[0]) if refprop else 0
    # unit
    out["refprop_name"]=props[out["refprop"]][0]
    mass=[v for n,v in props if n=="Mass"]
    out["mass_per_unit"]=mass[0] if mass else None
    if out["mass_per_unit"] is None:
        for k,v in out["matml"].items():
            if k.lower() in("grammage","flächengewicht") and v: out["mass_per_unit"]=float(v)
    nm=[t.text for t in root.iter() if local(t.tag)=="name" and t.get("{http://www.w3.org/XML/1998/namespace}lang") in("en","de")]
    return out
def per_kg(p):
    gf=p["gwp_fossil"] or {}
    g=gf.get("A1-A3")
    if g is None and all(k in gf for k in("A1","A2","A3")): g=gf["A1"]+gf["A2"]+gf["A3"]
    if g is None: return None
    if p["refprop_name"]=="Mass": return g/ p["ref_amount"]
    if p["mass_per_unit"]: return g/(p["ref_amount"]*p["mass_per_unit"])
    return None
def run(items,label=""):
    rows=[]
    for it in items:
        try: p=process(it["uuid"])
        except Exception as e: rows.append((it["name"],it["uuid"],"ERR "+str(e)));continue
        v=per_kg(p)
        rows.append((it["name"],it["uuid"],it["geo"],it["owner"],p["refprop_name"],p["mass_per_unit"],(p["gwp_fossil"] or {}).get("A1-A3") or sum((p["gwp_fossil"] or {}).get(k,0) for k in("A1","A2","A3")),v))
        print(rows[-1],flush=True)
    vals=[r[-1] for r in rows if isinstance(r[-1],float)]
    if vals: print("N=",len(vals),"median per kg=",statistics.median(vals),"min",min(vals),"max",max(vals))
    return rows
if __name__=="__main__":
    kw=dict(a.split("=",1) for a in sys.argv[1:])
    lst=listing(**kw)
    a2=[x for x in lst if any("A2" in c["name"] for c in x["compliance"])]
    print(len(lst),"datasets,",len(a2),"A2")
    run(a2)
