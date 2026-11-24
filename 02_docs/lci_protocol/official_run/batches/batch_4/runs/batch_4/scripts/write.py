import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from build import *
OKB="https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid="
NMD="https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/"
NMDM="https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
RICS="https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf"
WB="protocol_predetermined_values.xlsx"
DEC=[];DS=[];EPD=[];CFF=[];BIO=[]
def dec(mid,q,ans,val="",unit="",ev="",link="",step=""):
    DEC.append([RUN,mid,q,ans,val,unit,ev,link,step,DATE])
def sig(x,n=3):
    return float(f"{x:.{n}g}")
# ---- EPD sets
def epdset(cls,name=""):
    sel=[x for x in okb.index() if cls.lower() in x.get("classific","").lower() and okb.is_a2(x) and name.lower() in x["name"].lower()]
    vals=[];ids=[]
    for x in sel:
        v,u,m=okb.gwp_fossil_a1a3_per_kg(okb.detail(x["uuid"]))
        pk=v if (v is not None and u=="kg") else (v/m if v is not None and m else None)
        if pk is not None: vals.append(pk); ids.append(x["uuid"])
    return ids,vals
S={}
S["plywood"]=epdset("Holz / Holzwerkstoffe / Sperrholz")
S["aac"]=epdset("Mineralische Baustoffe / Steine und Elemente / Porenbeton")
S["concrete"]=epdset("Mörtel und Beton / Beton","C30/37")
for k,(i,v) in S.items(): print(k,len(v),statistics.median(v))
def epdrow(mid,chk,cat,ids,vals,ours,result,route,flags,reason,wear,dist=None,kept=""):
    med=statistics.median(vals) if vals else ""
    ratio=ours/med if vals and ours is not None else ""
    EPD.append([RUN,mid,chk,REL,cat,";".join(ids),len(vals),sig(med,4) if vals else "",sig(ours,4) if ours is not None else "not computed",sig(ratio,3) if ratio!="" else "",result,*flags,reason,sig(wear,3) if wear is not None else "not computed",route,sig(abs(ratio-1),3) if ratio!="" else "",kept])
def nmd(mid,cat,shares,mats):
    dec(mid,"C2 · ROUTE",cat,"",f"landfill {shares['landfill']*100:.0f} / incineration {shares.get('incineration',0)*100:.0f} / recycling {shares.get('recycling',0)*100:.0f} / reuse 0 %",f"sheet nmd_eol, row for '{mats}'","",NMD)
def a4(mid,t1,t2,t2ev,t3=None,t3ev="",t2link="",t3link=""):
    dec(mid,"A4 · T1",t1[0],"","",t1[1],NMDM)
    if t2 is not None: dec(mid,"A4 · T2",t2,"","",t2ev,t2link)
    if t3 is not None: dec(mid,"A4 · T3",t3,"","",t3ev,t3link)
# ================= decisions per material
# ---------- PLYWOOD
mid="plywood"; ids,vals=S[mid]; m=M[mid]
dec(mid,"D1","yes","market for plywood, RER","","ecoinvent 'plywood' (veneer sheets glued with urea-formaldehyde resin, sanded, cut) = hardwood veneer + adhesive, as in the input (veneer 0.922, adhesive 0.077); extra process inputs (tap water, lubricating oil, steel) are not constituents; wet mass 823 kg/m3, 7.1 % water, close to input (796 kg/m3, 6.8 % water)","","plywood; veneer; plywood production")
dec(mid,"D1","note","ecoinvent adhesive share 87 kg UF resin / 823 kg = 10.6 % vs input 7.7 % (PF/UF/MUF adhesive and coating)","","shares are not part of the D1 test; logged as difference","")
dec(mid,"D2","yes","market for plywood","","market dataset exists (RER and RoW)","")
dec(mid,"D3","RER","","","European market group none; RER market exists (rule 2)","")
dec(mid,"D4","single variant","","","only one 'plywood' market per location; unit m3, 1 kg = 1/823 m3","")
dec(mid,"CHECK 1","yes",sig(M[mid]["gwp_a13"],3),"kg CO2e/kg",f"ours {m['gwp_a13']:.4f} vs median {statistics.median(vals):.4f} of {len(vals)} EPDs, ratio {m['gwp_a13']/statistics.median(vals):.2f}: within 0.5-1.5","",)
a4(mid,("no","delivered as boards"),"yes","DE: ÖKOBAUDAT EPD 'Veneer plywood (German average)' (DE); ES: Garnica (La Rioja); IT: Bellotti SpA (Cermenate); FR: Garnica France plants -> at least 3 of 5","",
   "Garnica https://www.garnica.one/en-us/about-us.html ; Bellotti https://nauticexpo.com/soc/bellotti-spa-30295.html ; EPD "+OKB+"1c01243d-fd22-4655-bfaf-484dc024d620")
