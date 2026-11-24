# batch_1

# Summary, batch_1 (2026-11-19)

Four materials run: sawn_softwood, cork, fibre_cement, stone_wool. No STOP. Database ecoinvent 3.12 cut-off; ÖKOBAUDAT release OBD_2024_III (13 Nov 2026); GWP-fossil A1–A3 with EF 3.1 (climate change: fossil), kg CO2e per kg, 3 significant figures. Files: `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material>.xlsx`, `protocol_issues.md`.

| Material | Route kept | A1–A3 dataset | Ours | ÖKOBAUDAT median (n) | Ratio | Check |
| --- | --- | --- | --- | --- | --- | --- |
| sawn_softwood | exact (D1) | market for sawnwood, beam, softwood, raw, dried (u=10%), Europe w/o CH | 0.146 | 0.209 (6) | 0.70 | CHECK 1 pass |
| cork | approximate (D1b), **flagged** | market for cork slab, RER | 0.959 | 0.512 (1) | 1.87 | CHECK 2 fail, CHECK 3 fail, REVIEW keeps approximate |
| fibre_cement | approximate (D1b) | market for fibre cement facing tile, large format, GLO | 1.39 | 1.08 (7) | 1.29 | CHECK 2 pass |
| stone_wool | built from scratch | 4 constituents + BREF energy | 1.35 | 1.19 (4) | 1.14 | CHECK 3 pass |

## Per material

**sawn_softwood.** D1 yes (kiln dried, wood only; ecoinvent u=10 % vs input 12 %). D2 market, D3 Europe without Switzerland, D4 beam (board recorded). Row 0.00215 m³ (= 1 kg). No machines. A4: T1 no, T2 yes (DE, FR, IT) → 150 km. I1 no, L1 no (3 %), X1 no. NMD 34. CFF Solid wood; carbon archetype Wood, u = 0.12. Unsure: moisture gap in D1; Italian evidence for T2.

**cork.** D1 no (ecoinvent slab has 0.14 kg/kg melamine, phenolic and urea formaldehyde resins). D1b yes (same main constituent, cork). CHECK 2 fail (1.87×). Built from scratch: raw cork 1.06 kg (RoW market, literal D3), grinding with a hammer mill (median of three: Ottevanger 650 series, midpoints 60 kW, 7,000 kg/h, 962.5 kg; 0.00857 kWh/kg; wear share of GWP 8.3e-5, below 2 %). **Autoclave expansion and cutting: no machine data found, no rows (unresolved).** Built value 0.0355 kg/kg (ratio 0.07, incomplete) fails CHECK 3. REVIEW: distance approximate 0.871 vs built 0.931 → approximate match kept, flagged. A4: T2 no (FR, ES only), T3 yes → EU, lorry 1.5 tkm + sea 0.1 tkm. NMD 52; waste mapped to wood (W2 proxy). CFF Other plant-based; carbon archetype Cork, 1.0 kg. Unsure: the built LCI misses the steam step, so the REVIEW ranking uses an incomplete number; a complete build would probably be higher and could pass.

**fibre_cement.** D1 no (no pigments/water, cement 0.91 vs 0.714). D1b yes (same product, main constituent cement); D4 large format; GLO market (the only market). CHECK 2 pass at 1.29×. No machine rows. A4: T2 unclear (only ES confirmed) → national 150 km. NMD 8 (closest category). W1 recycling `waste cement-fibre slab, recycling` (CH); landfill via W2 (inert). CFF Mineral, crushed to aggregate; cellulose fibre in archetype Cellulose fibres and stalks, other constituents Non-biogenic. Unsure: GLO market vs CH production (both pass); the median depends on which EPDs count as "facade panels".

**stone_wool.** D1 no, D1b no (main constituent: briquettes 0.59 vs basalt in ecoinvent). Built: basalt (GLO market), cement-bonded briquettes → proxy cement Portland, binder → proxy phenolic resin, mineral oil → proxy lubricating oil (all TeR 4). Energy from EU BREF Table 3.29 (12.5 MJ/kg midpoint: melting 5.30, fiberising 3.18, curing 3.18 MJ heat; 0.235 kWh electricity for cutting); no machine datasheet with all three values found, so no machine rows. CHECK (mass) 0.997 = input sum. CHECK 3 pass at 1.14×. A4: T2 unclear (only DE confirmed) → 150 km. NMD 78. CFF Mineral wool; all constituents Non-biogenic. Unsure: BREF midpoints and the carrier (coke booked as natural-gas heat); proxies; the input sums to 0.997.

