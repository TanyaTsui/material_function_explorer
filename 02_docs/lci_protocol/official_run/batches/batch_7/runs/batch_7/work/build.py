import sys, statistics, json
sys.path.insert(0, "/tmp")
import obd_gwp
from lib import *

R = Rows()
OBD = "OBD_2024_III (latest datastock listed at oekobaudat.de, 2026-11-19)"
OBDL = "https://www.oekobaudat.de/OEKOBAU.DAT/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75/processes"
NMD = "https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/"
NMDM = "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf"
WG = "waste_gwp"

# ---- waste treatment datasets (W1 / W2), D3 order: Europe w/o CH, then single country (CH), then GLO, RoW
WOOD = dict(landfill="05340b91b158ef48ca6994ac19d71a42", incineration="90052db5ec4d19c2703b4600a95e85e8",
            recycling="cfd30a3023bf31babf15908c52f4ff5b")
PURW = dict(landfill="22cf329a2359a33e12f5c0451e9d7545", incineration="d07fd59757e7bef17cf8836d2f70fe05", recycling=None)
PLAST = dict(landfill="2d3eb9ef3fca8f2b629cee10b8e56af2", incineration="c96ef6f78d24a2cfc2f5b5b5b8138d8b", recycling=None)
ALW = dict(landfill="5d69d6253dbbb87252d7a677bb5a6509", incineration="22d4c8b243d47bda81025526d4cb89fc", recycling=None)

DIST = dict(landfill=50, incineration=100, recycling=50, reuse=50)
LOSS = 0.03 / 0.97   # prefab 3 % (NMD) -> kg lost per kg installed


def epd_set(uuids):
    out = []
    for u in uuids:
        i = obd_gwp.info(u)
        out.append(i)
    vals = [i["gwp_fossil_per_kg"] for i in out]
    assert all(v is not None for v in vals), [i for i in out if i["gwp_fossil_per_kg"] is None]
    return out, statistics.median(vals)


def gwp_of(items):
    t, per = bwx.gwp(items)
    return t, per


def tail(mat, a13, route, I1, L1, X1, waste, t2_ev, piece_ev, t3=None, kind="matched"):
    """Builds A4..C3-C4 blocks, logs the A4/A5/C1/C2/C3-C4 decisions and dataset rows.
    route: dict landfill/incineration/recycling/reuse shares (fractions)
    waste: list of dict(label, mass, ds={route: (code, rule, proxy, note)})"""
    prod = lambda m: f"{mat}, {m}"
    # ---- A4
    a4 = Block("A4", mat, a13.out_prod, a13.out_name, prod("A4"), f"{mat}, delivered to site")
    a4.add(LORRY, 0.15, "A4 · T2", 1, comment="national: 150 km one way, 0.15 tkm per kg (NMD 2020 §2.6.3.6)")
    R.ds(mat, "A4", "A4 lorry", LORRY, 0.15, rule="A4 · T2 national", TeR=1, candidates="fixed dataset (fixed_settings)")
    # ---- A5
    a5 = Block("A5", mat, a4.out_prod, a4.out_name, prod("A5"), f"{mat}, installed", prev_amount=fmt(1 + LOSS))
    a5.comment = f"loss = 0.03/0.97 = {LOSS:.6f} kg per kg installed (prefab, NMD 3 %)"
    if I1:
        a5.add(DIESEL, 0.015, "A5", 1, comment="0.015 MJ per kg installed (EPD Hub 0135 crane energy)")
        R.ds(mat, "A5", "A5 diesel", DIESEL, 0.015, rule="A5 (fixed value)", TeR=1)
    wt = sum(s * DIST[k] for k, s in route.items()) / 1000.0   # tkm per kg of waste
    a5.add(LORRY, LOSS * wt, "A5 loss", 1, comment=f"lost kg {LOSS:.6f} x route-weighted {wt:.4f} tkm per kg (C2 distances)")
    R.ds(mat, "A5", "A5 lorry (loss)", LORRY, fmt(LOSS * wt), rule="A5 · LOSS + C2 distances", TeR=1)
    # ---- C1
    c1 = Block("C1", mat, a5.out_prod, a5.out_name, prod("C1"), f"{mat}, demolished")
    if X1:
        c1.add(DIESEL, 0.036, "C1", 1, comment="0.036 MJ per kg (Bozdag & Secer 2007, One Click LCA default)")
        R.ds(mat, "C1", "C1 diesel", DIESEL, 0.036, rule="C1 (fixed value)", TeR=1)
    # ---- C2
    c2 = Block("C2", mat, c1.out_prod, c1.out_name, prod("C2"), f"{mat}, at waste site")
    c2.add(LORRY, wt, "C2", 1, comment="shares x distance: " + ", ".join(f"{k} {s:g}x{DIST[k]} km" for k, s in route.items() if s))
    R.ds(mat, "C2", "C2 lorry", LORRY, fmt(wt), rule="C2 BLOCK", TeR=1)
    # ---- C3-C4 (and A5 end of life for the lost kg)
    c34 = Block("C3–C4", mat, c2.out_prod, c2.out_name, prod("C3–C4"), f"{mat}, cradle to grave")
    for w in waste:
        for rt, share in route.items():
            if share <= 0: continue
            m = w["mass"] * share
            if rt == "reuse":
                R.dec(mat, f"W1: {w['label']} × reuse", "no row", 0, "kg", "Reuse: no row under the cut-off rule (benefit goes to D).", NMD)
                continue
            d = w["ds"].get(rt)
            if d is None:
                R.dec(mat, f"W1: {w['label']} × {rt}", "no row", 0, "kg",
                      "Recycling of metals and plastics: no row (cut-off rule, protocol W1 'No search needed').", NMD)
                continue
            code, rule, proxy, note = d
            a = bwx.get(code)
            sign = -1 if list(a.production())[0]["amount"] < 0 else 1
            R.dec(mat, f"W1: {w['label']} × {rt}", "yes" if rule == "W1" else "no", code and a["name"],
                  "", note, "", step="ecoinvent 3.12 cut-off, search_ecoinvent.py/Brightway name search")
            for blk, mm, mod in ((c34, m, "C3–C4"), (a5, m * LOSS, "A5")):
                amt = sign * mm
                cm = f"{w['label']} x {rt}: mass {mm:.6g} kg"
                if sign > 0: cm += "; reference product positive (recycling output), amount written positive so the burden counts"
                blk.add(code, amt, rule, 4 if proxy else 3, comment=cm)
                purpose = (f"C3-C4: {w['label']} × {rt}" if mod == "C3–C4" else f"A5 end of life: {w['label']} × {rt}")
                R.ds(mat, mod, purpose, code, fmt(amt), rule=rule, proxy="proxy" if proxy else "", TeR=4 if proxy else 3,
                     search_terms=note.split("|")[0] if "|" in note else "", candidates=note)
    return [a13, a4, a5, c1, c2, c34], wt


def common_decisions(mat, t1_ev, t2, t2_ev, t2_links, t3, I1, piece_ev, piece_link, X1, route_cat, route, cff, bioc, flag=""):
    R.dec(mat, "A4 · T1", "no", "", "", t1_ev, NMDM)
    R.dec(mat, "A4 · T2", "yes" if t2 else "no", "", "", t2_ev, t2_links)
    if not t2:
        R.dec(mat, "A4 · T3", "yes" if t3 else "no", "", "", "see T2 evidence", t2_links)
    R.dec(mat, "A5 · I1", "yes" if I1 else "no", "", "", piece_ev, piece_link)
    R.dec(mat, "A5 · L1", "no", "", "", "Prefab: delivered as finished beams/boards/profiles that are only fixed in place, not made in situ; waste rate 3 % (NMD).", NMDM)
    R.dec(mat, "A5 · LOSS", "3 %", f"{LOSS:.6f}", "kg per kg installed", "w = 3 %, loss = w/(1-w) = 0.03/0.97.", NMDM)
    R.dec(mat, "C1 · X1", "yes" if X1 else "no", "", "", ("Same piece weight and 50 kg threshold as A5 · I1: " + piece_ev), piece_link)
    R.dec(mat, "C2 · ROUTE", route_cat, "", "NMD category",
          "Shares (landfill/incineration/recycling/reuse %): " + "/".join(f"{route[k]*100:g}" for k in ("landfill", "incineration", "recycling", "reuse")) +
          " from sheet nmd_eol; transport 50 km (recycling, reuse, landfill) and 100 km (incineration).", NMD)
    R.dec(mat, "D · CFF · F1", cff, "", "CFF archetype", "Material found in column 'materials' of sheet cff_archetypes.", "protocol_predetermined_values.xlsx#cff_archetypes")
    R.add("cff_inputs.csv", material_id=mat, cff_archetype=cff, recycling_share=route["recycling"], reuse_share=route["reuse"],
          incineration_share=route["incineration"], landfill_share=route["landfill"], flag=flag, note="shares from C2 (nmd_eol)")
    for (c, kg, arch, moist, fl, note) in bioc:
        R.dec(mat, f"D · BIO-C · B1: {c}", arch, "", "carbon archetype",
              "Constituent looked up by name in column 'constituents' of sheet carbon_archetypes." + (" " + note if note else ""),
              "protocol_predetermined_values.xlsx#carbon_archetypes")
        R.add("bioc_inputs.csv", material_id=mat, constituent=c, kg_per_kg_product=kg, carbon_archetype=arch,
              moisture_content=moist, flag=fl, note=note)


