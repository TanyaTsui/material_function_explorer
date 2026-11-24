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
