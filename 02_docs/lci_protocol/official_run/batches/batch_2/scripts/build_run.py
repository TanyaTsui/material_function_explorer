"""Assemble batch_2 outputs (CSVs + LCI sheets) and compute GWP-fossil A1-A3 with Brightway (read-only)."""
import sys, csv, math, os, json
sys.path.insert(0, os.path.dirname(__file__))
from bw_tools import *
import openpyxl

RUN = "batch_2"; DATE = "2026-11-19"; OUT = f"runs/{RUN}"
ECO = "ecoinvent-3.12-cutoff"; EV = "3.12 cut-off"

def s3(x):
    return 0.0 if x == 0 else float(f"{x:.3g}")

# ---- fixed datasets -------------------------------------------------------------------------------------
FIX = {
 "elec": ("market group for electricity, medium voltage", "electricity, medium voltage", "RER", "kilowatt hour", "42ec2f4634364ee86921b4c6dfe2de31"),
 "heat": ("market for heat, district or industrial, natural gas", "heat, district or industrial, natural gas", "Europe without Switzerland", "megajoule", "eda02fda34ab477c467e7913b32b7649"),
 "diesel": ("diesel, burned in building machine", "diesel, burned in building machine", "GLO", "megajoule", "296e6382d45f0d345f81d498f7866bee"),
 "lorry": ("market for transport, freight, lorry, unspecified", "transport, freight, lorry, diesel, unspecified", "RER", "ton kilometer", "dd736ab7d965646d04b091ae5fa68d97"),
 "sea": ("market for transport, freight, sea, container ship, heavy fuel oil", "transport, freight, sea, container ship, heavy fuel oil", "GLO", "ton kilometer", "1d2cb4018daf428aebf419380c6a2975"),
 "machine": ("market for industrial machine, heavy, unspecified", "industrial machine, heavy, unspecified", "RER", "kilogram", "5a0b37c3a698f020385f42dbdfbf1b1f"),
}
GER = {"RER": 1, "Europe without Switzerland": 1, "CH": 2, "GLO": 3, "RoW": 4}

D3 = "D3 order (RER market first)"
W = {  # waste datasets (name, product, loc, unit, code)
 "wood_lf": ("treatment of waste wood, untreated, sanitary landfill", "waste wood, untreated", "CH", "kilogram", "05340b91b158ef48ca6994ac19d71a42"),
 "wood_inc": ("treatment of waste wood, untreated, municipal incineration FAE", "waste wood, untreated", "CH", "kilogram", "90052db5ec4d19c2703b4600a95e85e8"),
 "wood_rec": ("treatment of waste wood, post-consumer, sorting and shredding", "wood chips, from post-consumer wood, dry, measured as dry mass", "CH", "kilogram", "cfd30a3023bf31babf15908c52f4ff5b"),
 "pvc_lf": ("treatment of waste polyvinylchloride, sanitary landfill", "waste polyvinylchloride", "CH", "kilogram", "eb7a3c029f6e7009c12f9ea4162686ce"),
 "pvc_inc": ("treatment of waste polyvinylchloride, municipal incineration FAE", "waste polyvinylchloride", "CH", "kilogram", "8e0508e39e4528b8283f4b2006ba0355"),
 "plas_lf": ("treatment of waste plastic, mixture, sanitary landfill", "waste plastic, mixture", "CH", "kilogram", "2d3eb9ef3fca8f2b629cee10b8e56af2"),
 "plas_inc": ("treatment of waste plastic, mixture, municipal incineration FAE", "waste plastic, mixture", "CH", "kilogram", "c96ef6f78d24a2cfc2f5b5b5b8138d8b"),
 "inert_lf": ("treatment of inert waste, inert material landfill", "inert waste, for final disposal", "CH", "kilogram", "b253f543e0a0147f9a5ad42af0a8b913"),
 "min_rec": ("treatment of waste reinforced concrete, recycling", "waste reinforced concrete", "Europe without Switzerland", "kilogram", "389a9235a15802ec5592835af4b92016"),
}

MATS = {}
decisions, dchoices, epd, cff, bioc, issues = [], [], [], [], [], []

def dec(m, qid, ans, val="", unit="", ev="", link="", step=""):
    decisions.append(dict(run_id=RUN, material_id=m, question_id=qid, answer=ans, value=val, unit=unit, evidence=ev, source_link=link, search_step=step, date=DATE))

DC_COLS = "run_id,material_id,module,row_purpose,search_terms,candidates_considered,chosen_activity,reference_product,location,unit,amount,database,rule_applied,proxy,TeR,GeR,TiR,machine_type,machine_candidates,machine_used,power_kW,throughput_kg_per_h,machine_mass_kg,machine_life_h,values_as_found,value_source,value_link,conversions,per_kg_processed,ecoinvent_version,search_date".split(",")

class Mat:
    def __init__(self, mid, name):
        self.mid, self.name = mid, name
        self.blocks = {k: [] for k in ["A1–A3", "A4", "A5", "C1", "C2", "C3–C4"]}
        self.gwp_rows = []  # (label, code, amount, is_machine)
    def add(self, module, purpose, ds, amount, rule, TeR, GeR=None, TiR=1, proxy="", comment="", search="", cands="", extra=None, gwp=None):
        name, prod, loc, unit, code = ds
        amount = s3(amount)
        GeR = GeR if GeR is not None else GER.get(loc, 2)
        row = dict(name=name, amount=amount, unit=unit, location=loc, product=prod, db=ECO, type="technosphere", module=module,
                   rule=rule, TeR=TeR, GeR=GeR, TiR=TiR, DQR=round((TeR + GeR + TiR) / 3, 2), comment=comment)
        self.blocks[module].append(row)
        d = {c: "" for c in DC_COLS}
        d.update(run_id=RUN, material_id=self.mid, module=module, row_purpose=purpose, search_terms=search, candidates_considered=cands,
                 chosen_activity=name, reference_product=prod, location=loc, unit=unit, amount=amount, database=ECO, rule_applied=rule,
                 proxy=proxy, TeR=TeR, GeR=GeR, TiR=TiR, ecoinvent_version=EV, search_date=DATE)
        if extra: d.update(extra)
        dchoices.append(d)
        if module == "A1–A3" and (gwp is None or gwp):
            self.gwp_rows.append((purpose, code, amount, purpose.startswith("machine")))
        return row

def lorry(m, module, purpose, tkm, rule, comment=""):
    return m.add(module, purpose, FIX["lorry"], tkm, rule, 3, comment=comment)

