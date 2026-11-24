import sys, csv, os, json, statistics, math
sys.path.insert(0,os.path.dirname(__file__))
from bwh import *
import okb
import openpyxl
from openpyxl.styles import Font
RUN="batch_4"; OUT=os.path.join(os.path.dirname(__file__),".."); DATE="2026-11-19"
ECO="ecoinvent-3.12-cutoff"; REL="OBD_2024_III (OEKOBAUDAT release of 13.11.2026)"
_c={}
def unit_impact(name,loc,prod):
    k=(name,loc,prod)
    if k not in _c:
        a=one(name,loc,prod) if prod else one(name,loc); _c[k]=(a,gwp([(a,1)])[0])
    return _c[k]
def ger(loc):
    if loc in("RER","Europe without Switzerland"): return 1
    if loc in("DE","FR","IT","ES","NL","AT","SE","FI","PL","CH"): return 2
    if loc=="GLO": return 3
    if loc=="RoW": return 4
    return 5
LORRY=("market for transport, freight, lorry, unspecified","RER","transport, freight, lorry, diesel, unspecified","ton kilometer")
SEA=("market for transport, freight, sea, container ship, heavy fuel oil","GLO","transport, freight, sea, container ship, heavy fuel oil","ton kilometer")
DIESEL=("market for diesel, burned in building machine","GLO","diesel, burned in building machine","megajoule")
ELEC=("market group for electricity, medium voltage","RER","electricity, medium voltage","kilowatt hour")
HEAT=("market for heat, district or industrial, natural gas","Europe without Switzerland","heat, district or industrial, natural gas","megajoule")
MACH=("market for industrial machine, heavy, unspecified","RER","industrial machine, heavy, unspecified","kilogram")
LIFE_H=8*5000
LIFE_SRC="8 years (BMF AfA-Tabelle Baugewerbe: Trommelmischer 8 y; used for all machines as assumption) x 5,000 h/y (protocol default) = 40,000 h"
LIFE_LINK="https://www.bundesfinanzministerium.de/Content/DE/Standardartikel/Themen/Steuern/Weitere_Steuerthemen/Betriebspruefung/AfA-Tabellen/AfA-Tabelle_Baugewerbe.html"

def R(purpose,module,ds,amount,rule,TeR=None,comment="",proxy="",search="",cands="",weight=None,**mach):
    name,loc,prod,unit=ds
    return dict(purpose=purpose,module=module,name=name,loc=loc,prod=prod,unit=unit,amount=amount,rule=rule,TeR=TeR,
                GeR=ger(loc) if TeR is not None else None,TiR=1 if TeR is not None else None,comment=comment,proxy=proxy,
                search=search,cands=cands,weight=weight,mach=mach)
def waste(ds,amt,purpose,rule,TeR,comment,proxy="proxy (W2 fallback)",search="",cands=""):
    return R(purpose,"C3-C4",ds,amt,rule,TeR,comment,proxy,search,cands)

WOOD_LF=("treatment of waste wood, untreated, sanitary landfill","CH","waste wood, untreated","kilogram")
WOOD_INC=("treatment of waste wood, untreated, municipal incineration","GLO","waste wood, untreated","kilogram")
WOOD_REC=("treatment of waste wood, post-consumer, sorting and shredding","CH","wood chips, from post-consumer wood, dry, measured as dry mass","kilogram")
INERT_LF=("treatment of inert waste, inert material landfill","CH","inert waste, for final disposal","kilogram")
RC_REC=("treatment of waste reinforced concrete, recycling","Europe without Switzerland","waste reinforced concrete","kilogram")
CEM_REC=("treatment of waste cement in concrete and mortar, sorting plant","Europe without Switzerland","waste cement in concrete and mortar","kilogram")