dec(mid,"A4 · T2","(archetype)","national","lorry 150 km = 0.15 tkm","TRANSPORT · NATIONAL",NMDM)
dec(mid,"A5 · I1","no",39,"kg per piece","18 mm birch plywood sheet 2500 x 1250 mm weighs 39 kg (listing); at the EPD density 796 kg/m3 it is 44.8 kg: both under 50 kg, installed by hand (thickness 18 mm is a typical-board assumption)","https://www.penn-elcom.com/mc/18mm-thick-birch-wood-panel-m870018-eu")
dec(mid,"A5 · L1","no","","","prefab boards fixed dry -> 3 % waste (NMD)",NMDM)
dec(mid,"A5 · LOSS","0.0309","kg lost per kg installed","","0.03/(1-0.03)",NMDM)
dec(mid,"C1 · X1","no",39,"kg per piece","screwed/nailed boards under 50 kg, taken apart by hand; no diesel row","https://www.penn-elcom.com/mc/18mm-thick-birch-wood-panel-m870018-eu")
nmd(mid,"55 board material, clean",dict(landfill=.05,incineration=.85,recycling=.10),"plywood")
dec(mid,"C2 · TKM","",f"{M[mid]['c2_tkm']:.4f}","tkm per kg","0.05x50 + 0.85x100 + 0.10x50 km / 1000","")
for rt,sh_ in [("landfill",.05),("incineration",.85),("recycling",.10)]:
    dec(mid,f"W1: plywood × {rt}","no","","","no ecoinvent waste-treatment dataset named for plywood (searched 'waste plywood', 'treatment of waste wood'); -> W2 fallback class Wood, wood-based (sheet waste_fallback)","",)
    dec(mid,f"W2: plywood × {rt}","dataset","", "", {"landfill":"treatment of waste wood, untreated, sanitary landfill (CH; RoW also exists; CH first in D3)","incineration":"treatment of waste wood, untreated, municipal incineration (GLO; only one with this name)","recycling":"treatment of waste wood, post-consumer, sorting and shredding (CH)"}[rt],"")
dec(mid,"D · CFF · F1","Wood panels","","","sheet cff_archetypes: plywood in 'Wood panels'","")
dec(mid,"D · BIO-C · B1: beech veneer, incl. moisture","Wood","","","sheet carbon_archetypes","")
dec(mid,"D · BIO-C · B1: adhesive and coating, PF/UF/MUF","Non-biogenic","","","sheet carbon_archetypes","")
# ---------- AAC
mid="aac"; ids,vals=S[mid]; m=M[mid]
dec(mid,"D1","no","","","ecoinvent 'autoclaved aerated concrete block production' (CH, IN, RoW): sand 0.504, cement 0.26, quicklime 0.104, anhydrite 0.044, aluminium 0.0007 plus tap water 0.184 kg/kg (mass balance: ~0.09 kg water stays in the product) and packing; the input lists no water -> an extra constituent -> not an exact match (strict reading, see protocol_issues)","","autoclaved; aerated concrete; AAC")
dec(mid,"D1b","yes","market for autoclaved aerated concrete block, CH","","same product (AAC block) and state; main constituent quartz sand in both (0.594 input; 0.504 dataset); differences logged in dataset_choices","","")
dec(mid,"D2","yes","market","","market exists for CH, IN, RoW","")
dec(mid,"D3","CH","","","no European market group, RER, Europe w/o CH, DE, FR, IT, ES, NL, AT, SE, FI, PL market; CH is next in the country list (before GLO/RoW)","")
dec(mid,"D4","single variant","","","one dataset per location","")
dec(mid,"CHECK 2","yes",sig(m["gwp_a13"],3),"kg CO2e/kg",f"ours {m['gwp_a13']:.4f} vs median {statistics.median(vals):.4f} of {len(vals)} EPDs, ratio {m['gwp_a13']/statistics.median(vals):.2f}: within 0.5-1.5","")
a4(mid,("no","delivered as blocks/units"),"yes","DE: Xella 10 German AAC plants (EPD); IT: Xella Italia (ÖKOBAUDAT dataset in material_overview); NL: Ytong partition wall element NL (EPD in ÖKOBAUDAT); FR: Xella France plants -> at least 3 of 5","",
   "https://www.sentinel-holding.eu/Kunden/Xella%20Deutschland%20GmbH/zertifikat-12050-10-1021-en.pdf ; https://www.bft-international.com/en/artikel/artikel_en_1284443.html ; "+OKB+"75d70011-b0c7-46b1-9fa2-4d9cdbdf8c1a")
