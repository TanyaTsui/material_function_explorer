"""Builds batch_3 records from the decisions made while running protocol.md. Read-only on Brightway and the workbook."""
import sys, csv, statistics, math, os
sys.path.insert(0, os.path.dirname(__file__))
import calc, bwh
from calc import get, per, gwp
import openpyxl
from openpyxl.styles import Font

RUN = "batch_3"
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATE = "2026-11-19"
ECO = "ecoinvent-3.12-cutoff"
V = "3.12 cut-off"
OKB = "OBD_2024_III (latest datastock in the ÖKOBAUDAT API at run time); EN 15804+A2 datasets only"

decisions, choices, checks, cff, bioc = [], [], [], [], []

def dec(mid, q, ans, value="", unit="", ev="", link="", step=""):
    decisions.append(dict(run_id=RUN, material_id=mid, question_id=q, answer=ans, value=value, unit=unit,
                          evidence=ev, source_link=link, search_step=step, date=DATE))

CH_COLS = "run_id,material_id,module,row_purpose,search_terms,candidates_considered,chosen_activity,reference_product,location,unit,amount,database,rule_applied,proxy,TeR,GeR,TiR,machine_type,machine_candidates,machine_used,power_kW,throughput_kg_per_h,machine_mass_kg,machine_life_h,values_as_found,value_source,value_link,conversions,per_kg_processed,ecoinvent_version,search_date".split(",")

def ch(mid, module, purpose, act=None, loc=None, amount=None, rule="", proxy="", TeR="", GeR="", TiR="", search="", cands="", unit=None, prod=None, **kw):
    row = {c: "" for c in CH_COLS}
    row.update(run_id=RUN, material_id=mid, module=module, row_purpose=purpose, search_terms=search, candidates_considered=cands,
               chosen_activity=act or "", reference_product=prod or "", location=loc or "", unit=unit or "", amount=amount if amount is not None else "",
               database=ECO if act else "", rule_applied=rule, proxy=proxy, TeR=TeR, GeR=GeR, TiR=TiR, ecoinvent_version=V, search_date=DATE)
    row.update(kw)
    choices.append(row)
    return row

def GeR(loc):
    if loc in ("RER", "Europe without Switzerland"): return 1
    if loc in ("DE", "FR", "IT", "ES", "NL", "AT", "SE", "FI", "PL", "CH"): return 2
    if loc == "GLO": return 3
    if loc == "RoW": return 4
    return 5

def sig(x, n=3):
    if x == 0 or x == "" : return x
    return float(f"{x:.{n}g}")

# ---------------------------------------------------------------- fixed datasets
ELEC = get("market group for electricity, medium voltage", "RER")
HEAT = get("market for heat, district or industrial, natural gas", "Europe without Switzerland")
MACH = get("market for industrial machine, heavy, unspecified", "RER")
LORRY = get("market for transport, freight, lorry, unspecified", "RER")
SEA = get("market for transport, freight, sea, container ship, heavy fuel oil", "GLO")
DIESEL = get("diesel, burned in building machine", "GLO")
L_H = 25 * 5000  # machine life in hours: ecoinvent machine dataset declares 25 years, protocol default 5,000 h per year
ROUTE_KM = dict(landfill=50, incineration=100, recycling=50, reuse=50)
FIX = dict(electricity="market group for electricity, medium voltage", heat="market for heat, district or industrial, natural gas")

# nmd_eol (sheet nmd_eol), shares as fractions
EOL = {
    "34": dict(name="34 wood, untreated: beams, planks", landfill=.05, incineration=.80, recycling=.10, reuse=.05),
    "55": dict(name="55 board material, clean", landfill=.05, incineration=.85, recycling=.10, reuse=0.0),
    "52": dict(name="52 organic / bio-based, other", landfill=.05, incineration=.95, recycling=0.0, reuse=0.0),
}

# ------------------------------------------------------------------ waste datasets (W1/W2)
WOOD = dict(
    landfill=("treatment of waste wood, untreated, sanitary landfill", "CH", "waste wood, untreated"),
    incineration=("treatment of waste wood, untreated, municipal incineration FAE", "CH", "waste wood, untreated"),
    recycling=("treatment of waste wood, post-consumer, sorting and shredding", "CH", None))
PLASTIC = dict(
    landfill=("treatment of waste plastic, mixture, sanitary landfill", "CH", None),
    incineration=("treatment of waste plastic, mixture, municipal incineration FAE", "CH", None),
    recycling=None)  # no row (cut-off)
PP = dict(
    landfill=("treatment of waste polypropylene, sanitary landfill", "CH", None),
    incineration=("treatment of waste polypropylene, municipal incineration FAE", "CH", None),
    recycling=None)
MINERAL = dict(landfill=("treatment of inert waste, inert material landfill", "CH", None), incineration=None, recycling=("treatment of waste reinforced concrete, recycling", None, None))

def find_waste(name, loc):
    r = bwh.find(name, loc)
    if not r: return None
    pref = [a for a in r if a['reference product'].startswith(("waste", "inert waste"))]
    if pref: return pref[0]
    if len(r) > 1: print("WARNING several products for", name, loc, [a['reference product'] for a in r])
    return r[0]

# ---------------------------------------------------------------- generic module builder
def build_chain(mid, label, a1a3_rows, T_rows, loss, eol_key, waste_items, notes):
    """returns dict of blocks: each block = list of exchange dicts (beyond production + previous rows)"""
    blocks = {}
    blocks["A1–A3"] = a1a3_rows
    blocks["A4"] = T_rows
    shares = EOL[eol_key]
    kmw = sum(shares[r] * ROUTE_KM[r] for r in ROUTE_KM) / 1000.0  # tkm per kg
    # A5
    a5 = [dict(name=LORRY['name'], amount=loss * kmw, unit="ton kilometer", loc="RER", prod=LORRY['reference product'], db=ECO, type="technosphere",
               rule="NMD lorry", comment=f"A5 lorry (loss): {loss:.4f} kg lost × Σ(route share × km)/1000 = {kmw:.4f} tkm per kg", TeR=3, GeR=1, TiR=1)]
    c34 = []
    for (cname, mass, cls, act_table, w1rule) in waste_items:
        for route in ("landfill", "incineration", "recycling", "reuse"):
            s = shares[route]
            if s == 0: continue
            amt = -(loss * mass * s)
            tab = act_table.get(route) if route != "reuse" else None
            if route == "reuse" or tab is None:
                continue_note = "reuse: no row (cut-off)" if route == "reuse" else "no row (cut-off / no dataset for this class and route)"
                a5.append(dict(name=f"(no row) {cname} × {route}", amount=0, unit="kilogram", loc="", prod="", db="", type="note", rule="W2" if w1rule == "W2" else w1rule, comment=continue_note, TeR="", GeR="", TiR=""))
                continue
            n, l, _ = tab
            a = find_waste(n, l)
            if a is None:
                a5.append(dict(name=f"(no row) {cname} × {route}", amount=0, unit="kilogram", loc="", prod="", db="", type="note", rule=w1rule, comment=f"dataset {n} not found in ecoinvent 3.12", TeR="", GeR="", TiR=""))
                continue
            a5.append(dict(name=a['name'], amount=amt, unit=a['unit'], loc=a['location'], prod=a['reference product'], db=ECO, type="technosphere", rule=w1rule, comment=f"A5 end of life: {cname} × {route}", TeR=1 if w1rule == "W1" else 4, GeR=GeR(a['location']), TiR=1))
    blocks["A5"] = a5
    blocks["C1"] = []
    c2 = [dict(name=LORRY['name'], amount=kmw, unit="ton kilometer", loc="RER", prod=LORRY['reference product'], db=ECO, type="technosphere", rule="C2 · NMD", comment=f"C2 lorry: Σ(route share × km)/1000 for {shares['name']}", TeR=3, GeR=1, TiR=1)]
    blocks["C2"] = c2
    c34 = []
    for (cname, mass, cls, act_table, w1rule) in waste_items:
        for route in ("landfill", "incineration", "recycling", "reuse"):
            s = shares[route]
            if s == 0: continue
            amt = -(mass * s)
            tab = act_table.get(route) if route != "reuse" else None
            if route == "reuse" or tab is None:
                c34.append(dict(name=f"(no row) {cname} × {route}", amount=0, unit="kilogram", loc="", prod="", db="", type="note", rule=w1rule, comment="reuse: no row (cut-off)" if route == "reuse" else "no row: cut-off (metals/plastics recycling) or class has no dataset for this route", TeR="", GeR="", TiR=""))
                continue
            n, l, _ = tab
            a = find_waste(n, l)
            if a is None:
                c34.append(dict(name=f"(no row) {cname} × {route}", amount=0, unit="kilogram", loc="", prod="", db="", type="note", rule=w1rule, comment=f"dataset {n} not found", TeR="", GeR="", TiR=""))
                continue
            c34.append(dict(name=a['name'], amount=amt, unit=a['unit'], loc=a['location'], prod=a['reference product'], db=ECO, type="technosphere", rule=w1rule, comment=f"C3-C4: {cname} × {route}; mass {mass:g} kg × share {s:g}", TeR=1 if w1rule == "W1" else 4, GeR=GeR(a['location']), TiR=1))
    blocks["C3–C4"] = c34
    return blocks