def eol_rows(items,loss=None):
    """items: list of (label, mass_kg_per_kg, ds, route, rule, comment, proxy, sign)"""
    rows=[]
    for (label,m,ds,route,rule,cm,proxy,sign) in items:
        if loss is None:
            rows.append(R(f"C3-C4: {label} × {route}","C3-C4",ds,sign*m,rule,4 if proxy else 3,cm,proxy))
        else:
            rows.append(R(f"A5 end of life: {label} × {route}","A5",ds,sign*m*loss,rule,4 if proxy else 3,cm+f" (lost kg = {loss:.4g} per kg installed)",proxy))
    return rows

def lorry_tkm(km_by_route,shares): return sum(km_by_route[r]*shares[r] for r in shares)/1000
KM={"landfill":50,"incineration":100,"recycling":50,"reuse":50}

M={}
# ---------------------------------------------------------------- PLYWOOD
sh=dict(landfill=.05,incineration=.85,recycling=.10); c2=lorry_tkm(KM,sh); loss=.03/.97
ply_mass=823.0
items=[("plywood",1.0,WOOD_LF,"landfill","W2",  "W1 no (no 'waste plywood' treatment dataset); W2 class Wood, wood-based (waste_fallback)","proxy",-sh["landfill"]),
       ("plywood",1.0,WOOD_INC,"incineration","W2","W1 no; W2 class Wood, wood-based","proxy",-sh["incineration"]),
       ("plywood",1.0,WOOD_REC,"recycling","W2","W1 no; W2 class Wood; reference product of this dataset is wood chips (positive amount, burden of sorting+shredding; see protocol_issues)","proxy",sh["recycling"])]
def scale(items,f): return [(a,b*abs(s),c,d,e,g,h,(1 if s>0 else -1)) for (a,b,c,d,e,g,h,s) in [(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]) for i in items] for s in [i[7]]] 
def mk_items(base):  # base items with share baked in sign*share ; split magnitude/sign
    out=[]
    for (l,m,ds,rt,ru,cm,px,v) in base: out.append((l,m*abs(v),ds,rt,ru,cm,px,1 if v>0 else -1))
    return out
ply_items=mk_items(items)
M["plywood"]=dict(
 name="plywood", route="exact",
 A13=[R("finished product","A1-A3",("market for plywood","RER","plywood","cubic meter"),1/ply_mass,"D1 yes, D2 market, D3 RER",1,
        "1 kg of product = 1/823 m3 (ecoinvent wet mass 823 kg/m3 from dataset property); amount in m3",search="plywood; veneer; market for plywood",
        cands="market for plywood RER (chosen); market for plywood RoW; plywood production RER/RoW/CA-QC")],
 A4=[R("A4 lorry","A4",LORRY,0.15,"A4 T2 national 150 km")],
 loss=loss, A5_diesel=None, C1_diesel=None, c2_tkm=c2,
 A5_loss_lorry=True, eol=ply_items,
 c2_split=sh)
# ---------------------------------------------------------------- AAC
sh=dict(landfill=.01,recycling=.99); c2=lorry_tkm(KM,sh); loss=.05/.95
aac_items=mk_items([("AAC block",1.0,INERT_LF,"landfill","W2","W1 no (no waste AAC dataset); W2 class Mineral (AAC listed under Mineral in waste_fallback; main constituent sand)","proxy",-.01),
                    ("AAC block",1.0,RC_REC,"recycling","W2","W1 no; W2 class Mineral, recycling = treatment of waste reinforced concrete, recycling","proxy",-.99)])
M["aac"]=dict(name="AAC",route="approximate",
 A13=[R("finished product (approximate)","A1-A3",("market for autoclaved aerated concrete block","CH","autoclaved aerated concrete block","kilogram"),1.0,"D1b yes, D2 market, D3 CH (single European country)",2,
        "Differences vs input: ecoinvent adds tap water 0.184 kg/kg and packing (clay product) 1 kg/kg; sand 0.504 (input 0.594), cement 0.26 (0.223), quicklime 0.104 (0.148), anhydrite 0.044 (0.035), aluminium 0.0007 (0.0007)",
        search="aerated concrete; autoclaved; market for autoclaved aerated concrete block",cands="market for AAC block CH (chosen), IN, RoW; AAC block production CH/IN/RoW")],
 A4=[R("A4 lorry","A4",LORRY,0.15,"A4 T2 national 150 km")],
 loss=loss,A5_diesel=None,C1_diesel=0.036,c2_tkm=c2,A5_loss_lorry=True,eol=aac_items,c2_split=sh)