dec(mid,"A4 · T2","(archetype)","national","lorry 150 km = 0.15 tkm","TRANSPORT · NATIONAL",NMDM)
dec(mid,"A5 · I1","no",20,"kg per piece","typical block 625 x 250 x 300 mm (assumed typical) x 428 kg/m3 (EPD density) = 20 kg, under 50 kg; laid by hand","https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=e6819670-eb6c-4104-adea-f7f8bb2f49e6")
dec(mid,"A5 · L1","yes","","","masonry laid from small units with (thin-bed) mortar on site -> in situ, 5 % (NMD example: masonry laid with mortar)",NMDM)
dec(mid,"A5 · LOSS","0.0526","kg lost per kg installed","","0.05/0.95",NMDM)
dec(mid,"C1 · X1","yes","","","bonded with thin-bed mortar -> demolished by machine, diesel 0.036 MJ/kg","")
nmd(mid,"9 aerated concrete",dict(landfill=.01,recycling=.99),"AAC")
dec(mid,"C2 · TKM","",f"{m['c2_tkm']:.4f}","tkm per kg","all routes 50 km","")
for rt in ["landfill","recycling"]:
    dec(mid,f"W1: AAC block × {rt}","no","","","no waste AAC / aerated concrete treatment dataset (searched 'waste aerated', 'aerated'); the product itself is the waste material; -> W2","")
    dec(mid,f"W2: AAC block × {rt}","dataset","","",{"landfill":"treatment of inert waste, inert material landfill (CH)","recycling":"treatment of waste reinforced concrete, recycling (Europe w/o CH)"}[rt]+"; class Mineral chosen as AAC is listed in Mineral, Gypsum and Metal rows (main constituent sand)","")
dec(mid,"D · CFF · F1","Mineral, crushed to aggregate","","","sheet cff_archetypes","")
for c in ["quartz sand","cement","quicklime","anhydrite / gypsum","aluminium paste"]: dec(mid,f"D · BIO-C · B1: {c}","Non-biogenic","","","sheet carbon_archetypes","")
# ---------- MYCELIUM
mid="mycelium"; m=M[mid]
dec(mid,"D1","no","","","no mycelium / fungal composite or mushroom-based product in ecoinvent 3.12 cut-off (searched 'mycelium', 'mushroom', 'spawn')","","mycelium; mushroom; spawn")
dec(mid,"D1b","no","","","no product with the same name and state; test cannot be passed -> build from scratch","","mycelium")
dec(mid,"A4 · T1","no","","","delivered as panels",NMDM)
dec(mid,"A4 · T2","no","","","no manufacturer found in DE/FR/IT/ES; NL listing unverified; <3 of 5 (searched mycelium panel manufacturers)","https://circulareconomy.europa.eu/platform/en/good-practices/biomyc-developing-tailored-products-mycelium-composite")
dec(mid,"A4 · T3","yes","","","Europe: C-biotech and PermaFungi (Belgium), Myceen (Estonia), Biohm (UK) make mycelium panels -> EU manufactured: lorry 1,500 km + sea 100 km","https://biofuelsdigest.com/c-biotech-unveils-hemp-and-mycelium-construction-panels/ ; https://api.brusselstimes.com/brussels/235401/brussels-company-uses-food-waste-to-create-fungi-insulation/")
for n,amt in myc_consts:
    pass