def finish_block_dqr(a13, weights):
    num = den = 0
    for x, w in zip(a13.rows, weights):
        if x["DQR"] == "": continue
        num += x["DQR"] * w; den += w
    a13.comment += f" DQR (mass-weighted, energy/wear rows weighted by kg processed) = {num/den:.2f}" + (" (low quality, >3)" if num/den > 3 else "")
    return num / den


T1 = "Delivered as discrete pieces (beams, panels, boards, profiles), not loose or ready-mixed."
SRC_TIME = "ecoinvent 3.12 cut-off"

# =====================================================================================================
# GLULAM
# =====================================================================================================
mat = "glulam"
route34 = dict(landfill=0.05, incineration=0.80, recycling=0.10, reuse=0.05)
sg, med = epd_set(["ba8e3b37-f28b-4778-9e4c-336102cf589b", "efa55966-4f29-4f15-bfec-8c08b3945923", "c836b484-773f-4a07-9baa-c70da743ccea",
                    "78bfe151-3cf3-46cb-a1a5-61a79bbd5476", "86138863-3c1c-4345-9ae9-03ba28a5f9a7", "e8cf2935-ef5c-40db-a819-953a9ef12df8",
                    "5f0e3815-925b-4b54-ab3b-148017d4143d"])
GL = "6631d38ef5d3200876974978a3ea2ec7"
wm = 444.0
amt = 1 / wm
R.dec(mat, "D1", "yes", "market for glued laminated timber, average glue mix", "",
      "Soft-wood glulam, dried and planed, glued with a PUR/MUF mix. ecoinvent 'average glue mix' per m3 (444 kg wet mass): 8.37 kg MUF, 0.40 kg PUR, 0.31 kg phenolic resin = 2.0 % glue; sawn softwood dried to u=10 %. Constituents match the input (softwood lamellas + PUR/MUF adhesive); the 0.07 % phenolic resin is a minor part of the glue system. See protocol_issues.md (D1).",
      "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=73366123-98d1-4fb1-9edc-37ba4ba57331",
      "search_ecoinvent.py 'glued laminated timber'; candidates: production average glue mix (Europe w/o CH, RoW, CA-QC), MUF-glue (CH), PUR-glue (CH), markets for each; exchanges read with bw2data")
R.dec(mat, "D2", "yes", "market for glued laminated timber, average glue mix", "", "A market dataset exists, so it covers A2 transport.", "")
R.dec(mat, "D3", "Europe without Switzerland", "", "", "Market for the average glue mix exists for Europe without Switzerland (D3 rule 1); MUF and PUR markets exist only for CH.", "")
R.dec(mat, "D4", "average glue mix", "", "", "At Europe w/o CH only the average glue mix exists; the MUF-glue and PUR-glue variants (CH only) are recorded. The input adhesive is a PUR/MUF mix, so the average mix fits best.", "")
a13 = Block("A1–A3", mat, None, None, f"{mat}, A1–A3", f"{mat}, at factory gate")
a13.add(GL, amt, "D1 (D2-D4)", 1, comment=f"1 kg product = {amt:.6g} m3 at wet mass 444 kg/m3 (ecoinvent property 'wet mass'); input amount 1 kg per kg of product")
a13.comment = "Exact match D1. "
finish_block_dqr(a13, [1])
R.ds(mat, "A1–A3", "finished product", GL, fmt(amt), rule="D1 (D2-D4)", TeR=1, search_terms="glued laminated timber",
     candidates="production, average glue mix: Europe w/o CH, RoW, CA-QC; production MUF-glue CH; production PUR-glue CH; market MUF-glue CH; market PUR-glue CH; market average glue mix Europe w/o CH, RoW",
     conversions="m3 = kg / 444 kg/m3 (property 'wet mass' of the dataset)")
t, per = gwp_of([(GL, amt)])
ratio = t / med
R.add("epd_check.csv", material_id=mat, check_id="CHECK 1", okobaudat_release=OBD, category="3.1.04 Holz / Vollholz / Brettschichtholz (BSH) (CLT entry Hasslacher excluded)",
      epd_ids="; ".join(i["uuid"] for i in sg), n_epds=len(sg), epd_median=fmt(med, 4), our_gwp_fossil_a1a3=fmt(t, 4),
      ratio_to_median=fmt(ratio, 3), result="pass" if 0.5 <= ratio <= 1.5 else "fail",
      flag_units_mass="EPD per m3 converted with the EPD's own gross density (424-515 kg/m3); ours 1/444 m3 per kg",
      flag_dataset_state="ecoinvent glulam is dried, planed; EPDs are glulam at factory gate", flag_indicator="GWP-fossil only (EF 3.1 climate change: fossil)",
      flag_machine_rows="no machine rows (exact match)", likely_reason="", wear_share_of_gwp_fossil_a1a3="not applicable (no machine rows)",
      route="exact", distance_to_median=fmt(abs(ratio - 1), 3), lci_kept="exact")
R.dec(mat, "CHECK 1", "yes" if 0.5 <= ratio <= 1.5 else "no", fmt(ratio, 3), "x median", f"Ours {t:.4f} kg CO2e/kg vs median {med:.4f} of {len(sg)} EPDs ({OBD}).", OBDL)
glulam_res = dict(ours=t, med=med, ratio=ratio, n=len(sg))
common_decisions(mat, T1, True,
                 "Manufacturers found: DE Holzwerke Ladenburger (EPD in OEKOBAU.DAT); FR Schilliger Bois SAS (GL24h); IT Rubner (glulam, EN 14080); ES Egoin (Basque Country, glulam). 4 of 5 countries.",
                 "DE https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=73366123-98d1-4fb1-9edc-37ba4ba57331 ; FR https://egurtek.bilbaoexhibitioncentre.com/en/exhibitor/SCHILLIGER-BOIS-SAS/product/Glulam-Glued-Laminated-Timber-GL24h/25082/?idioma=US ; IT https://www.rubner.com/en/holzbau/glulam-manufacturer-supplier/ ; ES https://www.timber-online.net/wood_products/2023/04/relying-on-high-frequency-technology.html",
                 None, True,
                 "Typical beam: standard widths 80-280 mm (Rubner), e.g. 180 mm x 240 mm x 6 m x 480 kg/m3 = 124 kg > 50 kg. Dimensions partly assumed (only width range is sourced); density 480 kg/m3 from the EPD.",
                 "https://www.rubner.com/en/holzbau/glulam-manufacturer-supplier/", True,
                 "34 wood, untreated: beams, planks", route34, "Solid wood",
                 [("softwood lamellas, incl. moisture", 0.984, "Wood", round(11.5 / 86.9, 4), "", "moisture = 11.5 % water / 86.9 % atro from the input note"),
                  ("adhesive, PUR/MUF", 0.016, "Non-biogenic", "", "", "")])
waste = [dict(label="glulam (product)", mass=1.0, ds=dict(
    landfill=(WOOD["landfill"], "W2", True, "No ecoinvent waste dataset for glued laminated timber; the product is 98 % softwood, so the Wood class of sheet waste_fallback is used: treatment of waste wood, untreated, sanitary landfill (CH, D3 order) | proxy"),
    incineration=(WOOD["incineration"], "W2", True, "waste_fallback Wood class: treatment of waste wood, untreated, municipal incineration FAE (CH, D3 order) | proxy"),
    recycling=(WOOD["recycling"], "W2", True, "waste_fallback Wood class: treatment of waste wood, post-consumer, sorting and shredding (CH) | proxy")))]