def log_waste(mid, items, eol_key, loss):
    shares = EOL[eol_key]
    for (cname, mass, cls, tab, w1rule) in items:
        for route in ("landfill", "incineration", "recycling", "reuse"):
            s = shares[route]
            if s == 0: continue
            q = f"W1: {cname} × {route}"
            if route == "reuse":
                dec(mid, q, "no row", "", "", "Reuse: no row; under the cut-off rule the material leaves without burden, benefit goes to D.", "", "")
                ch(mid, "C3–C4", f"C3-C4: {cname} × {route}", rule="W1 (no search)", search="none (reuse)", amount=0)
                continue
            t = tab.get(route)
            if t is None:
                dec(mid, q, "no" if w1rule == "W2" else "yes", "no row", "", f"{cls}; route {route}: fallback sheet gives no row (cut-off for plastics recycling, or class has no dataset for this route).", "", "waste_fallback")
                ch(mid, "C3–C4", f"C3-C4: {cname} × {route}", rule=w1rule, proxy="yes" if w1rule == "W2" else "", search="see W1 scan", amount=0, TeR=4 if w1rule == "W2" else "", cands="no row written")
                continue
            n, l, _ = t
            a = find_waste(n, l)
            amt_c = -(mass * s)
            amt_a5 = -(loss * mass * s)
            if w1rule == "W1":
                dec(mid, q, "yes", n, "", f"Treatment dataset named for this waste material and route exists in ecoinvent 3.12; location by D3 ({l}).", "", "treatment of waste polypropylene")
            else:
                dec(mid, q, "no", n, "", f"No treatment dataset named for '{cname}' and route '{route}' (waste material does not match any 3.12 waste-treatment name); fallback class '{cls}' from sheet waste_fallback used (W2, proxy, TeR 4).", "", "scan of 'treatment of waste …' names, bw2data read-only")
            for purpose, amt in ((f"C3-C4: {cname} × {route}", amt_c), (f"A5 end of life: {cname} × {route}", amt_a5)):
                ch(mid, purpose[:2] if purpose.startswith("A5") else "C3–C4", purpose, act=a['name'], loc=a['location'], amount=sig(amt, 4), rule=w1rule, proxy="yes" if w1rule == "W2" else "", TeR=1 if w1rule == "W1" else 4,
                   GeR=GeR(a['location']), TiR=1, search="name-prefix scan 'treatment of waste' + search_ecoinvent 'shredding', 'post-consumer', 'sorting', 'reinforced concrete'",
                   cands="; ".join(f"{k}: {v[0]} [{v[1]}]" for k, v in tab.items() if v), unit=a['unit'], prod=a['reference product'])

# ---------------------------------------------------------------- write sheet
HDR = ["name", "amount", "unit", "location", "reference product", "database", "type", "module", "rule", "TeR", "GeR", "TiR", "DQR", "comment"]

def write_lci(mid, label, blocks, a1a3_loc="RER", transp_comment=None, loss=0.0):
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "LCI"
    ws.append(["Database", "raw_baselines"]); ws.append([])
    mods = ["A1–A3", "A4", "A5", "C1", "C2", "C3–C4"]
    prods = {"A1–A3": f"{label}, at factory gate", "A4": f"{label}, delivered to site", "A5": f"{label}, installed", "C1": f"{label}, demolished", "C2": f"{label}, at waste site", "C3–C4": f"{label}, cradle to grave"}
    prev = None
    for i, m in enumerate(mods):
        ws.append(["Activity", f"{label}, {m}"]); ws.append(["reference product", prods[m]]); ws.append(["unit", "kilogram"]); ws.append(["location", "RER"]); ws.append(["module", m])
        ws.append(["comment", blocks.get("_comment_" + m, "")]); ws.append(["Exchanges"]); ws.append(HDR)
        ws.append([f"{label}, {m}", 1, "kilogram", "RER", prods[m], "raw_baselines", "production", m, "–"])
        if prev:
            amt = 1 + loss if m == "A5" else 1
            ws.append([f"{label}, {prev[0]}", amt, "kilogram", "RER", prev[1], "raw_baselines", "technosphere", m, "–", "", "", "", "", "previous block" + (" (A5 takes 1 + loss)" if m == "A5" else "")])
        rows = blocks[m]
        # DQR mass-weighted: simple mean over material rows (see comment)
        for r in rows:
            if r['type'] == "note":
                ws.append([r['name'], 0, r['unit'], "", "", "", "note", m, r['rule'], "", "", "", "", r['comment']]); continue
            ter, ger, tir = r.get('TeR', ""), r.get('GeR', ""), r.get('TiR', "")
            dqr = round((ter + ger + tir) / 3, 2) if all(isinstance(x, (int, float)) for x in (ter, ger, tir)) else ""
            ws.append([r['name'], sig(r['amount'], 4), r['unit'], r['loc'], r['prod'], r['db'], r['type'], m, r['rule'], ter, ger, tir, dqr, r['comment']])
        ws.append([])
        prev = (f"{m}", prods[m]); prev = (m if False else f"{m}", prods[m])
        prev = (m, prods[m])
    for c in ws[1]: c.font = Font(bold=True)
    ws2 = wb.create_sheet("README")
    ws2.append(["Brightway Excel format, one block per module, chained (each block's first input is the previous block's output). Generated by run batch_3 from protocol.md."])
    ws2.append(["Rows with type 'note' have amount 0: they record a waste item for which the protocol writes no row. Waste sent to treatment has a negative amount."])
    ws2.append(["Module B and D have no rows. DQR = (TeR+GeR+TiR)/3 per row; TiR = 1 assumed for all ecoinvent 3.12 datasets (time period is not exposed in the Brightway project)."])
    wb.save(os.path.join(OUT, f"LCI_{mid}.xlsx"))

def rowd(act, amt, rule, TeR, comment, unit=None, proxy=False, GeRv=None):
    return dict(name=act['name'], amount=amt, unit=unit or act['unit'], loc=act['location'], prod=act['reference product'], db=ECO, type="technosphere",
                rule=rule, comment=comment + (" [proxy]" if proxy else ""), TeR=TeR, GeR=GeRv or GeR(act['location']), TiR=1)

def transport_rows(kind):
    if kind == "national": return [rowd(LORRY, 0.15, "T2 yes", 3, "A4 lorry 150 km: 1 kg × 0.001 × 150", GeRv=1)]
    if kind == "eu": return [rowd(LORRY, 1.5, "T3 yes", 3, "A4 lorry 1,500 km", GeRv=1), rowd(SEA, 0.1, "T3 yes", 3, "A4 ship 100 km", GeRv=3)]
    if kind == "global": return [rowd(LORRY, 0.5, "T3 no", 3, "A4 lorry 500 km", GeRv=1), rowd(SEA, 10.0, "T3 no", 3, "A4 ship 10,000 km", GeRv=3)]

