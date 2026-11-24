import csv, os, json, sys
sys.path.insert(0, os.path.dirname(__file__))
from bwh import *
from data import *
import openpyxl
from openpyxl.styles import Font

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ECODB = "ecoinvent-3.12-cutoff"
ORDER = ['RER', 'Europe without Switzerland', 'DE', 'FR', 'IT', 'ES', 'NL', 'AT', 'SE', 'FI', 'PL', 'CH', 'GLO', 'RoW']
_cache = {}


def gwp1(a):
    if a.key not in _cache:
        l = bc.LCA({a: 1}, M); l.lci(); l.lcia(); _cache[a.key] = l.score
    return _cache[a.key]


def pick(name, loc, ref):
    r = [a for a in DB if a['name'] == name and a['location'] == loc and a['reference product'] == ref]
    assert len(r) == 1, (name, loc, ref, len(r)); return r[0]


def pick_by_order(name, ref):
    c = [a for a in DB if a['name'] == name and a['reference product'] == ref]
    assert c, (name, ref)
    def k(a): return ORDER.index(a['location']) if a['location'] in ORDER else 99
    return sorted(c, key=k)[0]


def ger(loc):
    if loc in ('RER', 'Europe without Switzerland'): return 1
    if loc in ('DE', 'FR', 'IT', 'ES', 'NL', 'AT', 'SE', 'FI', 'PL', 'CH'): return 2
    if loc == 'GLO': return 3
    if loc == 'RoW': return 4
    return 5


DEC, DSC, EPD, CFF, BIO, ISS = [], [], [], [], [], []


def dec(mid, qid, answer, value="", unit="", evidence="", link="", step=""):
    DEC.append(dict(run_id=RUN, material_id=mid, question_id=qid, answer=answer, value=value, unit=unit, evidence=evidence, source_link=link, search_step=step, date=DATE))


def dsc(mid, module, purpose, **k):
    r = dict(run_id=RUN, material_id=mid, module=module, row_purpose=purpose, ecoinvent_version="3.12 cut-off", search_date=DATE)
    r.update(k); DSC.append(r)


def sig(x, n=3):
    if x == 0: return 0
    return float(f"{x:.{n}g}")


def machine_rows(mid, step, kgp, m):
    """returns list of exchange dicts for one step"""
    rows = []
    elec = m.get('elec_per_kg')
    if elec is None and m.get('power_kW'): elec = m['power_kW'] / m['throughput']
    heat = m.get('heat_per_kg', 0.0) or 0.0
    elec = elec or 0.0
    wear_per_kg = m['M'] / (m['throughput'] * m['L'])
    ter = 4 if m.get('proxy') else 3
    common = dict(machine_type=m['machine_type'], machine_candidates=m['candidates'], machine_used=m['used'],
                  power_kW=sig(m['power_kW']) if m.get('power_kW') else "n/a (energy per kg from source)",
                  throughput_kg_per_h=sig(m['throughput']), machine_mass_kg=sig(m['M']), machine_life_h=sig(m['L']),
                  values_as_found=m['found'], value_source=m.get('fallback', "machine datasheet / listing"), value_link=m['link'], conversions=m['conv'])
    if elec > 0:
        rows.append(dict(purpose=f"processing: {step} (electricity)", act=ELEC, amount=kgp * elec, unit="kilowatt hour", rule="P1 (fixed_settings electricity)", TeR=ter, proxy=m.get('proxy'), mach=dict(common, per_kg_processed=f"{sig(elec)} kWh/kg"), mod="A1–A3"))
    if heat > 0:
        rows.append(dict(purpose=f"processing: {step} (heat)", act=HEAT, amount=kgp * heat, unit="megajoule", rule="P1 (fixed_settings heat)", TeR=ter, proxy=m.get('proxy'), mach=dict(common, per_kg_processed=f"{sig(heat)} MJ/kg"), mod="A1–A3"))
    rows.append(dict(purpose=f"machine: {step}", act=MACH, amount=kgp * wear_per_kg, unit="kilogram", rule="P2 (fixed_settings machine)", TeR=ter, proxy=m.get('proxy'), mach=dict(common, per_kg_processed=f"{wear_per_kg:.3g} kg machine/kg"), mod="A1–A3"))
    return rows