blocks, wt = tail(mat, a13, route34, True, False, True, waste, "", "")
write_sheet(mat, blocks, os.path.join(OUT, f"LCI_{mat}.xlsx"))

# =====================================================================================================
# CLT
# =====================================================================================================
mat = "clt"
sc, med = epd_set(["7688e355-8e03-4f2f-94dc-741052b78a02", "8c4eb262-9ae6-4ace-8f3d-0b06f2007f3e", "06c6f44f-dc14-4095-8e3e-7e483eccf50c", "5c536009-b0a8-4539-86c2-c3b8247f7f1a"])
CL = "5f620b844187a2ff5e7fff0cfe67b7ba"
amt = 1 / 443.0
R.dec(mat, "D1", "yes", "market for cross-laminated timber", "",
      "ecoinvent CLT production (RER): sawn softwood dried (u=10 %) + 3.67 kg MUF + 3.29 kg PUR adhesive per m3 (443 kg wet mass) = 1.6 % adhesive; planed, no other constituent (0.016 kg ammonium sulfate per m3 is a process chemical). Same constituents as the input (softwood lamellas, 1-K PUR, MUF); the shares differ (input MUF 0.03 %).",
      "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=954a286e-36e6-4ceb-9ab9-ec4270b618aa",
      "search_ecoinvent.py 'cross laminated'; candidates: production CLT RER, RoW; market CLT RER, RoW; exchanges read with bw2data")
R.dec(mat, "D2", "yes", "market for cross-laminated timber", "", "Market dataset exists (covers A2).", "")
R.dec(mat, "D3", "RER", "", "", "market for cross-laminated timber exists for RER (rule 2; no Europe-w/o-CH market).", "")
R.dec(mat, "D4", "single variant", "", "", "Only one CLT variant per location; no glue-type variants.", "")
a13 = Block("A1–A3", mat, None, None, f"{mat}, A1–A3", f"{mat}, at factory gate")
a13.add(CL, amt, "D1 (D2-D4)", 1, comment=f"1 kg = {amt:.6g} m3 at wet mass 443 kg/m3")
a13.comment = "Exact match D1. "
finish_block_dqr(a13, [1])
R.ds(mat, "A1–A3", "finished product", CL, fmt(amt), rule="D1 (D2-D4)", TeR=1, search_terms="cross laminated",
     candidates="production CLT RER, RoW; market CLT RER, RoW", conversions="m3 = kg / 443 kg/m3 (property 'wet mass')")
t, per = gwp_of([(CL, amt)])
ratio = t / med
R.add("epd_check.csv", material_id=mat, check_id="CHECK 1", okobaudat_release=OBD, category="3.1.05 Brettschichtholzplatte (3 EPDs) + CLT EPD HASSLACHER filed under 3.1.04",
      epd_ids="; ".join(i["uuid"] for i in sc), n_epds=len(sc), epd_median=fmt(med, 4), our_gwp_fossil_a1a3=fmt(t, 4),
      ratio_to_median=fmt(ratio, 3), result="pass" if 0.5 <= ratio <= 1.5 else "fail",
      flag_units_mass="EPDs per m3, converted with each EPD's gross density (461-489 kg/m3); ours 1/443 m3 per kg",
      flag_dataset_state="TILLY solid wood panel is a 3-layer panel, kept because it is in the same OEKOBAU.DAT class", flag_indicator="GWP-fossil only",
      flag_machine_rows="no machine rows (exact match)", likely_reason="", wear_share_of_gwp_fossil_a1a3="not applicable (no machine rows)",
      route="exact", distance_to_median=fmt(abs(ratio - 1), 3), lci_kept="exact")
R.dec(mat, "CHECK 1", "yes" if 0.5 <= ratio <= 1.5 else "no", fmt(ratio, 3), "x median", f"Ours {t:.4f} vs median {med:.4f} of {len(sc)} EPDs ({OBD}). Close to the +50 % edge.", OBDL)
clt_res = dict(ours=t, med=med, ratio=ratio, n=len(sc))
common_decisions(mat, T1, True,
                 "Manufacturers found: DE Thuenen/German-average CLT EPD (OEKOBAU.DAT) and German producers; FR Piveteaubois (HEXAPLI CLT, Sainte-Florence); IT CLT EPD 'Brettsperrholz (Update)' IT in OEKOBAU.DAT (Rubner); ES Egoin (CLT, Basque Country). 4 of 5 countries.",
                 "DE https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=8c4eb262-9ae6-4ace-8f3d-0b06f2007f3e ; FR https://www.euwid-wood-products.com/news/wood-products/piveteau-bois-has-started-marketing-of-clt/ ; IT https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=06c6f44f-dc14-4095-8e3e-7e483eccf50c ; ES https://www.euwid-wood-products.com/news/wood-products/single/Artikel/egoin-aiming-to-boost-annual-clt-production-to-52000-m3.html",
                 None, True,
                 "CLT is delivered as wall/floor panels: even a small 1 m x 3 m x 0.06 m panel at 470.9 kg/m3 weighs 85 kg > 50 kg. Dimensions assumed (no panel size found: EUWID page paywalled); density from the input sheet.",
                 "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=954a286e-36e6-4ceb-9ab9-ec4270b618aa", True,
                 "34 wood, untreated: beams, planks", route34, "Solid wood",
                 [("softwood lamellas, incl. moisture", 0.99, "Wood", round(10.70 / 88.28, 4), "", "moisture = 10.70 % water / 88.28 % atro from the input note"),
                  ("adhesive, 1-K PUR", 0.0099, "Non-biogenic", "", "", ""), ("adhesive, MUF", 0.0003, "Non-biogenic", "", "", "")])
waste = [dict(label="CLT (product)", mass=1.0, ds=dict(
    landfill=(WOOD["landfill"], "W2", True, "No ecoinvent waste dataset for CLT; the product is 99 % softwood, Wood class of sheet waste_fallback: treatment of waste wood, untreated, sanitary landfill (CH) | proxy"),
    incineration=(WOOD["incineration"], "W2", True, "waste_fallback Wood class: treatment of waste wood, untreated, municipal incineration FAE (CH) | proxy"),
    recycling=(WOOD["recycling"], "W2", True, "waste_fallback Wood class: treatment of waste wood, post-consumer, sorting and shredding (CH) | proxy")))]
blocks, wt = tail(mat, a13, route34, True, False, True, waste, "", "")
write_sheet(mat, blocks, os.path.join(OUT, f"LCI_{mat}.xlsx"))

# =====================================================================================================
# SOFT WOOD FIBRE BOARD
# =====================================================================================================
mat = "soft_wood_fibre_board"
route55 = dict(landfill=0.05, incineration=0.85, recycling=0.10, reuse=0.0)
ss, med = epd_set(["1c22a17e-aca4-4126-9fde-f02c33aa741e", "77a553ca-357e-4910-b114-5aa912d4d0e2", "c91aa879-2826-4078-8bfa-baae349549cb", "5488d3f3-1e39-4a71-b357-ef605b65ed9c"])
FB = "082c9eb4b2f605fa370a6152b70b92f9"
amtfb = 1 / 157.7050342042623
CAT = "2.10.01 Daemmstoffe / Holzfasern / Holzfaserdaemmplatte (plates only; blow-in, flexible mat and loose shavings excluded)"
R.dec(mat, "D1", "no", "", "",
      "No soft-fibreboard dataset has only the input constituents (softwood fibres 94.5 %, PUR resin 4 %, paraffin 1.5 %). 'fibreboard production, soft, from wet & dry processes' (Europe w/o CH) also takes phenolic resin 0.44, latex 0.78, potato starch 1.27, vinyl acetate 0.77, nylon 6 0.65, aluminium sulfate 0.76, MDI 0.28, paraffin 1.82 kg per m3; 'without adhesives' (CH) has no PUR resin; 'latex bonded' (CH) is bonded with latex.",
      "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=40b5bfc6-83b6-43e3-8852-567822c56729",
      "search_ecoinvent.py 'fibreboard soft'; 'wood fibre'; exchanges read with bw2data. Candidates: production soft from wet & dry processes (Europe w/o CH, RoW, CA-QC); wet processes CH; latex bonded CH; without adhesives CH; markets RER/RoW")