def log_transport(mid, kind):
    if kind == "national": ch(mid, "A4", "A4 lorry", act=LORRY['name'], loc="RER", amount=0.15, rule="T2", TeR=3, GeR=1, TiR=1, unit="ton kilometer", prod=LORRY['reference product'], search="fixed (workbook fixed_settings)", conversions="1 kg × 0.001 × 150 km")
    if kind == "eu":
        ch(mid, "A4", "A4 lorry", act=LORRY['name'], loc="RER", amount=1.5, rule="T3", TeR=3, GeR=1, TiR=1, unit="ton kilometer", prod=LORRY['reference product'], search="fixed", conversions="1 kg × 0.001 × 1,500 km")
        ch(mid, "A4", "A4 ship", act=SEA['name'], loc="GLO", amount=0.1, rule="T3", TeR=3, GeR=3, TiR=1, unit="ton kilometer", prod=SEA['reference product'], search="fixed", conversions="1 kg × 0.001 × 100 km")
    if kind == "global":
        ch(mid, "A4", "A4 lorry", act=LORRY['name'], loc="RER", amount=0.5, rule="T3", TeR=3, GeR=1, TiR=1, unit="ton kilometer", prod=LORRY['reference product'], search="fixed", conversions="1 kg × 0.001 × 500 km")
        ch(mid, "A4", "A4 ship", act=SEA['name'], loc="GLO", amount=10.0, rule="T3", TeR=3, GeR=3, TiR=1, unit="ton kilometer", prod=SEA['reference product'], search="fixed", conversions="1 kg × 0.001 × 10,000 km")

def log_A4_A5_C(mid, label, t1_ev, t2, t3, kind, piece_ev, piece_kg, piece_link, loss_ev, eol_key, x1_ev, loss=0.03 / 0.97):
    L = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
    dec(mid, "A4 · T1", "no", "", "", t1_ev, L, "")
    dec(mid, "A4 · T2", t2[0], "", "", t2[1], t2[2], t2[3])
    if t3: dec(mid, "A4 · T3", t3[0], "", "", t3[1], t3[2], t3[3])
    log_transport(mid, kind)
    dec(mid, "A5 · I1", "no", piece_kg, "kg per piece", piece_ev, piece_link, "")
    dec(mid, "A5 · L1", "no", "3", "% waste (NMD prefab)", loss_ev, L, "")
    dec(mid, "A5 · LOSS", "0.03", f"{loss:.6f}", "kg lost per kg installed", "loss = w/(1-w) = 0.03/0.97", L, "")
    dec(mid, "C1 · X1", "no", "", "", x1_ev, piece_link, "")
    e = EOL[eol_key]
    dec(mid, "C2 · ROUTE", eol_key, e['name'], "", f"Material found in column materials of sheet nmd_eol: shares landfill {e['landfill']*100:g} / incineration {e['incineration']*100:g} / recycling {e['recycling']*100:g} / reuse {e['reuse']*100:g} %.", "https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/", "nmd_eol")
    kmw = sum(e[r] * ROUTE_KM[r] for r in ROUTE_KM) / 1000.0
    ch(mid, "A5", "A5 lorry (loss)", act=LORRY['name'], loc="RER", amount=sig(loss * kmw, 4), rule="NMD", TeR=3, GeR=1, TiR=1, unit="ton kilometer", prod=LORRY['reference product'], search="fixed", conversions=f"{loss:.5f} kg × Σ(share × km)/1000 = {loss:.5f} × {kmw:.4f}")
    ch(mid, "C2", "C2 lorry", act=LORRY['name'], loc="RER", amount=sig(kmw, 4), rule="C2 · NMD", TeR=3, GeR=1, TiR=1, unit="ton kilometer", prod=LORRY['reference product'], search="fixed", conversions="Σ(route share × km one way)/1000; sheet nmd_eol: recycling 50, reuse 50, landfill 50, incineration 100 km")
    return kmw

def cff_bioc(mid, label, cff_arch, eol_key, cons, flag_cff="", note_cff=""):
    e = EOL[eol_key]
    cff.append(dict(run_id=RUN, material_id=mid, cff_archetype=cff_arch, recycling_share=e['recycling'], reuse_share=e['reuse'], incineration_share=e['incineration'], landfill_share=e['landfill'], flag=flag_cff, note=note_cff))
    dec(mid, "D · CFF · F1", cff_arch, "", "", f"Material listed in column materials of sheet cff_archetypes row '{cff_arch}'.", "", "cff_archetypes")
    for (name, kg, arch, moist, flag, note) in cons:
        bioc.append(dict(run_id=RUN, material_id=mid, constituent=name, kg_per_kg_product=kg, carbon_archetype=arch, moisture_content=moist, flag=flag, note=note))
        dec(mid, f"D · BIO-C · B1: {name}", arch, "", "", "Constituent name found in column constituents of sheet carbon_archetypes." if not flag else note, "", "carbon_archetypes")