dec(mid,"D5: hemp hurd / fibre substrate (dry)","yes","market for hemp hurd, FR","","ecoinvent has hemp hurd (FR only)","","hemp; hemp hurd")
dec(mid,"D2: hemp hurd / fibre substrate (dry)","yes","market","","market for hemp hurd exists","")
dec(mid,"D3: hemp hurd / fibre substrate (dry)","FR","","","no European market group/RER/Europe w/o CH/DE; FR is the first country in the order","")
dec(mid,"D5: wheat flour (nutrient)","yes","market for wheat flour, RoW","","ecoinvent wheat flour markets: RoW, ZA","","wheat; market for wheat flour")
dec(mid,"D3: wheat flour (nutrient)","RoW","","","no European/GLO market; RoW precedes 'other' (ZA)","")
dec(mid,"D5: grain spawn","no","proxy: market for rye grain, CH","","no spawn dataset; rye grain is a common spawn grain (millet also exists, GLO); proxy flagged TeR 4","","spawn; mushroom; rye; millet")
dec(mid,"D3: grain spawn","CH","","","CH single European country before RoW","")
dec(mid,"CHECK","yes","1.000","kg","hurd 0.85 + flour 0.05 + spawn 0.10 = 1.00 = input","")
# machines
dec(mid,"P1: pasteurising substrate","machine","Rootlab 150 L electric autoclave","kWh/kg","0.107 kWh/kg (6 kW x 0.75 h / 42 kg); fewer than 3 complete datasheets (Hokken GXMQ lacks cycle time and mass; Consteril lacks power); craft/commercial scale -> proxy TeR 4","https://www.rootlab.com.au/product/autoclave-150-livers-vertical/".replace("livers","liters"))
dec(mid,"P2: pasteurising substrate","unclear","","kg","machine mass not on any datasheet found -> no wear row (lower-impact branch)","")
dec(mid,"P1: inoculation and mixing","machine","Magaldi Mixer 700 (median of 500/700/900)","kWh/kg",f"{mix_used[1]:.3e} kWh/kg; all three candidates from one manufacturer (Hokken ST-M350 lacks weight and throughput)","https://www.magaldi.com/en/applications/paddle-mixer")
dec(mid,"P2: inoculation and mixing","machine","Magaldi Mixer 700","kg per kg processed",f"{5720/(22500*LIFE_H):.3e}","https://www.magaldi.com/en/applications/paddle-mixer")
dec(mid,"P1: incubation","unclear","","","incubation is held in a climate-controlled room; no machine datasheet with power and throughput found (only laboratory incubators) -> no rows (lower-impact branch)","")
dec(mid,"P2: incubation","unclear","","","no P1 rows -> no machine row","")
dec(mid,"P1: moulding","unclear","","","no press/moulding datasheet found with power AND throughput (cycle time) for panel moulding -> no rows (lower-impact branch)","")
dec(mid,"P2: moulding","unclear","","","no P1 rows -> no machine row","")
dec(mid,"P1: heat deactivation and drying","machine","STELA WT-HS 830/100 belt dryer (median of Sulzle, STELA 830, STELA 3870)","kWh/kg",f"heat {dry_heat_kwh:.3f} kWh/kg, electricity {dry_el:.4f} kWh/kg; kg of water evaporated used as kg processed; values from a search summary of the brochure, PDF not readable -> proxy TeR 4","https://www.messe.de/apollo/ligna_2019/obs/Binary/A922945/922945_01820801.pdf")
dec(mid,"P2: heat deactivation and drying","unclear","","","dryer mass not found -> no wear row","")
dec(mid,"CHECK 3","no check possible","","","no EN 15804+A2 EPD for mycelium panels in ÖKOBAUDAT (searched name and classification)","")
dec(mid,"A5 · I1","no",5.4,"kg per piece","typical panel 1200 x 600 x 50 mm at ~150 kg/m3 = 5.4 kg (assumption; composites ~100-200 kg/m3)","https://materialdistrict.com/material/mycelium-composite-panel/")
dec(mid,"A5 · L1","no","","","prefab panels fixed dry -> 3 %",NMDM)
dec(mid,"A5 · LOSS","0.0309","kg lost per kg installed","","0.03/0.97",NMDM)
dec(mid,"C1 · X1","no",5.4,"kg per piece","mechanically fixed panels under 50 kg, by hand","")
nmd(mid,"52 organic / bio-based, other",dict(landfill=.05,incineration=.95),"mycelium")
dec(mid,"C2 · TKM","",f"{m['c2_tkm']:.4f}","tkm per kg","0.05x50 + 0.95x100 km / 1000","")
for n,_ in myc_consts:
    for rt in ["landfill","incineration"]:
        dec(mid,f"W1: {n} × {rt}","no","","","no waste dataset for this plant constituent; -> W2 class Other plant-based = as wood","")
        dec(mid,f"W2: {n} × {rt}","dataset","","",{"landfill":"treatment of waste wood, untreated, sanitary landfill (CH)","incineration":"treatment of waste wood, untreated, municipal incineration (GLO)"}[rt],"")