R.dec(mat, "D1b", "yes", "market for fibreboard, soft", "",
      "Same product (soft fibreboard) and delivered state; main constituent is wood fibre in both. Differences vs input per kg product (market, 157.7 kg/m3): MDI binder 0.18 % (input PUR 4.0 %), phenolic resin 0.28 %, latex 0.49 %, potato starch 0.81 %, vinyl acetate 0.49 %, nylon 6 0.41 %, aluminium sulfate 0.48 %, paraffin 1.15 % (input 1.5 %).",
      "", "constituent shares computed from exchanges of production activity soft fibreboard, wet & dry processes")
R.dec(mat, "D2", "yes", "market for fibreboard, soft", "", "Market dataset exists.", "")
R.dec(mat, "D3", "RER", "", "", "market for fibreboard, soft exists for RER (rule 2).", "")
R.dec(mat, "D4", "market for fibreboard, soft", "", "",
      "At RER three variants: plain, latex bonded, without adhesives. None matches the dry-process PUR/paraffin state better (the plain one contains an MDI binder and paraffin); first A-Z is the plain one. Others recorded.", "")
t_appx, per = gwp_of([(FB, amtfb)])
ratio_a = t_appx / med
R.add("epd_check.csv", material_id=mat, check_id="CHECK 2", okobaudat_release=OBD, category=CAT, epd_ids="; ".join(i["uuid"] for i in ss),
      n_epds=len(ss), epd_median=fmt(med, 4), our_gwp_fossil_a1a3=fmt(t_appx, 4), ratio_to_median=fmt(ratio_a, 3),
      result="pass" if 0.5 <= ratio_a <= 1.5 else "fail", flag_units_mass="EPD per m3 converted with gross density 160-162 kg/m3; ours 1/157.7 m3 per kg",
      flag_dataset_state="ecoinvent mix of wet and dry processes (EPDs: 3 dry, 1 wet; two best wood entries have identical values)",
      flag_indicator="GWP-fossil only", flag_machine_rows="no machine rows (approximate match)",
      likely_reason="ecoinvent soft fibreboard uses coal and gas heat (394 MJ hard-coal heat + 143 MJ gas heat per m3) and Polish/German grid; EPD plants may use wood-fired heat (not verified).",
      wear_share_of_gwp_fossil_a1a3="not applicable (no machine rows)", route="approximate", distance_to_median=fmt(abs(ratio_a - 1), 3), lci_kept="")
R.dec(mat, "CHECK 2", "yes" if 0.5 <= ratio_a <= 1.5 else "no", fmt(ratio_a, 3), "x median", f"Ours {t_appx:.4f} vs median {med:.4f} of {len(ss)} EPDs; fail, build from scratch.", OBDL)
R.ds(mat, "A1–A3", "finished product (approximate)", FB, fmt(amtfb), rule="D1b (D2-D4)", TeR=2, search_terms="fibreboard soft; wood fibre",
     candidates="markets RER: plain, latex bonded, without adhesives; productions Europe w/o CH, RoW, CA-QC, CH",
     conversions="m3 = kg / 157.7 kg/m3 (property 'wet mass')",
     proxy="approximate match: differs by MDI/phenolic/latex/starch/vinyl acetate/nylon/Al sulfate (see decision D1b)")

# ---- build from scratch
FIB, PUR, PAR = "0f745572d5c532c4b19eaf202f8123b7", "387dfd53d03ac4257183b4557377608c", "2a6ee0cf5ef883afd641ac5e84a2aa7b"
comp = [("softwood fibres (fir/spruce)", 0.945, FIB,
         "D5 yes: wood chips are the state in which softwood enters the factory (sawmill chips); 'market for wood chips, dry, measured as dry mass' RER. Amount taken as 0.945 kg per kg as in the input (moisture not stated in the input note, see protocol_issues).", "wood chips", "yes"),
        ("PUR resin", 0.04, PUR,
         "D5 yes: 'market for polyurethane adhesive' GLO (only PUR product market besides foams; no European one: D3 rule 5 GLO). The real binder is pMDI; kept as PUR resin as named in the input.", "polyurethane", "yes"),
        ("paraffin", 0.015, PAR, "D5 yes: 'market for paraffin' GLO (only one).", "paraffin", "yes")]
for (n, a, c, ev, st, ans) in comp:
    R.dec(mat, f"D5: {n}", ans, act(c)["name"] + " | " + act(c)["location"], "", ev, "", step=f"search_ecoinvent.py '{st}'")
    R.ds(mat, "A1–A3", f"constituent: {n}", c, a, rule="D5 (PICK: market, D3 location)", TeR=3, search_terms=st,
         candidates=("market for wood chips, dry, measured as dry mass RER/RoW; wood chips from industry in production datasets" if "wood" in st else ("market polyurethane adhesive GLO; PU rigid foam RER; PU flexible foam RER; MDI RER" if "poly" in st else "market for paraffin GLO")))