## Main things to look at

- **Machine data is the weak point.** Only grinding (cork) has a three-manufacturer comparison, on range midpoints. Five steps across cork and stone wool have no machine data (cork autoclave and cutting; stone wool cupola, fiberising, curing oven, cutting use BREF energy and no machine). The three-machine rule (power, throughput and mass from a datasheet) is rarely achievable for process-specific equipment.
- **Cork is flagged** (REVIEW). It is also the one case where an incomplete build decided nothing only because the distance of the approximate match was slightly smaller.
- **Latest ÖKOBAUDAT release changes the datasets** compared with the workbook links (three of four material_overview UUIDs are old versions).
- **Category definition for the median** is not given by the protocol; alternatives are in `epd_check.csv` (likely_reason) and `protocol_issues.md`. None changed a pass/fail.
- Not done: module B and D calculations (inputs written to `cff_inputs.csv` and `bioc_inputs.csv` only), premise scenario (applied by the model).


# batch_2

# Summary, batch_2 (run date 19 Nov 2026)

GWP-fossil A1–A3 per kg: EF 3.1 "climate change: fossil", ecoinvent 3.12 cut-off, computed with Brightway (read-only). Wear = share of machine (P2) rows. No material was stopped.

| Material | Route kept | GWP-fossil A1–A3 (kg CO2e/kg) | EPD median | Ratio | Check | Wear share |
| --- | --- | --- | --- | --- | --- | --- |
| sawn hardwood (oak) | D1 exact: market for sawnwood, hardwood, raw, dried (u=10%), RER | 0.133 | 0.139 (n=1) | 0.953 | CHECK 1 pass | 0 (no machine rows) |
| cotton canvas | built from scratch | 5.87 | none | – | CHECK 3: no check possible | 1.45e-4 |
| ceramic tile | D1b approximate: ceramic tile production, CH + A2 lorry 150 km | 0.432 | 0.694 (n=1) | 0.623 | CHECK 2 pass | 0 |
| PVC-U | built from scratch | 2.40 | 4.18 (n=2, not ÖKOBAUDAT) | 0.574 | CHECK 3 pass | 1.96e-4 |

## Per material

**Sawn hardwood (oak).** D1 yes (market, RER; moisture u=10 % vs 12 % and generic hardwood vs oak noted). Check 1 passes (ratio 0.95, one EPD). A4: made in DE/FR/NL → 150 km. A5: no machine, prefab → 3 %. No C1 row. Route 34 (5/80/10/5). CFF: Solid wood; biogenic: Wood, u = 0.12.

**Cotton canvas.** D1 no and D1b no: ecoinvent only has greige woven cotton (finishing is a separate dataset). Built: cotton fibre market GLO (1.1 kg). Machines: carding = Rieter C 81 (only 1 of 3 candidates complete); spinning = EDIPTEX study, ring Ne 16, 2.10 kWh/kg (proxy); weaving = industry-article value 3.2 kWh/kg (proxy, low confidence); wet finishing = stenter drying heat only, 2.58 MJ/kg (proxy). No ÖKOBAUDAT dataset, so no check. A4: T2 no (only NL found), T3 yes → EU (1.5 tkm lorry + 0.1 tkm ship). Route 52 (5/95/0/0), waste via W2 (wood datasets, CH).

**Ceramic tile.** D1 no (extra TiO2, stucco, metals; no kaolin). D1b yes (clay main constituent), check 2 passes. D2 was unclear (market only GLO): took production CH + A2 (lower impact; market GLO would give 0.796, ratio 1.15, also a pass). A4 national 150 km. L1 yes (set in adhesive) → 5 %; X1 yes (bonded) → diesel 0.036 MJ. Route 25 (15/0/80/5); waste via W2 mineral datasets.

**PVC-U.** D1 and D1b no (no PVC profile dataset; "window frame" is a whole frame with metal). Built: PVC resin, chalk (limestone, milled), TiO2 from datasets; impact modifier (PMMA) and Ca-Zn stabiliser (organic chemical) are proxies (TeR 4). Machines: dry blending = Jwell hot/cold mixer (median of three, 0.094 kWh/kg, no weight); profile extrusion = Jwell SJZ65/132 (37 kW, 215 kg/h, 4,000 kg; only two of three complete, lower-energy used); cutting = no data, no rows. Check 3 passes only against two non-ÖKOBAUDAT EPDs. Route 63 (10/10/80/0).