# =======================================================================================================
# 1. SAWN HARDWOOD (OAK)  -- exact match
# =======================================================================================================
m = Mat("sawn_hardwood_oak", "sawn hardwood (oak)"); MATS[m.mid] = m
ID = m.mid
OAKDS = ("market for sawnwood, hardwood, raw, dried (u=10%)", "sawnwood, hardwood, raw, dried (u=10%)", "RER", "cubic meter", "81a21abc6f4cd1fe6c7d62e873e9101e")
dec(ID, "D1", "yes", "market for sawnwood, hardwood, raw, dried (u=10%)", "", "Kiln-dried, rough-sawn (raw) hardwood sawnwood; wood is the only constituent. Differences logged: ecoinvent is generic hardwood, not oak, and dried to u=10 % (input: 12 %); treated as same delivered state (kiln dried, unplaned). Moisture/species gap noted in protocol_issues.md.", "", "search_ecoinvent.py 'sawnwood hardwood'; 'market sawnwood hardwood'; 'oak'")
dec(ID, "D2", "yes", "market exists", "", "market for sawnwood, hardwood, raw, dried (u=10%) exists (RER, Europe w/o CH is only for beam/board/lath sub-products).")
dec(ID, "D3", "RER", "RER", "", "No European market group; RER market exists (D3 item 2).")
dec(ID, "D4", "no variant", "", "", "Generic hardwood market preferred over beam/board/lath sub-variants (input names no product shape); others recorded: beam/board/lath raw dried u=10 % (Europe w/o CH).")
m.add("A1–A3", "finished product", OAKDS, 1 / 675.84, "D1/D2/D3", 1, TiR=1,
      comment="1 kg = 1/675.84 m3 (wet mass at u=10 % per ecoinvent property 'wet mass' 675.84 kg/m3)", search="sawnwood hardwood; market sawnwood hardwood; oak",
      cands="market for sawnwood, hardwood, raw, dried (u=10%) RER [chosen]; same for beam/board/lath (Europe w/o CH, CH, RoW); sawnwood production, hardwood, raw, dried (u=10%) Europe w/o CH",
      extra=dict(conversions="1 kg / 675.84 kg per m3 = 0.00148 m3"))