# machine specification: (step, type, candidates, used, power, thr, M, L, found, source, link, conv, elec_kWh_per_kg, heat_kWh_per_kg, proxy, wear?)
BREF = "https://aida.ineris.fr/sites/aida/files/documents-bref/WBPbref2016.pdf"
DENS_MDF = ((0.76 + 1.37) / 2 / ((1.23 + 2.91) / 2) + ((0.12 + 0.26) / 2) / ((0.19 + 0.52) / 2)) / 2  # t dry fibre per m3 panel, implied by BREF Table 3.3
steps = {
    "defibration of chips": dict(typ="refiner / defibrator (dry process, MDF-type fibre)",
        cand="1) Andritz TX68 twin-disc refiner: motor up to 40,000 kW, 1,500 admt/d, 51.6 t (complete, but oversized); 2) Chinese MDF pressurised refiner listing: 3,000-3,550 kW, 13-18 t/h, no mass; 3) Valmet Evolution Defibrator: no kW, t/h or mass on page. Only 1 complete datasheet.",
        used="Energy: EU BREF Wood-based Panels 2016 Table 3.3 (refining, MDF dry process) because no datasheet gives an operating-point power/throughput pair; wear: Andritz TX68 (only complete mass + capacity)",
        power="", thr=62500, M=51600, L=100000,
        found="BREF refining: power 0.13-0.40 MWh/t dry fibre; heat 0.38-1.44 MWh/t dry fibre. Andritz TX68: 51.6 t (w/o feeding and motor), up to 1,500 admt/d.",
        src="EU BREF Wood-based Panels (2016) Table 3.3; Andritz TX68 datasheet",
        link=BREF + " ; https://www.Andritz.com/resource/blob/333956/59706257b8250fee1b49f013cf9cfc07/spectrum40-technews-refinertx68-data.pdf",
        conv="BREF midpoints: power (0.13+0.40)/2 = 0.265 MWh/t = 0.265 kWh/kg; heat (0.38+1.44)/2 = 0.91 MWh/t = 0.91 kWh/kg x 3.6 = 3.276 MJ/kg. Throughput 1,500 admt/d / 24 = 62.5 t/h = 62,500 kg/h. Machine life 20 y x 5,000 h/y = 100,000 h (assumption, no source gives life).",
        el=0.265, ht=0.91, proxy=True, wear=True),
    "hydrophobing with paraffin": dict(typ="wax / additive dosing unit (blow-line or mixer dosing)",
        cand="1) JBT ProDOSE wax dosing unit 2.2 kW (food-industry unit, no throughput, no mass); 2) Dieffenbacher EVOjet M 2.0 blow-line dosing: up to 48 t/h fibre, no kW, no mass; 3) Spraying Systems PanelSpray-WX (OSB wax): no figures. No complete candidate.",
        used="proxy: 2.2 kW dosing unit (JBT ProDOSE) over the line capacity of the Ziegler/Grenzebach dry-process line (6 t/h)",
        power=2.2, thr=6000, M="", L="",
        found="2.2 kW (3 hp); line capacity 6 t/h (expandable to 10 t/h)",
        src="JBT ProDOSE listing (directindustry); Global Insulation report on the naturheld Huetten plant",
        link="https://www.directindustry.com/prod/jbt-corporation/product-236433-2844379.html ; https://globalinsulation.com/news/1891-naturheld-s-huetten-wood-fibre-insulation-plant-ready-for-commercial-operations",
        conv="2.2 kW / 6,000 kg/h = 0.000367 kWh/kg", el=2.2 / 6000, ht=0, proxy=True, wear=False),
    "drying fibres": dict(typ="flash tube / tube dryer for wood fibre",
        cand="1) VetterTec tube bundle dryer: 3,200 kg/h water evaporation, 36,000 kg empty weight, no kW; 2) Dieffenbacher flash tube dryer (MDF/insulation fibre): >60 t/h b.d., no kW, no mass; 3) Haarslev tube bundle dryer: 500-2,000 kg/h, 7.5-22 kW installed, no heat, no mass. No complete candidate.",
        used="Energy: BREF Table 3.3 drying (MDF dry process); wear: VetterTec smallest tube bundle dryer",
        power="", thr=3200, M=36000, L=100000,
        found="BREF drying: power 0.04-0.21 MWh/t dry fibre; heat 0.74-1.45 MWh/t dry fibre. VetterTec: 3,200 kg/h evaporation, 36,000 kg.",
        src="EU BREF Wood-based Panels (2016) Table 3.3; VetterTec brochure",
        link=BREF + " ; https://acc.making.com/wp-content/uploads/2024/09/VetterTec_10254_brochure.pdf",
        conv="power (0.04+0.21)/2 = 0.125 kWh/kg; heat (0.74+1.45)/2 = 1.095 kWh/kg x 3.6 = 3.942 MJ/kg. Water evaporation rate (kg/h) used as processing rate for fibre from wet chips (about 1 kg water per kg dry fibre). Life 100,000 h (assumption).",
        el=0.125, ht=1.095, proxy=True, wear=True),
    "adding resin, forming the mat": dict(typ="blow-line / resin dosing and mat forming station",
        cand="1) Dieffenbacher EVOjet M 2.0 (resin dosing, 48 t/h, no kW/mass); 2) JBT ProDOSE 2.2 kW dosing unit; 3) Grenzebach board forming system (dosing bins, belt scales, prepress): no figures. No complete candidate; forming-station fan power not found.",
        used="proxy: dosing unit only, 2.2 kW over 6 t/h (as hydrophobing); forming station power not found, not included",
        power=2.2, thr=6000, M="", L="",
        found="2.2 kW; 6 t/h line capacity", src="as hydrophobing",
        link="https://www.directindustry.com/prod/jbt-corporation/product-236433-2844379.html ; https://www.grenzebach.com/en/company/references/detail/built-in-record-time-production-line-for-flexible-wood-fiber-insulation-boards/",
        conv="2.2 kW / 6,000 kg/h = 0.000367 kWh/kg", el=2.2 / 6000, ht=0, proxy=True, wear=False),
    "curing with steam-air mixture": dict(typ="continuous hot-air / steam-air curing oven (closest in BREF: MDF hot press)",
        cand="1) BREF MDF pressing (power 0.01-0.09, heat 0.1-0.32 MWh/m3 panel); 2) Siempelkamp pre-heater curing for dry-process insulation board: no figures; 3) patent oven 130-200 C: no figures. No datasheet.",
        used="proxy: BREF MDF pressing per m3 divided by the dry fibre per m3 implied by BREF Table 3.3",
        power="", thr="", M="", L="",
        found="BREF Table 3.2 MDF pressing: power 0.01-0.09 MWh/m3, heat 0.1-0.32 MWh/m3 of finished panel", src="EU BREF Wood-based Panels (2016) Tables 3.2 and 3.3", link=BREF,
        conv=f"midpoints: power 0.05 MWh/m3, heat 0.21 MWh/m3; divided by {DENS_MDF:.3f} t dry fibre per m3 (ratio per m3 to per t in Table 3.3) = {0.05/DENS_MDF:.4f} kWh/kg power, {0.21/DENS_MDF:.4f} kWh/kg heat x 3.6 = {0.21/DENS_MDF*3.6:.3f} MJ/kg",
        el=0.05 / DENS_MDF, ht=0.21 / DENS_MDF, proxy=True, wear=False),
    "cutting": dict(typ="panel saw / sizing saw",
        cand="1) Homag panel saw 13.5 kW main motor (no mass, no throughput); 2) Casadei Busellato AXO 300 9 kW (no mass, no throughput); 3) Felder 35-75 kW (no throughput). No complete candidate.",
        used="proxy: Homag saw 13.5 kW over the line capacity 6 t/h (saw runs at line speed)",
        power=13.5, thr=6000, M="", L="",
        found="13.5 kW main saw motor (50 Hz); line 6 t/h", src="Homag panel dividing overview (Hoechsmann); Global Insulation (line capacity)",
        link="https://wtp.hoechsmann.com/sr/lexikon/pdf/hom_paneldividing_overview_2017_en.pdf ; https://globalinsulation.com/news/1891-naturheld-s-huetten-wood-fibre-insulation-plant-ready-for-commercial-operations",
        conv="13.5 kW / 6,000 kg/h = 0.00225 kWh/kg", el=13.5 / 6000, ht=0, proxy=True, wear=False),
}
stepdef = [("defibration of chips", 1.0), ("hydrophobing with paraffin", 1.0), ("drying fibres", 1.0),
           ("adding resin, forming the mat", 1.0), ("curing with steam-air mixture", 1.0), ("cutting", 1.0)]
a13b = Block("A1–A3", mat, None, None, f"{mat}, A1–A3", f"{mat}, at factory gate")
weights = []
gitems = []
for n, a, c, *_ in comp:
    a13b.add(c, a, "D5 (PICK)", 3, comment="input amount kg per kg")
    weights.append(a); gitems.append((c, a))
wear_total = 0.0
for (s, kgp) in stepdef:
    S = steps[s]
    R.dec(mat, f"P1: {s}", "machine/energy from fallback source", f"{S['el']:.4g} kWh/kg el; {S['ht']:.4g} kWh/kg heat", "kWh per kg processed",
          f"Step note is not 'no energy'; {S['used']}.", S["link"].split(" ; ")[0])
    R.dec(mat, f"P2: {s}", "wear row" if S["wear"] else "no wear row", "", "",
          ("Machine mass and capacity of one datasheet found (see dataset_choices)." if S["wear"] else "No machine mass found for this step; wear row not written (negligible, see protocol_issues.md)."), S["link"].split(" ; ")[-1])
    tr = 4
    el_amt = kgp * S["el"]
    if el_amt > 0:
        a13b.add(ELEC, el_amt, "P1", tr, comment=f"{s}: {S['el']:.5g} kWh/kg x {kgp} kg processed; proxy (no complete datasheet triple)")
        weights.append(kgp); gitems.append((ELEC, el_amt))
        R.ds(mat, "A1–A3", f"processing: {s} (electricity)", ELEC, fmt(el_amt), rule="P1", proxy="proxy", TeR=tr,
             machine_type=S["typ"], machine_candidates=S["cand"], machine_used=S["used"], power_kW=S["power"], throughput_kg_per_h=S["thr"],
             values_as_found=S["found"], value_source=S["src"], value_link=S["link"], conversions=S["conv"], per_kg_processed=fmt(S["el"]),
             search_terms="web search for datasheets + EU BREF WBP 2016")
    if S["ht"] > 0:
        h_amt = kgp * S["ht"] * 3.6
        a13b.add(HEAT, h_amt, "P1", tr, comment=f"{s}: {S['ht']:.5g} kWh/kg x 3.6 x {kgp} kg processed; proxy")
        weights.append(kgp); gitems.append((HEAT, h_amt))
        R.ds(mat, "A1–A3", f"processing: {s} (heat)", HEAT, fmt(h_amt), rule="P1", proxy="proxy", TeR=tr,
             machine_type=S["typ"], machine_candidates=S["cand"], machine_used=S["used"], power_kW=S["power"], throughput_kg_per_h=S["thr"],
             values_as_found=S["found"], value_source=S["src"], value_link=S["link"], conversions=S["conv"], per_kg_processed=str(fmt(S["ht"] * 3.6)) + " MJ",
             search_terms="web search for datasheets + EU BREF WBP 2016")
    if S["wear"]:
        w = kgp * S["M"] / (S["thr"] * S["L"])
        a13b.add(MACH, w, "P2", tr, comment=f"{s}: M {S['M']} kg / (throughput {S['thr']} kg/h x life {S['L']} h) x {kgp}")
        weights.append(kgp); gitems.append((MACH, w)); wear_total += w
        R.ds(mat, "A1–A3", f"machine: {s}", MACH, fmt(w), rule="P2", proxy="proxy", TeR=tr, machine_type=S["typ"],
             machine_candidates=S["cand"], machine_used=S["used"].split("wear:")[-1] if "wear:" in S["used"] else S["used"], power_kW=S["power"], throughput_kg_per_h=S["thr"],
             machine_mass_kg=S["M"], machine_life_h=S["L"], values_as_found=S["found"], value_source=S["src"], value_link=S["link"],
             conversions=S["conv"], per_kg_processed=fmt(S["M"] / (S["thr"] * S["L"])))
    else:
        R.ds(mat, "A1–A3", f"machine: {s}", None, "", rule="P2", proxy="no row", TeR="", machine_type=S["typ"],
             machine_candidates=S["cand"], values_as_found="no machine mass found; no wear row written", per_kg_processed="not computed")