# =============================================================== MATERIAL 1: engineered_bamboo
def bamboo():
    mid = "engineered_bamboo"; label = "engineered bamboo"
    dec(mid, "D1", "no", "", "", "No laminated bamboo board (or any bamboo board with MUF glue) in ecoinvent 3.12. Only bamboo culm, pole, flattened bamboo, woven bamboo mat (semi-products).", "", "search_ecoinvent: 'bamboo', 'laminated', 'board', 'melamine', 'urea formaldehyde'")
    dec(mid, "D1b", "no", "", "", "Test 1 fails: no ecoinvent dataset with the same name and delivered state (laminated bamboo board, sanded). Closest are semi-products (bamboo pole, flattened bamboo, woven bamboo mat), not the finished board.", "", "same searches")
    bamboo_pole = get("market for bamboo pole", "RoW"); muf = get("market for melamine urea formaldehyde adhesive", "GLO")
    dec(mid, "D5: bamboo strips, incl. moisture", "yes", bamboo_pole['name'], "", "Strips are made inside the factory by the steps 'splitting and planing'; the state entering the factory is the dried bamboo pole (u=20 %). Candidates: bamboo culm, bamboo pole, flattened bamboo. D2 market first; D3: no European/GLO dataset exists, RoW is the first available (BR, CN, CO, EC, PH are 'any other').", "", "search_ecoinvent 'bamboo'")
    dec(mid, "D5: adhesive, MUF", "yes", muf['name'], "", "Melamine urea formaldehyde adhesive exists; only a GLO market exists (D3 GLO, the first available).", "", "search_ecoinvent 'melamine', 'urea formaldehyde', 'adhesive'")
    ch(mid, "A1–A3", "constituent: bamboo strips, incl. moisture", act=bamboo_pole['name'], loc="RoW", amount=0.978, rule="D2 market, D3 RoW", TeR=1, GeR=4, TiR=1, unit="kilogram", prod=bamboo_pole['reference product'],
       search="bamboo", cands="market for bamboo culm [BR,CN,CO,EC,PH,RoW]; market for bamboo pole [same]; market for flattened bamboo [same]; market for woven bamboo mat [BR,CN,CO,PH,RoW]")
    ch(mid, "A1–A3", "constituent: adhesive, MUF", act=muf['name'], loc="GLO", amount=0.022, rule="D2 market, D3 GLO", TeR=1, GeR=3, TiR=1, unit="kilogram", prod=muf['reference product'],
       search="melamine; urea formaldehyde; adhesive", cands="market for melamine urea formaldehyde adhesive [GLO]; market for urea formaldehyde resin [RER, RoW] (resin, not adhesive)")
    rows = [rowd(bamboo_pole, 0.978, "D2", 1, "constituent: bamboo strips, incl. moisture"), rowd(muf, 0.022, "D2", 1, "constituent: adhesive, MUF")]
    dem = [(bamboo_pole, 0.978), (muf, 0.022)]
    # P1/P2 --------------------------------------------------------
    steps = ["splitting and planing strips", "boiling or steaming strips", "drying strips", "hot pressing", "sanding"]
    # step 1 splitting and planing
    e1 = 5.593 / 812.5   # kWh/kg
    wear1 = 530.0 / (812.5 * L_H)
    dec(mid, "P1: splitting and planing strips", "machine", f"{e1:.5f}", "kWh/kg", "No datasheet gives power, throughput and mass together for a bamboo splitter. Used: chain bamboo splitting machine, 7.5 HP = 5.59 kW and net 530 kg (ARSI Traders listing) with throughput 6-7 t per 8 h (N.K. & Son's listing for the same machine type, mid 6.5 t/8 h = 812.5 kg/h): mixed suppliers, so proxy TeR 4. Planing machine (Garnet four-side planer 6 kW, 350 kg) has no throughput: no row (lower-impact branch).", "https://m.indiamart.com/impcat/bamboo-splitting-machine.html", "")
    ch(mid, "A1–A3", "processing: splitting and planing strips (electricity)", act=ELEC['name'], loc="RER", amount=sig(1 * e1, 4), rule="P1 fixed", proxy="yes", TeR=4, GeR=1, TiR=1, unit="kilowatt hour", prod=ELEC['reference product'],
       search="web: bamboo splitting machine datasheet; bamboo strip planing", machine_type="bamboo chain splitting machine (planing: no usable data)",
       machine_candidates="(a) Garnet hydraulic splitter 3.75 kW, 500 kg, no throughput; (b) DN-103 timber dividing machine 3.0 kW, 260 kg, no throughput; (c) ARSI chain splitter 7.5 HP, 530 kg net, no throughput on listing; throughput from N.K. & Son's chain splitter listing. Only (c)+throughput gives all three values (mixed suppliers).",
       machine_used="ARSI Traders bamboo splitting machine (7.5 HP, net 530 kg) + throughput of N.K. & Son's bamboo chain splitter", power_kW=5.593, throughput_kg_per_h=812.5, machine_mass_kg=530, machine_life_h=L_H,
       values_as_found="7.5 HP; net weight 530 kg (6' model); 6-7 ton per day (8 hours)", value_source="IndiaMART listings (ARSI Traders; N.K. & Son's)", value_link="https://m.indiamart.com/impcat/bamboo-splitting-machine.html",
       conversions="7.5 HP × 0.7457 = 5.593 kW; 6.5 t / 8 h = 812.5 kg/h", per_kg_processed=sig(e1, 4))
    rows.append(rowd(ELEC, 1 * e1, "P1", 4, "processing: splitting and planing strips (electricity)", proxy=True)); dem.append((ELEC, e1))
    ch(mid, "A1–A3", "machine: splitting and planing strips", act=MACH['name'], loc="RER", amount=sig(wear1, 4), rule="P2 fixed", proxy="yes", TeR=4, GeR=1, TiR=1, unit="kilogram", prod=MACH['reference product'],
       search="fixed", machine_used="same machine as P1", power_kW=5.593, throughput_kg_per_h=812.5, machine_mass_kg=530, machine_life_h=L_H,
       values_as_found="net 530 kg (6' model); life: ecoinvent machine dataset declares 25 years; 5,000 h/year protocol default", value_source="IndiaMART ARSI Traders; ecoinvent dataset documentation",
       value_link="https://m.indiamart.com/impcat/bamboo-splitting-machine.html", conversions="L = 25 y × 5,000 h/y = 125,000 h; M ÷ (throughput × L) = 530 ÷ (812.5 × 125,000)", per_kg_processed=sig(wear1, 4))
    rows.append(rowd(MACH, wear1, "P2", 4, "machine: splitting and planing strips", proxy=True)); dem.append((MACH, wear1))
    # step 2 boiling
    dec(mid, "P1: boiling or steaming strips", "no machine found", "", "", "Searched boiling/steaming tanks for bamboo strips: only charcoal carbonisation furnaces and kilns were found, none with power, throughput and mass. No BREF value for this step. Unclear: rows omitted (lower-impact branch).", "", "web search")
    ch(mid, "A1–A3", "processing: boiling or steaming strips (heat)", rule="P1 unresolved", search="web: bamboo strips steaming boiling tank datasheet", cands="Beston/Shuliy carbonisation furnaces (not the same operation)", amount=0, values_as_found="no row written: no usable machine data")
    dec(mid, "P2: boiling or steaming strips", "no row", "", "", "Step has no energy rows.", "", "")
    # step 3 drying
    dec(mid, "P1: drying strips", "no machine found", "", "", "Kiln datasheets found (ISVE vacuum dryers: 6.5 m³, 6.5 kW heat, 7 kW electric) give no cycle time or mass, so no throughput. BREF OSB drying (0.1-0.4 MWh/m³ heat) was not applied because it describes green strands and would overstate drying of poles already dried to u=20 %. Unclear: rows omitted (lower-impact branch).", "https://www.directindustry.com/prod/isve/product-4605311-2866385.html", "web search")
    ch(mid, "A1–A3", "processing: drying strips (heat)", rule="P1 unresolved", search="web: timber drying kiln datasheet", cands="ISVE EM6V vacuum dryer 6.5 m³, ~6.5 kW heat, ~7 kW electric, no cycle time/mass; Secotherm, Mühlböck listings", amount=0, values_as_found="no row written")
    dec(mid, "P2: drying strips", "no row", "", "", "Step has no energy rows.", "", "")
    # step 4 hot pressing: BREF
    pe = 35.0 / 600.0; ph = 95.0 / 600.0 * 3.6
    dec(mid, "P1: hot pressing", "BREF fallback", f"{pe:.5f} kWh/kg; {ph:.4f} MJ/kg", "", "Press datasheets found (GTCO GTHP-800T-30L: 51.8 kW total, 75,000 kg, 30 openings, no cycle time) lack throughput. Next source, the EU BREF Wood-based Panels 2016, Table 3.2: pressing power 0.01-0.06 MWh/m³ of OSB (mid 0.035), pressing heat for OSB 'ND', particleboard 0.05-0.14 MWh/m³ (mid 0.095, used as proxy). Converted with 600 kg/m³ (panel density, Thünen OSB EPD). Proxy, TeR 4.", "https://aida.ineris.fr/sites/aida/files/documents-bref/WBPbref2016.pdf", "")
    ch(mid, "A1–A3", "processing: hot pressing (electricity)", act=ELEC['name'], loc="RER", amount=sig(pe, 4), rule="P1 BREF fallback", proxy="yes", TeR=4, GeR=1, TiR=1, unit="kilowatt hour", prod=ELEC['reference product'], search="web: plywood hot press datasheet; WBP BREF 2016",
       machine_type="hot press (multi-opening)", machine_candidates="GTCO GTHP-800T-30L 51.8 kW, 75,000 kg, no cycle time/throughput; Master Pur 1400 21.49 kW motor + 51.7 kW heating, no throughput, no mass; Raute R5/R7 no kW",
       machine_used="none (BREF sector average)", values_as_found="BREF Table 3.2 OSB pressing power 0.01-0.06 MWh/m³ of finished panel", value_source="EU BREF Production of Wood-based Panels (2016), Table 3.2", value_link="https://aida.ineris.fr/sites/aida/files/documents-bref/WBPbref2016.pdf",
       conversions="0.035 MWh/m³ = 35 kWh/m³; ÷ 600 kg/m³ = 0.0583 kWh/kg", per_kg_processed=sig(pe, 4))
    ch(mid, "A1–A3", "processing: hot pressing (heat)", act=HEAT['name'], loc="Europe without Switzerland", amount=sig(ph, 4), rule="P1 BREF fallback", proxy="yes", TeR=4, GeR=1, TiR=1, unit="megajoule", prod=HEAT['reference product'], search="WBP BREF 2016",
       machine_type="hot press (multi-opening)", machine_used="none (BREF sector average, particleboard pressing heat as proxy for OSB 'ND')", values_as_found="BREF Table 3.2 particleboard pressing heat 0.05-0.14 MWh/m³", value_source="EU BREF Wood-based Panels (2016), Table 3.2",
       value_link="https://aida.ineris.fr/sites/aida/files/documents-bref/WBPbref2016.pdf", conversions="0.095 MWh/m³ ÷ 600 kg/m³ = 0.158 kWh/kg × 3.6 = 0.57 MJ/kg", per_kg_processed=sig(ph, 4))
    rows += [rowd(ELEC, pe, "P1", 4, "processing: hot pressing (electricity)", proxy=True), rowd(HEAT, ph, "P1", 4, "processing: hot pressing (heat)", proxy=True)]; dem += [(ELEC, pe), (HEAT, ph)]
    dec(mid, "P2: hot pressing", "no row", "", "", "BREF has no machine mass; the press datasheet has no throughput, so M ÷ (throughput × L) cannot be formed. No wear row written (gap, see protocol_issues).", "", "")
    ch(mid, "A1–A3", "machine: hot pressing", rule="P2 unresolved", amount=0, values_as_found="no row: no throughput for the press with a known mass")
    # step 5 sanding
    dec(mid, "P1: sanding", "no machine found", "", "", "Wide-belt sander listings give power and weight (e.g. 11 kW / 670 kg; 15 kW / 1,228 kg) but no throughput, and the main datasheet pages were not retrievable. Unclear: rows omitted (lower-impact branch).", "https://www.exapro.com/felder-fw-952-p260204404", "web search")
    ch(mid, "A1–A3", "processing: sanding (electricity)", rule="P1 unresolved", search="web: wide belt sander datasheet", cands="Felder FW 952 11 kW ~800 kg; SCM Sandya; Weber KSF 3 1350; Heesemann: no throughput", amount=0, values_as_found="no row written")
    dec(mid, "P2: sanding", "no row", "", "", "Step has no energy rows.", "", "")
    # CHECK (mass)
    msum = 0.978 + 0.022
    dec(mid, "CHECK", "yes", f"{msum:.3f}", "kg", "Material rows sum to 1.000 kg = the constituent masses of the input (0.978 + 0.022).", "", "")
    # EPD check
    ours = gwp(dem)
    wear = per(MACH, wear1) / ours
    return mid, label, rows, dem, ours, wear