dec(mid,"D · CFF · F1","Other plant-based","","","sheet cff_archetypes","")
dec(mid,"D · BIO-C · B1: hemp hurd / fibre substrate (dry)","Cellulose fibres and stalks","","","sheet carbon_archetypes","")
dec(mid,"D · BIO-C · B1: wheat flour (nutrient)","Cellulose fibres and stalks","","","sheet carbon_archetypes","")
dec(mid,"D · BIO-C · B1: grain spawn","Mycelium","","","sheet carbon_archetypes","")
# ---------- CONCRETE
mid="concrete"; ids,vals=S[mid]; m=M[mid]; med=statistics.median(vals)
dec(mid,"D1","no","","","ecoinvent concrete 30MPa AT (market) also contains ground granulated blast furnace slag (~1 %), limestone filler and an organic admixture (~0.07 %), none listed in the input (aggregates, cement, water) -> extra constituents -> not an exact match (strict reading)","","concrete; market for concrete")
dec(mid,"D1b","yes","market for concrete, 30MPa, AT","","same product (ready-mix concrete) and state; main constituent aggregates (gravel+sand ~81 % vs 76.9 %); differences logged","","")
dec(mid,"D2","yes","market","","market for concrete exists","")
dec(mid,"D3","AT","","","no European market group, RER, Europe w/o CH, DE, FR, IT, ES, NL market for concrete; AT is the first in the country list","")
dec(mid,"D4","30MPa","","","variant matching C30/37 (30 MPa); alternatives: normal strength AT, 25MPa AT","")
dec(mid,"CHECK 2","no",sig(m["gwp_approx"],3),"kg CO2e/kg",f"ours {m['gwp_approx']:.4f} vs median {med:.4f} of {len(vals)} C30/37 EPDs, ratio {m['gwp_approx']/med:.2f} > 1.5 -> build from scratch","")
for n,a in [("aggregates",.769),("cement",.145),("water",.087)]:
    pass
dec(mid,"D5: aggregates","no","proxy: market for gravel, crushed, CH","","no 'aggregates' product; ecoinvent concrete uses gravel and sand; TeR 4","","aggregate; gravel; sand")
dec(mid,"D3: aggregates","CH","","","only European gravel market is CH","")
dec(mid,"D5: cement","yes","market for cement, unspecified, Europe without Switzerland","","","","market for cement")
dec(mid,"D3: cement","Europe without Switzerland","","","European market (rule 1/3)","")
dec(mid,"D5: water","yes","market group for tap water, RER","","","","market for tap water")
dec(mid,"D3: water","RER","","","European market group RER","")
dec(mid,"CHECK","yes","1.001","kg","0.769+0.145+0.087 = 1.001 = input sum","")
dec(mid,"P1: mixing","machine","Sicoma MAO3000/2000 (median of Sicoma, MEKA MB-T 2,0, Liebherr DW 4.5)","kWh/kg",f"{cu[1]:.3e} kWh/kg; MEKA and Liebherr datasheets give no cycle time (90 s from Sicoma borrowed)","https://catalog.jamiesonequipment.com/item/all-products-sicoma-mixers/gories-twin-shaft-mixers-twin-shaft-concrete-mixer/mao3000-2000")
dec(mid,"P2: mixing","machine","Sicoma MAO3000/2000","kg per kg processed",f"{cu[4]/(cu[3]*LIFE_H):.3e}",LIFE_LINK)
dec(mid,"CHECK 3","no",sig(m["gwp_a13"],3),"kg CO2e/kg",f"ours {m['gwp_a13']:.4f} vs median {med:.4f}, ratio {m['gwp_a13']/med:.2f} > 1.5","")
dec(mid,"REVIEW","keep built LCI, flagged",sig(m["gwp_a13"],3),"kg CO2e/kg",f"approximate 1.621x (distance 0.621), built 1.620x (distance 0.620); built is closer and lower; exact match not tried (D1 no)","")
dec(mid,"A4 · T1","yes","","","ready-mixed concrete delivered by truck, bulk -> 50 km",NMDM)
dec(mid,"A5 · I1","yes","","","poured or pumped on site; diesel 0.015 MJ/kg","")
dec(mid,"A5 · L1","yes","","","cast in situ -> 5 %",NMDM)
dec(mid,"A5 · LOSS","0.0526","kg lost per kg installed","","0.05/0.95",NMDM)
dec(mid,"C1 · X1","yes","","","cast in place -> demolished by machine, diesel 0.036 MJ/kg","")
nmd(mid,"8 concrete, masonry, reinforced concrete",dict(landfill=.01,recycling=.99),"concrete")
dec(mid,"C2 · TKM","",f"{m['c2_tkm']:.4f}","tkm per kg","all routes 50 km","")
for n,_ in [("aggregates",1),("cement",1),("water",1)]:
    dec(mid,f"W1: {n} × landfill","no","","","no landfill-route dataset named for this constituent; -> W2 class Mineral","")
    dec(mid,f"W2: {n} × landfill","dataset","","","treatment of inert waste, inert material landfill (CH)","")
    if n=="cement": dec(mid,f"W1: {n} × recycling","yes","","","treatment of waste cement in concrete and mortar, sorting plant (Europe w/o CH)","")
    else:
        dec(mid,f"W1: {n} × recycling","no","","","no waste dataset for this constituent -> W2","")
        dec(mid,f"W2: {n} × recycling","dataset","","","treatment of waste reinforced concrete, recycling (Europe w/o CH)","")