## Things I am unsure about

1. EPD medians rest on 0 to 2 EPDs each (ÖKOBAUDAT could not be searched by category). Oak and tile rest on a single EPD.
2. Machine data are the weakest part: for 6 of 7 built steps I could not get three complete datasheets; three steps use study values, one has no rows (PVC cutting). Wear shares are far below 2 % but several machines have no wear row. The Jwell values come from a search summary (page returned 403).
3. Cotton canvas is dominated by cotton fibre (3.81 of 5.87), but spinning and weaving energy values are low-confidence.
4. Open protocol questions (D2 vs D3 market GLO, FAE variants, sign of wood recycling, T2 "unclear") are in `protocol_issues.md`.
5. TiR = 1 for all datasets; the ceramic tile dataset is old (v2).

Files: `decisions.csv` (106 rows), `dataset_choices.csv` (65), `epd_check.csv` (4), `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material_id>.xlsx` ×4, `protocol_issues.md`. The build script is `scripts/build_run.py` in the working folder.


# batch_3

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


# batch_4

# Summary, batch_4 (ÖKOBAUDAT release OBD_2024_III, 13.11.2026; ecoinvent 3.12 cut-off)

GWP-fossil A1–A3 per kg, EF 3.1, computed read-only in Brightway.

| Material | Route kept | Dataset / machines | Ours (kg CO2e/kg) | EPD median (n) | Ratio | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| plywood | exact (D1 yes) | market for plywood, RER (m3, 823 kg/m3) | 0.496 | 0.405 (3) | 1.22 | CHECK 1 pass; no machine rows |
| mycelium | built (D1 no, D1b no) | hemp hurd FR 0.85, wheat flour RoW 0.05, rye grain CH (proxy for spawn) 0.10; autoclave (Rootlab, proxy), paddle mixer (Magaldi 700), belt dryer (STELA, proxy) | 0.656 | none | – | CHECK 3 no check possible; wear share 0.002 % |
| AAC | approximate (D1 no, D1b yes) | market for AAC block, CH | 0.359 | 0.461 (11) | 0.78 | CHECK 2 pass; no machine rows |
| concrete | built, flagged | gravel crushed CH (proxy) 0.769, cement Europe w/o CH 0.145, tap water RER 0.087; mixer Sicoma MAO3000/2000 | 0.118 | 0.0728 (63, C30/37) | 1.62 | CHECK 2 fail (1.62), CHECK 3 fail (1.62); REVIEW kept built (distance 0.620 vs 0.621), flagged; wear share 0.002 % |

Transport and end of life: plywood A4 150 km, 3 % loss, route 55; AAC A4 150 km, 5 % loss, diesel C1, route 9; mycelium A4 EU (1.5 tkm lorry + 0.1 sea), 3 % loss, route 52; concrete A4 bulk 50 km, 5 % loss, diesel A5 and C1, route 8.

Unsure about (details in protocol_issues.md):
- D1 for concrete and AAC hinges on how strictly "extra constituent" is read; the dataset is the same either way.
- Mycelium has no complete three-machine sets: incubation and moulding have no rows, pasteurising and drying are proxies, and the drying values come from a search summary of a PDF I could not read. The result is under- or over-stated by an unknown amount; the heat row is 36 % of it.
- Concrete fails by the same ratio on both routes: the EPD set is mostly low-clinker ECOPact mixes; cement carries ~95 % of our result.
- TiR = 1 for all datasets (time period unreadable); machine life 40,000 h is an assumption.
- W2 for plywood, AAC and mycelium uses fallback classes; the wood recycling dataset is entered with a positive amount.

Files: decisions.csv, dataset_choices.csv, epd_check.csv, cff_inputs.csv, bioc_inputs.csv, LCI_<material>.xlsx; scripts/ holds the code that produced them (read-only on Brightway and ÖKOBAUDAT).


# batch_5

# Summary, run batch_5

GWP-fossil A1–A3 per kg (EF 3.1, climate change: fossil, Brightway, read-only). Wear (P2 machine) share is below 0.4 % everywhere (limit 2 %). No material was stopped. All files are in `runs/batch_5/`; calculation scripts in `work/`.