# ---------------------------------------------------------------- MYCELIUM
sh=dict(landfill=.05,incineration=.95); c2=lorry_tkm(KM,sh); loss=.03/.97
myc_consts=[("hemp hurd / fibre substrate (dry)",.85),("wheat flour (nutrient)",.05),("grain spawn",.10)]
base=[]
for n,m in myc_consts:
    base.append((n,m,WOOD_LF,"landfill","W2","W1 no (no waste dataset for this constituent); W2 class Other plant-based = as wood","proxy",-sh["landfill"]))
    base.append((n,m,WOOD_INC,"incineration","W2","W1 no; W2 class Other plant-based = as wood","proxy",-sh["incineration"]))
myc_items=mk_items(base)
# machine numbers
rho_sub=150.0
mix=[("Magaldi Mixer 500",11,60,3200),("Magaldi Mixer 700",22,150,5720),("Magaldi Mixer 900",37,400,7600)]
mix_e=[(n,p/(q*rho_sub),p,q*rho_sub,mm) for n,p,q,mm in mix]
mix_used=sorted(mix_e,key=lambda x:x[1])[1]
past_kwh=6*0.75/42
dry_heat_kwh=1.0e3/820.0; dry_el=10/820.0
M["mycelium"]=dict(name="mycelium",route="built",
 A13=[R("constituent: hemp hurd / fibre substrate (dry)","A1-A3",("market for hemp hurd","FR","hemp hurd","kilogram"),.85,"D5 yes, D2 market, D3 FR",3,"market for hemp hurd (FR); only European hurd market",search="hemp; hemp hurd",cands="market for hemp hurd FR; market for hemp residues FR; decorticated fibre production, hemp FR"),
      R("constituent: wheat flour (nutrient)","A1-A3",("market for wheat flour","RoW","wheat flour","kilogram"),.05,"D5 yes, D2 market, D3 RoW",3,"no European wheat flour market; RoW before 'other' (ZA)",search="wheat; market for wheat flour",cands="market for wheat flour RoW (chosen), ZA"),
      R("constituent: grain spawn","A1-A3",("market for rye grain","CH","rye grain","kilogram"),.10,"D5 no, PROXY: rye grain (spawn substrate), D2 market, D3 CH",4,"grain spawn = sterilised grain colonised by mycelium; closest ecoinvent class: cereal grain; mycelium/inoculation burden not included",proxy="proxy",search="spawn; mushroom; rye; millet; wheat grain",cands="market for rye grain CH (chosen), RoW; market for wheat grain CH/RoW; market for millet GLO"),
      # processing
      R("processing: pasteurising substrate (electricity)","A1-A3",ELEC,1*past_kwh,"P1 (autoclave)",4,"Rootlab 150 L electric autoclave: 6 kW x 0.75 h / 42 kg = 0.107 kWh/kg; electric heating, so no heat row",proxy="proxy: craft-scale autoclave, no complete industrial datasheet",weight=1.0,
        machine_type="autoclave (steam sterilizer)",machine_candidates="Rootlab 150 L vertical autoclave (6 kW; 14x3 kg; 40-45 min; no mass) | Hokken GXMQ (11.5 kW; 1080 bags x 2.5 kg/cycle; no cycle time, no mass) | Consteril 26AV-HC (136 kg/cycle; no power)",machine_used="Rootlab 150 L vertical autoclave",power_kW=6,throughput=56.0,machine_mass="not found",machine_life="n/a",
        values_as_found="6 kW; load 14 x 3 kg bags = 42 kg; cycle 40-45 min (45 min used)",value_source="Rootlab product page",value_link="https://www.rootlab.com.au/product/autoclave-150-liters-vertical/",conversions="kg/h = 42 kg / 0.75 h = 56; kWh/kg = 6/56",per_kg=past_kwh),
      R("processing: inoculation and mixing (electricity)","A1-A3",ELEC,1*mix_used[1],"P1 (mixer)",3,f"{mix_used[0]}: {mix_used[2]} kW / ({mix_used[3]:.0f} kg/h)",weight=1.0,
        machine_type="continuous paddle mixer",machine_candidates="; ".join(f"{n} ({p} kW, {q} m3/h, {mm} kg, {e:.3e} kWh/kg)" for (n,e,p,qq,mm),(nn,p,q,mm2) in zip(mix_e,mix) for _ in [0] ) ,machine_used=mix_used[0],power_kW=mix_used[2],throughput=round(mix_used[3]),machine_mass=5720,machine_life=LIFE_H,
        values_as_found="Mixer 700: design capacity up to 150 m3/h, motor 22 kW, weight 5720 kg (Mixer 500: 11-15 kW, lower bound 11 used)",value_source="Magaldi paddle mixer page",value_link="https://www.magaldi.com/en/applications/paddle-mixer",conversions=f"kg/h = 150 m3/h x 150 kg/m3 (loose hemp hurd, rootlab.com.au/product/hemp-hurd-25l) = 22500; kWh/kg = 22/22500",per_kg=mix_used[1]),
      R("machine: inoculation and mixing","A1-A3",MACH,5720/(22500*LIFE_H),"P2",3,"M x t / L = 5720 x (1/22500) / 40000",weight=1.0,
        machine_type="continuous paddle mixer",machine_used="Magaldi Mixer 700",machine_mass=5720,machine_life=LIFE_H,throughput=22500,values_as_found="weight 5720 kg (net, standard)",value_source="Magaldi",value_link="https://www.magaldi.com/en/applications/paddle-mixer",conversions=LIFE_SRC,per_kg=5720/(22500*LIFE_H)),
      R("processing: heat deactivation and drying (electricity)","A1-A3",ELEC,dry_el,"P1 (dryer)",4,"STELA belt dryer WT-HS 830/100: 10 kW / 820 kg water per h (values from a search-result summary of the ligna 2019 brochure; PDF not readable here)",proxy="proxy: kg water evaporated used as kg processed; mass not found",weight=1.0,
        machine_type="belt dryer",machine_candidates="Sulzle Klein Conti-Dry (1000 kWh/t water heat, 120 kWh/t el.) | STELA WT-HS 830/100 (1.0 MW heat?, 820 kg/h, 10 kW el.) -> median heat | STELA QX 3870/100 (10 MW?, 3870 kg/h, 50 kW)",machine_used="STELA WT-HS 830/100",power_kW=10,throughput=820,machine_mass="not found",machine_life="n/a",values_as_found="heat input 1.0 (unit inferred MW), evaporation 820 kg/h, electrical 10 kW",value_source="STELA, ligna 2019 brochure (via search summary)",value_link="https://www.messe.de/apollo/ligna_2019/obs/Binary/A922945/922945_01820801.pdf",conversions="el kWh/kg = 10/820",per_kg=dry_el),
      R("processing: heat deactivation and drying (heat)","A1-A3",HEAT,dry_heat_kwh*3.6,"P1 (dryer)",4,"1.0 MW / 820 kg/h = 1.22 kWh/kg x 3.6 MJ/kWh",proxy="proxy: as above",weight=1.0,
        machine_type="belt dryer",machine_used="STELA WT-HS 830/100",power_kW=1000,throughput=820,machine_mass="not found",machine_life="n/a",values_as_found="thermal 1.0 MW (inferred)",value_source="STELA ligna 2019 brochure (via search summary)",value_link="https://www.messe.de/apollo/ligna_2019/obs/Binary/A922945/922945_01820801.pdf",conversions="1000 kW / 820 kg/h = 1.220 kWh/kg; x 3.6 = 4.39 MJ",per_kg=dry_heat_kwh)],
 A4=[R("A4 lorry","A4",LORRY,1.5,"A4 T3 EU 1,500 km"),R("A4 ship","A4",SEA,0.1,"A4 T3 EU 100 km")],
 loss=loss,A5_diesel=None,C1_diesel=None,c2_tkm=c2,A5_loss_lorry=True,eol=myc_items,c2_split=sh)