dec(mid,"D · CFF · F1","Mineral, crushed to aggregate","","","sheet cff_archetypes","")
for c in ["aggregates","cement","water"]: dec(mid,f"D · BIO-C · B1: {c}","Non-biogenic","","","sheet carbon_archetypes","")

# ================= dataset_choices rows
def dsrow(mid,r,module=None):
    mc=r["mach"]
    DS.append([RUN,mid,module or r["module"],r["purpose"],r["search"],r["cands"],r["name"],r["prod"],r["loc"],r["unit"],r["amount"],ECO if True else "",r["rule"],r["proxy"],r["TeR"] if r["TeR"] is not None else "",r["GeR"] if r["GeR"] is not None else "",r["TiR"] if r["TiR"] is not None else "",
        mc.get("machine_type",""),mc.get("machine_candidates",""),mc.get("machine_used",""),mc.get("power_kW",""),mc.get("throughput",""),mc.get("machine_mass",""),mc.get("machine_life",""),mc.get("values_as_found",""),mc.get("value_source",""),mc.get("value_link",""),mc.get("conversions",""),mc.get("per_kg",""),"3.12 cut-off",DATE])
def blocks(mid):
    m=M[mid]; loss=m["loss"]
    B={}
    A13=list(m["A13"]) if mid!="concrete" else list(m["A13"])
    B["A1-A3"]=A13
    B["A4"]=m["A4"]
    a5=[]
    if m["A5_diesel"]: a5.append(R("A5 diesel","A5",DIESEL,m["A5_diesel"],"A5 (I1 yes)"))
    a5.append(R("A5 lorry (loss)","A5",LORRY,loss*m["c2_tkm"],"A5 loss to waste, C2 distance",comment=f"loss {loss:.4f} x {m['c2_tkm']:.4f} tkm"))
    a5+=eol_rows(m["eol"],loss)
    B["A5"]=a5
    B["C1"]=[R("C1 diesel","C1",DIESEL,m["C1_diesel"],"C1 (X1 yes)")] if m["C1_diesel"] else []
    B["C2"]=[R("C2 lorry","C2",LORRY,m["c2_tkm"],"C2 route shares x distance",comment=json.dumps(m["c2_split"]))]
    B["C3-C4"]=eol_rows(m["eol"])
    return B
BL={}
for mid in M:
    BL[mid]=blocks(mid)
    for mod,rows in BL[mid].items():
        for r in rows: dsrow(mid,r)
    if mid=="concrete": dsrow(mid,M[mid]["approx"],"A1-A3")  # approximate LCI tried (not kept)
