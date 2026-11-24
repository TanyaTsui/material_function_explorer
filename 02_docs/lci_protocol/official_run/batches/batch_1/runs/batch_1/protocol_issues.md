# Protocol issues, batch_1

Format: step id · what was unclear · what I did. Dates 2026-11-19. Materials: sawn_softwood, cork, fibre_cement, stone_wool (no STOP for any material).

## Input and workbook

1. **INPUT, stone_wool: constituent shares sum to 0.997, not 1.** (0.37 + 0.59 + 0.035 + 0.002.) The protocol says shares sum to 1 before the run. The CHECK ("rows sum to the input masses") passes at 0.997, so no STOP. I used the masses as given; waste items use the same masses.
2. **INPUT, cork: mass basis of waste items.** The input has 1.06 kg raw cork per kg board (0.06 kg is a factory loss). W1 says "constituent mass × route share". For `bioc_inputs.csv` I used 1.0 kg (losses excluded, as B2 says). For the waste items I used the product itself (1 kg), since the kept LCI is a single dataset. For a built LCI, the 1.06 would double count the factory loss at end of life; the protocol does not say which to use.
3. **Workbook links point to older ÖKOBAUDAT releases.** The latest release is OBD_2024_III (13 Nov 2026). The material_overview UUIDs for sawn softwood (98fe03e2…), fibre cement (26a2ed2d…) and stone wool (eca9691f…, an EN 15804+A1 dataset) are old versions: in OBD_2024_III the same datasets have other UUIDs (2bd4c91f…, 161e1abd…, 732dcc2d…). Only cork (fdbe82c6…) matches the latest release. I used the latest release via the ÖKOBAUDAT soda4LCA API (`/resource/datastocks/bca3670a-8dcf-44d0-be1f-0633d9ba1a75`, read-only).
4. **`fixed_settings` status "check name".** Checked with Brightway: electricity `market group for electricity, medium voltage` RER, heat `market for heat, district or industrial, natural gas` Europe without Switzerland, machine `market for industrial machine, heavy, unspecified` RER, lorry RER, sea GLO all exist exactly as written. Diesel exists as `diesel, burned in building machine` (GLO) and `market for diesel, burned in building machine` (GLO); not needed here (I1 and X1 were no for all four).

## A1–A3 · D1 to D4

5. **D1 tolerance on "same constituents / same delivered state" is not defined.** Sawn softwood: ecoinvent has u=10 % and u=20 % kiln-dried raw sawnwood, no u=12 %. I answered yes (2-point moisture gap, same state "kiln dried, rough sawn"). A stricter reading gives no. Fibre cement: the ecoinvent tile has no pigments or water and 0.91 cement vs 0.714, so I answered no, then used D1b. Where the line sits (how large a constituent difference makes it "not the same") changes the route.
6. **D2 vs D3, fibre cement.** A market exists only as GLO ("market for fibre cement facing tile, large format", 99.2 % RoW + 0.8 % CH production). The CH production activity is a single European country (D3 rank 4), which comes before GLO (rank 5), but D2 says market first. "Global market groups are never used" names *groups*; this is a GLO *market*. I used the GLO market (literal D2). The CH production dataset (1.02 kg CO2e/kg) would also pass CHECK 2.
7. **D3 order puts RoW before "any other", so raw cork comes from RoW.** `market for cork, raw` exists for PT and RoW. PT is not in the D3 country list, so it ranks 7 ("any other"), after RoW (6). Literal order gives RoW, although cork is grown in Portugal (PT 0.0626 vs RoW 0.0305 kg CO2e/kg). The built cork LCI was not kept, so this did not change the result.
8. **D3 and the "FAE" incineration variants.** `treatment of waste wood, untreated, municipal incineration` exists as GLO and as `… municipal incineration FAE` (CH). D3 ranks a single country (CH) before GLO, so I took the CH FAE variant. The name differs from the route words in W1 ("municipal incineration"); I treated FAE as a variant.
9. **D4 and TeR.** Sawn softwood: beam and board both fit "rough sawn"; I took beam (first A–Z), TeR 2 (different variant). The protocol also says an exact match scores TeR 1, so the row could be 1 or 2.
10. **Unit of the exact-match row.** The row amount is "the amount from the input (kg)", but the ecoinvent sawnwood dataset is in m³. I converted with the activity property `wet mass` (464.64 kg/m³ at u=10 %): 1 kg = 0.00215 m³. The protocol does not say how to convert for datasets not in kg.
11. **TiR cannot be read from the Brightway data.** The ecoinvent activities in the project carry no time-period field. I set TiR = 1 for all rows (ecoinvent 3.12, 2020+). Several datasets are legacy ecoinvent v2 modules (cork slab, fibre cement tiles, stone wool), so TiR is probably worse for them.

## CHECK 1, 2, 3 (ÖKOBAUDAT)

12. **"The product's category" is not defined.** ÖKOBAUDAT classes mix products: 3.1.01 holds softwood and hardwood, fresh, dried and planed timber; 1.3.12 holds facade panels, cement boards, roof slates and PP fibres; 2.1.03 holds stone wool insulation and Rockpanel facade panels. I used the product-matching subset and recorded the rest:
   - sawn softwood: 6 softwood datasets, dried, not planed (median 0.209 kg/kg). All 11 A2 datasets with a mass of class 3.1.01: median 0.153; same outcome (pass).
   - fibre cement: 7 facade-panel datasets (median 1.08). With the 2 AQUAPANEL boards (n=9): median 1.06; same outcome.
   - stone wool: 3 ROCKWOOL average datasets + SeaRox/ProRox (median 1.19); Rockpanel excluded.
   - cork: only one A2 dataset in 2.9.01.
