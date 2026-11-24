"""Builds the batch_1 records and LCI sheets. Read-only on Brightway and on ÖKOBAUDAT."""
import csv, os, statistics as st, json
import openpyxl
from openpyxl.styles import Font
from acts import *
import epd_tool as et

RUN = "batch_1"; DATE = "2026-11-19"
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ECO = DB  # ecoinvent-3.12-cutoff
OBD = "OBD_2024_III (ÖBD-Release vom 13.11.2026)"
OBDL = "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75"

# ---------------------------------------------------------------- record writers
DEC, DSC, EPD, CFF, BIO = [], [], [], [], []

def dec(mat, qid, ans, value="", unit="", ev="", link="", step=""):
    DEC.append(dict(run_id=RUN, material_id=mat, question_id=qid, answer=ans, value=value, unit=unit,
                    evidence=ev, source_link=link, search_step=step, date=DATE))

DSC_COLS = "run_id,material_id,module,row_purpose,search_terms,candidates_considered,chosen_activity,reference_product,location,unit,amount,database,rule_applied,proxy,TeR,GeR,TiR,machine_type,machine_candidates,machine_used,power_kW,throughput_kg_per_h,machine_mass_kg,machine_life_h,values_as_found,value_source,value_link,conversions,per_kg_processed,ecoinvent_version,search_date".split(",")

def dsc(mat, module, purpose, act=None, amount="", rule="", proxy="", TeR="", GeR="", TiR=1, terms="", cands="", **kw):
    r = {c: "" for c in DSC_COLS}
    r.update(run_id=RUN, material_id=mat, module=module, row_purpose=purpose, search_terms=terms,
             candidates_considered=cands, amount=amount, rule_applied=rule, proxy=proxy, TeR=TeR, GeR=GeR, TiR=TiR,
             ecoinvent_version="3.12 cut-off", search_date=DATE)
    if act is not None:
        r.update(chosen_activity=act["name"], reference_product=act["reference product"], location=act["location"],
                 unit=act["unit"], database=ECO)
    r.update(kw)
    DSC.append(r)

def ger(loc):
    if loc in ("RER", "Europe without Switzerland"): return 1
    if loc in ("DE", "FR", "IT", "ES", "NL", "AT", "SE", "FI", "PL", "CH", "PT"): return 2
    if loc == "GLO": return 3
    if loc == "RoW": return 4
    return 5

def sig3(x):
    return float(f"{x:.3g}")

# ---------------------------------------------------------------- LCI sheet writer
HDR = ["name", "amount", "unit", "location", "reference product", "database", "type", "module", "rule", "TeR", "GeR", "TiR", "DQR", "comment"]

def ex(act, amount, module, rule, TeR, TiR=1, comment="", name=None):
    """exchange row for an ecoinvent activity"""
    g = ger(act["location"])
    return [name or act["name"], amount, act["unit"], act["location"], act["reference product"], ECO, "technosphere",
            module, rule, TeR, g, TiR, round((TeR + g + TiR) / 3, 2), comment]

def write_lci(mat, blocks, path):
    """blocks: list of (module, comment, [exchange rows]) in chain order A1-A3, A4, A5, C1, C2, C3-C4"""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "LCI"
    ws["A1"] = "Database"; ws["B1"] = "raw_baselines"
    r = 3; prev = None
    for module, comment, rows in blocks:
        act = f"{mat}, {module}"
        refp = {"A1–A3": "at factory gate", "A4": "delivered to site", "A5": "installed", "C1": "demolished",
                "C2": "at waste site", "C3–C4": "cradle to grave"}[module]
        for k, v in [("Activity", act), ("reference product", f"{mat}, {refp}"), ("unit", "kilogram"),
                     ("location", "RER"), ("module", module), ("comment", comment)]:
            ws.cell(r, 1, k); ws.cell(r, 2, v); r += 1
        ws.cell(r, 1, "Exchanges"); r += 1
        for j, h in enumerate(HDR): ws.cell(r, j + 1, h).font = Font(bold=True)
        r += 1
        ws.append  # no-op
        prod = [act, 1, "kilogram", "RER", f"{mat}, {refp}", "raw_baselines", "production", module, "–"]
        for j, v in enumerate(prod): ws.cell(r, j + 1, v)
        r += 1
        if prev:
            pm, prefp, pamt = prev
            row = [f"{mat}, {pm}", pamt, "kilogram", "RER", prefp, "raw_baselines", "technosphere", module, "–"]
            for j, v in enumerate(row): ws.cell(r, j + 1, v)
            ws.cell(r, 14, "previous block" + (" (A5 takes 1 + loss)" if module == "A5" else ""))
            r += 1
        for row in rows:
            for j, v in enumerate(row): ws.cell(r, j + 1, v)
            r += 1
        r += 1
        prev = (module, f"{mat}, {refp}", 1)
        if module == "A4": prev = (module, f"{mat}, {refp}", 1)
    # A5 takes 1 + loss: patch handled by caller via 'a5_in' marker
    wb.save(path)

def patch_a5_input(path, mat, loss):
    wb = openpyxl.load_workbook(path); ws = wb["LCI"]
    for row in ws.iter_rows(min_row=1):
        if row[0].value == f"{mat}, A4" and row[7].value == "A5":
            row[1].value = round(1 + loss, 6)
    wb.save(path)

# ---------------------------------------------------------------- common data
LORRY_TKM = lambda km: km / 1000
NMD = {  # shares landfill, incineration, recycling, reuse  (sheet nmd_eol)
    "34": dict(landfill=.05, incineration=.80, recycling=.10, reuse=.05),
    "52": dict(landfill=.05, incineration=.95, recycling=0, reuse=0),
    "8": dict(landfill=.01, incineration=0, recycling=.99, reuse=0),
    "78": dict(landfill=.85, incineration=.05, recycling=.10, reuse=0),
}
KM = dict(recycling=50, reuse=50, landfill=50, incineration=100)
def wkm(sh): return sum(sh[k] * KM[k] for k in sh)
LOSS = 0.03 / 0.97
NMDLINK = "https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/"
NMD2020 = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
RICS = "https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf"
WB = "protocol_predetermined_values.xlsx"

def eol_blocks(mat, items, shares, kept_single):
    """items: list of (label, mass_per_kg, {route: (activity or None, rule, proxy, comment)}). Returns (a5_rows, c34_rows)."""
    a5, c34 = [], []
    for label, mass, routes in items:
        for route, sh in shares.items():
            if sh == 0: continue
            act, rule, proxy, com = routes.get(route, (None, "", "", ""))
            if route == "reuse":
                dec(mat, f"W1: {label} × reuse", "no row", "", "", "Reuse: no row under the cut-off rule; benefit goes to D.", WB + " (protocol W1)")
                continue
            if act is None:
                dec(mat, f"W1: {label} × {route}", "no row", "", "", com, WB + " sheet waste_fallback")
                dsc(mat, "C3-C4", f"C3-C4: {label} × {route}", None, 0, rule, proxy, 4, "", 1, values_as_found=com)
                continue
            TeR = 4 if proxy else 1
            amt_c = -round(mass * sh, 6); amt_a = -round(LOSS * mass * sh, 6)
            c34.append(ex(act, amt_c, "C3–C4", rule, TeR, comment=f"{label} × {route}; share {sh}; {com}"))
            a5.append(ex(act, amt_a, "A5", rule, TeR, comment=f"loss {LOSS:.5f} kg × {label} × {route}; {com}"))
            dsc(mat, "C3-C4", f"C3-C4: {label} × {route}", act, amt_c, rule, proxy, TeR, ger(act["location"]),
                terms="see decisions.csv W1 row", values_as_found=com)
            dsc(mat, "A5", f"A5 end of life: {label} × {route}", act, amt_a, rule, proxy, TeR, ger(act["location"]),
                values_as_found=f"loss kg × share {sh}")
    return a5, c34