def build(mid, d):
    res = dict(mid=mid, d=d)
    # ---------- A1-A3 built ----------
    rows = []
    for (nm, amt, an, loc, ref, rule, ter, prox, terms, cands) in d['constituents']:
        rows.append(dict(purpose=f"constituent: {nm}", act=(an, loc, ref), amount=amt, unit="kilogram", rule=rule, TeR=ter, proxy=bool(prox), terms=terms, cands=cands, mod="A1–A3", cons=nm))
    for (sn, kgp, m, mode) in d['steps']:
        if mode == 'machine': rows += machine_rows(mid, sn, kgp, m)
    for r in rows:
        a = pick(*r['act']); r['bw'] = a; r['gwp'] = gwp1(a) * r['amount']
        r['GeR'] = ger(a['location']); r['TiR'] = 1; r['DQR'] = round((r['TeR'] + r['GeR'] + r['TiR']) / 3, 2)
    res['a13'] = rows
    res['a13_gwp'] = sum(r['gwp'] for r in rows)
    res['wear_gwp'] = sum(r['gwp'] for r in rows if r['purpose'].startswith('machine:'))
    res['wear_share'] = res['wear_gwp'] / res['a13_gwp']
    # approx (gypsum)
    if 'approx' in d:
        a = pick(*d['approx']); res['approx_bw'] = a; res['approx_gwp'] = gwp1(a)
    return res


def a4_rows(arch):
    if arch == 'national': return [("lorry", LORRY, 0.15)]
    if arch == 'eu': return [("lorry", LORRY, 1.5), ("sea", SEA, 0.1)]
    raise


DIST = dict(landfill=50, incineration=100, recycling=50, reuse=50)