# ================= epd_check
fl=lambda mid,ds_state,mach:["per m3 values divided by each EPD's mass property (kg/m3); ours by ecoinvent wet mass" if mid!="mycelium" else "n/a",ds_state,"GWP-fossil A1-A3 only both sides",mach]
mid="plywood"; ids,vals=S[mid]; m=M[mid]
med_ex=statistics.median([v for v in vals if abs(v-0.4814)>1e-3])
epdrow(mid,"CHECK 1","Holz / Holzwerkstoffe / Sperrholz",ids,vals,m["gwp_a13"],"pass","exact",fl(mid,"market for plywood RER matches state (sanded, cut); EPD set includes 'best wood CLT' filed under Sperrholz (0.481) and a generic plywood 0.285","no machine rows"),f"median without the misfiled CLT EPD would be {med_ex:.3f} (ratio {m['gwp_a13']/med_ex:.2f}, still pass); ecoinvent adhesive 10.6 % vs 7.7 %",0.0)
mid="aac"; ids,vals=S[mid]; m=M[mid]
epdrow(mid,"CHECK 2","Mineralische Baustoffe / Steine und Elemente / Porenbeton",ids,vals,m["gwp_a13"],"pass","approximate",fl(mid,"set includes Multipor insulation board (1.20), granulate (0.015), reinforced elements; median unchanged (0.461) when insulation board and granulate are removed","no machine rows"),"ecoinvent CH block with extra water; EPD set mostly German/Romanian Xella/Hebel products",0.0)
mid="mycelium"; m=M[mid]
epdrow(mid,"CHECK 3","none (no EPD category)",[],[],m["gwp_a13"],"no check possible","built",["n/a","n/a","GWP-fossil A1-A3 only","pasteurising and drying are proxy rows; incubation and moulding have no rows; wear rows only for mixing"],"no EN 15804+A2 mycelium EPD in ÖKOBAUDAT",m["wear"])
mid="concrete"; ids,vals=S[mid]; m=M[mid]
epdrow(mid,"CHECK 2","Mörtel und Beton / Beton (C30/37 in name, EN 15804+A2)",ids,vals,m["gwp_approx"],"fail","approximate",fl(mid,"market for concrete 30MPa AT includes slag, filler and admixture","no machine rows"),"EPDs are mostly German ECOPact (low-clinker) mixes; ecoinvent concrete uses unspecified cement and a market with transport",0.0)
epdrow(mid,"CHECK 3","Mörtel und Beton / Beton (C30/37 in name, EN 15804+A2)",ids,vals,m["gwp_a13"],"fail","built",fl(mid,"constituents from ecoinvent markets; aggregates proxied by crushed gravel","mixing: Sicoma mixer"),"cement 0.145 kg x ecoinvent cement (Europe w/o CH) carries ~95 % of the result; EPD C30/37 set (63) dominated by low-clinker ECOPact recipes",m["wear"])
epdrow(mid,"REVIEW","Mörtel und Beton / Beton (C30/37)",ids,vals,m["gwp_a13"],"flagged","built",["converted as above","ecoinvent datasets match state","GWP-fossil only","steps: mixing only (Sicoma MAO3000/2000, median of 3); no proxy machine"],f"approximate {m['gwp_approx']:.4f} (ratio {m['gwp_approx']/med:.3f}, distance {abs(m['gwp_approx']/med-1):.3f}); built {m['gwp_a13']:.4f} (ratio {m['gwp_a13']/med:.3f}, distance {abs(m['gwp_a13']/med-1):.3f}); exact not tried (D1 no). Kept built (closer, lower); flagged",m["wear"],kept="built")
# ================= cff / bioc
for mid,arch in [("plywood","Wood panels"),("aac","Mineral, crushed to aggregate"),("mycelium","Other plant-based"),("concrete","Mineral, crushed to aggregate")]:
    sh_=M[mid]["c2_split"]; CFF.append([RUN,mid,arch,sh_.get("recycling",0),0,sh_.get("incineration",0),sh_.get("landfill",0),"flagged: low data quality (REVIEW)" if mid=="concrete" else "", "from sheets cff_archetypes and nmd_eol"])
bio=[("plywood","beech veneer, incl. moisture",.922,"Wood",0.0796,"","moisture from input note: water 6.8 % / atro 85.4 % = 0.0796 (dry basis)"),("plywood","adhesive and coating, PF/UF/MUF",.077,"Non-biogenic","","",""),
     ("mycelium","hemp hurd / fibre substrate (dry)",.85,"Cellulose fibres and stalks","","","input says dry; archetype default moisture not applied by us"),("mycelium","wheat flour (nutrient)",.05,"Cellulose fibres and stalks","","",""),("mycelium","grain spawn",.10,"Mycelium","","",""),
     ("aac","quartz sand",.594,"Non-biogenic","","",""),("aac","cement",.223,"Non-biogenic","","",""),("aac","quicklime",.148,"Non-biogenic","","",""),("aac","anhydrite / gypsum",.035,"Non-biogenic","","",""),("aac","aluminium paste",.0007,"Non-biogenic","","",""),
     ("concrete","aggregates",.769,"Non-biogenic","","",""),("concrete","cement",.145,"Non-biogenic","","",""),("concrete","water",.087,"Non-biogenic","","","")]