def std_blocks(mat, a13rows, a13comment, transport, shares, items, extra_a4=None):
    """transport: dict lorry_km, sea_km"""
    blocks = []
    blocks.append(("A1–A3", a13comment, a13rows))
    a4 = []
    if transport["lorry"]:
        a4.append(ex(LORRY, transport["lorry"] / 1000, "A4", "A4 archetype", 1, comment=f"{transport['lorry']} km × 1 kg × 0.001"))
        dsc(mat, "A4", "A4 lorry", LORRY, transport["lorry"] / 1000, "A4 archetype", "", 1, 1, 1, terms="fixed dataset (fixed_settings)",
            values_as_found=f"{transport['lorry']} km", value_source=transport["src"], value_link=transport["link"])
    if transport["sea"]:
        a4.append(ex(SEA, transport["sea"] / 1000, "A4", "A4 archetype", 1, comment=f"{transport['sea']} km × 1 kg × 0.001"))
        dsc(mat, "A4", "A4 ship", SEA, transport["sea"] / 1000, "A4 archetype", "", 1, 3, 1, terms="fixed dataset (fixed_settings)",
            values_as_found=f"{transport['sea']} km", value_source=transport["src"], value_link=transport["link"])
    blocks.append(("A4", f"Transport to site: {transport['label']}", a4))
    a5, c34 = eol_blocks(mat, items, shares, True)
    lorry_loss = LOSS * wkm(shares) / 1000
    a5rows = [ex(LORRY, round(lorry_loss, 7), "A5", "A5 loss", 1, comment=f"loss {LOSS:.5f} kg × weighted C2 distance {wkm(shares):.1f} km ÷ 1000")] + a5
    dsc(mat, "A5", "A5 lorry (loss)", LORRY, round(lorry_loss, 7), "A5 loss", "", 1, 1, 1, terms="fixed dataset",
        values_as_found=f"loss {LOSS:.5f} kg; weighted distance {wkm(shares):.1f} km", value_source="NMD method 2020 §2.6.3.6", value_link=NMD2020)
    blocks.append(("A5", f"Installation: no machine row (I1 no); prefab loss 3 % → 1 + {LOSS:.5f} kg in", a5rows))
    blocks.append(("C1", "Deconstruction by hand (X1 no): no diesel row", []))
    c2amt = round(wkm(shares) / 1000, 6)
    blocks.append(("C2", f"Transport to treatment, weighted by NMD route shares: {wkm(shares):.1f} km one way", [ex(LORRY, c2amt, "C2", "C2 block", 1, comment=f"shares {shares}")]))
    dsc(mat, "C2", "C2 lorry", LORRY, c2amt, "C2 block", "", 1, 1, 1, terms="fixed dataset",
        values_as_found=f"shares {shares}; distances 50/50/50/100 km (sheet nmd_eol)", value_source="protocol_predetermined_values.xlsx sheet nmd_eol", value_link=NMD2020)
    blocks.append(("C3–C4", "End of life, NMD shares; waste has negative amount", c34))
    return blocks

# ---------------------------------------------------------------- ÖKOBAUDAT checks
def obd_value(uuid, dens=None):
    p = et.process(uuid); g = p["gwp_fossil"] or {}
    a = g.get("A1-A3") or sum(g.get(k, 0) for k in ("A1", "A2", "A3"))
    mpu = dens or p["mass_per_unit"]
    return a / (p["ref_amount"] * mpu), a, mpu

def epd_row(mat, cid, cat, ids, vals, ours, result, route, reason, flags=("", "", "", ""), wear="", kept="", ncount=None):
    med = st.median(vals)
    EPD.append(dict(run_id=RUN, material_id=mat, check_id=cid, okobaudat_release=OBD, category=cat, epd_ids="; ".join(ids),
                    n_epds=len(vals) if ncount is None else ncount, epd_median=sig3(med), our_gwp_fossil_a1a3=sig3(ours),
                    ratio_to_median=sig3(ours / med), result=result, flag_units_mass=flags[0], flag_dataset_state=flags[1],
                    flag_indicator=flags[2], flag_machine_rows=flags[3], likely_reason=reason,
                    wear_share_of_gwp_fossil_a1a3=wear, route=route, distance_to_median=sig3(abs(ours / med - 1)), lci_kept=kept))
    return med