# =============================================================== MATERIAL 2: OSB
def osb():
    mid = "osb3"; label = "OSB/3"
    market = get("market for oriented strand board", "RER")
    prod = get("oriented strand board production", "RER", "oriented strand board")
    dec(mid, "D1", "yes", market['name'], "", "ecoinvent OSB (EPF average) is made from softwood strands, MDI (about 3.0 %), a further organic chemical (0.86 %) and paraffin (1.8 %), uncoated at the factory gate: the same constituents as the input (wood strands, PMDI/MUF adhesive 5.1 %, paraffin wax 1.9 %); shares differ slightly. Delivered state: uncoated, trimmed board = 'board, unsanded'.", "", "search_ecoinvent 'oriented strand board'")
    dec(mid, "D2", "yes", market['name'], "", "market for oriented strand board exists (RER, RoW).", "", "")
    dec(mid, "D3", "RER", "", "", "market for oriented strand board [RER] is the European market; first rank available.", "", "")
    dec(mid, "D4", "no", "", "", "Only one variant per location (no strength-class or glue variants).", "", "")
    amt = 1 / 607.0
    ch(mid, "A1–A3", "finished product", act=market['name'], loc="RER", amount=sig(amt, 4), rule="D1, D2, D3 RER", TeR=1, GeR=1, TiR=1, unit="cubic meter", prod=market['reference product'], search="oriented strand board",
       cands="market for oriented strand board [RER, RoW]; oriented strand board production [CA-QC, RER, RoW]", conversions="1 kg ÷ 607 kg/m³ (wet mass of the ecoinvent dataset, property 'wet mass') = 0.001647 m³")
    ours = per(market, amt)
    dem = [(market, amt)]
    return mid, label, market, ours

# =============================================================== MATERIAL 3: hemp fibre mat
def hemp():
    mid = "hemp_fibre_mat"; label = "hemp fibre mat"
    dec(mid, "D1", "no", "", "", "No hemp (or any natural-fibre) insulation mat in ecoinvent 3.12: hemp datasheets are stems, decorticated/cottonised fibre, hurd, noil, residues (all FR) only.", "", "search_ecoinvent 'hemp', 'flax', 'insulation', 'fibre', 'jute', 'natural fibre'")
    dec(mid, "D1b", "no", "", "", "No dataset with the same name and delivered state (flexible insulation mat) exists; only fibre intermediates.", "", "same searches")
    fibre = get("market for decorticated fibre, hemp", "FR"); poly = get("market for fibre, polyester", "GLO"); soda = get("market for soda ash, light", "RER")
    dec(mid, "D5: hemp fibre", "yes", fibre['name'], "", "Fibre enters the mat factory as opened/decorticated fibre; cottonised fibre (textile grade) is a further step. Only FR exists (D3 single country).", "", "search_ecoinvent 'hemp'")
    dec(mid, "D5: bicomponent polyester fibre", "no", poly['name'], "", "No bicomponent (core/sheath PET) fibre in ecoinvent ('bicomponent' gives 0 hits). Closest: market for fibre, polyester [GLO] (same polymer class), flagged proxy TeR 4.", "", "search_ecoinvent 'bicomponent', 'polyester'")
    dec(mid, "D5: soda (sodium carbonate)", "yes", soda['name'], "", "Soda ash exists: light [RER, RoW], dense [GLO]. D3 picks RER (light); D4: dense has no European location, so no variant choice is left.", "", "search_ecoinvent 'soda'")
    ch(mid, "A1–A3", "constituent: hemp fibre", act=fibre['name'], loc="FR", amount=0.85, rule="D2 market, D3 FR", TeR=1, GeR=2, TiR=1, unit="kilogram", prod=fibre['reference product'], search="hemp", cands="market for decorticated fibre, hemp [FR]; market for cottonized fibre, hemp [FR]; market for hemp hurd [FR]; market for hemp noil [FR]")
    ch(mid, "A1–A3", "constituent: bicomponent polyester fibre", act=poly['name'], loc="GLO", amount=0.12, rule="PROXY (D5 no)", proxy="yes", TeR=4, GeR=3, TiR=1, unit="kilogram", prod=poly['reference product'], search="bicomponent; polyester", cands="market for fibre, polyester [GLO]; market for textile, nonwoven polyester [GLO]; polyester resins (not fibre)")
    ch(mid, "A1–A3", "constituent: soda (sodium carbonate)", act=soda['name'], loc="RER", amount=0.03, rule="D2 market, D3 RER", TeR=1, GeR=1, TiR=1, unit="kilogram", prod=soda['reference product'], search="soda", cands="market for soda ash, light [RER, RoW]; market for soda ash, dense [GLO]")
    rows = [rowd(fibre, 0.85, "D2", 1, "constituent: hemp fibre"), rowd(poly, 0.12, "PROXY", 4, "constituent: bicomponent polyester fibre", proxy=True), rowd(soda, 0.03, "D2", 1, "constituent: soda (sodium carbonate)")]
    dem = [(fibre, 0.85), (poly, 0.12), (soda, 0.03)]
    # fibre opening: Rieter A12
    e = 14.7 / 2400.0; w = 4050.0 / (2400.0 * L_H)
    dec(mid, "P1: fibre opening", "machine", f"{e:.5f}", "kWh/kg", "Three bale openers found. Complete (power, throughput, mass): Rieter UNIfloc A 12 only (14.7 kW, up to 2,400 kg/h, 4,050 kg net). Trützschler Blendomat BO-A (12.6 kW, 1,600 kg/h) and Changshu Hongyi HYKB-120 (3.75 kW, 200-300 kg/h) have no mass. Rule: a machine lacking one of the three is not used.", "https://www.rieter.com/products/systems/fiber-preparation/bale-opener-unifloc-a-12", "")
    ch(mid, "A1–A3", "processing: fibre opening (electricity)", act=ELEC['name'], loc="RER", amount=sig(e, 4), rule="P1 fixed", TeR=3, GeR=1, TiR=1, unit="kilowatt hour", prod=ELEC['reference product'], search="web: bale opener fibre opening datasheet",
       machine_type="automatic bale opener", machine_candidates="Rieter UNIfloc A 12 (14.7 kW, 2,400 kg/h, 4,050 kg): 0.00613 kWh/kg; Trützschler Blendomat BO-A (12.6 kW, 1,600 kg/h, mass not found): 0.00788; Changshu Hongyi HYKB-120 (3.75 kW, 200-300 kg/h, mass not found): 0.0125-0.0188",
       machine_used="Rieter UNIfloc A 12", power_kW=14.7, throughput_kg_per_h=2400, machine_mass_kg=4050, machine_life_h=L_H, values_as_found="installed power 14.7 kW; production up to 2 400 kg/h; net weight 4 050 kg (without longitudinal parts, control)",
       value_source="Rieter product page", value_link="https://www.rieter.com/products/systems/fiber-preparation/bale-opener-unifloc-a-12", conversions="14.7 kW ÷ 2,400 kg/h = 0.006125 kWh/kg; maximum rating used as throughput (operating point not given)", per_kg_processed=sig(e, 4))
    rows.append(rowd(ELEC, e, "P1", 3, "processing: fibre opening (electricity)")); dem.append((ELEC, e))
    ch(mid, "A1–A3", "machine: fibre opening", act=MACH['name'], loc="RER", amount=sig(w, 4), rule="P2 fixed", TeR=3, GeR=1, TiR=1, unit="kilogram", prod=MACH['reference product'], search="fixed", machine_used="Rieter UNIfloc A 12",
       power_kW=14.7, throughput_kg_per_h=2400, machine_mass_kg=4050, machine_life_h=L_H, values_as_found="net weight 4,050 kg; life: ecoinvent machine dataset 25 years × 5,000 h", value_source="Rieter product page; ecoinvent documentation", value_link="https://www.rieter.com/products/systems/fiber-preparation/bale-opener-unifloc-a-12",
       conversions="4,050 ÷ (2,400 × 125,000)", per_kg_processed=sig(w, 4))
    rows.append(rowd(MACH, w, "P2", 3, "machine: fibre opening")); dem.append((MACH, w))
    for step, why in [("soda impregnation", "No spraying or padding unit with power, throughput and mass found."),
                      ("carding / air-laying", "Laroche airlay (2,400 mm, 51 kW installed) has no throughput; AUTEFA gives t/h per metre without kW; a patent quoting 1,000 kg/h and 45-110 kW could not be verified (scanned PDF)."),
                      ("thermal bonding oven", "No oven datasheet with thermal power and throughput; a hemp patent gives 150 °C and 2 min but no power."),
                      ("cutting", "No mat-cutting machine with power, throughput and mass found (Spewe 1900ML listing has none).")]:
        dec(mid, f"P1: {step}", "no machine found", "", "", why + " Unclear: rows omitted (lower-impact branch). Not in the input as 'no energy', so this is a gap.", "", "web search")
        ch(mid, "A1–A3", f"processing: {step} ({'heat' if step=='thermal bonding oven' else 'electricity'})", rule="P1 unresolved", search="web search", amount=0, values_as_found="no row written: " + why)
        dec(mid, f"P2: {step}", "no row", "", "", "Step has no energy rows.", "", "")
    dec(mid, "CHECK", "yes", "1.000", "kg", "Material rows sum to 0.85 + 0.12 + 0.03 = 1.000 kg = input.", "", "")
    ours = gwp(dem); wear = per(MACH, w) / ours
    return mid, label, rows, dem, ours, wear