# ---------------------------------------------------------------- CONCRETE
sh=dict(landfill=.01,recycling=.99); c2=lorry_tkm(KM,sh); loss=.05/.95
rho_c=2414.28
cand=[("Sicoma MAO3000/2000",2*50*0.7457,107*0.764555*rho_c,7530.0),
      ("MEKA MB-T 2,0",74,2.0*40*rho_c,7200.0),
      ("Liebherr DW 4.5",150,4.5*40*rho_c,13200.0)]
cand_e=[(n,p/t,p,t,m) for n,p,t,m in cand]; cu=sorted(cand_e,key=lambda x:x[1])[1]
conc_base=[]
for n,m,dsl,dsr,cl,cr in [("aggregates",.769,INERT_LF,RC_REC,"W2","W2"),("cement",.145,INERT_LF,CEM_REC,"W2","W1"),("water",.087,INERT_LF,RC_REC,"W2","W2")]:
    conc_base.append((n,m,dsl,"landfill",cl,"W1 no landfill-route dataset for this constituent; W2 class Mineral","proxy",-.01))
    conc_base.append((n,m,dsr,"recycling",cr,("W1 yes: 'sorting plant' is a recycling-route word; waste cement in concrete and mortar matches cement" if cr=="W1" else "W1 no; W2 class Mineral recycling"),"" if cr=="W1" else "proxy",-.99))