def main():
    results = {}
    for mid, d in MATERIALS.items():
        r = build(mid, d); results[mid] = r
        nm = d['name']
        # ------------ decisions: D1 .. ------------
        dec(mid, "D1", d['d1'][0], "", "", d['d1'][1], d['d1'][2], "search_ecoinvent.py: " + ("; ".join(["hempcrete", "hemp"]) if mid == 'hempcrete' else "gypsum --field product; plasterboard" if mid == 'gypsum_board' else "flat glass; toughened; tempering" if mid == 'toughened_glass' else "glass fabric; ptfe; polytetrafluoroethylene; fabric --field product"))
        # CHECK 1 not reached
        dec(mid, "D1b", d['d1b'][0], r.get('approx_bw')['name'] + " [GLO]" if 'approx_bw' in r else "", "", d['d1b'][1], d['d1b'][2])
        if 'approx_bw' in r:
            dec(mid, "D2", "yes", "market for gypsum plasterboard", "", "Market dataset exists (market first).", "")
            dec(mid, "D3", "GLO", "", "", "Only market location is GLO (a market, not a market group; production is CH/RoW). D2 market-first decides.", "")
            dec(mid, "D4", "no variants", "", "", "One dataset for this product and location.", "")
            dsc(mid, "A1–A3", "finished product (approximate)", search_terms="gypsum --field product; plasterboard", candidates_considered="market for gypsum plasterboard GLO; gypsum plasterboard production CH, RoW; gypsum fibreboard (different product)",
                chosen_activity=r['approx_bw']['name'], reference_product=r['approx_bw']['reference product'], location="GLO", unit="kilogram", amount=1, database=ECODB, rule_applied="D1b/D2/D3 (tried; failed CHECK 2, not kept)", proxy="",
                TeR=2, GeR=3, TiR=1, values_as_found=f"GWP-fossil A1-A3 {r['approx_gwp']:.3g} kg CO2e/kg; differences: extra glass fibre 0.016 %, silicone 0.013 %, surfactant 1e-5, corrugated board 4.8 % vs recycled paper 3.5 %, starch 0.29 % vs additives 3.5 %; stucco 0.811 vs gypsum 0.93 (water of crystallisation)")
        # ------------ D5 etc ------------
        for x in r['a13']:
            if x['purpose'].startswith('constituent:'):
                nmc = x['cons']
                dec(mid, f"D5: {nmc}", "no" if x['proxy'] else "yes", x['bw']['name'] + f" [{x['bw']['location']}]", "", x['rule'] + ". Candidates: " + x['cands'], "", "search_ecoinvent.py: " + x['terms'])
                dsc(mid, "A1–A3", x['purpose'], search_terms=x['terms'], candidates_considered=x['cands'], chosen_activity=x['bw']['name'], reference_product=x['bw']['reference product'], location=x['bw']['location'], unit="kilogram",
                    amount=x['amount'], database=ECODB, rule_applied=x['rule'], proxy="proxy" if x['proxy'] else "", TeR=x['TeR'], GeR=x['GeR'], TiR=1)
        for (sn, kgp, m, mode) in d['steps']:
            if mode == 'noenergy':
                dec(mid, f"P1: {sn}", "no energy", "", "", "Note of the step in input starts with 'no energy' (no heat input, IsoHemp): no rows, no machine row.", "")
                dec(mid, f"P2: {sn}", "no row", "", "", "Step has no energy rows.", "")
                continue
            elec = m.get('elec_per_kg') if m.get('elec_per_kg') is not None else (m['power_kW'] / m['throughput'] if m.get('power_kW') else 0)
            heat = m.get('heat_per_kg', 0) or 0
            dec(mid, f"P1: {sn}", m['used'], f"{sig(elec)} kWh/kg; {sig(heat)} MJ/kg", "per kg processed", f"Machine type: {m['machine_type']}. Candidates: {m['candidates']}. Values: {m['found']}", m['link'])
            wear = m['M'] / (m['throughput'] * m['L'])
            dec(mid, f"P2: {sn}", f"{wear:.3g}", "kg machine per kg processed", "", f"M {sig(m['M'])} kg, throughput {sig(m['throughput'])} kg/h, L {sig(m['L'])} h (same machine as P1)", m['link'])
        for x in r['a13']:
            if x['purpose'].startswith(('processing', 'machine')):
                m = x['mach']
                dsc(mid, "A1–A3", x['purpose'], chosen_activity=x['bw']['name'], reference_product=x['bw']['reference product'], location=x['bw']['location'], unit=x['unit'],
                    amount=x['amount'], database=ECODB, rule_applied=x['rule'], proxy="proxy" if x['proxy'] else "", TeR=x['TeR'], GeR=x['GeR'], TiR=1,
                    machine_type=m['machine_type'], machine_candidates=m['machine_candidates'], machine_used=m['machine_used'], power_kW=m['power_kW'], throughput_kg_per_h=m['throughput_kg_per_h'],
                    machine_mass_kg=m['machine_mass_kg'], machine_life_h=m['machine_life_h'], values_as_found=m['values_as_found'], value_source=m['value_source'], value_link=m['value_link'], conversions=m['conversions'], per_kg_processed=m['per_kg_processed'])
        # mass check
        ssum = sum(c[1] for c in d['constituents'])
        dec(mid, "CHECK", "yes", f"{ssum:.3f}", "kg", f"Material rows sum to {ssum:.3f} kg, equal to the constituent masses in the input.", "")
        # ------------ EPD checks ------------
        e = d['epd']
        base = dict(run_id=RUN, material_id=mid, wear_share_of_gwp_fossil_a1a3=f"{r['wear_share']:.3%}")
        gw = r['a13_gwp']
        if mid == 'gypsum_board':
            med = e['median']; ra = r['approx_gwp'] / med
            EPD.append(dict(base, check_id="CHECK 2", okobaudat_release=e['release'], category=e['category'], epd_ids=e['ids'], n_epds=e['n'], epd_median=f"{med:.3f}", our_gwp_fossil_a1a3=f"{r['approx_gwp']:.3g}", ratio_to_median=f"{ra:.2f}",
                            result="fail", flag_units_mass="m2 board converted with 10 kg/m2 (EPD)", flag_dataset_state="market GLO plasterboard", flag_indicator="GWP-fossil both sides", flag_machine_rows="n/a (dataset)",
                            likely_reason="ecoinvent board 0.36 kg/kg vs EPD 0.157: ecoinvent uses stucco 0.811 kg and heat 1.3 MJ + RoW supply chain; EPD from German producers; "+e['note'], wear_share_of_gwp_fossil_a1a3="n/a", route="approximate", distance_to_median=f"{abs(ra-1):.2f}", lci_kept=""))
            rb = gw / med
            EPD.append(dict(base, check_id="CHECK 3", okobaudat_release=e['release'], category=e['category'], epd_ids=e['ids'], n_epds=e['n'], epd_median=f"{med:.3f}", our_gwp_fossil_a1a3=f"{gw:.3g}", ratio_to_median=f"{rb:.2f}",
                            result="fail", flag_units_mass="10 kg/m2", flag_dataset_state="constituents in state entering the factory; calcining as explicit step", flag_indicator="GWP-fossil both sides", flag_machine_rows="all steps proxy or vendor figure (see dataset_choices)",
                            likely_reason="Drying heat (Watlow whole-plant low value) and the starch proxy (1.54 kg CO2e/kg x 3.5 %) dominate; EPD plants likely use less heat per kg board.", route="built", distance_to_median=f"{abs(rb-1):.2f}", lci_kept=""))
            da, db_ = abs(ra - 1), abs(rb - 1)
            kept = "built" if db_ <= da else "approximate"
            if kept != "built": raise SystemExit("approximate kept: not implemented")
            EPD.append(dict(base, check_id="REVIEW", okobaudat_release=e['release'], category=e['category'], epd_ids=e['ids'], n_epds=e['n'], epd_median=f"{med:.3f}", our_gwp_fossil_a1a3=f"approx {r['approx_gwp']:.3g}; built {gw:.3g}", ratio_to_median=f"approx {ra:.2f}; built {rb:.2f}",
                            result="flagged", flag_units_mass="ok", flag_dataset_state="ok", flag_indicator="ok", flag_machine_rows="drying heat dominates (4.5 MJ/kg); proxies in forming, cutting",
                            likely_reason=f"Distances {da:.2f} (approximate) vs {db_:.2f} (built): built kept (closer). Both about 2.2-2.3x the single EPD read; a one-EPD median and the heat/starch proxies explain the gap.", route="built", distance_to_median=f"{db_:.2f}", lci_kept="built (flagged)"))
            dec(mid, "CHECK 2", "no", f"{ra:.2f}", "x median", "Approximate match fails: outside 0.5-1.5x of 0.157.", e['link'])
            dec(mid, "CHECK 3", "no", f"{rb:.2f}", "x median", "Built LCI outside 0.5-1.5x.", e['link'])
            dec(mid, "REVIEW", "built", f"approx {da:.2f} vs built {db_:.2f}", "distance", "Built LCI is closer to the median: kept and flagged.", e['link'])
            r['kept'] = 'built'; r['flag'] = 'review: all routes failed'
        elif mid == 'toughened_glass':
            med = e['median']; rb = gw / med
            EPD.append(dict(base, check_id="CHECK 3", okobaudat_release=e['release'], category=e['category'], epd_ids=e['ids'], n_epds=e['n'], epd_median=f"{med:.3f}", our_gwp_fossil_a1a3=f"{gw:.3g}", ratio_to_median=f"{rb:.2f}",
                            result="fail", flag_units_mass="3.46 kg CO2e per m2 per mm / 2.5 kg per m2 per mm", flag_dataset_state="batch constituents; melt as heat row", flag_indicator="EPD value is GWP total (A1 version, no fossil split); ours fossil", flag_machine_rows="melting heat 5 MJ/kg (low end of BREF range), tempering 0.49 kWh/kg",
                            likely_reason="Protocol has no row for process CO2 from carbonates in the melt (~0.17 kg CO2/kg), melt heat at low end, no electricity for melt/float line; EPD is a different version (A1) from one source.", route="built", distance_to_median=f"{abs(rb-1):.2f}", lci_kept=""))
            EPD.append(dict(base, check_id="REVIEW", okobaudat_release=e['release'], category=e['category'], epd_ids=e['ids'], n_epds=e['n'], epd_median=f"{med:.3f}", our_gwp_fossil_a1a3=f"built {gw:.3g}", ratio_to_median=f"built {rb:.2f}",
                            result="flagged", flag_units_mass="ok", flag_dataset_state="ok (no toughened glass dataset in ecoinvent)", flag_indicator="total vs fossil (EPD A1 version)", flag_machine_rows="tempering and melting carry the energy; machine mass for both assumed",
                            likely_reason="Only the built LCI was tried (D1 and D1b no), so it is kept and flagged; see CHECK 3.", route="built", distance_to_median=f"{abs(rb-1):.2f}", lci_kept="built (flagged)"))
            dec(mid, "CHECK 3", "no", f"{rb:.2f}", "x median", "Built LCI below 0.5x of the median (1.384 per kg).", e['link'])
            dec(mid, "REVIEW", "built", f"{abs(rb-1):.2f}", "distance", "Only one route tried; kept and flagged.", e['link'])
            r['kept'] = 'built'; r['flag'] = 'review: check 3 failed'
        else:
            dec(mid, "CHECK 3", "no check possible", f"{gw:.3g}", "kg CO2e fossil/kg", "No ÖKOBAUDAT / EN 15804+A2 dataset for this product in material_overview ('no ÖKOBAUDAT dataset found').", "")
            EPD.append(dict(base, check_id="CHECK 3", okobaudat_release="n/a", category="none found", epd_ids="", n_epds=0, epd_median="", our_gwp_fossil_a1a3=f"{gw:.3g}", ratio_to_median="", result="no check possible",
                            flag_units_mass="", flag_dataset_state="", flag_indicator="", flag_machine_rows="", likely_reason="No EPD in ÖKOBAUDAT per material_overview; source EPDs (IsoHemp / Sheerfill) are outside the check.", route="built", distance_to_median="", lci_kept="built"))
            r['kept'] = 'built'; r['flag'] = ''
        # ------------ A4 ------------
        link1 = d['t1'][2]
        dec(mid, "A4 · T1", d['t1'][0], "", "", d['t1'][1], link1)
        dec(mid, "A4 · T2", d['t2'][0], "", "", d['t2'][1], d['t2'][2])
        if d['t3']: dec(mid, "A4 · T3", d['t3'][0], "", "", d['t3'][1], d['t3'][2])
        a4 = a4_rows(d['archetype'])
        for lab, act, tkm in a4:
            a = pick(*act)
            dsc(mid, "A4", f"A4 {lab}", chosen_activity=a['name'], reference_product=a['reference product'], location=a['location'], unit="ton kilometer", amount=tkm, database=ECODB, rule_applied="A4 archetype " + d['archetype'], TeR=1, GeR=ger(a['location']), TiR=1,
                values_as_found=("lorry 150 km (NMD 2020 §2.6.3.6)" if d['archetype'] == 'national' else "lorry 1,500 km + container ship 100 km (RICS WLCA 2023 Table 17)"))
        r['a4'] = a4
        # ------------ A5 ------------
        dec(mid, "A5 · I1", d['i1'][0], "", "", d['i1'][1], d['i1'][2])
        if d['i1_yes']: pass
        dec(mid, "A5 · L1", d['l1'][0], "", "", d['l1'][1], d['l1'][2] or "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf")
        w = d['w']; loss = w / (1 - w); r['loss'] = loss
        dec(mid, "A5 · LOSS", f"{w:.0%}", f"{loss:.4f}", "kg lost per kg installed", f"w = {w:.2f}; loss = w/(1-w) = {loss:.4f}", "https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf")
        # ------------ C1 ------------
        dec(mid, "C1 · X1", d['x1'][0], "", "", d['x1'][1], d['x1'][2] or "")
        # ------------ C2 ------------
        sh = d['shares']
        dec(mid, "C2 · ROUTE", d['nmd_cat'], f"landfill {sh['landfill']} / incineration {sh['incineration']} / recycling {sh['recycling']} / reuse {sh['reuse']}", "% of mass", "From sheet nmd_eol, unchanged.", "https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/")
        c2tkm = sum(sh[k] / 100 * DIST[k] for k in sh) / 1000
        r['c2tkm'] = c2tkm
        dsc(mid, "C2", "C2 lorry", chosen_activity=LORRY[0], reference_product=LORRY[2], location="RER", unit="ton kilometer", amount=c2tkm, database=ECODB, rule_applied="C2 share-weighted distance", TeR=1, GeR=1, TiR=1,
            values_as_found="distances 50 km recycling/reuse/landfill, 100 km incineration (nmd_eol)")
        dsc(mid, "A5", "A5 lorry (loss)", chosen_activity=LORRY[0], reference_product=LORRY[2], location="RER", unit="ton kilometer", amount=loss * c2tkm, database=ECODB, rule_applied="A5 loss x C2 distance", TeR=1, GeR=1, TiR=1)
        if d['i1_yes']:
            dsc(mid, "A5", "A5 diesel", chosen_activity=DIESEL[0], reference_product=DIESEL[2], location="GLO", unit="megajoule", amount=0.015, database=ECODB, rule_applied="A5", TeR=1, GeR=3, TiR=1)
        if d['x1_yes']:
            dsc(mid, "C1", "C1 diesel", chosen_activity=DIESEL[0], reference_product=DIESEL[2], location="GLO", unit="megajoule", amount=0.036, database=ECODB, rule_applied="C1", TeR=1, GeR=3, TiR=1)
        # ------------ W1 ------------
        wrows = []
        for (nm, amt, *_rest) in d['constituents']:
            for route, share in sh.items():
                if share == 0: continue
                key = WMAP[mid][nm][route]
                qid = f"W1: {nm} × {route}"
                if key is None:
                    why = "recycling of metals/plastics (cut-off)" if route == 'recycling' else "class has no dataset for this route ('—' in waste_fallback)"
                    dec(mid, qid, "no", "no row", "", f"No treatment dataset searched/needed: {why}. W2 fallback: no row.", "")
                    dsc(mid, "C3–C4", f"C3-C4: {nm} × {route}", rule_applied="W2 no row", proxy="proxy", amount=0, TeR=4, values_as_found=why)
                    continue
                rule, an, ref = W[key]
                a = pick_by_order(an, ref)
                if rule == "W1":
                    dec(mid, qid, "yes", an + f" [{a['location']}]", "", f"Treatment dataset named for the waste material and route found; location by D3 order.", "")
                else:
                    dec(mid, qid, "no", an + f" [{a['location']}]", "", f"No ecoinvent treatment dataset named for this waste material and route; W2 fallback from waste_fallback sheet (proxy, TeR 4).", "")
                for (purpose_mod, mult) in (("C3–C4", 1.0), ("A5", loss)):
                    pass
                wrows.append((nm, route, amt * share / 100, a, rule))
                dsc(mid, "C3–C4", f"C3-C4: {nm} × {route}", search_terms=an, chosen_activity=a['name'], reference_product=a['reference product'], location=a['location'], unit="kilogram", amount=-amt * share / 100, database=ECODB, rule_applied=rule,
                    proxy="proxy" if rule == "W2" else "", TeR=4 if rule == "W2" else 1, GeR=ger(a['location']), TiR=1)
                dsc(mid, "A5", f"A5 end of life: {nm} × {route}", chosen_activity=a['name'], reference_product=a['reference product'], location=a['location'], unit="kilogram", amount=-loss * amt * share / 100, database=ECODB, rule_applied=rule,
                    proxy="proxy" if rule == "W2" else "", TeR=4 if rule == "W2" else 1, GeR=ger(a['location']), TiR=1)
        r['wrows'] = wrows
        # ------------ D ------------
        dec(mid, "D · CFF · F1", d['cff'], "", "", "Material found in column 'materials' of sheet cff_archetypes.", "")
        CFF.append(dict(run_id=RUN, material_id=mid, cff_archetype=d['cff'], recycling_share=sh['recycling'] / 100, reuse_share=sh['reuse'] / 100, incineration_share=sh['incineration'] / 100, landfill_share=sh['landfill'] / 100,
                        flag=("† closest NMD category (assumption)" if mid in ('hempcrete', 'ptfe_coated_glass_fabric') else "") + (" review flag" if r['flag'] else ""), note="NMD category " + d['nmd_cat']))
        for (nm, amt, *_x) in d['constituents']:
            dec(mid, f"D · BIO-C · B1: {nm}", d['carbon'][nm], "", "", "Constituent found by name in sheet carbon_archetypes.", "")
            BIO.append(dict(run_id=RUN, material_id=mid, constituent=nm, kg_per_kg_product=amt, carbon_archetype=d['carbon'][nm], moisture_content="", flag="",
                            note=("water listed as its own constituent; archetype default moisture would double count: model should not add moisture to hemp shiv" if (mid == 'hempcrete' and nm == 'hemp shiv') else "")))
    return results