**Big caveat:** no machine had a complete datasheet (kW, kg/h, mass) from three manufacturers; most machine values are proxies or assumptions, all marked in `dataset_choices.csv` and `protocol_issues.md`. ÖKOBAUDAT could not be queried, so each median rests on the one EPD PDF I could read.

| Material | Route kept | GWP-fossil A1–A3 | CHECK |
| --- | --- | --- | --- |
| hempcrete | built | 0.646 | no check possible (no ÖKOBAUDAT dataset) |
| gypsum board | built, flagged | 0.352 (approx. match 0.360) | CHECK 2 fail (2.29× median 0.157), CHECK 3 fail (2.24×); REVIEW keeps built |
| toughened glass | built, flagged | 0.547 | CHECK 3 fail (0.40× median 1.384); REVIEW: only route tried |
| PTFE-coated glass fabric | built | 99.7 | no check possible |

## hempcrete
D1 no, D1b no (nothing in ecoinvent). Constituents: hemp hurd (market FR), hydrated lime packed (RER), hydraulic lime (RER), tap water (market group RER). Machines: mixing = 6 ft pan mixer (proxy, 2 of 3 candidates complete); moulding and pressing = WITECH BP-18 biomass press (proxy, TeR 4); air drying: no energy. A4 national 150 km (T2 unclear, lower-impact branch); A5 no machine (piece weight unclear), in situ 5 %; C1 diesel (bonded); NMD category 8. Lime and hemp dominate (hydraulic lime 0.42 of 0.65).

## gypsum board
D1 no (ecoinvent board has extra glass fibre, silicone), D1b yes (market for gypsum plasterboard GLO), CHECK 2 fail → built. Built: mineral gypsum, waste paper, starch as proxy for additives (TeR 4). Steps: calcining (vertical kiln, 190 kcal/kg, vendor figure), mixing and forming (mixer proxy), drying (Watlow low value minus calcining, 4.5 MJ/kg; 0.25 of 0.35 total), cutting (glass cutter proxy). Unsure: dryer mass and throughput are assumptions; one EPD only for the median. A4 national 150 km, 3 % loss, NMD 27 (95 % landfill).

## toughened glass
D1 no, D1b no (no toughened dataset). Built from six batch constituents (all ecoinvent markets). Melting heat 5 MJ/kg (low end of the BREF-type range), tempering furnace Liaoda YD-F-2436 at 0.49 kWh/kg (median of 3, mass not listed → assumed), cutting Toyocc (median of 3), batch mixing mixer proxy. CHECK 3 fails low: no carbonate process CO₂ row exists in the protocol (about 0.17 kg CO₂/kg missing). The EPD is EN 15804+A1, GWP total. A4 national (T2 unclear).

## PTFE-coated glass fabric
D1 no, D1b no. Glass fibre (market GLO) 0.35 and PTFE (market GLO) 0.65. Weaving = generic textile 3.2 kWh/kg (proxy); dip coating and sintering = heat balance (about 2.4 MJ/kg, proxy). A4 EU (T2 no, T3 yes): lorry 1.5 + ship 0.1 tkm. NMD 62 (85 % incineration). 99.7 kg CO₂e/kg is almost all PTFE: please check the input shares.


# batch_6

# Summary, run batch_6 (2026-11-19)

Database ecoinvent 3.12 cut-off, EF 3.1 climate change: fossil, ÖKOBAUDAT via API (A2 datasets). Machine/energy values partly from BREF and search summaries: see `protocol_issues.md` 9-14. All four materials went through; none stopped.

| material | route kept | GWP-fossil A1-A3, kg CO2e/kg | ÖKOBAUDAT median (n) | ratio | check |
| --- | --- | --- | --- | --- | --- |
| mdf | built from scratch (flagged) | 0.815 | 0.461 (5) | 1.77 | CHECK 1 fail (1.89), CHECK 3 fail, REVIEW keeps built |
| clay brick masonry | built from scratch (flagged) | 0.309 | 0.196 (1, brick only) | 1.58 | CHECK 3 fail (only one route), kept flagged |
| structural steel | built from scratch | 0.762 | 0.560 (1) | 1.36 | CHECK 2 fail (4.07), CHECK 3 pass |
| PVC-coated polyester | built from scratch | 3.44 | 4.13 (1, PVC roofing sheet) | 0.83 | CHECK 3 pass (energy of coating missing) |

