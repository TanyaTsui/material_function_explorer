# Summary, run batch_3 (19 Nov 2026)

ecoinvent 3.12 cut-off; EF 3.1 climate change: fossil, A1–A3 per kg (read-only Brightway). ÖKOBAUDAT release OBD_2024_III. No material stopped (STOP). Full list of protocol problems: `protocol_issues.md`. The main caveat: complete machine datasheets were almost never available, so many P1/P2 steps have no rows.

| material | route kept | A1–A3 GWP-fossil (kg CO2e/kg) | ÖKOBAUDAT median (n) | ratio | check |
| --- | --- | --- | --- | --- | --- |
| osb3 | exact match (D1) | 0.407 | 0.457 (4) | 0.89 | CHECK 1 pass |
| engineered_bamboo | built | 0.433 | none | n/a | no check possible (MOSO EPD 0.436, information only) |
| hemp_fibre_mat | built | 1.35 | 1.01 (2) | 1.33 | CHECK 3 pass |
| straw_bale | built, **flagged** | 0.0538 | 0.124 (2) | 0.43 | CHECK 2 fail (0.40×), CHECK 3 fail, REVIEW keeps built |

## osb3
- D1 yes: `market for oriented strand board` RER (607 kg/m³, 0.001647 m³ per kg). D2 market, D3 RER, D4 one variant. TeR 1, GeR 1.
- A4: T1 no, T2 no (DE, FR confirmed only), T3 yes → EU (1.5 tkm lorry + 0.1 tkm ship). A5: I1 no (≈ 34 kg board), L1 no → 3 %. C1 X1 no. C2: NMD 55 (5/85/10/0). Waste: wood fallback (W2) for the product.
- CFF: wood panels. Bio-C: wood strands = Wood; adhesive and paraffin = non-biogenic.
- Unsure: "same constituents" with adhesive share 3.9 % (dataset) vs 5.1 % (input).

## engineered_bamboo
- D1 no, D1b no (no laminated bamboo board in ecoinvent). Built: bamboo pole (market, RoW) 0.978 kg; MUF adhesive (market, GLO) 0.022 kg.
- Machines: splitting = chain splitter 5.59 kW, 530 kg (mixed-supplier throughput 812.5 kg/h, proxy TeR 4) → 0.00688 kWh/kg + wear 5.2×10⁻⁶ kg. Hot pressing = BREF fallback (0.0583 kWh/kg electricity, 0.57 MJ/kg heat, proxy). **No rows** for planing, boiling/steaming, drying, sanding (no machine data); no wear row for the press.
- A4: T2 no, T3 no → global (0.5 tkm lorry + 10 tkm ship). I1 no (49 kg at mid thickness, borderline), L1 → 3 %, X1 no. C2: NMD 34 (5/80/10/5). CFF: solid wood. Bio-C: bamboo; MUF non-biogenic.
- Unsure: the missing heat steps; D3 gives RoW although the board is made from Chinese bamboo; I1 borderline.

## hemp_fibre_mat
- D1 no, D1b no. Built: decorticated hemp fibre FR 0.85; bicomponent polyester → `fibre, polyester` GLO (**proxy**, TeR 4) 0.12; soda ash light RER 0.03.
- Machines: fibre opening = Rieter UNIfloc A 12 (14.7 kW, 2,400 kg/h, 4,050 kg) → 0.006125 kWh/kg + wear 1.35×10⁻⁵ kg (the only complete triple of the batch). **No rows** for soda impregnation, carding/air-laying, thermal bonding oven, cutting.
- A4: T2 no (DE only, Thermo Hanf, Nördlingen), T3 yes → EU. I1 no, L1 → 3 %, X1 no. C2: NMD 52 (5/95/0/0). CFF: other plant-based. Bio-C: hemp fibre = cellulose; rest non-biogenic.
- Unsure: the pass comes with the heat and web-forming energy missing; EPD median rests on two mats.

## straw_bale
- D1 no (PP twine missing in `market for straw`), D1b yes: `market for straw`, Europe without Switzerland, TeR 2 → CHECK 2 fail (0.0492; 0.40×). Built: straw 0.998 + PP twine 0.002 (granulate, proxy) → 0.0538 (0.43×), CHECK 3 fail. REVIEW: built kept (distance 0.565 vs 0.602), **flagged**.
- P1: baling is inside the straw dataset (no row); storage no energy. No machine rows.
- A4: T2 unclear → lower-impact branch (national, 0.15 tkm). I1 no (≈ 16 kg bale), L1 → 3 %, X1 no. C2: NMD 52. W1 yes for PP twine (waste polypropylene); straw by W2 (wood). CFF: other plant-based.
- Unsure: EPD category (2 EPDs; bale and blown straw), the low ecoinvent burden of co-product straw; T2 evidence.

## Files
`decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material_id>.xlsx` (4), `protocol_issues.md`, `scripts/` (build, calculation and ÖKOBAUDAT helper scripts, read-only on Brightway).