# ------------------------------------------------------------------ writers
def write_csv(name, rows, cols):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, "") for c in cols})


def cols_of(fn):
    return open(os.path.join(OUT, fn), encoding="utf-8").readline().strip().split(",")


HEAD = ['name', 'amount', 'unit', 'location', 'reference product', 'database', 'type', 'module', 'rule', 'TeR', 'GeR', 'TiR', 'DQR', 'comment']


def write_lci(mid, r):
    d = r['d']; wb = openpyxl.Workbook(); ws = wb.active; ws.title = "LCI"
    ws['A1'] = 'Database'; ws['B1'] = 'raw_baselines'
    row = 3
    prev = None
    blocks = [("A1–A3", "at factory gate"), ("A4", "delivered to site"), ("A5", "installed"), ("C1", "demolished"), ("C2", "at waste site"), ("C3–C4", "cradle to grave")]
    loss = r['loss']
    for mod, refp in blocks:
        act = f"{mid}, {mod}"
        for lab, val in (("Activity", act), ("reference product", f"{mid}, {refp}"), ("unit", "kilogram"), ("location", "RER"), ("module", mod), ("comment", "")):
            ws.cell(row, 1, lab); ws.cell(row, 2, val); row += 1
        ws.cell(row, 1, "Exchanges"); row += 1
        for i, h in enumerate(HEAD): ws.cell(row, i + 1, h)
        row += 1
        def ex(name, amt, unit, loc, refprod, db, typ, rule, ter, ger_, tir, comment=""):
            nonlocal row
            dqr = round((ter + ger_ + tir) / 3, 2) if isinstance(ter, (int, float)) else ""
            vals = [name, amt, unit, loc, refprod, db, typ, mod, rule, ter, ger_, tir, dqr, comment]
            for i, v in enumerate(vals): ws.cell(row, i + 1, v)
            row += 1
        ex(act, 1, "kilogram", "RER", f"{mid}, {refp}", "raw_baselines", "production", "–", "", "", "", "")
        if mod == "A1–A3":
            for x in r['a13']:
                ex(x['bw']['name'], sig(x['amount'], 4), x['unit'], x['bw']['location'], x['bw']['reference product'], ECODB, "technosphere", x['rule'], x['TeR'], x['GeR'], x['TiR'], x['purpose'] + (" [proxy]" if x['proxy'] else ""))
        else:
            ex(prev[0], 1 + loss if mod == "A5" else 1, "kilogram", "RER", prev[1], "raw_baselines", "technosphere", "–", "", "", "", "previous block" + (" (A5 takes 1 + loss)" if mod == "A5" else ""))
            if mod == "A4":
                for lab, a_, tkm in r['a4']:
                    a = pick(*a_); ex(a['name'], tkm, "ton kilometer", a['location'], a['reference product'], ECODB, "technosphere", "A4 archetype " + d['archetype'], 1, ger(a['location']), 1, f"A4 {lab}")
            if mod == "A5":
                if d['i1_yes']:
                    a = pick(*DIESEL); ex(a['name'], 0.015, "megajoule", "GLO", a['reference product'], ECODB, "technosphere", "A5", 1, 3, 1, "A5 diesel")
                a = pick(*LORRY); ex(a['name'], sig(loss * r['c2tkm'], 4), "ton kilometer", "RER", a['reference product'], ECODB, "technosphere", "A5 loss x C2 distance", 1, 1, 1, "A5 lorry (loss)")
                for (nm, route, m_, a, rule) in r['wrows']:
                    ex(a['name'], -sig(loss * m_, 4), "kilogram", a['location'], a['reference product'], ECODB, "technosphere", rule, 4 if rule == "W2" else 1, ger(a['location']), 1, f"A5 end of life: {nm} × {route}" + (" [proxy]" if rule == "W2" else ""))
            if mod == "C1" and d['x1_yes']:
                a = pick(*DIESEL); ex(a['name'], 0.036, "megajoule", "GLO", a['reference product'], ECODB, "technosphere", "C1", 1, 3, 1, "C1 diesel")
            if mod == "C2":
                a = pick(*LORRY); ex(a['name'], sig(r['c2tkm'], 4), "ton kilometer", "RER", a['reference product'], ECODB, "technosphere", "C2 share-weighted distance", 1, 1, 1, "C2 lorry")
            if mod == "C3–C4":
                for (nm, route, m_, a, rule) in r['wrows']:
                    ex(a['name'], -sig(m_, 4), "kilogram", a['location'], a['reference product'], ECODB, "technosphere", rule, 4 if rule == "W2" else 1, ger(a['location']), 1, f"C3-C4: {nm} × {route}" + (" [proxy]" if rule == "W2" else ""))
        prev = (act, f"{mid}, {refp}")
        row += 1
    ws.column_dimensions['A'].width = 60
    wb.save(os.path.join(OUT, f"LCI_{mid}.xlsx"))


if __name__ == "__main__":
    res = main()
    for mid, r in res.items():
        write_lci(mid, r)
    write_csv("decisions.csv", DEC, cols_of("decisions.csv"))
    write_csv("dataset_choices.csv", DSC, cols_of("dataset_choices.csv"))
    write_csv("epd_check.csv", EPD, cols_of("epd_check.csv"))
    write_csv("cff_inputs.csv", CFF, cols_of("cff_inputs.csv"))
    write_csv("bioc_inputs.csv", BIO, cols_of("bioc_inputs.csv"))
    summ = {}
    for mid, r in res.items():
        top = sorted(r['a13'], key=lambda x: -x['gwp'])[:6]
        summ[mid] = dict(gwp=r['a13_gwp'], wear_share=r['wear_share'], approx=r.get('approx_gwp'), top=[(x['purpose'], round(x['gwp'], 4)) for x in top], loss=r['loss'], c2tkm=r['c2tkm'])
    json.dump(summ, open(os.path.join(OUT, "work", "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))