Wear (P2 machine rows) share of GWP-fossil A1-A3: MDF 0.012 %; other materials have no machine rows.

## mdf
- D1 yes: `market for medium density fibreboard` RER (EPF average; UF 46.4 + MF 41.8 kg/m3 resin, paraffin, wood; 1 kg = 1/684 m3). CHECK 1 failed (0.872 vs 0.461). D1b no (the same dataset cannot be picked again; other fibreboards are other products). Built:
  wood fibres -> proxy `market for wood chips, green` (Europe w/o CH); UMF -> proxy UF resin RER; paraffin RER/GLO.
- Machines/energy: chipping = drum chipper, median of three datasheets (Liantai UTM, 110 kW, 15 t/h, 7 t; kWh 0.0073/kg). Steaming (3.28 MJ), refining (0.265 kWh), flash drying (0.125 kWh + 3.94 MJ), hot pressing (0.068 kWh + 1.03 MJ): EU BREF WBP midpoints, no datasheet had all three values; refiner, press, sander have machine rows (proxy mass), steaming and drying none. Sanding: Heesemann HSM 2 (13.4 kW, 4.5 t) with assumed throughput; saws not modelled.
- Both LCIs ~1.8-1.9x the median: natural-gas heat (0.446 of 0.815), electricity and UF resin; probably biomass heat in the EPDs (not checked).
- A4: T2 yes (DE, IT, FR) -> 150 km; I1 no (39 kg board, assumed format); L1 no (3 %); X1 no. EOL NMD 55 (5/85/10/0).

## clay brick masonry
- D1 no, D1b no (masonry with mortar is not `clay brick`; protocol issue 5). Built: `market for clay brick` RoW 0.8 (D2/D3 literal; RER production would be 0.250 instead of 0.332) + `market for cement mortar` CH 0.2.
- All five steps are inside the brick dataset (grinding, mixing, extrusion, drying, firing): no energy or machine rows.
- CHECK 3 1.58x (EPD is brick only, 1 EPD): flagged. A4: T2 unclear -> yes (DE, NL confirmed); I1 no; L1 yes 5 %; X1 yes. EOL NMD 32 (1/0/99/0).

## structural steel
- D1 no; D1b yes (`market for steel, low-alloyed, hot rolled` GLO, 74 % converter steel); CHECK 2 fail (2.28 vs 0.56). Built: `market for steel, structural, 100% scrap` (EAF, GLO) 1 kg + hot rolling from EU BREF 2022 (1.8 MJ heat, 0.056 kWh); EAF melting is inside the dataset; no machine row (no mass found). CHECK 3 pass (1.36).
- A4: T2 unclear -> yes (DE, IT confirmed); I1 yes (IPE 200, 134 kg; diesel 0.015 MJ); L1 no 3 %; X1 yes. EOL NMD 70 (1/0/94/5): only landfill gets a row.

## PVC-coated polyester
- D1 no, D1b no. Built: polyester filament (`market for fibre, polyester` GLO, includes melt spinning), PVC emulsion RER, plasticiser = proxy DOTP, flame retardant/fillers/stabilisers = proxy aluminium hydroxide, acrylic varnish RER.
- Only weaving has energy rows (vendor benchmark 3.6 kWh/kg x 0.2 kg); coating/gelling oven and lacquering: unclear, no rows (largest gap).
- A4: T2 unclear -> yes; I1 yes (roll 131 kg); L1 no 3 %; X1 yes. EOL NMD 62 (10/85/5/0).

## Unsure about
Machine values (protocol issues 9-14), the D2/D3 literal reading (RoW brick, GLO steel/polyester), brick D1b, T2 for steel/brick/PVC, assumed piece weights, the positive sign for wood sorting and shredding, and the PVC check (reference is a roofing sheet, coating energy missing).


# batch_7

# Summary, batch_7 (run 2026-11-19)