def main():
    # ============================================================ MATERIAL 1: sawn_softwood
    m = "sawn_softwood"
    wood_u = ["2bd4c91f-16e5-4e01-b8b5-0c01aac363ce", "1549fb80-44c7-42b3-a806-124206bff53d", "f00557bd-5b73-4624-8c7b-834db8e8b106",
              "0b87961e-ea66-4757-b483-229ece59cb97", "9f6cf0e4-7455-4c31-a99f-552926c4040e", "8bed6eec-b795-4585-b036-77f4344c1cf9"]
    wood_n = ["Nadelschnittholz - getrocknet (Durchschnitt DE)", "EGGER Schnittholz", "Schnittholz Fichte (generisch)", "Schnittholz Kiefer (generisch)",
              "Schnittholz Lärche (generisch)", "Schnittholz Zeder (generisch)"]
    wv = [obd_value(u)[0] for u in wood_u]
    wood_all_median = 0.15265311385053276  # class 3.1.01, all 11 A2 datasets with mass (see work/epd_wood_cork.json)
    beam = A("market for sawnwood, beam, softwood, raw, dried (u=10%)", "Europe without Switzerland")
    board = A("market for sawnwood, board, softwood, raw, dried (u=10%)", "Europe without Switzerland")
    wet_mass = 464.64  # kg per m3 at u=10 % (property 'wet mass' of the activity)
    amt_m3 = round(1 / wet_mass, 8)
    our_wood = gwp([(beam, amt_m3)])
    ex_terms = "sawnwood, softwood; sawnwood board softwood; sawn timber; softwood dried"
    cand = ("market for sawnwood, beam/board, softwood, raw, dried (u=10%) [Europe without Switzerland, CH, RoW]; "
            "kiln drying to u=20% and air drying to u=20% variants; planed variants (state differs); no u=12 % dataset")
    dec(m, "D1", "yes", "market for sawnwood, beam, softwood, raw, dried (u=10%)", "", "Wood only (no extra constituent); kiln dried, raw (= rough sawn), untreated. Moisture u=10 % vs 12 % of the input: 2-point difference, no u=12 % dataset exists; accepted as the same delivered state (kiln dried). Carbon content 0.494, wet mass 464.64 kg/m3.", "", ex_terms)
    dec(m, "D2", "yes", "market for sawnwood, beam, softwood, raw, dried (u=10%)", "", "Market dataset exists.", "")
    dec(m, "D3", "Europe without Switzerland", "", "", "Market datasets exist for Europe without Switzerland, CH and RoW; the European market is first in the order.", "")
    dec(m, "D4", "beam", "", "", "beam and board variants both match 'rough sawn'; none matches better, so first A–Z: beam. Other variant recorded: board (GWP-fossil 0.141 vs 0.146 kg/kg).", "")
    dsc(m, "A1-A3", "finished product", beam, amt_m3, "D1; D2; D3; D4", "", 2, 1, 1, terms=ex_terms, cands=cand,
        values_as_found=f"1 kg ÷ wet mass 464.64 kg/m3 (u=10 %)", value_source="ecoinvent 3.12 activity property 'wet mass'", conversions="1 kg / 464.64 kg per m3 = 0.00215 m3",
        value_link="")
    ours = our_wood / 1.0 if False else gwp([(beam, amt_m3)])
    med = epd_row(m, "CHECK 1", "3.1.01 Holz / Vollholz / Bau-Schnittholz: softwood sawn timber, dried, not planed", wood_u, wv, ours, "pass", "exact",
                  f"Pass. Softwood set: {', '.join(wood_n)}. Class-wide median over all 11 A2 datasets with a mass (incl. hardwood, fresh, planed): {wood_all_median:.3f}; ratio {ours/wood_all_median:.2f}, also pass. Kiln-drying energy and moisture differ between EPDs.",
                  ("per m3 converted with each dataset's mass per m3 (484–716 kg/m3); EGGER 503 kg/m3", "ecoinvent u=10 % vs EPD u=12 %", "GWP-fossil only", "n/a (dataset)"),
                  wear="not applicable (single dataset, no machine rows)", kept="exact", ncount=len(wv))
    dec(m, "CHECK 1", "yes", sig3(ours), "kg CO2e/kg", f"Ours {sig3(ours)} vs median {sig3(med)} (n={len(wv)}), ratio {ours/med:.2f}: within 0.5–1.5.", OBDL)
    # A4
    wood_tr = dict(lorry=150, sea=0, label="national, 150 km lorry", src="NMD method 2020 §2.6.3.6", link=NMD2020)
    dec(m, "A4 · T1", "no", "", "", "Sawn timber is delivered as pieces (boards, beams), not loose or ready-mixed.", NMD2020)
    dec(m, "A4 · T2", "yes", "DE, FR, IT", "countries", "DE: EGGER sawn timber (EPD in ÖKOBAUDAT, Brilon plant); FR: NEOFOR Bonneville sawmill (>60,000 m3 logs/yr, spruce/fir); IT: general sawmills, e.g. Segheria Codarri (Varese) – kiln drying not confirmed for IT. 3 of 5 reached; ES and NL not verified.",
        "https://materials.oneclicklca.com/en/material/kiln-dried-sawn-timber/6a4800c7aef3155d3535d2f1 ; https://draaf.auvergne-rhone-alpes.agriculture.gouv.fr/IMG/pdf/presentation_scierie_nbb_-_scolytes.pdf ; https://www.georisques.gouv.fr/webappReport/ws/installations/inspection/SswoERCTnxqsnLmG6EId4N9byO6cleai", "web search: sawn softwood manufacturer by country")
    # A5/C1/L1
    dec(m, "A5 · I1", "no", 19.4, "kg per piece", "Typical piece 50 × 200 × 4000 mm = 0.04 m3 × 484.5 kg/m3 (density of the ÖKOBAUDAT dataset) = 19.4 kg < 50 kg. Dimensions are our assumption for a typical joist.", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=2bd4c91f-16e5-4e01-b8b5-0c01aac363ce")
    dec(m, "A5 · L1", "no", "3 % waste; loss = 0.03/0.97 = 0.0309", "", "Prefab timber placed dry/fixed mechanically, not made in situ.", NMD2020)
    dec(m, "C1 · X1", "no", 19.4, "kg per piece", "Taken apart by hand: mechanically fixed, not cast or bonded; piece < 50 kg.", "")
    sh = NMD["34"]
    dec(m, "C2 · ROUTE", "34", "34 wood, untreated: beams, planks", "category", f"Sheet nmd_eol: landfill 5 / incineration 80 / recycling 10 / reuse 5 %.", NMDLINK)
    W = lambda n, loc, prod=None: A(n, loc, prod)
    wl = W("treatment of waste wood, untreated, sanitary landfill", "CH", "waste wood, untreated")
    wi = W("treatment of waste wood, untreated, municipal incineration FAE", "CH", "waste wood, untreated")
    wr = W("treatment of waste wood, post-consumer, sorting and shredding", "CH")
    routes_w = dict(landfill=(wl, "W1", "", "waste wood, untreated: CH (single country before GLO/RoW)"),
                    incineration=(wi, "W1", "", "waste wood, untreated; CH FAE variant (CH precedes GLO in D3)"),
                    recycling=(wr, "W1", "", "post-consumer wood sorting and shredding; CH"))
    for r_, (a_, *_x) in routes_w.items():
        dec(m, f"W1: sawn softwood × {r_}", "yes", a_["name"], "", f"Exact waste material (waste wood, untreated) and route words; location {a_['location']} by D3 (no RER/Europe w/o CH dataset).", "")
    dec(m, "W1: sawn softwood × reuse", "no row", "", "", "Reuse: no row (cut-off).", "")
    items = [("sawn softwood", 1.0, routes_w)]
    a13 = [ex(beam, amt_m3, "A1–A3", "D1; D2; D3; D4", 2, comment="1 kg of product = 1/464.64 m3 (wet mass at u=10 %); exact match; variant beam (D4)")]
    blocks = std_blocks(m, a13, "Exact match (D1): market for sawnwood, beam, softwood, raw, dried (u=10%)", wood_tr, sh, items)
    p = f"{OUT}/LCI_{m}.xlsx"; write_lci(m, blocks, p); patch_a5_input(p, m, LOSS)
    CFF.append(dict(run_id=RUN, material_id=m, cff_archetype="Solid wood", recycling_share=.10, reuse_share=.05, incineration_share=.80, landfill_share=.05, flag="", note="NMD category 34; sheet cff_archetypes"))
    dec(m, "D · CFF · F1", "Solid wood", "", "", "Material listed in cff_archetypes row 'Solid wood'.", WB)
    BIO.append(dict(run_id=RUN, material_id=m, constituent="softwood timber, incl. 12 % moisture", kg_per_kg_product=1, carbon_archetype="Wood", moisture_content=0.12, flag="", note="u = 12 % from input note"))
    dec(m, "D · BIO-C · B1: softwood timber, incl. 12 % moisture", "Wood", "", "", "Constituent listed under archetype Wood in carbon_archetypes.", WB)
    for s_, why in [("sawing", "Exact match: steps are inside the ecoinvent dataset"), ("kiln drying", "Exact match"), ("sorting, packing", "Exact match / note 'no energy'")]:
        dec(m, f"P1: {s_}", "skipped", "", "", why + ": no machine rows (protocol P1 applies only to LCIs built from scratch).", "")
    wood_res = dict(ours=ours, med=med)

    # ============================================================ MATERIAL 2: cork
    m = "cork"
    ck = A("market for cork slab", "RER"); ck_prod = A("cork slab production", "RER")
    craw = A("market for cork, raw", "RoW")
    cork_ours = gwp1(ck)
    cork_ids = ["fdbe82c6-7073-4f8c-a540-c37a6bf16cd6"]
    cv, ca, cmpu = obd_value(cork_ids[0])
    cork_terms = "cork; cork slab; market for cork slab; cork, raw"
    dec(m, "D1", "no", "cork slab production, RER", "", "Dataset 'cork slab production' (RER) contains resin binders per kg slab: melamine formaldehyde resin 0.056 kg, phenolic resin 0.028 kg, urea formaldehyde resin 0.056 kg (0.14 kg of 1.14 kg inputs, 12 %); the input is pure expanded cork without binder. Not an exact match (protocol example).", "", cork_terms)
    dec(m, "D1b", "yes", "market for cork slab (RER)", "", "Same product (cork slab = cork board/underlay/insulation) and same main constituent (cork, 1.06 kg raw cork per kg). Differences: + melamine formaldehyde resin 0.056 kg/kg, + phenolic resin 0.028, + urea formaldehyde resin 0.056 (≈ 0.14 kg/kg slab); dataset also uses 1 kWh electricity + 4.92 MJ wood-chip heat per kg. Delivered state 'as sold' vs ecoinvent 'cork slab' (documentation: used as underlay or insulation).", "", cork_terms)
    dec(m, "D2", "yes", "market for cork slab", "", "Market exists (RER).", "")
    dec(m, "D3", "RER", "", "", "RER market exists: first in D3 order.", "")
    dec(m, "D4", "none", "", "", "Only one variant (RER); RoW market also exists.", "")
    dsc(m, "A1-A3", "finished product (approximate)", ck, 1, "D1b; D2; D3", "", 2, 1, 1, terms=cork_terms,
        cands="cork slab production RER/RoW; market for cork slab RER/RoW; constituents differ: melamine formaldehyde resin 0.056, phenolic resin 0.028, urea formaldehyde resin 0.056 kg/kg",
        values_as_found="legacy ecoinvent v2 dataset (Portuguese producer, used for Europe)", value_source="ecoinvent 3.12 documentation")
    med = epd_row(m, "CHECK 2", "2.9.01 Dämmstoffe / Expandierter Kork", cork_ids, [cv], cork_ours, "fail", "approximate",
                  "Fail: ours is 1.87× the median. The ecoinvent slab contains ~12 % formaldehyde-type resins that the pure board does not, and 4.92 MJ heat + 1 kWh. Only one EN 15804+A2 dataset (Sphera generic, 40.98 kg CO2e per m3 at 80 kg/m3); the Amorim ICB EPD (82.8 kg CO2e per 115 kg = 0.72 kg/kg, EPD Hub 0281) is not in ÖKOBAUDAT and not used.",
                  ("m3 → kg with 80 kg/m3 (dataset flow property)", "dataset is slab with binder", "GWP-fossil only", "n/a (dataset)"),
                  wear="not applicable", kept="", ncount=1)
    dec(m, "CHECK 2", "no", sig3(cork_ours), "kg CO2e/kg", f"Ours {sig3(cork_ours)} vs median {sig3(med)} (n=1), ratio {cork_ours/med:.2f} > 1.5.", OBDL)
    # build from scratch
    hm = dict(power=60.0, thr=7000.0, mass=962.5)
    life_h = 25 * 5000
    e_kwh = 1.06 * hm["power"] / hm["thr"]
    wear = 1.06 * hm["mass"] / (hm["thr"] * life_h)
    built_cork = gwp([(craw, 1.06), (ELEC, e_kwh), (MACH, wear)])
    wear_share = gwp([(MACH, wear)]) / built_cork
    dec(m, "D5: raw cork granules", "yes", "market for cork, raw", "", "ecoinvent has 'cork, raw' (forestry, PT/RoW). D3: no dataset in RER/Europe w/o CH/DE…CH/GLO; RoW (rank 6) comes before 'any other' (PT, rank 7) in the written order, so RoW. Note: the PT market is Portuguese, which is where cork is grown (GWP 0.0626 vs RoW 0.0305 kg/kg). Literal order applied; see protocol_issues.", "", "cork; cork, raw")
    dsc(m, "A1-A3", "constituent: raw cork granules", craw, 1.06, "D5; D2; D3", "", 1, 4, 1, terms="cork; cork, raw", cands="market for cork, raw PT/RoW; cork forestry PT/RoW",
        values_as_found="built route, NOT KEPT (REVIEW)")
    # P1/P2 grinding
    cands_g = ("Siebtechnik TEMA HM 4a: 18.5 kW, 7,000 kg/h (10 mm gap), 1,310 kg → 0.00264 kWh/kg | "
               "Ottevanger 650 series: 30–90 kW, 2–12 t/h, 750–1,175 kg excl. motor (midpoints 60 kW, 7,000 kg/h, 962.5 kg) → 0.00857 kWh/kg | "
               "Bruks-Siwertell HH 300x850: 75–110 kW, 2–4 t/h, 1,400 kg excl. motor (midpoints 92.5 kW, 3,000 kg/h) → 0.0308 kWh/kg")
    dec(m, "P1: grinding", "Ottevanger hammer mill 650 series", 0.00857, "kWh/kg processed", "Hammer mill (usual machine for grinding). Three manufacturers; median energy per kg = Ottevanger (0.00857 kWh/kg). Ottevanger and Bruks datasheets give RANGES per series, not per model: midpoints used. Cork-specific throughput not published.",
        "https://making.com/equipment/industrial-hammer-mill-for-granulate-grinding ; https://www.siebtechnik-tema.com/hammer-and-hammer-impact-mills/ ; https://bruks-siwertell.com/milling/hammer-mill-green-materials", "web search: hammer mill datasheet")
    dsc(m, "A1-A3", "processing: grinding (electricity)", ELEC, round(e_kwh, 6), "P1", "", 3, 1, 1, terms="hammer mill datasheet power throughput weight",
        machine_type="hammer mill", machine_candidates=cands_g, machine_used="Ottevanger 650 series (midpoints)", power_kW=60, throughput_kg_per_h=7000, machine_mass_kg=962.5,
        values_as_found="30–90 kW; 2–12 t/h; 750–1,175 kg (excl. motor)", value_source="Ottevanger Milling Engineers via making.com", value_link="https://making.com/equipment/industrial-hammer-mill-for-granulate-grinding",
        conversions="60 kW ÷ 7,000 kg/h = 0.00857 kWh/kg; × 1.06 kg processed", per_kg_processed=0.0085714, values_as_found_note="NOT KEPT (REVIEW)")
    dsc(m, "A1-A3", "machine: grinding", MACH, wear, "P2", "", 3, 1, 1, machine_type="hammer mill", machine_used="Ottevanger 650 series (midpoints)", power_kW=60, throughput_kg_per_h=7000,
        machine_mass_kg=962.5, machine_life_h=life_h, values_as_found="M 962.5 kg (excl. motor); life: no datasheet value; ecoinvent machine dataset documents 'service life declared by the producer: 25 years'; 5,000 h/yr assumed",
        value_source="ecoinvent 3.12 documentation of 'industrial machine production, heavy, unspecified'; protocol default 5,000 h/yr", value_link="",
        conversions="962.5 ÷ (7,000 × 125,000) = 1.10e-6 kg/kg; × 1.06 = %.3g kg" % wear, per_kg_processed=962.5 / (7000 * life_h))
    for s_, nm in [("autoclave expansion (superheated steam)", "autoclave"), ("cutting blocks into boards", "block cutting saw")]:
        dec(m, f"P1: {s_}", "unresolved", "", "", f"No public datasheet with power, throughput and mass found for a cork {nm} (searched: cork autoclave in EN/PT, steam consumption; band saws for foam/cork blocks – no throughput; no BREF for cork; Amorim EPD gives totals only). No row written; built LCI is incomplete.", "https://www.mdpi.com/1996-1944/9/5/394")
        dsc(m, "A1-A3", f"processing: {s_} (heat)", None, 0, "P1", "unresolved", 3, "", 1, machine_type=nm, values_as_found="no machine data found; no rows written")
    dec(m, "P1: cooling and stabilising", "no energy", "", "", "Note of the step starts with 'no energy': no rows.", WB + " sheet input_definitions")
    dec(m, "CHECK", "yes", 1.06, "kg", "Material row raw cork 1.06 kg = constituent mass of the input.", "")
    cork_epd_ids = cork_ids
    epd_row(m, "CHECK 3", "2.9.01 Dämmstoffe / Expandierter Kork", cork_ids, [cv], built_cork, "fail", "built",
            "Fail: ours is far below the median because 2 of 4 steps (autoclave heat, cutting) have no machine data and no rows (incomplete build); raw cork 0.0305 kg/kg × 1.06 + grinding only.",
            ("m3 → kg with 80 kg/m3", "raw cork RoW market", "GWP-fossil only", "autoclave, cutting missing; grinding hammer mill median machine; wear share 8.3e-5"),
            wear=sig3(wear_share), kept="", ncount=1)
    dec(m, "CHECK 3", "no", sig3(built_cork), "kg CO2e/kg", f"Ours {sig3(built_cork)} vs median {sig3(med)}, ratio {built_cork/med:.2f}.", OBDL)
    d_ap = abs(cork_ours / med - 1); d_b = abs(built_cork / med - 1)
    kept = "approximate" if d_ap <= d_b else "built"
    epd_row(m, "REVIEW", "2.9.01 Dämmstoffe / Expandierter Kork", cork_ids, [cv], cork_ours if kept == "approximate" else built_cork, "flagged", kept,
            f"Compared: approximate match {sig3(cork_ours)} (ratio {cork_ours/med:.2f}, distance {d_ap:.3f}); built {sig3(built_cork)} (ratio {built_cork/med:.2f}, distance {d_b:.3f}; incomplete: autoclave and cutting missing). No exact match was tried (D1 no). Kept: {kept}. Likely reason for the gap: the ecoinvent slab carries resin binders; the built LCI lacks the steam step. A complete built LCI would be higher.",
            ("m3 → kg 80 kg/m3 (one EPD)", "slab vs pure board", "GWP-fossil only", "built: grinding only"), wear=sig3(wear_share), kept=kept, ncount=1)
    dec(m, "REVIEW", kept, "", "", f"Distances: approximate {d_ap:.3f}, built {d_b:.3f}; keep the closer.", "")
    assert kept == "approximate"
    # transport etc. cork
    ct = dict(lorry=1500, sea=100, label="EU manufactured: lorry 1,500 km + container ship 100 km", src="RICS WLCA 2023 Table 17", link=RICS)
    dec(m, "A4 · T1", "no", "", "", "Cork boards are discrete products.", NMD2020)
    dec(m, "A4 · T2", "no", "FR, ES confirmed", "countries", "FR: Agglolux-CBL (Soustons) makes expanded cork; ES: Barnacork (Aglocork expanded cork panels). DE: Zipse is a distributor/partner of Amorim, not a confirmed producer; NL: Pro Suber (Tilburg) – no production confirmed; IT: only Amorim's Corkpan brand. 2 of 5 confirmed.",
        "https://automa.net/company/agglolux-cbl ; https://arquitecturaviva.com/brands/products/sistema-de-paneles-de-corcho-expandido-aglocork ; https://amorimcorksolutions.com/en-us/about-us/blog/from-portugal-to-germany-a-partnership-built-on-cork/", "web search: expanded cork manufacturers")
    dec(m, "A4 · T3", "yes", "Amorim Cork Insulation, Portugal", "", "Amorim Isolamentos (Portugal) is the market leader in expanded cork board.", "https://www.bcork.amorim.com/en/about-us/who-we-are/")
    dec(m, "A5 · I1", "no", 4, "kg per piece", "Board 1000 × 500 × 100 mm = 0.05 m3 × 80 kg/m3 (density of the ÖKOBAUDAT dataset) = 4 kg; dimensions our assumption.", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=fdbe82c6-7073-4f8c-a540-c37a6bf16cd6")
    dec(m, "A5 · L1", "no", "3 % waste", "", "Boards placed dry/fixed, prefab.", NMD2020)
    dec(m, "C1 · X1", "no", 4, "kg per piece", "Taken apart by hand, not cast or bonded (mechanical fixing assumed); piece < 50 kg.", "")
    sh = NMD["52"]
    dec(m, "C2 · ROUTE", "52", "52 organic / bio-based, other", "category", "Sheet nmd_eol: landfill 5 / incineration 95 / recycling 0 / reuse 0 %.", NMDLINK)
    cl = W("treatment of waste wood, untreated, sanitary landfill", "CH", "waste wood, untreated")
    ci = W("treatment of waste wood, untreated, municipal incineration FAE", "CH", "waste wood, untreated")
    dec(m, "W1: cork slab × landfill", "no", "", "", "No ecoinvent waste treatment named for waste cork / cork slab.", "", "ecoinvent scan: names starting 'treatment of waste cork'")
    dec(m, "W1: cork slab × incineration", "no", "", "", "As above.", "")
    dec(m, "W2: cork slab × landfill", cl["name"], "", "", "Sheet waste_fallback: class 'Other plant-based' (raw cork granules): landfill = as wood → treatment of waste wood, untreated, sanitary landfill (CH). Proxy TeR 4.", WB)
    dec(m, "W2: cork slab × incineration", ci["name"], "", "", "Class 'Other plant-based': incineration = as wood (CH FAE variant).", WB)
    items = [("cork slab", 1.0, dict(landfill=(cl, "W2", "proxy", "waste wood proxy"), incineration=(ci, "W2", "proxy", "waste wood proxy")))]
    a13 = [ex(ck, 1, "A1–A3", "D1b; D2; D3", 2, comment="approximate match; REVIEW kept; resin binders differ (see dataset_choices)")]
    blocks = std_blocks(m, a13, "Approximate match (D1b): market for cork slab, RER; kept after REVIEW", ct, sh, items)
    p = f"{OUT}/LCI_{m}.xlsx"; write_lci(m, blocks, p); patch_a5_input(p, m, LOSS)
    CFF.append(dict(run_id=RUN, material_id=m, cff_archetype="Other plant-based", recycling_share=0, reuse_share=0, incineration_share=.95, landfill_share=.05, flag="REVIEW-flagged (approximate match kept)", note="NMD category 52"))
    dec(m, "D · CFF · F1", "Other plant-based", "", "", "Listed in cff_archetypes.", WB)
    BIO.append(dict(run_id=RUN, material_id=m, constituent="raw cork granules", kg_per_kg_product=1.0, carbon_archetype="Cork", moisture_content="", flag="", note="1.06 kg input minus 0.06 kg loss"))
    dec(m, "D · BIO-C · B1: raw cork granules", "Cork", "", "", "Listed under Cork.", WB)
    cork_a4 = None

    # ============================================================ MATERIAL 3: fibre_cement
    m = "fibre_cement"
    fl_big = A("market for fibre cement facing tile, large format", "GLO")
    fl_small = A("market for fibre cement facing tile, small format", "GLO")
    fl_gen = A("market for fibre cement facing tile", "GLO")
    fc_ours = gwp1(fl_big)
    l = et.listing(classId="1.3.12"); full = {x["uuid"][:8]: x["uuid"] for x in l}
    fc_set = [("Cementex/Cementex Extreme", "b144ce25"), ("Faserzementplatte (Fassade) generic", "161e1abd"), ("Genesis Faserzementplatte", "c76c5eed"),
              ("Swisspearl Carat/Avera/Vintago/Reflex", "436dc453"), ("Swisspearl Nobilis/Planea/Terra/Purio", "4ab586da"),
              ("Swisspearl pigmentierte Faserzementplatte", "8548f6a1"), ("Swisspearl Zenor", "7ccd30f4")]
    fcv = []; fc_ids = []
    for n_, k in fc_set:
        v, a_, mp = obd_value(full[k]); fcv.append(v); fc_ids.append(f"{full[k]} ({n_})")
    fc_terms = "fibre cement; fibre-cement (bw2data scan)"
    dec(m, "D1", "no", "fibre cement facing tile, large format (CH/RoW)", "", "Dataset is cement 0.909 kg, sulfate pulp 0.091 kg, acrylic dispersion 0.016, PE fibre 0.018, limestone 0.05, chemical inorganic 0.017 per kg tile; the input has cement 0.714, pigments 0.095, water 0.071, other 0.048. Pigments and water missing, cement share differs: not the same constituents.", "", fc_terms)
    dec(m, "D1b", "yes", "market for fibre cement facing tile, large format (GLO)", "", "Same product (large-format fibre cement facade tile) and same main constituent (cement). Differences: no pigments (0.095 in input), no water (0.071), cement 0.909 vs 0.714, + cellulose 0.091 vs 0.048, + acrylic coating 0.016 vs 0.024, + PE fibre 0.018 (PVA in input), + limestone ~0.05.", "", fc_terms)
    dec(m, "D2", "yes", "market for fibre cement facing tile, large format", "", "Market exists (GLO only).", "")
    dec(m, "D3", "GLO", "", "", "No RER/Europe w/o CH market. The only market is GLO ('market for', 99.2 % RoW + 0.8 % CH production); the CH production activity would be a single European country (rank 4) before GLO (rank 5) but D2 says market first. Literal reading: GLO market. The CH production dataset (1.02 kg/kg, ratio 0.94 to the median) would also pass CHECK 2; see protocol_issues.", "")
    dec(m, "D4", "large format", "", "", "Large-format tile matches a facade panel; alternatives recorded: small format, generic 'facing tile' market (GWP 1.37 kg/kg).", "")
    dsc(m, "A1-A3", "finished product (approximate)", fl_big, 1, "D1b; D2; D3; D4", "", 2, 3, 1, terms=fc_terms,
        cands="fibre cement facing tile production large format CH/RoW; small format; generic; corrugated slab; roof slate; markets GLO",
        values_as_found="differences: no pigments (0.095 kg), no water (0.071), cement 0.909 vs 0.714, pulp 0.091 vs 0.048, acrylic 0.016 vs 0.024, PE fibre 0.018 vs PVA/fillers 0.048, + limestone ~0.05",
        value_source="ecoinvent 3.12 activity exchanges")
    med = epd_row(m, "CHECK 2", "1.3.12 Mineralische Baustoffe / Steine und Elemente / Faserzement: facade panels", fc_ids, fcv, fc_ours, "pass", "approximate",
                  "Pass: ratio 1.29. Facade-panel set of 7 A2 datasets (Etex Cementex; Sphera generic; Etex Genesis; 4 Swisspearl). Excluded: AQUAPANEL cement boards (different product), polypropylene fibres, Swisspearl roof slate. With AQUAPANEL included (n=9) the median is 1.06 and the result is the same. Large spread between the generic (0.67 kg/kg) and the Swisspearl/Genesis EPDs (1.06–1.30).",
                  ("per m2 → per kg with grammage 12–14.6 kg/m2 from the flow data", "coated vs uncoated panels mixed", "GWP-fossil only", "n/a (dataset)"),
                  wear="not applicable", kept="approximate", ncount=len(fcv))
    dec(m, "CHECK 2", "yes", sig3(fc_ours), "kg CO2e/kg", f"Ours {sig3(fc_ours)} vs median {sig3(med)} (n={len(fcv)}), ratio {fc_ours/med:.2f}.", OBDL)
    fct = dict(lorry=150, sea=0, label="national, 150 km lorry (T2 unclear → lower-impact branch)", src="NMD method 2020 §2.6.3.6", link=NMD2020)
    dec(m, "A4 · T1", "no", "", "", "Panels are discrete products.", NMD2020)
    dec(m, "A4 · T2", "unclear", "ES confirmed", "countries", "Only ES confirmed with a source: Etex, Portillo (Valladolid) site, 27,000 m2 covered; Etex Germany Exteriors is the German arm (plant location not stated in the results); FR, IT, NL not found. Unclear → lower-impact branch (yes, national).",
        "https://www.alimarket.es/construccion/noticia_amp/312484/el-grupo-etex-integra-sus-marcas-para-fachadas-y-cubiertas-en-una-unica-ensena", "web search: fibre cement facade plants")
    dec(m, "A5 · I1", "no", 40.6, "kg per piece", "Panel 1250 × 2500 mm = 3.125 m2 × 13 kg/m2 (grammage of the ÖKOBAUDAT dataset 'Faserzementplatte (Fassade)') = 40.6 kg < 50 kg; format is our assumption (large panels exist).", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=161e1abd-fe38-45f6-8658-8bf4fa88eb7c")
    dec(m, "A5 · L1", "no", "3 % waste", "", "Facade panels are prefab, fixed dry.", NMD2020)
    dec(m, "C1 · X1", "no", 40.6, "kg per piece", "Mechanically fixed panels removed by hand; < 50 kg.", "")
    sh = NMD["8"]
    dec(m, "C2 · ROUTE", "8", "8 concrete, masonry, reinforced concrete (†closest for fibre cement)", "category", "Sheet nmd_eol: landfill 1 / incineration 0 / recycling 99 / reuse 0 %.", NMDLINK)
    f_rec = W("treatment of waste cement-fibre slab, recycling", "CH")
    f_lf = W("treatment of inert waste, inert material landfill", "CH", "inert waste, for final disposal")
    dec(m, "W1: fibre cement × recycling", "yes", f_rec["name"], "", "Dataset for waste cement-fibre slab with route 'recycling'; CH by D3 (no RER/Europe w/o CH).", "")
    dec(m, "W1: fibre cement × landfill", "no", "", "", "'treatment of waste cement-fibre slab, collection for final disposal' is a collection step, not named inert material/sanitary landfill; no dataset with the route words.", "")
    dec(m, "W2: fibre cement × landfill", f_lf["name"], "", "", "Sheet waste_fallback class Mineral (cement): landfill = treatment of inert waste, inert material landfill (CH). Proxy TeR 4.", WB)
    items = [("fibre cement", 1.0, dict(recycling=(f_rec, "W1", "", "waste cement-fibre slab"), landfill=(f_lf, "W2", "proxy", "inert waste proxy")))]
    a13 = [ex(fl_big, 1, "A1–A3", "D1b; D2; D3; D4", 2, comment="approximate match, CHECK 2 pass; GLO market (99.2 % RoW production)")]
    blocks = std_blocks(m, a13, "Approximate match (D1b): market for fibre cement facing tile, large format, GLO", fct, sh, items)
    p = f"{OUT}/LCI_{m}.xlsx"; write_lci(m, blocks, p); patch_a5_input(p, m, LOSS)
    CFF.append(dict(run_id=RUN, material_id=m, cff_archetype="Mineral, crushed to aggregate", recycling_share=.99, reuse_share=0, incineration_share=0, landfill_share=.01, flag="", note="NMD category 8 (closest)"))
    dec(m, "D · CFF · F1", "Mineral, crushed to aggregate", "", "", "Listed in cff_archetypes.", WB)
    fcb = [("cement", .714, "Non-biogenic"), ("pigments", .095, "Non-biogenic"), ("cellulose fibre", .048, "Cellulose fibres and stalks"), ("water", .071, "Non-biogenic"),
           ("coating", .024, "Non-biogenic"), ("other (PVA fibre, fillers)", .048, "Non-biogenic")]
    for c_, kg, arch in fcb:
        BIO.append(dict(run_id=RUN, material_id=m, constituent=c_, kg_per_kg_product=kg, carbon_archetype=arch, moisture_content="", flag="", note=""))
        dec(m, f"D · BIO-C · B1: {c_}", arch, "", "", "Looked up in carbon_archetypes.", WB)
    for s_ in ["pulping cellulose", "mixing slurry", "Hatschek forming and pressing", "coating with oven curing", "cutting"]:
        dec(m, f"P1: {s_}", "skipped", "", "", "Approximate match kept (CHECK 2 pass): no build from scratch, no machine rows.", "")
    dec(m, "P1: curing", "skipped", "", "", "Approximate match kept; note also says 'no energy'.", "")

    # ============================================================ MATERIAL 4: stone_wool
    m = "stone_wool"
    sw_ids = ["17fd7497-26ba-4442-be48-54f83c0583de", "732dcc2d-1131-4a75-a669-e871675b5ba4", "15fb59fb-085b-4d66-9240-d098e4724112"]
    sw_dens = [159, 99, 38]
    swv = []; swi = []
    for u, d_, n_ in zip(sw_ids, sw_dens, ["ROCKWOOL high density (159 kg/m3)", "ROCKWOOL medium density (99 kg/m3)", "ROCKWOOL low density (38 kg/m3)"]):
        v, a_, mp = obd_value(u, d_); swv.append(v); swi.append(f"{u} ({n_})")
    v, a_, mp = obd_value("64aeaeb6-bb0f-4e18-a97b-c31b1407ad66"); swv.append(v); swi.append("64aeaeb6-bb0f-4e18-a97b-c31b1407ad66 (SeaRox/ProRox families, technical insulation)")
    basalt = A("market for basalt", "GLO"); cem = A("market for cement, Portland", "Europe without Switzerland")
    phen = A("market for phenolic resin", "RER"); oil = A("market for lubricating oil", "RER")
    sw_terms = "stone wool; glass wool; market for stone wool; basalt; phenolic resin"
    dec(m, "D1", "no", "stone wool production / stone wool, packed (CH/RoW)", "", "Dataset: basalt 0.705, cement 0.145, dolomite 0.082, limestone 0.093, coke 5.2 MJ, urea 0.029, phenol 0.022, formaldehyde 0.060; the input has basalt 0.37, cement-bonded briquettes 0.59, binder 0.035, mineral oil 0.002. Different constituents.", "", sw_terms)
    dec(m, "D1b", "no", "stone wool production (CH/RoW)", "", "Same product, but test 2 fails: the main constituent of the input is cement-bonded briquettes (0.59 > basalt 0.37), the dataset's main constituent is basalt (0.705 kg). Answer no → build from scratch.", "", sw_terms)
    # constituents
    cons = [("diabase / basalt", .37, basalt, "yes", "", "D5; D3 (GLO market only)"),
            ("cement-bonded briquettes (recycled)", .59, cem, "no", "proxy", "PROXY: cement, Portland (Europe w/o CH); briquettes are cement-bonded recycled wool and cement"),
            ("binder, urea-modified phenol-formaldehyde", .035, phen, "no", "proxy", "PROXY: phenolic resin (no urea-modified PF in ecoinvent)"),
            ("mineral oil", .002, oil, "no", "proxy", "PROXY: lubricating oil (no mineral oil dataset)")]
    for n_, kg, a_, yn, pr, note in cons:
        dec(m, f"D5: {n_}", yn, a_["name"], "", note + f"; location {a_['location']} by D3.", "", f"bw2data scan names containing '{n_.split(',')[0].split(' /')[0]}'")
        dsc(m, "A1-A3", f"constituent: {n_}", a_, kg, "D5; D2; D3" if not pr else "PROXY", pr, 4 if pr else 1, ger(a_["location"]), 1, terms=n_, values_as_found=note)
    swc = [(a_, kg) for _, kg, a_, *_ in cons]
    # BREF energy
    tot = 12.5  # MJ per kg, midpoint of 7–18 GJ/t
    sh_ = dict(melting=50, fiber=30, curing=30, other=8); ssum = sum(sh_.values())
    heat = {k: tot * sh_[k] / ssum for k in ("melting", "fiber", "curing")}
    elec_mj = tot * sh_["other"] / ssum; elec_kwh = elec_mj / 3.6
    bref_link = "https://bureau-industrial-transformation.jrc.ec.europa.eu/sites/default/files/2020-03/superseded_gls_bref_1201.pdf"
    steps = [("cupola melting", "melting", HEAT, heat["melting"], "MJ"), ("fiberising, binder spraying", "fiber", HEAT, heat["fiber"], "MJ"),
             ("curing oven", "curing", HEAT, heat["curing"], "MJ"), ("cutting", "other", ELEC, elec_kwh, "kWh")]
    for s_, k, act, amt, u_ in steps:
        dec(m, f"P1: {s_}", "BREF", round(amt, 4), u_, "No public datasheet with power, throughput and mass found (searched cupola/fiberising/curing oven: only Grenzebach cupola 6–8 t/h melt without kW; no spinner/oven kW). Next source: EU BREF Glass Manufacturing 2001, Table 3.29 (stone and slag wool): total 7–18 GJ/t finished product (midpoint 12.5); melting 30–70 %, fiberising 25–35 %, curing/drying 25–35 %, others 6–10 % (midpoints 50/30/30/8, normalised to 118 %). 'Others' (general services, electricity) assigned to cutting. All melting/fiberising/curing energy booked as heat from the fixed natural-gas dataset although the cupola burns coke (limitation).", bref_link, "BREF Table 3.29")
        dsc(m, "A1-A3", f"processing: {s_} ({'heat' if act is HEAT else 'electricity'})", act, round(amt, 5), "P1", "BREF", 3, ger(act["location"]), 1,
            terms="stone wool cupola fiberising curing oven datasheet; EU BREF glass", machine_type=s_, machine_candidates="no datasheet found; BREF used",
            values_as_found=f"BREF Table 3.29: total 7–18 GJ/t (mid 12.5); share {sh_[k]} % of 118 % (normalised)",
            value_source="EU BREF Glass Manufacturing Industry (Dec 2001), section 3.8.5, Table 3.29", value_link=bref_link,
            conversions=f"12.5 MJ/kg × {sh_[k]}/{ssum} = {amt if u_=='MJ' else elec_mj:.3f} MJ/kg" + ("; ÷ 3.6 = %.4f kWh" % elec_kwh if u_ == "kWh" else ""), per_kg_processed=round(amt, 5))
        dec(m, f"P2: {s_}", "no machine row", "", "", "Energy from BREF, not from a machine: no machine mass/life available; no wear row.", bref_link)
    dec(m, "CHECK", "yes", sum(k for _, k, *_ in cons), "kg", "Material rows 0.37 + 0.59 + 0.035 + 0.002 = 0.997 kg = sum of the input constituents (the input itself sums to 0.997, not 1; see protocol_issues).", "")
    sw_ours = gwp(swc + [(HEAT, heat["melting"] + heat["fiber"] + heat["curing"]), (ELEC, elec_kwh)])
    med = epd_row(m, "CHECK 3", "2.1.03 Dämmstoffe / Mineralwolle / Steinwolle: unfaced stone wool insulation", swi, swv, sw_ours, "pass", "built",
                  "Pass: ratio 1.14 (EN 15804+A2 ROCKWOOL average datasets, per m3 ÷ declared bulk density 159/99/38 kg/m3 from the EPD text, plus SeaRox/ProRox). Rockpanel facade panels (A2) excluded as a different product. Built LCI energy is a BREF midpoint, not machine data; proxies for briquettes, binder and oil.",
                  ("per m3 ÷ declared bulk density from EPD text", "dry stone wool, unfaced", "GWP-fossil only", "no machine rows (BREF energy); proxies: briquettes (cement), binder (phenolic resin), oil (lubricating oil)"),
                  wear="0 (no machine rows)", kept="built", ncount=len(swv))
    dec(m, "CHECK 3", "yes", sig3(sw_ours), "kg CO2e/kg", f"Ours {sig3(sw_ours)} vs median {sig3(med)} (n={len(swv)}), ratio {sw_ours/med:.2f}.", OBDL)
    swt = dict(lorry=150, sea=0, label="national, 150 km lorry (T2 unclear → lower-impact branch)", src="NMD method 2020 §2.6.3.6", link=NMD2020)
    dec(m, "A4 · T1", "no", "", "", "Boards are discrete products.", NMD2020)
    dec(m, "A4 · T2", "unclear", "DE confirmed", "countries", "ROCKWOOL Gladbeck (1954) and Neuburg a.d. Donau, Germany; the EPD lists sites 'Gladbeck, Neuburg…'; NL/FR/IT/ES sites not confirmed by the search. Unclear → lower-impact branch (yes, national).",
        "https://www.rockwool.com/de/unternehmen/company-information/ ; https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=732dcc2d-1131-4a75-a669-e871675b5ba4", "web search: Rockwool factories")
    dec(m, "A5 · I1", "no", 7.1, "kg per piece", "Board 1200 × 600 × 100 mm = 0.072 m3 × 99 kg/m3 (ÖKOBAUDAT medium-density dataset) = 7.1 kg; dimensions our assumption.", "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=732dcc2d-1131-4a75-a669-e871675b5ba4")
    dec(m, "A5 · L1", "no", "3 % waste", "", "Prefab boards placed dry.", NMD2020)
    dec(m, "C1 · X1", "no", 7.1, "kg per piece", "Taken apart by hand, not bonded; < 50 kg.", "")
    sh = NMD["78"]
    dec(m, "C2 · ROUTE", "78", "78 stone wool", "category", "Sheet nmd_eol: landfill 85 / incineration 5 / recycling 10 / reuse 0 %.", NMDLINK)
    mw_lf = W("treatment of waste mineral wool, inert material landfill", "Europe without Switzerland", "waste mineral wool, for final disposal")
    rc_rec = W("treatment of waste reinforced concrete, recycling", "Europe without Switzerland")
    pl_lf = W("treatment of waste plastic, mixture, sanitary landfill", "CH", "waste plastic, mixture")
    pl_in = W("treatment of waste plastic, mixture, municipal incineration FAE", "CH", "waste plastic, mixture")
    mineral = dict(landfill=(mw_lf, "W2", "proxy", "mineral wool class landfill"), incineration=(None, "W2", "", "sheet: '—' for mineral wool incineration: no row"),
                   recycling=(rc_rec, "W2", "proxy", "'as mineral': waste reinforced concrete recycling"))
    plastic = dict(landfill=(pl_lf, "W2", "proxy", "plastic class landfill"), incineration=(pl_in, "W2", "proxy", "plastic class incineration; CH FAE"),
                   recycling=(None, "W2", "", "plastic recycling: no row (cut-off)"))
    for c_, cls, rt in [("diabase / basalt", "Mineral wool", mineral), ("cement-bonded briquettes (recycled)", "Mineral wool", mineral),
                        ("binder, urea-modified phenol-formaldehyde", "Plastic, resin, binder, coating", plastic), ("mineral oil", "Plastic, resin, binder, coating", plastic)]:
        dec(m, f"W1: {c_} × landfill", "no", "", "", "No ecoinvent waste treatment named for this constituent and route.", "", "ecoinvent scan: treatment of waste mineral wool / plastic")
        dec(m, f"W2: {c_}", cls, "", "", "Sheet waste_fallback: " + "; ".join(f"{k} → {v[0]['name'] if v[0] else 'no row'}" for k, v in rt.items()), WB)
    items = [(c_, kg, mineral if i < 2 else plastic) for i, (c_, kg, *_x) in enumerate(cons)]
    a13 = [ex(a_, kg, "A1–A3", "D5; PROXY" if pr else "D5; D2; D3", 4 if pr else 1, comment=note) for _, kg, a_, yn, pr, note in cons]
    a13 += [ex(HEAT, round(heat["melting"], 5), "A1–A3", "P1", 3, comment="processing: cupola melting (heat); BREF Table 3.29; MJ"),
            ex(HEAT, round(heat["fiber"], 5), "A1–A3", "P1", 3, comment="processing: fiberising, binder spraying (heat); BREF; MJ"),
            ex(HEAT, round(heat["curing"], 5), "A1–A3", "P1", 3, comment="processing: curing oven (heat); BREF; MJ"),
            ex(ELEC, round(elec_kwh, 5), "A1–A3", "P1", 3, comment="processing: cutting (electricity); BREF 'others'; kWh")]
    blocks = std_blocks(m, a13, "Built from scratch (CHECK 3 pass); energy from BREF Table 3.29; proxies flagged", swt, sh, items)
    p = f"{OUT}/LCI_{m}.xlsx"; write_lci(m, blocks, p); patch_a5_input(p, m, LOSS)
    CFF.append(dict(run_id=RUN, material_id=m, cff_archetype="Mineral wool", recycling_share=.10, reuse_share=0, incineration_share=.05, landfill_share=.85, flag="built with proxies and BREF energy", note="NMD category 78"))
    dec(m, "D · CFF · F1", "Mineral wool", "", "", "Listed in cff_archetypes.", WB)
    for c_, kg, *_x in cons:
        BIO.append(dict(run_id=RUN, material_id=m, constituent=c_, kg_per_kg_product=kg, carbon_archetype="Non-biogenic", moisture_content="", flag="", note=""))
        dec(m, f"D · BIO-C · B1: {c_}", "Non-biogenic", "", "", "Listed under Non-biogenic.", WB)

    # ---------------------------------------------------------------- write CSVs
    def wcsv(name, rows, cols):
        with open(f"{OUT}/{name}", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    def cols(name): return open(f"{OUT}/{name}").readline().strip().split(",")
    wcsv("decisions.csv", DEC, cols("decisions.csv"))
    wcsv("dataset_choices.csv", DSC, DSC_COLS)
    wcsv("epd_check.csv", EPD, cols("epd_check.csv"))
    wcsv("cff_inputs.csv", CFF, cols("cff_inputs.csv"))
    wcsv("bioc_inputs.csv", BIO, cols("bioc_inputs.csv"))
    print("wood", wood_res["ours"], wood_res["med"], "| cork", cork_ours, built_cork, med if False else "", "| fc", fc_ours, "| sw", sw_ours)
    print("cork wear share", wear_share, "med cork", cv, "med fc", st.median(fcv), "med sw", st.median(swv))

if __name__ == "__main__":
    main()