a13b.comment = "Built from scratch (constituents + BREF/proxy energy rows). "
dqr_b = finish_block_dqr(a13b, weights)
R.dec(mat, "CHECK", "yes", 1.0, "kg", "Material rows sum 0.945 + 0.040 + 0.015 = 1.000 kg, equal to the input constituents.", "")
t_b, per_b = gwp_of(gitems)
wear_share_b = sum(p for (c, _), p in zip(gitems, per_b) if c == MACH) / t_b
ratio_b = t_b / med
R.add("epd_check.csv", material_id=mat, check_id="CHECK 3", okobaudat_release=OBD, category=CAT, epd_ids="; ".join(i["uuid"] for i in ss),
      n_epds=len(ss), epd_median=fmt(med, 4), our_gwp_fossil_a1a3=fmt(t_b, 4), ratio_to_median=fmt(ratio_b, 3),
      result="pass" if 0.5 <= ratio_b <= 1.5 else "fail", flag_units_mass="as CHECK 2", flag_dataset_state="constituents: wood chips, PUR adhesive, paraffin",
      flag_indicator="GWP-fossil only", flag_machine_rows="all energy rows are BREF/vendor proxies (TeR 4); wear rows only for refiner and dryer",
      likely_reason="Heat (refining + drying + curing = 8.3 MJ/kg of natural gas heat) carries about half of the result; EPD plants may use wood-fired heat or CHP (not verified).",
      wear_share_of_gwp_fossil_a1a3=f"{wear_share_b:.4%}", route="built", distance_to_median=fmt(abs(ratio_b - 1), 3), lci_kept="")
R.dec(mat, "CHECK 3", "yes" if 0.5 <= ratio_b <= 1.5 else "no", fmt(ratio_b, 3), "x median", f"Ours {t_b:.4f} vs median {med:.4f}; fail, review.", OBDL)
dist_a, dist_b = abs(ratio_a - 1), abs(ratio_b - 1)
keep = "built" if dist_b < dist_a or (dist_b == dist_a and t_b < t_appx) else "approximate"
R.add("epd_check.csv", material_id=mat, check_id="REVIEW", okobaudat_release=OBD, category=CAT, epd_ids="; ".join(i["uuid"] for i in ss),
      n_epds=len(ss), epd_median=fmt(med, 4), our_gwp_fossil_a1a3=f"approximate {t_appx:.4f}; built {t_b:.4f}",
      ratio_to_median=f"approximate {ratio_a:.3f}; built {ratio_b:.3f}", result="flagged",
      flag_units_mass="per m3 -> per kg with the EPD gross density; moisture counted once in the product mass", flag_dataset_state="approximate: plain soft fibreboard market (wet+dry); built: dry-process constituents",
      flag_indicator="GWP-fossil only on both sides",
      flag_machine_rows="built: refining and drying carry most energy (BREF Table 3.3 midpoints), curing from BREF MDF pressing, dosing and saw from vendor kW over a 6 t/h line; all proxy",
      likely_reason="Both routes are about 1.7-1.9x the median: the median rests on 4 entries, two of which are the same best wood EPD (identical values), the others German generic or average datasets. No exact match existed. Cause not verified.",
      wear_share_of_gwp_fossil_a1a3=f"{wear_share_b:.4%}", route=keep, distance_to_median=f"approximate {dist_a:.3f}; built {dist_b:.3f}", lci_kept=keep)
R.dec(mat, "REVIEW", keep, f"approximate {dist_a:.3f} vs built {dist_b:.3f}", "distance to median", f"Both failed; the one closest to the median is kept ({keep}) and flagged.", OBDL)
sfb_res = dict(ours_built=t_b, ours_appx=t_appx, med=med, ratio_b=ratio_b, ratio_a=ratio_a, keep=keep, wear=wear_share_b, n=len(ss))
assert keep == "built"
common_decisions(mat, T1, True,
                 "Manufacturers found: DE GUTEX (Waldshut-Tiengen/Eschbach) and Ziegler/naturheld (Huetten/Grafenwoehr); FR STEICO Casteljaloux and Soprema Pavatex (Golbey, Chavelot); IT Renovo Bioedil (Iglesias, Sardinia). 3 of 5 countries.",
                 "DE https://www.grenzebach.com/en/company/references/detail/built-in-record-time-production-line-for-flexible-wood-fiber-insulation-boards/ ; FR https://steico.com/industry/about-steico/steico-today ; IT https://www.bimobject.com/uk/renovo-bioedil",
                 None, False,
                 "Boards are small formats: 1.2 m x 0.6 m x 0.06 m at 162 kg/m3 (ÖKOBAUDAT dry-process average) = 7 kg; even a 2.5 x 1.2 x 0.1 m board is 49 kg. Formats assumed, density sourced.",
                 "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=5488d3f3-1e39-4a71-b357-ef605b65ed9c", False,
                 "55 board material, clean", route55, "Wood panels",
                 [("softwood fibres (fir/spruce)", 0.945, "Wood", "", "", "moisture not given in the input, archetype default is used"),
                  ("PUR resin", 0.04, "Non-biogenic", "", "", ""), ("paraffin", 0.015, "Non-biogenic", "", "", "")],
                 flag="flagged: all checks failed, built LCI kept")
waste = [dict(label="softwood fibres (fir/spruce)", mass=0.945, ds=dict(
              landfill=(WOOD["landfill"], "W1", False, "treatment of waste wood, untreated, sanitary landfill: waste wood matches the wood fibre; CH (D3 rule 4)"),
              incineration=(WOOD["incineration"], "W1", False, "treatment of waste wood, untreated, municipal incineration FAE (CH)"),
              recycling=(WOOD["recycling"], "W1", False, "treatment of waste wood, post-consumer, sorting and shredding (CH)"))),
         dict(label="PUR resin", mass=0.04, ds=dict(
              landfill=(PURW["landfill"], "W1", False, "treatment of waste polyurethane, sanitary landfill (CH)"),
              incineration=(PURW["incineration"], "W1", False, "treatment of waste polyurethane, municipal incineration FAE (CH)"), recycling=None)),
         dict(label="paraffin", mass=0.015, ds=dict(
              landfill=(PLAST["landfill"], "W2", True, "No waste paraffin dataset; waste_fallback class 'Plastic, resin, binder, coating': treatment of waste plastic, mixture, sanitary landfill (CH) | proxy"),
              incineration=(PLAST["incineration"], "W2", True, "waste_fallback: treatment of waste plastic, mixture, municipal incineration FAE (CH) | proxy"), recycling=None))]
blocks, wt = tail(mat, a13b, route55, False, False, False, waste, "", "")
write_sheet(mat, blocks, os.path.join(OUT, f"LCI_{mat}.xlsx"))

# =====================================================================================================
# ALUMINIUM EXTRUSION
# =====================================================================================================
mat = "aluminium_extrusion"
routeAl = dict(landfill=0.03, incineration=0.03, recycling=0.94, reuse=0.0)
ids_al = ["3feca796-791b-46d3-8160-95ef243ffb9d", "c5982fc9-a486-4f00-82a2-59985d8ab196", "0cb92770-9007-48c6-bc03-466af8894419", "f9072c8d-516a-43fe-826e-8fbca55317e3",
          "ab2d3b4a-44f6-4fbf-baaa-7928391f0af0", "c7fce05e-9c84-4483-9478-cce575262437", "46ae537f-ddf7-49bb-8a30-f83d27941260", "6c0d5e07-1ff6-4a04-9d38-571c68c5602b",
          "76045543-d6d4-4549-8a84-dc2a7a2e2acd", "84d12825-bee9-4f48-832b-96dc7a2c2de0"]
