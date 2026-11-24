# Summary: run_A (2026-11-12)

Database: ecoinvent 3.12 cut-off (read-only). EPD check against ÖKOBAUDAT release OBD_2024_II (22.07.2026), using EF v3.1 climate change: fossil. Every row has TiR = 5 because the dataset time period could not be read (see protocol_issues.md #1).

## osb3: OSB/3 (EN 300), floor or roof deck, indoor, 50 years
- **Composition (S1):** median of 3 IBU EPDs in ÖKOBAUDAT (Egger, Sonae Arauco, Kronospan): wood including moisture 0.951, pMDI/MUF 0.0339, wax and additives 0.0149 kg/kg.
- **A1–A3:** D1 exact match, `market for oriented strand board` RER, 0.00165 m³ (1 kg ÷ 607 kg/m³, the dataset's own wet density). TeR 1.
- **EPD check:** 0.407 kg CO2e/kg, inside the ÖKOBAUDAT range 0.282–0.579 (4 datasets). **Pass.**
- **A4:** nationally manufactured (DE Egger, FR Swiss Krono, IT I-PAN), 150 km → 0.15 tkm.
- **A5:** prefab, 3 % waste → 1.031 kg delivered. No machine energy (board 22.7 kg).
- **B2 / B3:** no rows.
- **C1:** diesel 0.036 MJ/kg, because floor-deck T&G joints are glued (bonded).
- **End of life:** NMD category 55 (landfill 5 / incineration 85 / recycling 10) → 0.0925 tkm. Waste-wood treatments.
- **Unsure:** whether a glued T&G joint counts as "bonded" (C1); how the wood-recycling row is signed (shredding, positive, dry mass); whether I-PAN still makes OSB in Italy.

## hempcrete: hemp-lime blocks, interior partition, indoor, 50 years
- **Composition (S1):** Schönthaler EPD (the only hemp-lime EPD in ÖKOBAUDAT) gives ranges of hemp 20–55 % and binder 45–80 %. I used the midpoints: hemp shives 0.375, binder 0.625.
- **A1–A3:** no hempcrete in ecoinvent, so I built it (D5, TeR 3):
  - `market for hemp hurd` FR, 0.375 kg
  - `market for hydraulic lime` RER, 0.625 kg
  - processing energy from ecoinvent `concrete block production` DE (the EPD says the blocks are made on a concrete-block plant): 0.002 kWh RER electricity and 0.0216 MJ diesel per kg
- **EPD check:** 0.755 vs. the ÖKOBAUDAT mean of 0.424 (±50 %). **Fail, flagged, not changed.** Hydraulic lime makes up 82 % of our value, and the binder share is only known as a range. Both ÖKOBAUDAT datasets come from one producer, who uses PV electricity.
- **A4:** made in IT, FR and ES → 150 km.
- **A5:** laid with mortar → in situ, 5 % waste → 1.053 kg delivered. Blocks weigh at most 22.5 kg, so no machine energy.
- **B2 / B3:** no rows.
- **C1:** diesel, because the blocks are bonded with mortar.
- **End of life:** NMD category 8, masonry (landfill 1 / recycling 99), using waste-concrete treatment proxies (TeR 5).
- **Unsure (most uncertain of the three):**
  - the binder share
  - processing energy, which is borrowed from concrete blocks
  - the end-of-life category: the EPD itself assumes incineration

## cork: expanded cork board (EN 13170), screened as exterior rainscreen cladding, outdoor, 40 years
- **Composition (S1):** 100 % cork, no binder (Amorim EPD HUB-0281).
- **A1–A3:** ecoinvent `cork slab` is resin-bonded (0.14 kg/kg of MF/UF/PF resin), so D1 is no. D5 was unclear, because no autoclave-expansion route was found. I took the conservative branch, D6 proxy: `market for cork slab` RER, 1 kg, TeR 4.
- **EPD check:** 0.959 vs. the ÖKOBAUDAT generic expanded cork at 0.512 (±50 %). **Fail, flagged, not changed.** The gap is the resin in the proxy. For comparison, Amorim HUB-0281 gives 0.720.
- **A4:** made only in ES among the five countries, otherwise Portugal → EU category: 1.5 tkm lorry and 0.1 tkm container ship (GLO).
- **A5:** prefab, 3 % waste. Boards weigh up to 14 kg, so no machine energy.
- **B2:** the function is outdoor, but neither the maker nor the EPD prescribes recoating → no rows.
- **B3:** no rows.
- **C1:** fixing could be adhesive or mechanical, so this was unclear → diesel (conservative).
- **End of life:** NMD category 52, bio-based insulation (landfill 5 / incineration 95) → 0.0975 tkm. Waste-wood treatments as proxies (TeR 5).
- **Unsure:**
  - the D6 proxy is the main weakness; a D5 route from raw cork plus steam would likely sit near the EPDs
  - C1 fixing method
  - the end-of-life category: insulation vs. cladding

## Files
`decisions.csv` (83 rows), `dataset_choices.csv` (33 rows), `material_definitions.csv`, `epd_check.csv`, `LCI_osb3.xlsx`, `LCI_hempcrete.xlsx`, `LCI_cork.xlsx`, `protocol_issues.md`.