# =============================================================== MATERIAL 4: straw bale
def straw():
    mid = "straw_bale"; label = "straw bale"
    straw_m = get("market for straw", "Europe without Switzerland")
    pp = get("market for polypropylene, granulate", "RER")
    dec(mid, "D1", "no", "", "", "ecoinvent 'straw' (market for straw; rye/oat co-product, harvested and baled with 'baling' and 'bale loading') has no polypropylene twine (baling uses PE wrap film). Input lists PP twine 0.2 %, so by D1 ('without a constituent the input lists') it is not an exact match.", "", "search_ecoinvent 'straw', 'baling', 'twine'")
    dec(mid, "D1b", "yes", straw_m['name'], "", "Test 1: same product (straw, baled: the rye production dataset includes baling) and delivered state. Test 2: main constituent straw (99.8 %). Difference: PP twine 0.2 % missing in the dataset.", "", "same searches")
    dec(mid, "D2", "yes", straw_m['name'], "", "market for straw exists.", "", "")
    dec(mid, "D3", "Europe without Switzerland", "", "", "market for straw [CH, Europe without Switzerland, RoW]; European market group first. 'straw, stand-alone production' [RER] and 'straw, organic' [CH, RoW] are other variants.", "", "")
    dec(mid, "D4", "market for straw", "", "", "Variants: plain straw (cereal co-product), organic, stand-alone production. None matches the input state better, so first A-Z: 'market for straw'. TeR 2.", "", "")
    ch(mid, "A1–A3", "finished product (approximate)", act=straw_m['name'], loc="Europe without Switzerland", amount=1.0, rule="D1b, D2, D3, D4", TeR=2, GeR=1, TiR=1, unit="kilogram", prod=straw_m['reference product'], search="straw; baling; twine",
       cands="market for straw [CH, Europe without Switzerland, RoW]; market for straw, organic [CH, RoW]; market for straw, stand-alone production [RER, RoW]", conversions="constituents that differ from the input: polypropylene twine 0.002 kg per kg missing from the dataset")
    ours_a = per(straw_m, 1.0)
    # built route
    dec(mid, "D5: wheat / rye straw", "yes", straw_m['name'], "", "Straw enters as the baled co-product; market for straw EWS (same dataset as D1b).", "", "search_ecoinvent 'straw'")
    dec(mid, "D5: polypropylene twine", "no", pp['name'], "", "No twine/rope/tape dataset ('twine' 0 hits). Closest: polypropylene, granulate (RER market), the raw polymer: proxy TeR 4.", "", "search_ecoinvent 'twine', 'polypropylene'")
    ch(mid, "A1–A3", "constituent: wheat / rye straw", act=straw_m['name'], loc="Europe without Switzerland", amount=0.998, rule="D2, D3, D4", TeR=2, GeR=1, TiR=1, unit="kilogram", prod=straw_m['reference product'], search="straw", cands="see D1b row")
    ch(mid, "A1–A3", "constituent: polypropylene twine", act=pp['name'], loc="RER", amount=0.002, rule="PROXY (D5 no)", proxy="yes", TeR=4, GeR=1, TiR=1, unit="kilogram", prod=pp['reference product'], search="polypropylene; twine", cands="market for polypropylene, granulate [RER and others]")
    dec(mid, "P1: baling", "no row", "", "", "The straw dataset already contains baling (rye production uses 'baling' and 'bale loading'), so no row (P1 rule 2). Logged.", "", "")
    dec(mid, "P1: storage", "no row", "", "", "Note of the step starts with 'no energy'.", "", "")
    ch(mid, "A1–A3", "processing: baling (electricity)", rule="P1 in dataset", amount=0, values_as_found="no row: included in market for straw")
    rows = [rowd(straw_m, 0.998, "D2-D4", 2, "constituent: wheat / rye straw"), rowd(pp, 0.002, "PROXY", 4, "constituent: polypropylene twine", proxy=True)]
    dem = [(straw_m, 0.998), (pp, 0.002)]
    dec(mid, "CHECK", "yes", "1.000", "kg", "0.998 + 0.002 = 1.000 kg = input.", "", "")
    ours_b = gwp(dem)
    return mid, label, straw_m, ours_a, rows, dem, ours_b

def epd_row(mid, check_id, category, ids, vals, ours, result, route, lci_kept="", wear="", reason="", fu="", fd="", fi="", fm=""):
    med = statistics.median(vals) if vals else ""
    checks.append(dict(run_id=RUN, material_id=mid, check_id=check_id, okobaudat_release=OKB, category=category, epd_ids=ids, n_epds=len(vals), epd_median=sig(med, 4) if med != "" else "no EPD in ÖKOBAUDAT",
                       our_gwp_fossil_a1a3=sig(ours, 4), ratio_to_median=sig(ours / med, 3) if med != "" else "", result=result, flag_units_mass=fu, flag_dataset_state=fd, flag_indicator=fi, flag_machine_rows=fm,
                       likely_reason=reason, wear_share_of_gwp_fossil_a1a3=(f"{wear:.2e}" if wear != "" else "not applicable"), route=route, distance_to_median=sig(abs(ours / med - 1), 3) if med != "" else "", lci_kept=lci_kept))
    return med