Four materials, none stopped. Values are GWP-fossil A1–A3 per kg (EF 3.1, climate change: fossil, ecoinvent 3.12 cut-off), compared with the median of EN 15804+A2 EPDs in the latest OEKOBAU.DAT data stock listed by its API (OBD_2024_III, read per EPD with the API; per-EPD values are converted to kg with each EPD's gross density).

| Material | Route kept | Ours | EPD median (n) | Ratio | Check |
| --- | --- | --- | --- | --- | --- |
| glulam | exact (D1) | 0.340 | 0.291 (7) | 1.17 | CHECK 1 pass |
| CLT | exact (D1) | 0.349 | 0.242 (4) | 1.44 | CHECK 1 pass (near +50 % edge) |
| soft wood fibre board | built, flagged | 0.919 | 0.540 (4) | 1.70 | CHECK 2 fail (1.70), CHECK 3 fail (1.70), REVIEW |
| aluminium extrusion | built, flagged | 13.0 | 4.17 (10) | 3.11 | CHECK 3 fail, REVIEW (only one LCI) |

## glulam
- D1 yes: `market for glued laminated timber, average glue mix`, Europe without Switzerland (D2 market, D3 rule 1, D4 only variant there). Unsure: the dataset has 0.07 % phenolic resin besides PUR/MUF (see protocol_issues).
- A4: T2 yes (DE, FR, IT, ES), lorry 0.15 tkm. A5: I1 yes (beam about 124 kg), L1 no, 3 % loss. C1: X1 yes. Route 34 (5/80/10/5). CFF: Solid wood. Waste via Wood class of waste_fallback (proxy).

## CLT
- D1 yes: `market for cross-laminated timber`, RER. ecoinvent glue shares differ from the input (MUF), same constituents.
- A4: T2 yes (DE, FR, IT, ES). I1 yes, X1 yes, route 34. Ratio 1.44, only just inside the limit.

## soft wood fibre board
- D1 no (extra binders in every candidate). D1b yes: `market for fibreboard, soft`, RER (differences logged: MDI 0.18 %, phenolic, latex, starch, vinyl acetate, nylon, Al sulfate). CHECK 2 fails (1.70).
- Built: wood chips (RER market) 0.945, polyurethane adhesive (GLO) 0.04, paraffin (GLO) 0.015; mass check passes.
- Machines (all proxy, TeR 4, see protocol_issues): refining and drying energy from BREF Table 3.3 midpoints (refining 0.265 kWh/kg electricity + 0.91 kWh/kg heat; drying 0.125 + 1.095), curing from BREF MDF pressing, dosing and saw from vendor kW over a 6 t/h line. Wear rows only for refiner (Andritz TX68) and dryer (VetterTec); wear share 0.033 %.
- CHECK 3 fails (1.70). REVIEW: built 1.701 vs approximate 1.704 times the median; built kept and flagged (a tie in practice). Heat from natural gas is half of the built result.
- A4: T2 yes (DE, FR, IT), 0.15 tkm. I1 no (boards below 50 kg), X1 no. Route 55 (5/85/10/0). CFF: Wood panels.

## aluminium extrusion
- D1 and D1b no (ecoinvent has only the extrusion process, not the profile). D5: `market for aluminium, wrought alloy` GLO (no European dataset; D3 rule 5).
- Steps: billet heating gas 0.195 kWh/kg (0.702 MJ), extrusion electricity 0.196 kWh/kg (US DOE bandwidth study, derived), ageing oven gas 0.080 kWh/kg (0.288 MJ), cutting: no separate row (inside the DOE plant electricity). No wear rows (no mass with throughput found), so the wear share is "not computed".
- CHECK 3 fails: 12.96 vs 4.17 (3.1x). The alloy market alone is 12.84; the energy rows are 1 %. The EPD median is pulled down by low-carbon and recycled profiles; the GDA EPD named in the input sheet has 1.92. Flagged, kept.
- A4: T2 yes (DE, FR, IT, ES). I1 no, X1 no. Route 4 (3/3/94/0). CFF: Aluminium. Landfill and incineration rows only (recycling has no row, cut-off).

## Biggest uncertainties
1. Machine values (P1/P2) are fallback figures, not three-machine medians; see protocol_issues.md.
2. Median of the aluminium category depends on which EPDs count as "profiles".
3. Piece weights (I1/X1) rest on assumed formats; the A4 category for all four is "national" (150 km).
4. Amounts of wood products are in m³ (kg ÷ wet mass of the dataset).

Files: `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material>.xlsx`, `protocol_issues.md`; the scripts that wrote them are in `work/` (read-only use of Brightway; no database or workbook was changed).