conc_items=mk_items(conc_base)
M["concrete"]=dict(name="concrete",route="built",
 A13=[R("constituent: aggregates","A1-A3",("market for gravel, crushed","CH","gravel, crushed","kilogram"),.769,"D5 no (no product 'aggregates'), PROXY gravel, crushed; D2 market; D3 CH",4,"ecoinvent concrete uses gravel 1055 + sand 895 kg/m3; one constituent -> one row; first A-Z of the gravel/sand candidates",proxy="proxy",search="aggregate; gravel; sand",cands="market for gravel, crushed CH (chosen), RoW; market for gravel, round CH; market for sand CH"),
      R("constituent: cement","A1-A3",("market for cement, unspecified","Europe without Switzerland","cement, unspecified","kilogram"),.145,"D5 yes, D2 market, D3 Europe w/o CH",3,"variant 'unspecified' matches input 'cement' (no type given)",search="market for cement",cands="market for cement, unspecified Europe w/o CH (chosen); CEM II/A, CEM II/B etc."),
      R("constituent: water","A1-A3",("market group for tap water","RER","tap water","kilogram"),.087,"D5 yes, D2 market group, D3 RER",3,"mixing water as tap water",search="market for tap water",cands="market group for tap water RER (chosen); market for tap water Europe w/o CH"),
      R("processing: mixing (electricity)","A1-A3",ELEC,cu[1],"P1 (concrete mixer)",3,f"{cu[0]}: {cu[2]:.4g} kW / {cu[3]:.0f} kg/h",weight=1.0,
        machine_type="twin-shaft concrete mixer",machine_candidates="; ".join(f"{n}: {p:.1f} kW, {t:.0f} kg/h, {m:.0f} kg, {e:.3e} kWh/kg" for n,e,p,t,m in cand_e),machine_used=cu[0],power_kW=round(cu[2],2),throughput=round(cu[3]),machine_mass=cu[4],machine_life=LIFE_H,
        values_as_found="MAO3000/2000: 2 x 50 HP, 107 yd3/h, 90 s cycle, 16,600 lb empty mixer w/o skip. MEKA MB-T 2,0: 2x37 kW, 2.0 m3/batch, 7200 kg (no cycle time: 90 s borrowed from Sicoma). Liebherr DW 4.5: 2x75 kW, 4.5 m3, 13200 kg (no cycle time: 90 s borrowed)",value_source="Jamieson/Sicoma; MEKA; Liebherr",value_link="https://catalog.jamiesonequipment.com/item/all-products-sicoma-mixers/gories-twin-shaft-mixers-twin-shaft-concrete-mixer/mao3000-2000 | https://www.mekaglobal.com/en/products/concrete-batching-plants/concrete-mixers/twin-shaft-concrete-mixers | https://www.liebherr.com/en-az/p/85981-4898360",conversions="HP x 0.7457; yd3 x 0.764555; x 2414 kg/m3 (ecoinvent wet mass of concrete 30MPa AT); batch machines: 3600/90 s = 40 batches/h",per_kg=cu[1]),
      R("machine: mixing","A1-A3",MACH,cu[4]/(cu[3]*LIFE_H),"P2",3,f"{cu[4]:.0f} kg / ({cu[3]:.0f} kg/h x 40,000 h)",weight=1.0,
        machine_type="twin-shaft concrete mixer",machine_used=cu[0],machine_mass=cu[4],machine_life=LIFE_H,throughput=round(cu[3]),values_as_found="empty mixer weight 16,600 lb without skip = 7,530 kg",value_source="Jamieson/Sicoma MAO3000/2000",value_link="https://catalog.jamiesonequipment.com/item/all-products-sicoma-mixers/gories-twin-shaft-mixers-twin-shaft-concrete-mixer/mao3000-2000",conversions=LIFE_SRC,per_kg=cu[4]/(cu[3]*LIFE_H))],
 A4=[R("A4 lorry","A4",LORRY,0.05,"A4 T1 bulk 50 km")],
 loss=loss,A5_diesel=0.015,C1_diesel=0.036,c2_tkm=c2,A5_loss_lorry=True,eol=conc_items,c2_split=sh,
 approx=R("finished product (approximate)","A1-A3",("market for concrete, 30MPa","AT","concrete, 30MPa","cubic meter"),1/2414.28,"D1b yes, D2 market, D3 AT, D4 30MPa",2,"Differences: ground granulated blast furnace slag ~21-24 kg/m3 (~1 %), limestone filler ~5 kg/m3, admixture (organic chemical) ~1.5-1.8 kg/m3 not in input; aggregates 1950/2414 = 0.81 (input 0.769), cement 0.108-0.119 (input 0.145), water 0.072 (input 0.087)",search="concrete; market for concrete; concrete production",cands="market for concrete, 30MPa AT (chosen); market for concrete, normal strength AT; 25MPa AT; 30MPa CH/BR/RoW/ZA; 37MPa CH"))

# -------------------------------------------------------------- compute
def score(r):
    a,s=unit_impact(r["name"],r["loc"],r["prod"]); return r["amount"]*s
for k,m in M.items():
    rows=m["A13"]; tot=sum(score(r) for r in rows); wear=sum(score(r) for r in rows if r["purpose"].startswith("machine:"))
    m["gwp_a13"]=tot; m["wear"]=wear/tot if tot else 0
M["concrete"]["gwp_approx"]=score(M["concrete"]["approx"])
for k in M: print(k,"A1-A3 GWP-fossil per kg",M[k]["gwp_a13"],"wear share",M[k]["wear"])
print("concrete approx",M["concrete"]["gwp_approx"])
print("mix cand",cand_e,"used",cu[0]); print("myc mix",mix_e,mix_used[0]); print("past",past_kwh,"dry heat",dry_heat_kwh*3.6,"el",dry_el)
for r in M["mycelium"]["A13"]: print(r["purpose"],r["amount"],score(r))
for r in M["concrete"]["A13"]: print(r["purpose"],r["amount"],score(r))