def main():
    # -------- OSB
    mid, label, market, ours = osb()
    ids = "766ea5bd-3f0f-4d48-a399-9c4a372524d8; 22527f3b-5985-41a7-8028-655142979cfd; 881736f8-1bb1-4e9f-852a-cc9a1f676343; aab0ed28-e5b0-43d6-a932-4cdc4770c518"
    vals = [172.249356295023 / 611, 217.60065735196 / 630, 341.409532128807 / 600, 347.38249887094076 / 600]
    med = statistics.median(vals)
    res = "pass" if 0.5 * med <= ours <= 1.5 * med else "fail"
    dec(mid, "CHECK 1", "yes" if res == "pass" else "no", f"{ours:.4f}", "kg CO2e fossil / kg", f"GWP-fossil A1-A3 {ours:.4f} kg/kg vs median {med:.4f} of 4 EN 15804+A2 OSB EPDs (EGGER 2024, Kronospan 2023, AGEPAN 2022, Thünen DE 2023): ratio {ours/med:.2f}, within 0.5-1.5.", "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75/processes?format=json&search=true&classId=3.2.04", "ÖKOBAUDAT service API, class 3.2.04")
    epd_row(mid, "CHECK 1", "Holz / Holzwerkstoffe / OSB-Platte (3.2.04)", ids, vals, ours, res, "exact", lci_kept="exact", wear=0.0,
            reason="Per kg = GWP-fossil A1-A3 per m³ ÷ declared density (611, 630, 600, 600 kg/m³). Sample ÖKOBAUDAT values per m³: 172, 218, 341, 347 kg CO2e.", fu="per m³ converted with declared gross density; ecoinvent per m³ with wet mass 607 kg/m³", fd="ok: uncoated board", fi="GWP-fossil on both sides", fm="no machine rows (exact match)")
    # A4..C
    L = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
    loss = 0.03 / 0.97
    log_A4_A5_C(mid, label, "Boards (discrete products), not loose or ready-mixed.",
                ("no", "Confirmed OSB makers: DE (EGGER Wismar and Brilon; Swiss Krono/Glunz Heiligengrabe, Meppen), FR (Swiss Krono Sully-sur-Loire). No NL or IT producer found; Spain only a Kronospan project (Tortosa) reported as planned. Trade press names Germany, Romania and Poland as the largest producers. Fewer than 3 of DE/FR/IT/ES/NL.", "https://www.wbpionline.com/analysis/osb-still-a-top-perfomer-9728235/", "web search"),
                ("yes", "Made in Europe: EGGER, Wismar, Germany (also Brilon DE, Rădăuți RO, Hexham UK).", "https://www.egger.com/en/building-products/presentation-building-products-division?country=DK", "web search"),
                "eu", "Typical piece: OSB 3 2,500 × 1,250 × 18 mm = about 34 kg (retailer figures 33.6-34.0 kg; 0.05625 m³ × 600 kg/m³ = 33.8 kg), under 50 kg; not poured.", 34, "https://www.taloon.com/osb3-levy-kronospan-18x1250x2500-mm",
                "Boards are fixed dry (nailed/screwed), not made in situ.", "55", "Boards nailed or screwed, not cast or bonded in a mortar/adhesive sense; piece about 34 kg < 50 kg.")
    # waste: product itself
    items = [("oriented strand board (product)", 1.0, "Wood, wood-based", WOOD, "W2")]
    log_waste(mid, items, "55", loss)
    blocks = build_chain(mid, label, [rowd(market, amt := 1 / 607.0, "D1-D3", 1, "finished product: 1 kg ÷ 607 kg/m³", unit="cubic meter")], transport_rows("eu"), loss, "55", items, {})
    dec(mid, "A4 BLOCK", "EU", "", "", "Lorry 1.5 tkm + ship 0.1 tkm", "", "")
    write_lci(mid, label, blocks, loss=loss)
    cff_bioc(mid, label, "Wood panels", "55", [("wood strands, incl. moisture", 0.93, "Wood", "", "", ""), ("adhesive, PMDI/MUF", 0.051, "Non-biogenic", "", "", ""), ("paraffin wax", 0.019, "Non-biogenic", "", "", "")])
    dec(mid, "CHECK 3", "not run", "", "", "Exact match passed check 1; later routes not tried.", "", "")
    osb_ours = ours; osb_med = med

    # -------- Bamboo
    mid, label, rows, dem, ours, wear = bamboo()
    epd_row(mid, "CHECK 3", "Holz / Holzwerkstoffe (no bamboo class); searched names 'Bambus', 'bamboo'", "none", [], ours, "no check possible", "built", lci_kept="built", wear=wear,
            reason="No EN 15804+A2 bamboo EPD in ÖKOBAUDAT (OBD_2024_III). For information only (not the protocol test): MOSO Solid laminated bamboo EPD (NIBE, EN 15804+A2, 2022) GWP-fossil A1-A3 = 95.7 + 9.28 + 200 = 305 kg CO2e per m³ at 700 kg/m³ = 0.436 kg/kg; our LCI = %.3f." % ours,
            fu="n/a", fd="bamboo pole at u=20 %", fi="GWP-fossil only", fm="steps boiling, drying, sanding unresolved: no rows; splitting mixed-supplier proxy; hot pressing from BREF")
    dec(mid, "CHECK 3", "no check possible", f"{ours:.4f}", "kg CO2e fossil / kg", "No ÖKOBAUDAT EPD for laminated bamboo. LCI kept. MOSO EPD value 0.436 kg/kg quoted for information only.", "https://www.moso-bamboo.com/wp-content/uploads/20170315_EPD_INT_Moso_Solid_EN.pdf", "")
    L = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
    log_A4_A5_C(mid, label, "Delivered as boards/panels.",
                ("no", "MOSO (the input source) produces in China (EPD: 'Manufacturing plant CN', Zwaag NL is the office). CBI study: bamboo panels are not produced in Europe. Bamdura (NL) and KUL (DE) are small, panel output unconfirmed. Far below 3 of 5.", "https://www.moso-bamboo.com/wp-content/uploads/20170315_EPD_INT_Moso_Solid_EN.pdf", "EPD + web search"),
                ("no", "No confirmed European factory for laminated bamboo panels (Bamdura BV, Ravenstein NL makes laminated bamboo goods, mainly garden equipment/furniture; panel production not confirmed). Source EPD gives production in China.", "https://www.galabau-messe.com/en/exhibitors/bamdura-bv-2303693", "web search"),
                "global", "MOSO Solid Panel: typically 2,440 × 1,220 × 7-40 mm at 700 kg/m³; mid thickness 23.5 mm gives 49 kg (20 mm: 42 kg; 40 mm: 83 kg). Under 50 kg at typical thickness; borderline, answered no (lower-impact branch).", 49, "https://www.moso-bamboo.com/wp-content/uploads/20170315_EPD_INT_Moso_Solid_EN.pdf",
                "Panels are fixed dry, not made in situ.", "34", "Panels screwed/fixed; typical piece under 50 kg; not cast or bonded on site.")
    items = [("bamboo strips, incl. moisture", 0.978, "Other plant-based (as wood)", WOOD, "W2"), ("adhesive, MUF", 0.022, "Plastic, resin, binder, coating", PLASTIC, "W2")]
    log_waste(mid, items, "34", loss)
    blocks = build_chain(mid, label, rows, transport_rows("global"), loss, "34", items, {})
    dec(mid, "A4 BLOCK", "Global", "", "", "Lorry 0.5 tkm + ship 10 tkm", "", "")
    write_lci(mid, label, blocks, loss=loss)
    cff_bioc(mid, label, "Solid wood", "34", [("bamboo strips, incl. moisture", 0.978, "Bamboo", "", "", ""), ("adhesive, MUF", 0.022, "Non-biogenic", "", "", "")])
    bam = (ours, wear)

    # -------- Hemp
    mid, label, rows, dem, ours, wear = hemp()
    ids = "1018517a-1fb0-40c9-aa82-d7d3c2687b49; 4089074f-a1b7-411b-a888-5839b1b053e6"
    vals = [32.05543285966216 / 36.0, 1.95003747157489 / 1.72]
    med = statistics.median(vals)
    res = "pass" if 0.5 * med <= ours <= 1.5 * med else "fail"
    epd_row(mid, "CHECK 3", "Dämmstoffe / Hanffaser (2.13)", ids, vals, ours, res, "built", lci_kept="built", wear=wear,
            reason="Two EN 15804+A2 hemp-fibre mats: HempFlax Thermo Hanf Combi Jute (32.06 kg CO2e per 36 kg declared unit = 0.890/kg) and HemKor Jute blend (1.95 per m² at 1.72 kg/m² = 1.13/kg). Hanfvlies (2.13.01) has no GWP-fossil A1-A3 value and is excluded. Our LCI has no thermal-bonding, carding, impregnation or cutting energy (unresolved), so the pass is partly from omitted energy.",
            fu="HempFlax per 36 kg (declared unit = 1 m³); HemKor per m² converted with grammage 1.72 kg/m²", fd="hemp-jute blends in EPDs, hemp only in input", fi="GWP-fossil on both sides", fm="only fibre opening has machine rows")
    dec(mid, "CHECK 3", "yes" if res == "pass" else "no", f"{ours:.4f}", "kg CO2e fossil / kg", f"Our {ours:.3f} vs median {med:.3f} (2 EPDs): ratio {ours/med:.2f}.", "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75/processes?format=json&search=true&name=Hanf", "ÖKOBAUDAT service API")
    log_A4_A5_C(mid, label, "Mats/rolls (discrete products).",
                ("no", "Mat makers found: DE (HempFlax Building Solutions / Thermo Hanf, Nördlingen). NL is the HempFlax group seat (fields; mat plant is in DE); IsoHemp (BE) makes blocks, not mats. No FR/IT/ES mat maker found. Fewer than 3 of 5.", "https://www.thermo-hanf.de/en/about/", "web search"),
                ("yes", "Made in Europe: Thermo Hanf, Nördlingen, Germany.", "https://www.thermo-hanf.de/en/about/", "web search"),
                "eu", "Mat: density 36 kg/m³ (EPD); even a 1.2 × 0.6 × 0.24 m pack is 6 kg. Far under 50 kg.", 6, "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=1018517a-1fb0-40c9-aa82-d7d3c2687b49",
                "Mats placed dry between framing.", "52", "Mats pushed between studs, not bonded; piece ≈ 6 kg < 50 kg.")
    items = [("hemp fibre", 0.85, "Other plant-based (as wood)", WOOD, "W2"), ("bicomponent polyester fibre", 0.12, "Plastic, resin, binder, coating", PLASTIC, "W2"), ("soda (sodium carbonate)", 0.03, "Mineral", MINERAL, "W2")]
    log_waste(mid, items, "52", loss)
    blocks = build_chain(mid, label, rows, transport_rows("eu"), loss, "52", items, {})
    dec(mid, "A4 BLOCK", "EU", "", "", "Lorry 1.5 tkm + ship 0.1 tkm", "", "")
    write_lci(mid, label, blocks, loss=loss)
    cff_bioc(mid, label, "Other plant-based", "52", [("hemp fibre", 0.85, "Cellulose fibres and stalks", "", "", ""), ("bicomponent polyester fibre", 0.12, "Non-biogenic", "", "", ""), ("soda (sodium carbonate)", 0.03, "Non-biogenic", "", "", "")])
    hemp_res = (ours, med, res, wear)

    # -------- Straw
    mid, label, straw_m, ours_a, rows, dem, ours_b = straw()
    ids = "00fe2655-02ad-4ded-925a-af9b8f1a27c8; 15ec902a-44f0-4d3e-9d5a-e3ccb09397ba"
    vals = [18.4935067097017 / 100.0, 6.573644700000001 / 105.0]
    med = statistics.median(vals)
    res_a = "pass" if 0.5 * med <= ours_a <= 1.5 * med else "fail"
    epd_row(mid, "CHECK 2", "Dämmstoffe / Stroh (straw bale and blown straw)", ids, vals, ours_a, res_a, "approximate", lci_kept="", wear=0.0,
            reason="Our value is the ecoinvent straw co-product (rye/oat straw, allocated burden is small). EPDs: FASBA Baustroh bales 0.185/kg, DPM ISO-Stroh blown straw 0.0626/kg. Excluded: Huppenberger straw boards (binder-bonded panels, 0.725/kg), generic Strohdämmung (no GWP-fossil value), ClayTec plasters.",
            fu="per m³ ÷ declared density 100 and 105 kg/m³", fd="bale vs blown straw", fi="GWP-fossil on both sides", fm="no machine rows")
    dec(mid, "CHECK 2", "yes" if res_a == "pass" else "no", f"{ours_a:.4f}", "kg CO2e fossil / kg", f"Our {ours_a:.4f} vs median {med:.4f} (2 EPDs): ratio {ours_a/med:.2f}; below 0.5 so fails. Keep for the review; build from scratch.", "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75/processes?format=json&search=true&name=Stroh", "ÖKOBAUDAT service API")
    res_b = "pass" if 0.5 * med <= ours_b <= 1.5 * med else "fail"
    wear_b = 0.0
    epd_row(mid, "CHECK 3", "Dämmstoffe / Stroh", ids, vals, ours_b, res_b, "built", lci_kept="", wear=wear_b,
            reason="Built = straw 0.998 kg + PP twine 0.002 kg; baling is inside the straw dataset, storage has no energy. Still below the EPDs.", fu="as CHECK 2", fd="as CHECK 2", fi="GWP-fossil", fm="no machine rows")
    dec(mid, "CHECK 3", "yes" if res_b == "pass" else "no", f"{ours_b:.4f}", "kg CO2e fossil / kg", f"Our {ours_b:.4f} vs median {med:.4f}: ratio {ours_b/med:.2f}; fails.", "", "")
    da, db_ = abs(ours_a / med - 1), abs(ours_b / med - 1)
    kept = "built" if db_ < da else ("approximate" if da < db_ else ("built" if ours_b <= ours_a else "approximate"))
    epd_row(mid, "REVIEW", "Dämmstoffe / Stroh", ids, vals, ours_b if kept == "built" else ours_a, "flagged", kept, lci_kept=kept, wear=0.0,
            reason=f"Approximate match {ours_a:.4f} (distance {da:.3f}) vs built {ours_b:.4f} (distance {db_:.3f}); closest kept. Likely reason: ecoinvent straw is a low-burden co-product of cereal production while EPDs (FASBA, DPM) include harvesting, baling, storage and transport as main product; EPDs come from two producers.",
            fu="ok", fd="ok", fi="GWP-fossil only", fm="no machine rows")
    dec(mid, "REVIEW", kept, "", "", f"Kept {kept}: distance {db_ if kept=='built' else da:.3f}; flagged.", "", "")
    log_A4_A5_C(mid, label, "Bales are discrete products.",
                ("unclear", "Bale producers: DE (FASBA-certified building bales, FASBA e.V.), AT (ETA for straw bales); Baustroh is baled on farms wherever cereals grow, but no named manufacturer with link was found for FR, IT, ES, NL. Unclear: lower-impact branch taken (national, 150 km).", "https://www.baunetzwissen.de/nachhaltig-bauen/fachwissen/konstruktionen-elemente/strohballenbau-8142364", "web search"),
                None, "national", "Bale 0.35 × 0.48 m cross-section × 0.8-1.0 m × 100 kg/m³ = about 13-17 kg (length not documented in the source: assumption). Far under 50 kg.", 16, "https://www.baunetzwissen.de/nachhaltig-bauen/fachwissen/konstruktionen-elemente/strohballenbau-8142364",
                "Bales stacked dry, then plastered; the bale itself is prefab.", "52", "Bales stacked and pinned; piece about 16 kg < 50 kg; plaster is a separate material.")
    items = [("wheat / rye straw", 0.998, "Other plant-based (as wood)", WOOD, "W2"), ("polypropylene twine", 0.002, "Plastic (W1 polypropylene)", PP, "W1")]
    log_waste(mid, items, "52", loss)
    use_rows = rows
    blocks = build_chain(mid, label, use_rows, transport_rows("national"), loss, "52", items, {})
    dec(mid, "A4 BLOCK", "National", "", "", "Lorry 0.15 tkm", "", "")
    write_lci(mid, label, blocks, loss=loss)
    cff_bioc(mid, label, "Other plant-based", "52", [("wheat / rye straw", 0.998, "Cellulose fibres and stalks", "", "", ""), ("polypropylene twine", 0.002, "Non-biogenic", "", "", "")])
    # write csvs
    def wr(name, rows, cols):
        with open(os.path.join(OUT, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for r in rows: w.writerow({c: r.get(c, "") for c in cols})
    wr("decisions.csv", decisions, "run_id,material_id,question_id,answer,value,unit,evidence,source_link,search_step,date".split(","))
    wr("dataset_choices.csv", choices, CH_COLS)
    wr("epd_check.csv", checks, "run_id,material_id,check_id,okobaudat_release,category,epd_ids,n_epds,epd_median,our_gwp_fossil_a1a3,ratio_to_median,result,flag_units_mass,flag_dataset_state,flag_indicator,flag_machine_rows,likely_reason,wear_share_of_gwp_fossil_a1a3,route,distance_to_median,lci_kept".split(","))
    wr("cff_inputs.csv", cff, "run_id,material_id,cff_archetype,recycling_share,reuse_share,incineration_share,landfill_share,flag,note".split(","))
    wr("bioc_inputs.csv", bioc, "run_id,material_id,constituent,kg_per_kg_product,carbon_archetype,moisture_content,flag,note".split(","))
    print("OSB", osb_ours, osb_med, osb_ours / osb_med)
    print("bamboo", bam)
    print("hemp", hemp_res, hemp_res[0] / hemp_res[1])
    print("straw approx", ours_a, "built", ours_b, "median", med, ours_a / med, ours_b / med, kept)

if __name__ == "__main__":
    main()