13. **Mass per declared unit is missing in the API for several EPDs.** ROCKWOOL datasets: density taken from the declared bulk density in the EPD text (159/99/38 kg/m³). Area-based EPDs: grammage from the flow data (MatML `Grammage`). EGGER "Schnittholz" appears twice (two versions); counted once. The Rubner EPD "Schnittholz" (AT) has no mass in the API and is a planed product; excluded.
14. **Stone wool has no unambiguous exact/approximate stand-in.** D1b test 2 (same main constituent) fails because the input's main constituent is the cement-bonded briquettes (0.59 > basalt 0.37). I followed the test literally. If briquettes counted as "cement + basalt-class mineral", the answer could be yes.

## P1 / P2 (machines)

15. **The three-machine rule cannot be met for most process steps.** Only hammer mills (cork grinding) have public datasheets with power, throughput and weight. For cork autoclave expansion and block cutting, and for cupola melting, fiberising and curing oven (stone wool), no datasheet gives all three values (searches in EN/PT; band saws gave kW and weight but no throughput; Grenzebach gives cupola melt rate 6–8 t/h but no kW). Fibre cement steps were not researched because the approximate match passed CHECK 2.
16. **Ranges instead of values.** Ottevanger and Bruks-Siwertell publish ranges per series (kW, t/h, kg), not per model. I used midpoints and logged them as such. The "median of three" then rests on midpoints.
17. **Unresolved steps.** Cork autoclave expansion and cutting: logged "unresolved", no rows. The built cork LCI is therefore incomplete; its CHECK 3 value (0.0355 kg/kg) is an artefact of missing steps. The protocol has no state for "step could not be resolved".
18. **BREF fallback has no machine, so P2 cannot run.** For stone wool I used EU BREF Glass Manufacturing 2001, Table 3.29 (7–18 GJ/t finished product; shares melting 30–70 %, fiberising 25–35 %, curing 25–35 %, others 6–10 %). Midpoints sum to 118 %, so I normalised. No machine mass or life exists, so no wear rows. The BREF energy is booked as heat from the fixed natural-gas dataset although the cupola burns coke, and "others" (services) as electricity assigned to the cutting step. These are my choices; the protocol does not say how to split BREF energy over carriers.
19. **Machine life.** Datasheets give no life. P2 says "if the source gives years, multiply by hours/year". I took 25 years from the documentation of the ecoinvent machine dataset ("service life declared by the producer: 25 years") × 5,000 h/yr = 125,000 h, which is not a datasheet source of the machine used.
20. **Rated power vs real use.** Hammer-mill rated power ÷ rated throughput is a catalogue ratio; throughput is for a 10 mm screen and a stated material (not cork).

## A4, A5, C1

21. **T2 needs 3 of 5 countries, but the search finds few producers.** Sawn softwood: DE (EGGER, ÖKOBAUDAT EPD), FR (NEOFOR Bonneville), IT (a general sawmill; kiln drying not confirmed) = 3 → yes, evidence is thin for IT. Cork: only FR and ES confirmed → no (then T3 yes). Fibre cement and stone wool: only one country confirmed with a source → logged "unclear", lower-impact branch (national, 150 km).
22. **Piece weights (I1, X1).** The protocol says take the typical piece weight from the datasheet or EPD. The ÖKOBAUDAT datasets give density or grammage but no piece format, so formats are my assumptions (joist 50×200×4,000 mm; cork board 1000×500×100; fibre cement panel 1250×2500 mm; stone wool board 1200×600×100). Large fibre cement panels (3 m+) can exceed 50 kg; I1/X1 would then flip to yes (diesel rows).

## C2, C3–C4

23. **Waste material when the A1–A3 row is a single dataset.** "The product itself is the one waste material", but W2 is keyed by constituent. Cork slab: mapped to the class of `raw cork granules` (Other plant-based → as wood). Fibre cement: W1 found `treatment of waste cement-fibre slab, recycling` (yes); for landfill, `… collection for final disposal` is a collection step without landfill route words, so W2 (mineral: inert material landfill).
24. **W1 recycling for wood.** `treatment of waste wood, post-consumer, sorting and shredding` has wood chips as reference product (not a waste). I used it as the recycling dataset (the same dataset is the W2 entry for wood).
25. **C2 lorry row.** I wrote one lorry row per block with the NMD-share-weighted distance (wood 90 km, cork 97.5, fibre cement 50, stone wool 52.5). The protocol says "lorry tkm per route share"; one summed row gives the same impact.
26. **Mineral class W2 for stone wool incineration is "—".** 5 % of stone wool incinerates (NMD 78); no row written for basalt and briquettes (mass 0.0185 + 0.0295 kg per kg lost to nothing). The mass leaves the system without burden (lower impact).

## Tools

27. **search_ecoinvent.py** prints very long lists for broad terms. For exact-name checks and location comparisons I also used read-only bw2data scans (names and exchanges). No write to the project. Queries are recorded in `search_terms`.
28. **ÖKOBAUDAT access.** The workbook README says ÖKOBAUDAT was not reachable from the workspace; here the API at oekobaudat.de worked with a normal User-Agent. I read it only.
29. **Rounding.** 3 significant figures for reported values (CSV checks, summary). LCI sheet amounts keep more digits (e.g. 0.00215221 m³) because 3 s.f. would change the mass by 0.1 %.
30. **Side effect.** I installed `pypdf` into `/tmp/pylib` (outside the project and the Brightway environment) to read downloaded PDFs. Nothing else outside `runs/batch_1/` was written.