sa, medA = epd_set(ids_al)
CATA = "4.3.02 Metalle / Aluminium / Aluminiumprofil (plain extruded profiles; facade/roof systems, panels, coated, anodised and 3 EMERUS entries with implausible values 14,277-42,401 per kg excluded)"
ALW_ = "38b174060ab1bc1ab84e81c0a75f7666"
R.dec(mat, "D1", "no", "", "",
      "ecoinvent has no extruded aluminium profile as a product: 'section bar extrusion, aluminium' (RER, RoW, GLO market) is the extrusion process only (0.013 kg alloy, 1.14 kWh, 2.7 MJ heat per kg) and takes the metal as an input; the finished profile with its alloy is not a dataset.",
      "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=b2cf3328-5507-4db1-a5c8-8cc0cea13729",
      "search_ecoinvent.py 'aluminium extrusion'; 'extruded aluminium' (0 hits); 'section bar extrusion'; impact extrusion datasets are cold impact extrusion of parts (not profiles)")
R.dec(mat, "D1b", "no", "", "", "Test 2 cannot hold: the only candidate is a process dataset whose reference product is the extrusion service, not a profile whose main constituent is aluminium alloy EN AW-6060. Answered no; build from scratch.", "", "same search")
R.dec(mat, "D5: aluminium alloy EN AW-6060", "yes", "market for aluminium, wrought alloy | GLO", "",
      "6060 is a wrought alloy. Candidates: market for aluminium, wrought alloy (GLO); aluminium ingot, primary, to aluminium, wrought alloy market (GLO); treatment of aluminium scrap, new/post-consumer, at remelter (RER, scrap only). No European market; D3 order gives GLO (rule 5) for a market, the scrap-only RER datasets are not the alloy market. The EPD billet is 70-80 % scrap (material_overview), not applied: the input gives only the alloy.",
      "", step="search_ecoinvent.py 'aluminium, wrought alloy'; 'aluminium alloy'")
R.ds(mat, "A1–A3", "constituent: aluminium alloy EN AW-6060", ALW_, 1.0, rule="D5 (PICK: market, D3 GLO)", TeR=3,
     search_terms="aluminium, wrought alloy; aluminium alloy", candidates="market for aluminium, wrought alloy GLO; aluminium ingot, primary, to aluminium, wrought alloy market GLO; treatment of aluminium scrap, new, at remelter RER/RoW; ...post-consumer, at remelter RER/RoW")
GUIDE = "https://aluminium-guide.com/en/kak-sekonomit-gaz-na-proizvodstve-alyuminievyx-profilej/"
DOE = "https://www.energy.gov/sites/prod/files/2016/04/f30/Aluminum%20Report.pdf"
# DOE derived electricity of extrusion
onsite_btu_lb = 2948
tot_onsite, offs = 2.64, 0.57   # TBtu, Table 3-2
elec_tbtu = offs / (10553 / 3412 - 1)
el_btu_lb = onsite_btu_lb * elec_tbtu / tot_onsite
el_kwh_kg = el_btu_lb / 3412 / 0.45359237
alsteps = [
    ("billet heating", dict(typ="gas-fired billet heating furnace (induction heater as alternative)",
        cand="A) gas-fired billet furnace, aluminium-guide.com: 175-215 kWh/t gas (mid 0.195 kWh/kg); B) induction preheater, EU CORDIS project: 171-178 kWh/t electricity (mid 0.1745); C) induction heater, DW Induction vendor: 240-280 kWh/t electricity (mid 0.260). Median of energy per kg = A (0.195). No datasheet with kW, kg/h and mass.",
        used="A) gas-fired billet furnace (median energy per kg of the three)", power="", thr="", M="", L="",
        found="175-215 kWh/t gas (billet heating furnace)", src="aluminium-guide.com gas saving techniques for 6xxx alloys (estimate for a scrap-to-profile line)",
        link=GUIDE + " ; https://cordis.europa.eu/project/id/EE.-00147-79/it ; https://dw-inductionheater.com/product/induction-aluminum-billet-preheat-furnaces-for-forging-extrusion-and-forming-applications",
        conv="midpoint 195 kWh/t / 1000 = 0.195 kWh/kg gas heat x 3.6 = 0.702 MJ/kg", el=0, ht=0.195)),
    ("extrusion", dict(typ="direct hydraulic extrusion press (plant electricity incl. pumps, stretcher, saw)",
        cand="Press datasheets: Youngstown 1650T 2x132 kW (no output, no mass); Schloemann-Siemag 1250T 3x200 kW (no output, no mass); Jindal 750 UST 160 kW (no output, no mass). None gives kg/h and mass. Fallback: US DOE bandwidth study, extrusion sub-area.",
        used="US DOE aluminium bandwidth study, Table 3-2, extrusion: electricity share of 2,948 Btu/lb onsite", power="", thr="", M="", L="",
        found="Extrusion: onsite 2,948 Btu/lb; 2.64 TBtu onsite, offsite losses 0.57 TBtu (10,553 Btu/kWh primary)", src="US DOE, Bandwidth Study on Energy Use and Potential Energy Saving Opportunities in U.S. Aluminum Manufacturing (2016)",
        link=DOE,
        conv=f"electricity onsite = 0.57 / (10,553/3,412 - 1) = {elec_tbtu:.3f} TBtu of 2.64 TBtu = {elec_tbtu/tot_onsite:.1%}; x 2,948 Btu/lb = {el_btu_lb:.0f} Btu/lb = {el_kwh_kg:.3f} kWh/kg. The fuel share (US average, 1.7 kWh/kg) is not used: billet heating and ageing take their fuel from the EU figures",
        el=el_kwh_kg, ht=0)),
    ("ageing oven", dict(typ="gas-fired batch ageing oven",
        cand="A) ageing oven, aluminium-guide.com: 75-85 kWh/t gas (mid 0.080); B) Wawick twin-chamber electric: 40.5 kW per oven, 1,285 kg net load, 5 h cycle assumed from the guide = 0.158 kWh/kg; C) 24 kW electric oven, 2,000 kg load, 5 h = 0.060 kWh/kg. Median = A (0.080). No datasheet gives mass.",
        used="A) gas-fired ageing oven (median energy per kg)", power="", thr="", M="", L="",
        found="75-85 kWh/t gas (ageing oven)", src="aluminium-guide.com; Wawick listing (machineseeker); 24 kW oven listing",
        link=GUIDE + " ; https://www.machineseeker.nz/seco%2Fwawick-sdbf-24.16.30%2F600e/i-21201050 ; https://scarletalloys.pages.dev/products/industrial-oven/io-aging1-aluminium-ageing-oven",
        conv="midpoint 80 kWh/t / 1000 = 0.080 kWh/kg gas heat x 3.6 = 0.288 MJ/kg; candidates B and C: kW x 5 h / kg load", el=0, ht=0.080)),
    ("cutting", dict(typ="aluminium profile double-mitre saw",
        cand="Rongqi 2x1.5 kW, 1,800 kg; Schueco PDG Twin 2x2.2 kW, 480 kg; Mecal SW453 2x2.2 kW, about 1,700 kg; Schtec 3 kW, 430 kg. All lack throughput in kg/h. Cutting is part of the extrusion plant electricity from the DOE study.",
        used="no separate rows: sawing is inside the DOE extrusion-plant electricity of step 'extrusion' (avoid double counting)", power="", thr="", M="", L="",
        found="saw motor 2x1.5 to 2x2.2 kW; no kg/h", src="alcircle (Rongqi), Schueco, Mecal, Schtec listings",
        link="https://www.alcircle.com/biz/rongqi-machinery-products/18223/aluminium-double-mitre-saw ; https://www.schueco.com/in/fabricators/metal-fabrication-machines/saws", conv="", el=0, ht=0)),
]
a13c = Block("A1–A3", mat, None, None, f"{mat}, A1–A3", f"{mat}, at factory gate")
a13c.add(ALW_, 1.0, "D5 (PICK)", 3, comment="input amount kg per kg (no losses stated)")
weights = [1.0]; gitems = [(ALW_, 1.0)]
for s, S in alsteps:
    R.dec(mat, f"P1: {s}", "fallback source" if S["el"] or S["ht"] else "no rows", f"{S['el']:.4g} kWh/kg el; {S['ht']:.4g} kWh/kg heat", "kWh per kg processed",
          S["used"] + ". No machine datasheet gives power and throughput at the same operating point.", S["link"].split(" ; ")[0])
    R.dec(mat, f"P2: {s}", "no wear row", "", "", "No datasheet gives machine mass together with throughput for the type; wear row not written (see protocol_issues.md).", S["link"].split(" ; ")[-1])
    if S["el"]:
        a13c.add(ELEC, S["el"], "P1", 4, comment=f"{s}: {S['el']:.4g} kWh/kg x 1 kg processed (proxy/fallback)")
        weights.append(1.0); gitems.append((ELEC, S["el"]))
        R.ds(mat, "A1–A3", f"processing: {s} (electricity)", ELEC, fmt(S["el"]), rule="P1", proxy="proxy", TeR=4, machine_type=S["typ"],
             machine_candidates=S["cand"], machine_used=S["used"], values_as_found=S["found"], value_source=S["src"], value_link=S["link"],
             conversions=S["conv"], per_kg_processed=fmt(S["el"]), search_terms="web search for datasheets; US DOE bandwidth study")
    if S["ht"]:
        h = S["ht"] * 3.6
        a13c.add(HEAT, h, "P1", 4, comment=f"{s}: {S['ht']:.4g} kWh/kg x 3.6 x 1 kg processed (fallback)")
        weights.append(1.0); gitems.append((HEAT, h))
        R.ds(mat, "A1–A3", f"processing: {s} (heat)", HEAT, fmt(h), rule="P1", proxy="proxy", TeR=4, machine_type=S["typ"],
             machine_candidates=S["cand"], machine_used=S["used"], values_as_found=S["found"], value_source=S["src"], value_link=S["link"],
             conversions=S["conv"], per_kg_processed=str(fmt(h)) + " MJ", search_terms="web search for datasheets; aluminium-guide.com")
    if not (S["el"] or S["ht"]):
        R.ds(mat, "A1–A3", f"processing: {s} (electricity)", None, "", rule="P1", proxy="no row", TeR="", machine_type=S["typ"],
             machine_candidates=S["cand"], machine_used=S["used"], values_as_found=S["found"], value_source=S["src"], value_link=S["link"],
             conversions="no separate row", per_kg_processed="0")
    R.ds(mat, "A1–A3", f"machine: {s}", None, "", rule="P2", proxy="no row", TeR="", machine_type=S["typ"], machine_candidates=S["cand"],
         values_as_found="no machine mass with throughput found; no wear row", per_kg_processed="not computed")