for b in bio: BIO.append([RUN,*b])
# ================= write csv
def wcsv(fn,hdr,rows):
    with open(os.path.join(OUT,fn),"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
def hdr(fn): return open(os.path.join(os.path.dirname(OUT),"..","templates",fn)).readline().strip().split(",")
T=os.path.join(OUT,"..","..","templates")
def h(fn): return open(os.path.join(T,fn)).readline().strip().split(",")
wcsv("decisions.csv",h("decisions.csv"),DEC); wcsv("dataset_choices.csv",h("dataset_choices.csv"),DS); wcsv("epd_check.csv",h("epd_check.csv"),EPD)
wcsv("cff_inputs.csv",h("cff_inputs.csv"),CFF); wcsv("bioc_inputs.csv",h("bioc_inputs.csv"),BIO)
# ================= LCI sheets
def dqr(r): 
    v=[r[k] for k in("TeR","GeR","TiR") if r[k] is not None]; return sig(sum(v)/3,3) if v else None
def write_lci(mid):
    m=M[mid]; B=BL[mid]; wb=openpyxl.Workbook(); ws=wb.active; ws.title="LCI"
    bold=Font(bold=True); ws.append(["Database","raw_baselines"]); ws.append([])
    chain=[("A1-A3","A1–A3",f"{mid}, at factory gate",None),("A4","A4",f"{mid}, delivered to site","A1-A3"),("A5","A5",f"{mid}, installed","A4"),("C1","C1",f"{mid}, demolished","A5"),("C2","C2",f"{mid}, at waste site","C1"),("C3-C4","C3–C4",f"{mid}, cradle to grave","C2")]
    names={k:(lab,ref) for k,lab,ref,_ in chain}
    for key,lab,ref,prev in chain:
        rows=B[key]
        comment=""
        if key=="A1-A3":
            ws_=[(r["weight"] if r["weight"] is not None else (r["amount"] if r["unit"]=="kilogram" else 1.0),dqr(r)) for r in rows if dqr(r) is not None]
            tw=sum(w for w,_ in ws_); d=sum(w*q for w,q in ws_)/tw if tw else None
            comment=f"route: {m['route']}; mass-weighted DQR {d:.2f}" + (" (above 3: low quality)" if d and d>3 else "")
            if mid=="concrete": comment+="; flagged (CHECK 3 failed, REVIEW kept built LCI)"
            if mid=="mycelium": comment+="; incubation and moulding have no rows (no machine data); wear only for mixing"
        for a,b in [("Activity",f"{mid}, {lab}"),("reference product",ref),("unit","kilogram"),("location","RER"),("module",lab),("comment",comment)]: ws.append([a,b])
        ws.append(["Exchanges"]); ws.append(["name","amount","unit","location","reference product","database","type","module","rule","TeR","GeR","TiR","DQR","comment"])
        for c in ws[ws.max_row]: c.font=bold
        ws.append([f"{mid}, {lab}",1,"kilogram","RER",ref,"raw_baselines","production",lab,"–",None,None,None,None,None])
        if prev:
            amt=1+m["loss"] if key=="A5" else 1
            ws.append([f"{mid}, {names[prev][0]}",amt,"kilogram","RER",names[prev][1],"raw_baselines","technosphere",lab,"–",None,None,None,None,"previous block"+(" (A5 takes 1 + loss)" if key=="A5" else "")])
        for r in rows:
            ws.append([r["name"],r["amount"],r["unit"],r["loc"],r["prod"],ECO,"technosphere",lab,r["rule"],r["TeR"],r["GeR"],r["TiR"],dqr(r),(r["comment"]+(" | "+r["proxy"] if r["proxy"] else ""))[:400]])
        ws.append([])
    wb.create_sheet("README").append(["Per kg of material, cradle to grave. Modules B and D are not written. Waste treatment rows have negative amounts (ecoinvent convention) except sorting-and-shredding of wood, whose reference product is wood chips (positive amount)."])
    wb.save(os.path.join(OUT,f"LCI_{mid}.xlsx"))
for mid in M: write_lci(mid)
# also whole-chain GWP for info
for mid in M:
    tot=0
    for mod,rows in BL[mid].items():
        for r in rows: tot+=score(r)
    print(mid,"A1-A5,C1-C4 rows (excl. previous-block chaining, loss scaling) sum:",tot)
print("done",len(DEC),len(DS),len(EPD))