dec(ID, "CHECK 1", "yes", "0.953", "ratio to median", "Ours 0.1327 kg CO2e/kg vs EPD 0.1393 (99.84 kg CO2e/m3 ÷ 716.8 kg/m3); single EPD = median; see epd_check.csv", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=17bcb2ce-39fd-400b-baf9-370c63589efd")

# =======================================================================================================
# 2. COTTON CANVAS -- built from scratch
# =======================================================================================================
c = Mat("cotton_canvas", "cotton canvas"); MATS[c.mid] = c
ID = c.mid
dec(ID, "D1", "no", "", "", "ecoinvent 'textile, woven cotton' (market GLO; production RoW/IN/BD) is woven grey cloth made from bought-in cotton yarn; finishing is a separate service ('finishing, textile, woven cotton'). No finished woven cotton fabric dataset: delivered state differs.", "", "search_ecoinvent.py 'cotton fabric'; 'textile woven cotton'; 'fibre cotton'")
dec(ID, "D1b", "no", "market for textile, woven cotton (GLO) considered", "", "Test 1 fails: delivered state (finished, wet-finished and dried) differs from ecoinvent greige woven textile; the finished state exists only as a second dataset, not as a product. Main constituent (cotton) would match. Note: GWP of this stand-in would be 9.76 + 0.63 (finishing) kg CO2e/kg.")
dec(ID, "D5: cotton fibre", "yes", "market for fibre, cotton (GLO)", "", "Cotton fibre exists as market GLO; production datasets only BD, IN, RoW (no European). D3: no European/RER; no listed European country; GLO market (item 5) used. Organic variant not chosen (input says cotton fibre).", "", "search_ecoinvent.py 'fibre cotton'")
CF = ("market for fibre, cotton", "fibre, cotton", "GLO", "kilogram", "c490b9b959b9037990fb5fe28ad24f8e")
c.add("A1–A3", "constituent: cotton fibre", CF, 1.1, "D5/D2/D3", 3, search="fibre cotton",
      cands="market for fibre, cotton GLO [chosen]; market for fibre, cotton, organic GLO; fibre production, cotton, ginning BD/IN/RoW", comment="1.1 kg per kg product incl. 10 % loss (input)")
dec(ID, "CHECK (mass)", "yes", "1.1", "kg", "Material rows sum to 1.1 kg cotton fibre = input.")

# machine steps (P1/P2)
STEPS_COTTON = {}
def machine_rows(mm, step, kg_proc, kwh_per_kg=None, heat_mj_per_kg=None, mach=None, fallback=None, proxy="", ter=3):
    """kwh_per_kg electricity; heat_mj_per_kg heat already in MJ."""
    if kwh_per_kg is not None:
        base = dict(machine_type=(mach or {}).get("type", fallback["type"] if fallback else ""),
                    machine_candidates=(mach or {}).get("cands", fallback["cands"] if fallback else ""),
                    machine_used=(mach or {}).get("used", fallback["used"] if fallback else ""),
                    power_kW=(mach or {}).get("kw", ""), throughput_kg_per_h=(mach or {}).get("kgh", ""),
                    machine_mass_kg=(mach or {}).get("mass", ""), machine_life_h=(mach or {}).get("life", ""),
                    values_as_found=(mach or fallback)["found"], value_source=(mach or fallback)["src"], value_link=(mach or fallback)["link"],
                    conversions=(mach or fallback)["conv"], per_kg_processed=f"{kwh_per_kg:.4g} kWh/kg")
        mm.add("A1–A3", f"processing: {step} (electricity)", FIX["elec"], kg_proc * kwh_per_kg, "P1", ter, proxy=proxy, extra=base,
               comment=f"{kg_proc} kg processed × {kwh_per_kg:.4g} kWh/kg")
    if heat_mj_per_kg is not None:
        base = dict(machine_type=fallback["type"], machine_candidates=fallback["cands"], machine_used=fallback["used"],
                    values_as_found=fallback["found"], value_source=fallback["src"], value_link=fallback["link"],
                    conversions=fallback["conv"], per_kg_processed=f"{heat_mj_per_kg:.4g} MJ/kg")
        mm.add("A1–A3", f"processing: {step} (heat)", FIX["heat"], kg_proc * heat_mj_per_kg, "P1", ter, proxy=proxy, extra=base,
               comment=f"{kg_proc} kg processed × {heat_mj_per_kg:.4g} MJ/kg")
def wear_row(mm, step, kg_proc, M, tkgh, L, found, src, link, conv, proxy="", ter=3):
    per = M / (tkgh * L)
    mm.add("A1–A3", f"machine: {step}", FIX["machine"], kg_proc * per, "P2", ter, proxy=proxy, comment=f"{kg_proc} × {M}/({tkgh}×{L})",
           extra=dict(machine_type="", machine_used="", power_kW="", throughput_kg_per_h=tkgh, machine_mass_kg=M, machine_life_h=L,
                      values_as_found=found, value_source=src, value_link=link, conversions=conv, per_kg_processed=f"{per:.4g} kg machine/kg"))
    return per

# --- opening and carding: Rieter C 81
card = dict(type="card (carding machine)", used="Rieter C 81 (CH)", kw=33.5, kgh=300, mass=9200, life=100000,
  cands="(1) Rieter C 81 CH: 33.5 kW, up to 300 kg/h, 9,200 kg [complete]; (2) Truetzschler TC 19i DE: max 260 kg/h, ~6,700 kg net, power only from a third-party listing (2.5 kW installed, implausible) [incomplete, not used]; (3) Marzoli C701 IT: up to 270 kg/h, no power or weight found [incomplete, not used]. Only 1 of 3 complete: median rule could not be applied.",
  found="33.5 kW installed power (without coiler); production up to 300 kg/h; machine weight 9,200 kg with standard chute",
  src="Rieter product page, Card C 81", link="https://www.rieter.com/products/systems/fiber-preparation/card-c-81", conv="0.1117 kWh/kg = 33.5 kW ÷ 300 kg/h (rated power at max throughput)")
dec(ID, "P1: opening and carding", "machine", "Rieter C 81", "", "Usual machine for carding: a revolving-flat card. Only 1 of 3 candidates had power + throughput + mass; used it and flagged.", card["link"])
machine_rows(c, "opening and carding", 1.1, kwh_per_kg=33.5 / 300, mach=card)
dec(ID, "P2: opening and carding", "machine", "9200 kg; 300 kg/h; 100,000 h", "", "Life: no source found; assumption 20 years × 5,000 h/yr = 100,000 h.", card["link"])
wear_row(c, "opening and carding", 1.1, 9200, 300, 100000, "M 9,200 kg; throughput 300 kg/h; life not in source (assumed 20 y × 5,000 h)", card["src"], card["link"], "9,200 ÷ (300 × 100,000) = 3.07e-4 kg/kg")
# spinning: fallback study
spin = dict(type="ring spinning frame (no machine datasheet with power: fallback study)", used="study value: ring spinning, 100 % carded cotton, Ne 16",
  cands="Rieter G 38 (CH): 1,824 spindles, up to 28,000 rpm, but no kW/kg per h/weight in the sources found; Marzoli, Zinser/Saurer not found. No candidate complete → EDIPTEX study (next source per P1).",
  found="Table 9.1: ring spinning, 100 % carded cotton or synthetic, Ne 16: total 2.10 kWh/kg yarn (7.6 MJ/kg)",
  src="EDIPTEX Working Report 24 (Danish EPA, 2007), Annex, Table 9.1", link="https://www2.mst.dk/udgiv/publications/2007/978-87-7052-515-2/html/kap16_eng.htm",
  conv="2.10 kWh/kg used directly; the table's total includes preparation (possible overlap with carding step: not removed, not verifiable)")
dec(ID, "P1: spinning", "proxy (study)", "2.10 kWh/kg", "kWh/kg", "No machine datasheet gave power + throughput + weight; used peer-reviewed/agency study value per P1 fallback. Ne 16 chosen for coarse canvas yarn (assumption).", spin["link"])
machine_rows(c, "spinning", 1.05, kwh_per_kg=2.10, fallback=spin, proxy="proxy", ter=4)
dec(ID, "P2: spinning", "not computed", "", "", "No machine mass/life from a datasheet; no wear row (study value used, not a machine). Estimated effect < 1 %.")
# weaving
weav = dict(type="air-jet loom (fallback: published specific energy)", used="published value, air-jet weaving",
  cands="Picanol OmniPlus-i, Lindauer Dornier A1, Itema A9500: no kW / kg per h / weight found on product pages. No candidate complete → published specific energy.",
  found="air-jet loom power consumption 3.2 kWh/kg (fabric); no method stated (low confidence)",
  src="Fibre2Fashion, 'Energy optimisation in textile mills'", link="https://www.alchempro.com/industry-article/7956/energy-optimisation-in-textile-mills", conv="3.2 kWh/kg used directly")
dec(ID, "P1: weaving", "proxy (published value)", "3.2 kWh/kg", "kWh/kg", "No loom datasheet gave all three values; used industry article value (unverified). Flagged proxy, TeR 4.", weav["link"])
machine_rows(c, "weaving", 1.0, kwh_per_kg=3.2, fallback=weav, proxy="proxy", ter=4)
dec(ID, "P2: weaving", "not computed", "", "", "No loom mass found; no wear row.")
# finishing
fin = dict(type="stenter frame (drying part of wet finishing); thermal", used="study value: cotton stenter SEC",
  cands="Monforts Montex stenter: only relative savings found, no kW or kg/h. No candidate complete → study.",
  found="Specific energy of cotton stenter drying 4,889 / 3,586 / 4,304 kJ per kg water evaporated (three dryers); median 4,304. Water to evaporate 0.6 kg/kg fabric = assumption (after mangle ~70 % pick-up to ~10 % residual); wet processing (scouring, bleaching, washing) heat and electricity not found → not included",
  src="Drying Technology 2021 stenter energy model (DOI 10.1080/07373937.2021.1907401)", link="https://informahealthcare.com/doi/full/10.1080/07373937.2021.1907401",
  conv="4,304 kJ/kg water × 0.6 kg water/kg = 2.58 MJ/kg (heat dataset is in MJ; no ×3.6)")
dec(ID, "P1: wet finishing and drying", "proxy (study)", "2.58 MJ/kg heat", "MJ/kg", "Only the drying heat could be sourced; the wet-processing part is missing (lower impact branch, 'unclear').", fin["link"])
machine_rows(c, "wet finishing and drying", 1.0, heat_mj_per_kg=2.58, fallback=fin, proxy="proxy", ter=4)
dec(ID, "P2: wet finishing and drying", "not computed", "", "", "No stenter mass found; no wear row.")

# =======================================================================================================
# 3. CERAMIC TILE -- approximate match (D1b)
# =======================================================================================================
t = Mat("ceramic_tile", "ceramic tile"); MATS[t.mid] = t
ID = t.mid
dec(ID, "D1", "no", "ceramic tile production (CH, RoW)", "", "ecoinvent tile: clay 0.489, feldspar 0.386, silica sand 0.17, limestone 0.077, stucco 0.062, TiO2 0.018, zinc, lead, tin, barite, sodium perborate, Al-oxide (oxidic ceramic, one producer). Input: clays 0.556, feldspar 0.265, kaolin 0.074, limestone, sand, glaze. Extra constituents (stucco, TiO2, metals) and no kaolin → not exact.", "", "search_ecoinvent.py 'ceramic tile'")
dec(ID, "D1b", "yes", "ceramic tile production, CH (market for ceramic tile GLO also exists)", "", "Same product (ceramic tile), main constituent clay in both (0.556 vs 0.489). Differences: dataset has feldspar 0.386 (input 0.265), stucco 0.062, TiO2 0.018, lead/zinc/tin/barite/Na-perborate/Al-oxide ≈ 0.011 total; lacks kaolin 0.074 and a separate glaze; sand 0.17 (input 0.032). Dataset is v2-era, one producer.", "")
dec(ID, "D2", "unclear", "market GLO vs production CH", "", "A 'market for ceramic tile' exists but only for GLO; D3 puts a single European country (CH production) before GLO, yet D2 says market first. Unclear → lower-impact branch: production CH + A2 lorry row (0.41 vs 0.80 kg CO2e/kg).", "")
dec(ID, "D3", "CH", "CH", "", "Production datasets exist for CH and RoW; CH is a European country (D3 item 4).", "")
dec(ID, "D4", "no variant", "", "", "Single ceramic tile product at the chosen location.", "")
TILE = ("ceramic tile production", "ceramic tile", "CH", "kilogram", "40d4921150cedc6781cf92286a2586f1")
t.add("A1–A3", "finished product (approximate)", TILE, 1.0, "D1b/D2/D3", 2, GeR=2, search="ceramic tile",
      cands="ceramic tile production CH [chosen]; ceramic tile production RoW; market for ceramic tile GLO (0.796 kg CO2e/kg); frit production for ceramic tile (not a tile)",
      comment="approximate match; differs from input: +feldspar, +stucco, +TiO2, +Pb/Zn/Sn/barite, −kaolin, −separate glaze",
      extra=dict(machine_type="", values_as_found="differences from input (kg/kg): feldspar +0.121; sand +0.138; limestone +0.045; stucco +0.062; TiO2 +0.018; Pb 0.0067; Zn 0.0034; Na-perborate 0.0061; barite 0.0006; kaolin −0.074; clay −0.067"))
# A2 transport row added after T2 decision, below.

# =======================================================================================================
# 4. PVC-U -- built from scratch
# =======================================================================================================
p = Mat("pvc_u", "PVC-U"); MATS[p.mid] = p
ID = p.mid
dec(ID, "D1", "no", "", "", "ecoinvent has no PVC window profile dataset: 'plastic profiles' (RER) is recycled mixed polyolefin; 'window frame, poly vinyl chloride' is a whole frame per m2 (94.5 kg, with steel/aluminium reinforcement and fittings).", "", "search_ecoinvent.py 'plastic profile'; 'window frame'; 'polyvinylchloride'; 'rigid polyvinylchloride'")
dec(ID, "D1b", "no", "", "", "Test 1 fails: 'window frame' is a different product (frame with reinforcement per m2); 'plastic profiles' fails test 2 (main constituent recycled polyolefin, not PVC).")
def d5(name, ans, ds_name, ev):
    dec(ID, f"D5: {name}", ans, ds_name, "", ev, "", "search_ecoinvent.py")
d5("PVC resin", "yes", "market for polyvinyl chloride, suspension polymerised (RER)", "Rigid window profiles use S-PVC; RER market exists (D3 item 2).")
d5("chalk filler", "yes", "market for limestone, milled, loose (RER)", "Chalk = ground limestone (workbook lists 'chalk (limestone)'); loose variant alphabetically first and matches dry powder; RER market.")
d5("impact modifier (acrylate)", "no", "proxy: market for polymethyl methacrylate (RER)", "No acrylate impact modifier dataset; PMMA is the closest acrylic polymer of the same class. TeR 4.")
d5("Ca-Zn stabiliser", "no", "proxy: market for chemical, organic, unspecified (GLO)", "No metal-soap stabiliser dataset (no Ca/Zn stearate found); organic chemical (calcium/zinc soaps) is the closest class. GLO is the only location. TeR 4.")
d5("TiO2 pigment", "yes", "market for titanium dioxide (RER)", "RER market exists.")
RES = ("market for polyvinyl chloride, suspension polymerised", "polyvinyl chloride, suspension polymerised", "RER", "kilogram", "d6418d3ed7ed3b7e7f5f809823204e52")
CHK = ("market for limestone, milled, loose", "limestone, milled, loose", "RER", "kilogram", "3a710cca1d991102f239e2e6fab2cfa0")
IMP = ("market for polymethyl methacrylate", "polymethyl methacrylate", "RER", "kilogram", "4d1f98622fb5e0fd052e1d9029e37017")
STA = ("market for chemical, organic, unspecified", "chemical, organic, unspecified", "GLO", "kilogram", "8d2ebc01bb260a7e6e86df9b51de8280")
TIO = ("market for titanium dioxide", "titanium dioxide", "RER", "kilogram", "ba91adc96f7bfb8d699e74a9bb0ea472")
p.add("A1–A3", "constituent: PVC resin", RES, 0.81, "D5/D2/D3", 3, search="polyvinylchloride; polyvinyl chloride suspension", cands="market for polyvinyl chloride, suspension polymerised RER [chosen]; emulsion polymerised; production datasets RER/CN/RNA/RAF…")
p.add("A1–A3", "constituent: chalk filler", CHK, 0.081, "D5/D2/D3/D4", 3, search="limestone milled; calcium carbonate", cands="market for limestone, milled, loose RER [chosen]; limestone, milled, packed (Europe w/o CH); calcium carbonate, precipitated RER")
p.add("A1–A3", "constituent: impact modifier (acrylate)", IMP, 0.049, "PROXY", 4, proxy="proxy", search="acrylic; methyl methacrylate", cands="market for polymethyl methacrylate RER [chosen]; methyl methacrylate RER; acrylic dispersion; acrylic binder", comment="proxy: closest acrylic polymer")
p.add("A1–A3", "constituent: Ca-Zn stabiliser", STA, 0.028, "PROXY", 4, proxy="proxy", search="stabiliser; zinc stearate; calcium stearate; chemical organic", cands="market for chemical, organic, unspecified GLO [chosen]; zinc oxide GLO; chemical, inorganic GLO", comment="proxy: organic chemical (metal soaps)")
p.add("A1–A3", "constituent: TiO2 pigment", TIO, 0.032, "D5/D2/D3", 3, search="titanium dioxide", cands="market for titanium dioxide RER [chosen]; RoW")
dec(ID, "CHECK (mass)", "yes", "1.000", "kg", "0.81+0.081+0.049+0.028+0.032 = 1.000 = input.")
# dry blending: Jwell mixer median
blend = dict(type="hot/cold PVC mixer (dry blending)", used="Jwell PVC hot/cold mixer series (range as found)",
  cands="(1) ARGUS MASZYNY S-1000 (PL): 650–850 kg/h, motors 47/67/15 kW (roles not labelled; 47+15 taken) = 0.083 kWh/kg; (2) Jwell PVC mixer (CN): 30–160 kW, 330–1,650 kg/h = 0.091–0.097 kWh/kg (mid 0.094); (3) ERK PVC Makine 500 kg turbo mixer (TR): heater up to 250 kW + cooler 37 kW, 500 kg × 3–4 batch/h = 0.164 kWh/kg. Median = Jwell. No candidate lists machine weight → not used for wear.",
  found="Jwell: motor power ~30 to 160 kW, output ~330 to 1,650 kg/h across 150–2,100 L models (summary of vendor table; the table could not be re-opened, 403)",
  src="Jwell Group, PVC mixer; ARGUS MASZYNY S-series; ERK PVC Makine listings",
  link="https://www.jwell-group.com/Plastic-recycling-machine/jwell-pvc-mixer ; https://www.plastech.pl/en/b2b-marketplace/hot-cold-mixer-108515 ; https://www.makinaturkiye.com/en/500-kg-yatay-turbo-pvc-hammadde-mikseri-karistirici-v-19757",
  conv="0.094 kWh/kg = mean of 30 kW÷330 kg/h (0.091) and 160 kW÷1,650 kg/h (0.097)")
dec(ID, "P1: dry blending", "machine", "Jwell PVC hot/cold mixer (median of 3)", "0.094 kWh/kg", "Median of three candidates by energy per kg; datasheets lack weights and exact motor roles, flagged.", blend["link"])
machine_rows(p, "dry blending", 1.0, kwh_per_kg=0.094, mach=blend)
dec(ID, "P2: dry blending", "not computed", "", "", "None of the three mixer sources gives machine weight; no wear row.")
# extrusion
ext = dict(type="conical twin-screw extruder, PVC profile line", used="Jwell SJZ65/132 window-profile line (CN)",
  cands="(1) Jwell SJZ65/132: 37 kW, 180–250 kg/h (215), 4,000 kg = 0.172 kWh/kg [complete]; (2) Reifenhaeuser 63 mm twin-screw (DE, used-machine listing): 43 kW, ~200 kg/h, 3,000 kg = 0.215 kWh/kg [complete]; (3) Bausano E-ON 63 (IT): 51 kW installed, 50–220 kg/h (135) = 0.378 kWh/kg, no weight [incomplete]; KraussMaffei KMD 73: 57 kW drive, 330 kg/h, no weight. Only two complete: the lower-energy one is used (unclear → lower impact).",
  kw=37, kgh=215, mass=4000, life=100000,
  found="extruder motor 37 kW; output 180–250 kg/h; weight 4,000 kg (Jwell SJZ65/132). Motor rating only, ancillaries (haul-off, cooling, vacuum) not included",
  src="Jwell Group PVC window profile extrusion line (via search summary; page returned 403 on re-fetch); Exapro Reifenhaeuser listing; Bausano E-ON",
  link="https://www.jwell-group.com/Profile-extrusion-machine/jwell-pvc-windows-high-speed-profile-extrusion-line ; https://www.exapro.com/reifenhauser-bt-1000-2-63k-p260214127 ; https://www.bausano.com/en/extruders-range/twin-screw-extruders/e-on-conical-twin-screw-extruder",
  conv="0.172 kWh/kg = 37 kW ÷ 215 kg/h (midpoint of 180–250)")
dec(ID, "P1: profile extrusion", "machine", "Jwell SJZ65/132", "0.172 kWh/kg", "Only two of three candidates complete; lower-energy one taken (unclear → lower impact). Motor power understates line power: flagged.", ext["link"])
machine_rows(p, "profile extrusion", 1.0, kwh_per_kg=37 / 215, mach=ext)
dec(ID, "P2: profile extrusion", "machine", "4000 kg; 215 kg/h; 100,000 h", "", "Life: no source; assumption 20 y × 5,000 h/yr.", ext["link"])
wear_row(p, "profile extrusion", 1.0, 4000, 215, 100000, "M 4,000 kg; throughput 215 kg/h; life assumed 20 y × 5,000 h", "Jwell SJZ65/132", ext["link"].split(" ; ")[0], "4,000 ÷ (215 × 100,000) = 1.86e-4 kg/kg")
dec(ID, "P1: cutting", "unclear", "no rows", "", "No profile saw datasheet (power, throughput in kg/h, mass) could be found in this session. Lower-impact branch: no rows. Cutting a profile is small compared with extrusion.")
dec(ID, "P2: cutting", "no row", "", "", "No energy rows → no machine row.")

# =======================================================================================================
# A4 / A5 / C1 / C2 / C3-C4 for each material
# =======================================================================================================
EOL = {  # shares landfill, incineration, recycling, reuse ; category
 "sawn_hardwood_oak": ("34 wood, untreated: beams, planks", 0.05, 0.80, 0.10, 0.05),
 "cotton_canvas": ("52 organic / bio-based, other", 0.05, 0.95, 0.0, 0.0),
 "ceramic_tile": ("25 fine ceramics", 0.15, 0.0, 0.80, 0.05),
 "pvc_u": ("63 PVC window profiles", 0.10, 0.10, 0.80, 0.0),
}
KM = {"lf": 50, "inc": 100, "rec": 50, "reuse": 50}
A4 = {}   # mid -> (lorry tkm, sea tkm)
LOSS = {"sawn_hardwood_oak": 0.03, "cotton_canvas": 0.03, "ceramic_tile": 0.05, "pvc_u": 0.03}
X1 = {"ceramic_tile": True}

NMDL = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
for mid, ans in [("sawn_hardwood_oak", None), ("cotton_canvas", None), ("ceramic_tile", None), ("pvc_u", None)]:
    dec(mid, "A4 · T1", "no", "", "", "Delivered as pieces (boards / rolls / tiles / profile bars), not loose or ready-mixed.", NMDL)
dec("sawn_hardwood_oak", "A4 · T2", "yes", "DE, FR, NL", "", "Oak sawmills: DE Friedrich Schnatmeier GmbH (6,000–8,000 m3 oak/yr); FR Ducerf / Ageorges (oak sawmills); NL Rollé Group (kilns in NL). 3 of 5.", "https://ttjonline.com/analysis/beyond-the-boule ; https://rolle.drupal03.fruitcake.dev/ageorges-france", "web search 'oak sawn timber sawmill manufacturer ...'")
dec("cotton_canvas", "A4 · T2", "no", "NL (TenCate), ES (blend only)", "", "Only NL (TenCate heavy cotton tent canvas, self-produced) and a Spanish canvas (50 % cotton blend) found; no DE, FR or IT cotton canvas weaver found. Fewer than 3 countries found (one web query only; 'unclear' resolved to no). Taking T3 (EU) adds 1.5 tkm lorry + 0.1 tkm sea.", "https://esvocampingshop.com/en/tent-canvas-cotton-ten-cate-340-gr-m-grey-69495", "web search 'cotton canvas fabric weaver manufacturer ...'")
dec("cotton_canvas", "A4 · T3", "yes", "NL: TenCate", "", "TenCate (NL) makes heavy cotton tent canvas in Europe.", "https://esvocampingshop.com/en/tent-canvas-cotton-ten-cate-340-gr-m-grey-69495")
dec("ceramic_tile", "A4 · T2", "yes", "DE, IT, ES", "", "DE Villeroy & Boch (Mettlach), IT Marazzi (Sassuolo/Fiorano), ES Porcelanosa. 3 of 5.", "https://www.archiexpo.com/soc/marazzi-9022.html ; https://eqs-news.com/company/villeroy-boch-ag/info/5b75bfd1-ea7c-11e8-902f-2c44fd856d8c ; https://www.architectatwork.com/es/curated/brands/porcelanosa-group-85230", "web search ceramic tile manufacturers")
dec("pvc_u", "A4 · T2", "yes", "DE, FR, IT", "", "profine Group (Kömmerling/KBE/Trocal): DE Pirmasens and Berlin; FR Marmoutier; IT Bosaro; VEKA AG Sendenhorst DE. 3 of 5.", "https://www.koemmerling.com/en/contact/production-sites/ ; https://www.profine-group.com/en/company/", "web search PVC-U window profile manufacturer plants")
A4["sawn_hardwood_oak"] = (0.15, 0); A4["cotton_canvas"] = (1.5, 0.1); A4["ceramic_tile"] = (0.15, 0); A4["pvc_u"] = (0.15, 0)

# A2 row for tile (production dataset, no market used)
t.add("A1–A3", "A2 transport", FIX["lorry"], 0.15, "D2 (A2 row)", 3, comment="production dataset: A2 lorry with A4 national distance 150 km")

# --- I1 / L1 / X1 decisions
PW = {
 "sawn_hardwood_oak": ("no", "Typical oak board 25–50 mm × 150 mm × 3 m ≈ 8–25 kg at 717 kg/m3 (EPD density); not poured; individual pieces < 50 kg (beams up to ~57 kg exist, boards are the typical piece).", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=17bcb2ce-39fd-400b-baf9-370c63589efd"),
 "cotton_canvas": ("no", "Roll of 340 g/m2 canvas, 1.75 m × 30 m ≈ 18 kg (< 50 kg).", "https://esvocampingshop.com/en/tent-canvas-cotton-ten-cate-340-gr-m-grey-69495"),
 "ceramic_tile": ("no", "18.65 kg/m2 (EPD); a 60×60 cm tile = 6.7 kg; not poured.", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=a2b5b7c9-db13-4dbd-be23-b0ff9f0cbd98"),
 "pvc_u": ("no", "Window profile bar 6 m × ~1–2 kg/m ≈ 6–12 kg; complete 1.23 × 1.48 m window < 50 kg; not poured.", "https://fintecnic.eu/app/uploads/2023/11/2022-05-epd-kunststofffenster-mit-2-scheiben-isolierglas-englisch-plastic-window-with-double-insulating-gass-unit1.pdf"),
}
L1 = {
 "sawn_hardwood_oak": ("no", "Prefab timber placed dry/fixed mechanically: 3 % (NMD)."),
 "cotton_canvas": ("no", "Fabric rolls fixed in place: prefab, 3 % (NMD)."),
 "ceramic_tile": ("yes", "Tiles set in adhesive/mortar on site (protocol example): 5 % (NMD)."),
 "pvc_u": ("no", "Prefab profiles/windows: 3 % (NMD)."),
}
X1D = {
 "sawn_hardwood_oak": ("no", "Fixed mechanically, pieces < 50 kg."),
 "cotton_canvas": ("no", "Fixed mechanically/by hand; roll < 50 kg."),
 "ceramic_tile": ("yes", "Tiles are bonded with adhesive/mortar → demolished by machine (protocol X1 'bonded')."),
 "pvc_u": ("no", "Mechanically fixed; pieces < 50 kg."),
}
for mid in MATS:
    a, ev, lk = PW[mid]; dec(mid, "A5 · I1", a, "", "", ev, lk)
    a, ev = L1[mid]; dec(mid, "A5 · L1", a, f"{LOSS[mid]*100:.0f} %", "waste rate", ev, NMDL)
    a, ev = X1D[mid]; dec(mid, "C1 · X1", a, "", "", ev, NMDL)
    cat = EOL[mid]; dec(mid, "C2 · ROUTE", cat[0].split(" ")[0], f"landfill {cat[1]*100:.0f} / incineration {cat[2]*100:.0f} / recycling {cat[3]*100:.0f} / reuse {cat[4]*100:.0f} %", "% of mass", f"NMD category {cat[0]} (workbook sheet nmd_eol)", "https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/")

def weighted_km(mid):
    _, lf, inc, rec, reuse = EOL[mid]
    return lf * 50 + inc * 100 + rec * 50 + reuse * 50

# waste item definitions: (constituent, mass per kg product, {route: dataset key or None (no row)})
def waste_items(mid):
    _, lf, inc, rec, reuse = EOL[mid]
    items = []
    if mid == "sawn_hardwood_oak":
        items = [("oak timber (wood)", 1.0, dict(lf="wood_lf", inc="wood_inc", rec="wood_rec"), "W1")]
    elif mid == "cotton_canvas":
        items = [("cotton fibre", 1.0, dict(lf="wood_lf", inc="wood_inc", rec="wood_rec"), "W2")]
    elif mid == "ceramic_tile":
        items = [("ceramic tile (product itself)", 1.0, dict(lf="inert_lf", rec="min_rec"), "W2")]
    elif mid == "pvc_u":
        items = [("PVC resin", 0.81, dict(lf="pvc_lf", inc="pvc_inc", rec=None), "W1"),
                 ("chalk filler", 0.081, dict(lf="inert_lf", inc=None, rec="min_rec"), "W2"),
                 ("impact modifier (acrylate)", 0.049, dict(lf="plas_lf", inc="plas_inc", rec=None), "W2"),
                 ("Ca-Zn stabiliser", 0.028, dict(lf="plas_lf", inc="plas_inc", rec=None), "W2"),
                 ("TiO2 pigment", 0.032, dict(lf="inert_lf", inc=None, rec="min_rec"), "W2")]
    return items

ROUTES = [("lf", "landfill", 1), ("inc", "incineration", 2), ("rec", "recycling", 3), ("reuse", "reuse", 4)]
def eol_rows(mid, mm, module, scale, purpose_prefix, log=False):
    """Write waste rows; amount negative; scale = kg of product going to EOL"""
    sh = dict(lf=EOL[mid][1], inc=EOL[mid][2], rec=EOL[mid][3], reuse=EOL[mid][4])
    for cname, cmass, rmap, rule in waste_items(mid):
        for rk, rname, _ in ROUTES:
            share = sh[rk]
            if share == 0: continue
            mass = cmass * share * scale
            tag = f"{cname} × {rname}"
            if rk == "reuse":
                if log: dec(mid, f"W1: {tag}", "no row", "", "", "Reuse: no row (cut-off), benefit in D.");
                continue
            key = rmap.get(rk, None)
            if key is None:
                if log:
                    if rk == "rec": dec(mid, f"W1: {tag}", "no row", "", "", "Recycling of plastics: no row (cut-off).")
                    else: dec(mid, f"W2: {tag}", "no row", "—", "", "Class has no dataset for this route (workbook '—'): no row.")
                continue
            ds = W[key]
            sign = 1 if key == "wood_rec" else -1
            comment = f"{rule}; waste item {tag}" + ("; reference product is wood chips (+1), amount positive: burden of sorting/shredding, see protocol_issues" if key == "wood_rec" else "")
            proxy = "proxy" if rule == "W2" else ""
            ter = 4 if rule == "W2" else 3
            if module == "C3–C4":
                purpose = f"C3-C4: {tag}"
            else:
                purpose = f"A5 end of life: {tag}"
            # not part of A1-A3 gwp; use add but module key
            row = mm.add(module, purpose, ds, sign * mass, rule, ter, proxy=proxy, comment=comment, gwp=False)
            if log:
                dec(mid, f"W1: {tag}" if rule == "W1" else f"W2: {tag}", "yes" if rule == "W1" else "no → fallback", ds[0] + " " + ds[2], "", f"{rule}: " + ("treatment dataset exists for this waste material and route (D3: CH before GLO)." if rule == "W1" else "no dataset for this waste material (e.g. no waste cotton / ceramic tile); class fallback from sheet waste_fallback, proxy TeR 4."), "", "search_ecoinvent.py 'treatment of waste ...'")

for mid, mm in MATS.items():
    lo, se = A4[mid]
    dec(mid, "A4 BLOCK", "archetype", f"lorry {lo*1000:.0f} km, sea {se*1000:.0f} km", "", {0.15: "National 150 km", 1.5: "EU manufactured: lorry 1,500 + container ship 100 km"}[lo], NMDL)
    mm.blocks["A4"].append(dict(name=f"{mm.name}, A1–A3", amount=1, unit="kilogram", location="RER", product=f"{mm.name}, at factory gate", db="raw_baselines", type="technosphere", module="A4", rule="–", TeR="", GeR="", TiR="", DQR="", comment="previous block"))
    mm.add("A4", "A4 lorry", FIX["lorry"], lo, "A4 archetype", 3)
    if se: mm.add("A4", "A4 ship", FIX["sea"], se, "A4 archetype", 3)
    w = LOSS[mid]; loss = w / (1 - w)
    mm.blocks["A5"].append(dict(name=f"{mm.name}, A4", amount=s3(1 + loss), unit="kilogram", location="RER", product=f"{mm.name}, delivered to site", db="raw_baselines", type="technosphere", module="A5", rule="–", TeR="", GeR="", TiR="", DQR="", comment=f"previous block (1 + loss), loss = {w}/(1-{w}) = {loss:.4f}"))
    mm.add("A5", "A5 lorry (loss)", FIX["lorry"], loss * weighted_km(mid) / 1000, "A5 loss", 3, comment=f"lost {loss:.4f} kg × weighted EOL distance {weighted_km(mid):.1f} km")
    eol_rows(mid, mm, "A5", loss, "A5")
    mm.blocks["C1"].append(dict(name=f"{mm.name}, A5", amount=1, unit="kilogram", location="RER", product=f"{mm.name}, installed", db="raw_baselines", type="technosphere", module="C1", rule="–", TeR="", GeR="", TiR="", DQR="", comment="previous block"))
    if X1.get(mid): mm.add("C1", "C1 diesel", FIX["diesel"], 0.036, "C1", 3)
    mm.blocks["C2"].append(dict(name=f"{mm.name}, C1", amount=1, unit="kilogram", location="RER", product=f"{mm.name}, demolished", db="raw_baselines", type="technosphere", module="C2", rule="–", TeR="", GeR="", TiR="", DQR="", comment="previous block"))
    mm.add("C2", "C2 lorry", FIX["lorry"], weighted_km(mid) / 1000, "C2", 3, comment=f"weighted distance {weighted_km(mid):.1f} km")
    mm.blocks["C3–C4"].append(dict(name=f"{mm.name}, C2", amount=1, unit="kilogram", location="RER", product=f"{mm.name}, at waste site", db="raw_baselines", type="technosphere", module="C3–C4", rule="–", TeR="", GeR="", TiR="", DQR="", comment="previous block"))
    eol_rows(mid, mm, "C3–C4", 1.0, "C3-C4", log=True)

# =======================================================================================================
# GWP-fossil A1-A3
# =======================================================================================================
RES_G = {}
for mid, mm in MATS.items():
    tot, parts = gwp([(a, b, c_) for a, b, c_, _ in mm.gwp_rows])
    wear = sum(v for k, v in parts.items() if k.startswith("machine"))
    RES_G[mid] = (tot, wear / tot if tot else 0, parts)
    print(mid, round(tot, 4), "wear share", f"{(wear/tot if tot else 0):.2e}", {k: round(v, 4) for k, v in parts.items()})
# tile alternatives for the record
tile_market = gwp([("m", "48f48d85e954106325c695640e0295be", 1)])[0]
print("tile market", tile_market)
json.dump({k: [v[0], v[1], v[2]] for k, v in RES_G.items()}, open("scripts/gwp_results.json", "w"), indent=1)

# =======================================================================================================
# EPD checks
# =======================================================================================================
def epd_row(mid, cid, cat, ids, n, med, ours, res, route, flags=None, reason="", lci_kept="", rel="not stated on dataset page (latest online 19 Nov 2026)"):
    flags = flags or {}
    ratio = ours / med if med else ""
    epd.append(dict(run_id=RUN, material_id=mid, check_id=cid, okobaudat_release=rel, category=cat, epd_ids=ids, n_epds=n,
                    epd_median=s3(med) if med else "no check possible", our_gwp_fossil_a1a3=s3(ours), ratio_to_median=s3(ratio) if med else "",
                    result=res, flag_units_mass=flags.get("u", ""), flag_dataset_state=flags.get("s", ""), flag_indicator=flags.get("i", ""),
                    flag_machine_rows=flags.get("m", ""), likely_reason=reason, wear_share_of_gwp_fossil_a1a3=f"{RES_G[mid][1]:.2e}",
                    route=route, distance_to_median=s3(abs(ratio - 1)) if med else "", lci_kept=lci_kept))
oak_med = 99.84 / 716.8
epd_row("sawn_hardwood_oak", "CHECK 1", "Wood: sawn timber, oak", "17bcb2ce-39fd-400b-baf9-370c63589efd (Schnittholz Eiche 12 %, Sphera)", 1, oak_med, RES_G["sawn_hardwood_oak"][0],
        "pass" if 0.5 <= RES_G["sawn_hardwood_oak"][0] / oak_med <= 1.5 else "fail", "exact",
        flags=dict(u="99.84 kg CO2e/m3 ÷ 716.8 kg/m3 (12 % moisture) = per kg at 12 %; ours per kg of wet mass at u=10 %", s="ecoinvent u=10 % vs EPD 12 %; generic hardwood vs oak", i="'Climate change-Fossil' A1-A3 on EPD side; EF 3.1 climate change: fossil on ours", m="none (exact match)"),
        reason="Only one EPD found in the time available; ecoinvent dataset is hardwood average", lci_kept="exact")
t_med = 12.94 / 18.65
epd_row("ceramic_tile", "CHECK 2", "Ceramic tiles", "a2b5b7c9-db13-4dbd-be23-b0ff9f0cbd98 (Keramische Fliesen und Platten, BKF; v00.08.000)", 1, t_med, RES_G["ceramic_tile"][0],
        "pass" if 0.5 <= RES_G["ceramic_tile"][0] / t_med <= 1.5 else "fail", "approximate",
        flags=dict(u="12.94 kg CO2e per m2 ÷ 18.65 kg/m2 (dataset page; workbook overview says 17.97 kg/m2)", s="ecoinvent tile is v2-era oxidic ceramic, one producer; ours is CH production + A2 150 km", i="EPD page shows total GWP A1-A3 only (fossil not separate); biogenic share negligible for tile", m="none (approximate match)"),
        reason="Single EPD (BKF average); market GLO alternative would give 0.796 (ratio 1.15, also pass)", lci_kept="approximate")
epd_row("cotton_canvas", "CHECK 3", "Textiles: woven cotton fabric", "none found", 0, None, RES_G["cotton_canvas"][0], "no check possible", "built",
        flags=dict(m="carding: machine datasheet; spinning, weaving, finishing: published specific-energy values (proxy)"), reason="No ÖKOBAUDAT dataset for cotton canvas (workbook: 'no ÖKOBAUDAT dataset found')", lci_kept="built")
pv_med = (3.65 + 4.71) / 2
epd_row("pvc_u", "CHECK 3", "PVC-U window profiles", "EGE PROFIL EPD-EPT-20150011-CAA1-EN (3.65 kg CO2e/kg, EN 15804+A1); Saray PVC profile (4.71 kg CO2e/kg, EN 15804+A1). Both via One Click LCA, not ÖKOBAUDAT", 2, pv_med, RES_G["pvc_u"][0],
        "pass" if 0.5 <= RES_G["pvc_u"][0] / pv_med <= 1.5 else "fail", "built",
        flags=dict(u="per kg of profile as declared", s="EPDs are EN 15804+A1, total GWP A1-A3 (not A2 fossil)", i="A1 EPDs report total GWP, mixed with biogenic (negligible for PVC)", m="cutting step has no rows; dry blending without wear; extrusion with motor power only"),
        reason="ÖKOBAUDAT PVC window-profile dataset could not be reached; median from two other single-company EPDs; the fintecnic window EPD in the input is per window, not per kg of profile", rel="not ÖKOBAUDAT (One Click LCA entries)", lci_kept="built")

# =======================================================================================================
# CFF / BIOC
# =======================================================================================================
CFF = {"sawn_hardwood_oak": "Solid wood", "cotton_canvas": "Other plant-based", "ceramic_tile": "Mineral, crushed to aggregate", "pvc_u": "PVC"}
for mid, a in CFF.items():
    cat, lf, inc, rec, reuse = EOL[mid]
    cff.append(dict(run_id=RUN, material_id=mid, cff_archetype=a, recycling_share=rec, reuse_share=reuse, incineration_share=inc, landfill_share=lf, flag="", note=f"NMD category {cat}"))
def bio(mid, cons, kg, arch, moist="", flag="", note=""):
    bioc.append(dict(run_id=RUN, material_id=mid, constituent=cons, kg_per_kg_product=kg, carbon_archetype=arch, moisture_content=moist, flag=flag, note=note))
bio("sawn_hardwood_oak", "oak timber, incl. 12 % moisture", 1, "Wood", 0.12, note="input gives u = 12 %")
bio("cotton_canvas", "cotton fibre", 1.0, "Cellulose fibres and stalks", "", note="1.1 kg in input incl. 10 % loss; losses excluded: 1 kg ends up in the product")
for cn, kg in [("clays", 0.556), ("feldspar", 0.265), ("kaolin", 0.074), ("limestone", 0.032), ("sand", 0.032), ("glaze", 0.042)]: bio("ceramic_tile", cn, kg, "Non-biogenic")
for cn, kg in [("PVC resin", 0.81), ("chalk filler", 0.081), ("impact modifier (acrylate)", 0.049), ("Ca-Zn stabiliser", 0.028), ("TiO2 pigment", 0.032)]: bio("pvc_u", cn, kg, "Non-biogenic")
for mid in MATS:
    cat = EOL[mid]
    dec(mid, "D · CFF · F1", CFF[mid], "", "", f"Key: material listed in column materials of sheet cff_archetypes ({CFF[mid]}).")
for r in bioc:
    dec(r["material_id"], f"D · BIO-C · B1: {r['constituent']}", r["carbon_archetype"], "", "", "Constituent listed in sheet carbon_archetypes.")

# =======================================================================================================
# write CSVs
# =======================================================================================================
def wcsv(fn, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(f"{OUT}/{fn}", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in cols})
def tcols(fn): return open(f"templates/{fn}").readline().strip().split(",")
wcsv("decisions.csv", decisions, tcols("decisions.csv"))
wcsv("dataset_choices.csv", dchoices, DC_COLS)
wcsv("epd_check.csv", epd, tcols("epd_check.csv"))
wcsv("cff_inputs.csv", cff, tcols("cff_inputs.csv"))
wcsv("bioc_inputs.csv", bioc, tcols("bioc_inputs.csv"))

# =======================================================================================================
# LCI sheets
# =======================================================================================================
HDR = ["name", "amount", "unit", "location", "reference product", "database", "type", "module", "rule", "TeR", "GeR", "TiR", "DQR", "comment"]
SUFFIX = {"A1–A3": "at factory gate", "A4": "delivered to site", "A5": "installed", "C1": "demolished", "C2": "at waste site", "C3–C4": "cradle to grave"}
for mid, mm in MATS.items():
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "LCI"
    ws.append(["Database", "raw_baselines"])
    for mod in ["A1–A3", "A4", "A5", "C1", "C2", "C3–C4"]:
        nm = f"{mid}, {mod}"; prod = f"{mid}, {SUFFIX[mod]}"
        ws.append(["Activity", nm]); ws.append(["reference product", prod]); ws.append(["unit", "kilogram"]); ws.append(["location", "RER"])
        ws.append(["module", mod]); ws.append(["comment", f"batch_2 run, {DATE}"]); ws.append(["Exchanges"]); ws.append(HDR)
        ws.append([nm, 1, "kilogram", "RER", prod, "raw_baselines", "production", mod, "–"])
        prev = {"A4": "A1–A3", "A5": "A4", "C1": "A5", "C2": "C1", "C3–C4": "C2"}
        for r in mm.blocks[mod]:
            r = dict(r)
            if r["db"] == "raw_baselines":  # previous-block row: rename id
                r["name"] = f"{mid}, {prev[mod]}"; r["product"] = f"{mid}, {SUFFIX[prev[mod]]}"
            ws.append([r["name"], r["amount"], r["unit"], r["location"], r["product"], r["db"], r["type"], r["module"], r["rule"], r["TeR"], r["GeR"], r["TiR"], r["DQR"], r["comment"]])
        ws.append([])
    # DQR (mass-weighted over A1-A3 rows) in a note
    rows = [r for r in mm.blocks["A1–A3"]]
    if rows:
        wsum = sum(r["amount"] for r in rows if r["unit"] == "kilogram") or 1
        ws.append(["DQR note", "A1–A3 DQR simple mean of rows: " + str(round(sum(r["DQR"] for r in rows) / len(rows), 2))])
    wb.save(f"{OUT}/LCI_{mid}.xlsx")
print("done")