a13c.comment = "Built from scratch (alloy + fallback energy rows). "
finish_block_dqr(a13c, weights)
R.dec(mat, "CHECK", "yes", 1.0, "kg", "Material rows sum 1.000 kg aluminium alloy, equal to the input.", "")
t_c, per_c = gwp_of(gitems)
ratio_c = t_c / medA
R.add("epd_check.csv", material_id=mat, check_id="CHECK 3", okobaudat_release=OBD, category=CATA, epd_ids="; ".join(i["uuid"] for i in sa),
      n_epds=len(sa), epd_median=fmt(medA, 4), our_gwp_fossil_a1a3=fmt(t_c, 4), ratio_to_median=fmt(ratio_c, 3),
      result="pass" if 0.5 <= ratio_c <= 1.5 else "fail", flag_units_mass="EPDs are per kg",
      flag_dataset_state="Several EPDs are low-carbon / recycled-content profiles (1.9-4.5 kg CO2e/kg); the input alloy is the ecoinvent global wrought-alloy market (mostly primary)",
      flag_indicator="GWP-fossil only", flag_machine_rows="energy rows are fallback figures (gas furnace, ageing oven, DOE electricity); no wear rows",
      likely_reason="The alloy market (12.8 kg CO2e/kg) is the whole result; EPD profiles use 70-100 % scrap or hydropower primary metal. The GDA EPD named in the input sheet has 1.92 kg CO2e/kg.",
      wear_share_of_gwp_fossil_a1a3="not computed (no wear rows: no machine mass with throughput found)", route="built", distance_to_median=fmt(abs(ratio_c - 1), 3), lci_kept="")
R.dec(mat, "CHECK 3", "yes" if 0.5 <= ratio_c <= 1.5 else "no", fmt(ratio_c, 3), "x median", f"Ours {t_c:.4f} vs median {medA:.4f} of {len(sa)} EPDs; fail, review.", OBDL)
R.add("epd_check.csv", material_id=mat, check_id="REVIEW", okobaudat_release=OBD, category=CATA, epd_ids="; ".join(i["uuid"] for i in sa),
      n_epds=len(sa), epd_median=fmt(medA, 4), our_gwp_fossil_a1a3=f"built {t_c:.4f}", ratio_to_median=f"built {ratio_c:.3f}", result="flagged",
      flag_units_mass="per kg on both sides", flag_dataset_state="no exact or approximate match existed (D1, D1b no), only the built LCI was tried",
      flag_indicator="GWP-fossil only", flag_machine_rows="built: billet heating gas 0.195 kWh/kg, ageing gas 0.080 kWh/kg, press electricity 0.196 kWh/kg; sawing inside press figure; no wear",
      likely_reason="Alloy market is mostly primary aluminium; EPD median is pulled down by low-carbon and recycled profiles. Energy rows are only 1 % of the result.",
      wear_share_of_gwp_fossil_a1a3="not computed", route="built", distance_to_median=fmt(abs(ratio_c - 1), 3), lci_kept="built")
R.dec(mat, "REVIEW", "built", f"distance {abs(ratio_c-1):.3f}", "distance to median", "Only one LCI was tried; it is kept and flagged.", OBDL)
al_res = dict(ours=t_c, med=medA, ratio=ratio_c, n=len(sa))
common_decisions(mat, T1, True,
                 "Manufacturers found: DE Hydro Extrusion Offenburg; FR Hydro Extrusions (Luce, Albi, Chateauroux, Puget-sur-Argens); IT Metra (and Hydro Feltre); ES Cortizo (Padron) and Exlabesa. 4 of 5 countries.",
                 "DE https://new.shapesbyhydro.com/en/global/about-hydro/hydro-worldwide/europe/germany/offenburg/hydro-extrusion-offenburg-gmbh ; FR/IT/ES https://www.alcircle.com/news/europe-holds-10-of-global-aluminium-extrusion-demand-supported-by-germanys-constellium-frances-hydro-extrusions-italys-metra-121201",
                 None, False,
                 "Profiles are cut to 6-6.5 m; typical window/facade profile 1-5 kg/m gives 6-33 kg per piece, below 50 kg. Section masses assumed (no datasheet read).",
                 "https://www.oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?lang=en&uuid=b2cf3328-5507-4db1-a5c8-8cc0cea13729", False,
                 "4 aluminium profiles, sheets", routeAl, "Aluminium",
                 [("aluminium alloy EN AW-6060", 1.0, "Non-biogenic", "", "", "")], flag="flagged: check 3 failed, built LCI kept")
waste = [dict(label="aluminium alloy EN AW-6060", mass=1.0, ds=dict(
    landfill=(ALW["landfill"], "W1", False, "treatment of waste aluminium, sanitary landfill (CH; no European dataset, D3 rule 4)"),
    incineration=(ALW["incineration"], "W1", False, "treatment of waste aluminium, municipal incineration (Europe without Switzerland, D3 rule 1)"),
    recycling=None))]
blocks, wt = tail(mat, a13c, routeAl, False, False, False, waste, "", "")
write_sheet(mat, blocks, os.path.join(OUT, f"LCI_{mat}.xlsx"))

R.write()
json.dump(dict(glulam=glulam_res, clt=clt_res, sfb=sfb_res, al=al_res, dens_mdf=DENS_MDF, el_kwh_kg=el_kwh_kg), open(os.path.join(OUT, "work", "results.json"), "w"), indent=1, default=float)
print(json.dumps(dict(glulam=glulam_res, clt=clt_res, sfb=sfb_res, al=al_res, dens=DENS_MDF, al_el=el_kwh_kg), indent=1, default=float))
