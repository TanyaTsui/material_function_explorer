# batch_1

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


# batch_2

# Protocol issues, batch_2 (19 Nov 2026)

Step id · what was unclear or went wrong · what I did.

## Protocol ambiguities

- **D1 (oak) · "same delivered state".** ecoinvent has hardwood sawnwood only at u=10 % and u=20 %, generic hardwood (not oak). The input says 12 %, oak. I read "kiln dried, rough sawn (raw)" as the delivered state and answered D1 yes (TeR 1), logging the moisture and species gap. A stricter reading would send it to D1b (TeR 2); the dataset and the result would be the same.
- **D2 vs D3 (ceramic tile).** D2 says market first, D3 says a single European country comes before GLO. The only market for ceramic tile is GLO; production exists for CH. I logged "unclear" and took the lower-impact branch: production CH + A2 lorry row (0.41 vs 0.80 kg CO2e/kg). Please state which rule wins when a market exists only at GLO.
- **D3 vs "FAE" variants (waste incineration).** Municipal incineration datasets exist as GLO (no European country) and as "… FAE" for CH. D3 puts CH before GLO, so I used the CH "FAE" variants even though sheet `waste_fallback` names the GLO dataset without "FAE". Please decide whether FAE counts as a variant (D4) or as a different dataset.
- **W1/W2 for recycling of wood.** `treatment of waste wood, post-consumer, sorting and shredding` has wood chips as reference product (+1 kg), not a negative waste flow. A negative amount would give a credit. I wrote a positive amount (burden of sorting and shredding) and flagged it. This contradicts "waste has a negative amount" and the cut-off logic; please check. Same question for the plastics and metals "no row" rule.
- **C3–C4 and A5 waste mass.** "Constituent mass × route share" is ambiguous when the input includes manufacturing loss (cotton: 1.1 kg fibre per kg). I used the mass in 1 kg of product (1.0 kg), because the loss is not in the product.
- **P1 "three machines".** In this session the manufacturers' datasheets rarely give power, throughput and mass together (many PDFs did not load, several pages returned 403). Candidates are logged as found. The median rule could not be applied for most steps. Please say whether a step with a study value (no machine) should still get a wear row (I wrote none).
- **P1 batch machines / roles of motors.** Datasheets list several motors (heater, cooler, main). The protocol does not say which to add up. For the PVC mixer I took the median of three candidates by energy per kg; the motor roles of the ARGUS and ERK listings are not labelled.
- **P2 machine life.** No source gave a life in years or hours. I assumed 20 years × 5,000 h = 100,000 h (the protocol only gives the 5,000 h/yr default, not a number of years).
- **A4 · T2 for cotton canvas.** A single web query found NL only (TenCate) and a Spanish blend. "Unclear" resolved to no, then T3 yes (EU, 1.5 + 0.1 tkm). The "unclear → lower impact" rule would arguably pick T2 yes here (150 km, lower impact). I followed the evidence (fewer than 3 countries found), not the rule; a deeper search may flip it.
- **DQR.** Mass-weighted DQR (energy and wear rows carry kg processed) was not computed; the sheet carries per-row DQR and a simple mean in a note.
- **TiR.** I did not read the time period of each ecoinvent dataset; TiR = 1 for all datasets (release 3.12) except none changed. Note the ceramic tile dataset is an ecoinvent v2-era dataset (TiR would be worse).
- **CHECK 1/2/3 "every EPD in the category".** Only the EPDs I could reach were used (n = 1, 1, 0, 2). See epd_check.csv; ÖKOBAUDAT could not be searched by category from here.

## Input / workbook inconsistencies

- `material_overview` gives 17.97 kg/m² for ceramic tile; the ÖKOBAUDAT dataset page gives 18.65 kg/m² (conversion factor to 1 kg). I used 18.65.
- The ÖKOBAUDAT tile page shows total GWP A1-A3 (12.94 kg CO2e/m²), not GWP-fossil separately.
- `material_overview` row for PVC-U: the linked fintecnic EPD is a whole plastic window (per window with glazing), not a per-kg profile EPD. No ÖKOBAUDAT UUID was available; the check median uses two other PVC profile EPDs (One Click LCA entries, EN 15804+A1, EGE PROFIL 3.65 and Saray 4.71 kg CO2e/kg).
- `waste_fallback`: the workbook lists `treatment of waste reinforced concrete, recycling` for mineral recycling (used for tile, chalk, TiO2). Its output is a negative waste flow, so a negative amount is right there.
- Ceramic tile: the workbook has no glaze or kaolin dataset because the approximate match passed check 2 (not needed).

## Data limits (not protocol faults)

- Cotton canvas spinning: EDIPTEX Table 9.1 gives total energy per kg yarn including preparation; possible double counting with the carding step (not removed).
- Cotton weaving 3.2 kWh/kg: an industry article without method. Low confidence.
- Cotton wet finishing: only stenter drying heat (cotton SEC 4,304 kJ/kg water × assumed 0.6 kg water/kg fabric). Scouring/bleaching heat and finishing electricity are missing (lower-impact branch).
- PVC-U: cutting step has no rows (no datasheet); dry blending has no wear row (no weight); extrusion uses motor power only (ancillaries missing). All three bias the result low.
- Jwell pages returned 403 on re-fetch; the Jwell values come from a search summary of the vendor table. Check them before publishing.
- Heat rows stay on natural gas (limitation stated in P1).


# batch_3

# Protocol issues, run batch_3 (19 Nov 2026)

Materials: engineered_bamboo, osb3, hemp_fibre_mat, straw_bale. No material hit STOP (all CHECK mass sums = input).

## 1. P1/P2: the three-machine median rule could almost never be met (biggest issue)
- **P1, all machine steps.** Public datasheets rarely give power, throughput (kg/h) and net mass for the same machine. Throughput is the usual gap (bamboo splitters, presses, sanders, drum dryers, blenders). Several datasheet pages were also unreadable (403 from exapro; Alibaba pages empty; PDFs not text). Result: a complete (power, throughput, mass) triple was found for **one** machine only (Rieter UNIfloc A 12, hemp fibre opening). The "three candidates, take the median" rule was therefore not applied anywhere; the candidates found are logged with the fields they lack.
- **What I did** when a step had no complete machine: (a) the EU BREF (Wood-based Panels 2016, Table 3.2) where it covers the same operation (bamboo hot pressing); (b) a mixed-supplier combination, flagged proxy TeR 4 (bamboo splitting); (c) otherwise **no rows**, logged as "no machine found", following the "unclear → lower impact" rule. Steps without rows: bamboo boiling/steaming, drying, sanding, planing; hemp soda impregnation, carding/air-laying, thermal bonding oven, cutting. This biases the LCI low, mostly for hemp (the bonding oven is the main heat user) and bamboo (drying and boiling heat). **Please decide** whether "no machine found" should mean "omit" or "use a proxy"; the protocol text ("closest machine type that does the same kind of work") says proxy, but no proxy with a complete triple was available either.
- **Suggestion:** allow the energy of a step from a published unit-process or BREF value per kg/m³ as a normal route, not only as a fallback after three datasheets; or add a table of reference machines to the workbook (as the old AR0 to AR13 archetypes did).
- **Throughput at what operating point?** Datasheets give "up to" ratings. I used the maximum (Rieter 2,400 kg/h). The Rieter page and an older leaflet disagree (2,400 vs 2,000 kg/h); I used the page. The protocol does not say which to take.
- **Heat vs electricity for machines that use both (kilns, presses):** BREF gives OSB pressing heat as "ND"; I used particleboard pressing heat as a proxy. The protocol does not say which sector value to use when the product's own is missing.
- **P2 machine life:** datasheets never give hours. I used the life declared by the ecoinvent machine dataset itself (25 years, a rock crusher) × the protocol default 5,000 h/y = 125,000 h. The protocol's "years from the source" has no source for most machines. Wear rows are tiny (≈ 3×10⁻⁵ of GWP-fossil for bamboo and hemp, far under the 1–2 % flag).
- **P2 when P1 used the BREF:** the BREF has no machine mass, so no wear row can be formed (bamboo hot pressing). The protocol does not cover this case.
- **P1 amount for drying (OSB input note "0.885 × (0.80 − 0.03)")** the step amount is 1, but the note looks like a water mass. Not needed in batch_3 because OSB matched exactly, but it is unclear whether the throughput should be of wet or dry material.

## 2. D1: exact match and the "same constituents" test
- OSB: the ecoinvent dataset has MDI + another organic chemical + paraffin; the input has "adhesive, PMDI/MUF" 5.1 %. Constituents match in kind, shares differ (3.9 % vs 5.1 % adhesive). The test text ("extra or missing constituent") does not say how much share difference is allowed; I answered yes.
- Straw bale: ecoinvent "straw" is a co-product of cereal production with baling inside. Polypropylene twine (0.2 %) is missing, so D1 = no by the letter; D1b = yes (main constituent straw). An exact-match reading would also have been defensible; the result of check 2 is a low ratio either way.
- Bamboo: ecoinvent has only semi-products (pole, flattened bamboo, woven mat); D1b test 1 "same product and delivered state" fails, so no approximate match. Fine, but note that a stand-in (flattened bamboo) was never considered by the test.

## 3. D3 / D4
- **D3 for bamboo:** no European or GLO bamboo dataset exists; the order says "RoW" before "any other", and RoW exists, so RoW (a weighted average of BR, CN, CO, PH) is used. Reasonable, but the actual supply to the MOSO board is CN.
- **D3 tier 1 vs 2 for straw:** 'market for straw' has an Europe-without-Switzerland dataset, while 'straw, stand-alone production' has RER. Both are tier 1/2 of the location order. D4 then picks the first A–Z name (plain straw). The protocol does not say whether location or variant is decided first when two products tie on location rank.
- **D3 for waste:** the wood-landfill, wood-recycling and plastic treatments exist only for CH and RoW; the incinerations for GLO, CH (as "… FAE"), GB. D3's list has CH last among countries but before GLO, so CH is taken. GB is in no tier of the list (falls into "other"). "FAE" (CH) is a different variant of municipal incineration (D4 not defined for waste).
- **D5 / PROXY:** hemp bicomponent polyester fibre → "fibre, polyester" (GLO); PP twine → PP granulate. The state entering the factory (fibre vs granulate) is the tolerance of "same raw-material class".

## 4. TeR/GeR/TiR scoring
- TeR for a constituent row that matched in D5 is not defined by the table (TeR 1 = D1 exact, 3 = built from constituents). I used TeR 1 for a plain D5 pick, 2 where a D4 variant choice was needed (straw), 4 for proxy.
- TiR: the Brightway project does not expose dataset time periods, so TiR = 1 was assumed for every ecoinvent 3.12 dataset. DQR therefore underestimates.
- DQR is written per row; the mass-weighted DQR over the rows is not computed in the sheet.

## 5. W1 / W2 waste
- **Exact match (OSB):** the protocol says the product itself is the one waste material, but the sheet `waste_fallback` has no row for the product "OSB". I used the class of its main constituent (wood) and the wood fallback (W2).
- **The fallback sheet names a recycling dataset ("treatment of waste wood, post-consumer, sorting and shredding")**, which exists in 3.12 (CH, RoW) but its reference product is wood chips (positive), not a waste: the sign convention "waste sent to treatment is negative" is therefore ambiguous for this dataset. I used the negative amount like the other rows.
- The mineral recycling fallback "treatment of waste reinforced concrete, recycling" does not exist in 3.12 (only "concrete, not reinforced, recycling"). Not needed in this batch (route 52 has recycling 0).
- Reuse: no row, so the 5 % reuse share of bamboo (category 34) is not in the C3–C4 rows and the C3–C4 mass sums to 0.95 for that material. That follows the protocol; the model should know.
- The A5 end-of-life rows carry the lost kg (3/97) split by constituent and route. The protocol says "as C3–C4" but does not say whether the A5 loss uses the C2 lorry distance for every route; I did, weighted by share.

## 6. ÖKOBAUDAT checks
- The ÖKOBAUDAT service API (oekobaudat.de/OEKOBAU.DAT/resource/datastocks/...) was reachable and gave all EPDs; "latest release" = OBD_2024_III (last data stock in the list; the stock list has no dates). The README says the site is blocked, but the API worked.
- **Category choice is not defined** (e.g. which EPDs count as "straw bale": I took bale and blown straw EPDs, and excluded binder-bonded straw boards, plasters and generic datasets without a GWP-fossil value; for hemp I took the two hemp-fibre mat EPDs and excluded hemp-lime blocks). Medians are sensitive to this with n = 2.
- **No ÖKOBAUDAT EPD for laminated bamboo**: "no check possible" per protocol. The input itself is sourced from the MOSO EPD, which is not in ÖKOBAUDAT; I quote it as information only (0.436 kg/kg fossil A1–A3, vs our 0.433).
- Units: some EPDs are per m² (HemKor), per declared unit of 36 kg (HempFlax, ÖKOBAUDAT lists the reference unit as kg with mass 36), or per m³; converted with the grammage/density in the dataset.
- Straw: our ecoinvent value is low because straw is a cereal co-product; both routes (approximate 0.40×, built 0.43×) fail. REVIEW keeps the built LCI (closer). The protocol's A5/A4 chain is not affected.
- **Hemp passes check 3 (1.33×)** partly because several energy steps carry no rows; the pass should not be read as validation of the energy side.

## 7. A4 / A5 / C1 tests
- T2 needs a named manufacturer with link in each of ≥3 countries; the web search gave few such pages. OSB: DE and FR confirmed (and trade press naming DE, RO, PL as main producers) → no. Straw bales: **unclear** (farm-baled product with no manufacturer list) → lower-impact branch (yes, 150 km). I used "unclear" only where evidence was missing both ways; a reviewer may prefer a fixed rule (e.g. "no named manufacturer found = no").
- I1 for bamboo is borderline: typical MOSO panel (2,440 × 1,220 × 7–40 mm, 700 kg/m³) gives 49 kg at 23.5 mm, 83 kg at 40 mm. "Typical delivered piece" is not defined (mid-range thickness used).
- Straw bale: bale length (0.8–1.0 m) is not in the source; piece weight 13–17 kg is an assumption.
- L1: straw bales are stacked dry (prefab, 3 %); plastering is a separate material.

## 8. Other
- The ecoinvent OSB dataset is per m³; the A1–A3 row amount is 1 kg ÷ 607 kg/m³ (wet mass property of the dataset). The protocol says "amount from the input in kg", but the dataset unit is m³: a conversion rule is missing.
- Brightway Excel: rows that need no entry (unresolved steps, reuse, no-row routes) are written as type "note" with amount 0, so they are visible; remove them before import if the importer does not accept them.
- `search_ecoinvent.py` only prints name-substring matches; to find waste-treatment datasets by route I also scanned names in bw2data (read-only), as noted in the log.


# batch_4

# Protocol issues, batch_4

| Step | What was unclear | What I did |
| --- | --- | --- |
| D1 | No materiality threshold for "extra constituent". Concrete: slag ~1 %, filler, admixture 0.07 %. AAC: process water 0.184 kg/kg, ~0.09 kg of it stays in the product. Plywood: tap water 15 % is process water. | Read strictly: a material that stays in the product and is not in the input = extra. Concrete and AAC: D1 no, then D1b yes. Plywood: D1 yes (process water not a constituent). The dataset chosen is the same either way, but TeR and the check differ (1 vs 2). Please add a threshold and a definition of process water. |
| D1 / unit | Matched datasets in m3 (plywood, concrete). | 1 kg = 1 / wet mass (823 and 2414 kg/m3, dataset property); amount written in m3. |
| TiR | The time period of an ecoinvent 3.12 dataset cannot be read from Brightway. | TiR = 1 for all ecoinvent 3.12 datasets. Probably too generous. |
| CHECK 1/2/3 category | "Product's category" is not defined. Concrete has 289 A2 EPDs in Beton (all strengths). Plywood category Sperrholz holds a CLT EPD ("best wood CLT"). Porenbeton holds insulation board and granulate. | Concrete: EPDs with "C30/37" in the name (63 with a value, median 0.0728 kg/kg). Plywood and AAC: the full ÖKOBAUDAT category as filed. Sensitivities are in epd_check.csv. The ÖKOBAUDAT API (release OBD_2024_III, 13.11.2026) was read directly. |
| P1 / three machines | Datasheets almost never give kg/h for batch machines (mixers, presses, autoclaves, dryers), and rarely both machine mass and power. A complete set of three manufacturers was not found for any step. | Concrete mixing: three machines (Sicoma, MEKA, Liebherr); cycle time 90 s from the Sicoma sheet borrowed for the other two. Mycelium: see below. Please say whether borrowed cycle times are allowed. |
| P1 mycelium: pasteurising | Only a craft/commercial 150 L autoclave (Rootlab) has power, load and cycle time. Hokken GXMQ (industrial) lacks cycle time and mass. | Rootlab used, proxy TeR 4, electricity only (electric heating); no wear row (mass missing). A study (Grimm et al.) suggests autoclave heat ~4.3 MJ/kg dry substrate, ~10x higher; I took the lower value (rule: unclear -> lower impact). |
| P1 mycelium: mixing | Three candidates from one manufacturer (Magaldi, continuous ash/humidifier paddle mixers); substrate density 150 kg/m3 from a retailer. | Median (Mixer 700) used, TeR 3, flagged. |
| P1 mycelium: incubation, moulding | No industrial machine with power and throughput found (only lab incubators; presses without cycle time). | "unclear", no rows (lower-impact branch). Impact is under-stated. |
| P1 mycelium: drying | Dryer figures taken from a search-result summary of the STELA ligna 2019 brochure; the PDF could not be read (units of "heat" inferred as MW); dryer mass not found. kg processed = 1 but a dryer works per kg of water. | Used kg water evaporated as kg processed (as the plywood note does for drying); TeR 4; no wear row. This row (4.39 MJ heat) is 36 % of the mycelium result: please verify. |
| P2 life | No machine life on any datasheet. | 8 years (BMF AfA-Tabelle Baugewerbe, mixers) x 5,000 h/y for all machines: assumption. |
| W1 / product as waste | When the LCI is one dataset (plywood, AAC) the "waste material" is the product, which is not in the `constituents` column of waste_fallback. | Plywood: class Wood, wood-based. AAC: class Mineral (AAC is also listed under Gypsum and Metal). |
| W2 recycling of wood | `treatment of waste wood, post-consumer, sorting and shredding` has reference product wood chips (+1 kg), not a negative waste service. | Used a positive amount (burden of sorting and shredding); a negative amount would be a credit. Other waste rows are negative. |
| W1 cement | "waste cement in concrete and mortar, sorting plant" is a recycling-route word, but the waste is hardened cement. | Accepted as the match for the cement constituent, recycling route. |
| D5 aggregates | No ecoinvent product "aggregates" (gravel and sand). | Proxy gravel, crushed (CH), TeR 4. |
| Water as waste | Water has a waste_fallback entry (Mineral) although it does not become waste. | Followed the sheet (tiny mass). |
| Concrete C30/37 vs "30MPa" | Variant naming differs (cylinder vs cube strength). | 30MPa taken as C30/37 (D4). |
| A4 T2 | "At least 3 of 5 countries" with one company in two countries (Garnica ES and FR). | Counted per country plants; plywood also via the ÖKOBAUDAT German-average EPD. |
| Piece weights | Dimensions assumed for AAC (625x250x300 mm) and mycelium panel (1200x600x50 mm, 150 kg/m3). | Both far under 50 kg; flagged as assumptions. |
| Machine search | Manufacturer pages gave data in different forms (HP, yd3/h, litres, m3/batch). | Converted as in the P1 table. |


# batch_5

# Protocol issues, run batch_5 (hempcrete, gypsum board, toughened glass, PTFE-coated glass fabric)

No material was stopped (the CHECK "rows sum to input" passed for all four).

## Tools and sources: what was and was not possible

- **P1/P2 three-machine rule could not be met for most steps.** The web search returned summaries, not datasheets. A machine with kW, kg/h *and* net mass from three manufacturers was found for none of the 14 steps. What was done instead is logged per row in `dataset_choices.csv` (`machine_candidates`, `values_as_found`): the candidates found, the one used, and every value that is an ASSUMPTION is marked as such. Steps built from a vendor/study figure instead of a datasheet carry `proxy` and TeR 4. **Decision for the protocol:** say what to do when the datasheet lacks the machine mass (most listings do). Machine wear is below 1 % of GWP in every material here, so the effect is small, but the rule as written excludes nearly every machine.
- **Throughput in kg/h is rarely on a datasheet** (cutting lines give m/min, tempering furnaces m²/h, presses blocks/h, looms m/min). Conversions needed an area mass or a cut length per m². The protocol table covers m³/h, t/h and batches only. Added assumptions: glass 6 mm = 15 kg/m², 2 m of cut per m², mixer cycle 3 min.
- **Machine life** is never on a datasheet; I used 15 years × 5,000 h = 75,000 h (assumption), and 18 years × 8,760 h for the float furnace (Glass for Europe: 16–20 years, 24/7).
- **Installed power ≠ running power.** The tempering furnace is taken at installed power (841 kW), which overstates energy (the source itself says installed power is unrelated to consumption). Left unchanged, as P1 asks for the rated value.
- **ÖKOBAUDAT could not be queried** (API returns 403; the site is blocked). The median is taken from the one EPD PDF I could read per material: BV Gips plasterboard EPD (EN 15804+A2) and BV Flachglas ESG EPD (EN 15804+A1, not A2; GWP total, no fossil split). "n_epds = 1" therefore means "one read", not "one in the category". The protocol says to take every A2 dataset in the category; this was not possible. The release is logged as "not verified".
- **The gips.de link in the input (BV Gips EPD) returned 404.** The same BV Gips EPD (EPD-BVG-20210344-IBE1-EN) was read via a Danogips copy.
- PDFs could not be read by the Read tool (no poppler); pypdf was installed to a temporary folder outside the project to extract the text of EPDs (downloads in `runs/batch_5/downloads/`).

## Ambiguities in the protocol

- **D2 vs D3, market GLO.** `market for gypsum plasterboard` exists only as GLO (a *market*, not a market group), and the production datasets are CH and RoW. D2 says market first, D3 says single European countries come before GLO and "global market groups are never used". I took the GLO market (D2 wins; it is not a market group). A production dataset CH plus an A2 row would have been the other reading. The approximate match failed CHECK 2 anyway, so it did not reach the sheet.
- **D1: how strict is "extra constituent"?** The ecoinvent plasterboard contains 0.016 % glass fibre and 0.013 % silicone that the input does not list. Read strictly (as I did) it is not an exact match, which sends nearly every ecoinvent product to D1b. A tolerance (e.g. constituents under 1 %) would be a sharper test.
- **D1/D1b for toughened glass.** ecoinvent has flat glass and a tempering process separately; the protocol has no way to combine "dataset + process" so it goes to the full build, which then lacks the carbonate process CO₂ (see below).
- **Gypsum: calcined gypsum constituent vs calcining step.** The input lists the constituent "gypsum (calcined …)" 0.93 *and* a step "calcining gypsum to stucco" (0.93). I read the constituent as mineral gypsum entering the factory (`market for gypsum, mineral`) and put the calcining energy in the step. `market for stucco` would have double counted. Please say which is intended.
- **Glass batch vs product.** Input constituents (batch shares) sum to 0.996 per kg of glass, while the step "batch mixing" processes 1.2 kg per kg. The two are inconsistent as masses: the constituents are shares of the batch, so per kg of glass the batch is about 1.2 kg. The protocol check ("rows sum to input") passes (0.996), but the LCI only carries 0.996 kg of raw materials for 1 kg of glass.
- **Glass process emissions are not covered by any protocol step:** CO₂ released from soda ash, dolomite and limestone in the melt (about 0.17 kg CO₂ per kg glass) is neither in the constituent datasets nor in a machine row. It is the main reason the glass LCI is far below the EPD. Not corrected (checks never change numbers).
- **Water, and waste treatment of water.** Hempcrete lists water (0.128) as a constituent, so it gets an end-of-life item per route (W2 mineral fallback). Most of it evaporates in reality; the protocol (each constituent × route) treats it as waste mass.
- **W2 fallback gives odd treatments:** hemp shiv recycling → wood sorting and shredding (the sheet says "as wood"); lime, water, soda ash and silica sand recycling → "treatment of waste reinforced concrete, recycling" (the sheet says "as mineral"). Followed unchanged.
- **W1 for plasterboard** (not used in the final LCI): ecoinvent names the landfill route "collection for final disposal" for waste gypsum plasterboard; the protocol's route words (sanitary / inert material landfill) do not match.
- **A5 loss rows.** The protocol says the lost kg goes to waste (lorry + end of life) but does not say which module the end-of-life rows belong to. I put them in the A5 block (rows `A5 lorry (loss)` and `A5 end of life: …`), with the same datasets as C3–C4.
- **Diesel dataset.** The sheet says `diesel, burned in building machine` (GLO, MJ); ecoinvent has both this activity and `market for diesel, burned in building machine`. I used the activity named in the sheet.
- **Heat dataset name.** fixed_settings: `market for heat, district or industrial, natural gas, Europe without Switzerland` exists as written (MJ). Electricity: `market group for electricity, medium voltage`, RER exists. Machine: `market for industrial machine, heavy, unspecified` RER exists (2.52 kg CO₂e per kg).
- **The sheet `carbon_archetypes` lists water as non-biogenic and hemp shiv as "cellulose fibres and stalks" with a default moisture of 0.10.** Hempcrete has water as a separate constituent, so applying the default moisture to hemp shiv would count its moisture twice. Noted in `bioc_inputs.csv`; no moisture given.
- **T2/I1 evidence is thin.** Plant lists per country could not be completed with the search tool. T2 for hempcrete and glass is logged "unclear" and takes the lower-impact (national 150 km) branch as the protocol says; I1 for hempcrete and PTFE is "unclear" (piece weight not found) → no machine row.
- **DQR.** TiR set to 1 for every ecoinvent 3.12 dataset (release year 2025) since the dataset reference years were not read; GeR for CH counted as "one country" (2).
- **GeR for market GLO datasets** (silica sand, glass fibre, PTFE, plasterboard): GLO markets are the only market locations, so rank 3.
- **PTFE dispersion** was taken as PTFE polymer (solids) because the input says "(solids)".
- **Heat rows stay on natural gas** (limitation noted in the protocol); the dip-coating/sintering oven is gas-fired in the heat-balance estimate.

## Result worth a second look
- **PTFE-coated glass fabric: 99.7 kg CO2e (fossil) per kg**, 98.3 of it from `market for polytetrafluoroethylene` (151 kg CO2e/kg) × 0.65 kg. The input share (0.65 PTFE, 0.35 glass; both marked "assumption") drives this; Sheerfill-type membranes are mostly glass fabric by mass. No ÖKOBAUDAT check exists. Not changed; please verify the input shares.


# batch_6

# Protocol issues, run batch_6 (mdf, clay brick masonry, structural steel, PVC-coated polyester)

Date of run: 2026-11-19. Each note: step, what was unclear, what I did.

## Rules that conflict or are open to two readings

1. **D2 "market first" vs D3 location order** (all materials). When the only market datasets sit in a poor location (clay brick: markets EC and RoW only; steel: market GLO only; polyester fibre: market GLO only) while a production dataset exists in RER, D2 and D3 give different answers. I applied the rule literally: market first, then the first location among the markets. Result: `market for clay brick` RoW (0.332 kg CO2e/kg) instead of RER production (0.250). A statement of which of the two wins would remove this. The sentence "Global market groups are never used" also does not say whether a GLO *market* (not a market group, e.g. steel, structural, 100% scrap) is allowed; I allowed it.
2. **W1 location with "FAE" variants.** `treatment of waste ... municipal incineration FAE` exists only for CH, the plain name only for GLO. D3 ranks CH before GLO, so I took the CH "FAE" dataset (a Swiss fly-ash-extraction variant). The name does not match the route words exactly. Same for waste brick (`sorting plant`, Europe without Switzerland, chosen over `recycling`, CH): the W1 route words allow "recycling, sorting or crushing", and D3 picked the better location, not the better-named dataset.
3. **W1 recycling dataset with a positive reference flow.** `treatment of waste wood, post-consumer, sorting and shredding` (CH) produces wood chips (+1 kg) and takes waste wood as input; all other treatment datasets have a production amount of -1 kg of waste. Writing "negative amount" for it would give a credit for chips. I wrote the amount **positive** (burden of the sorting and shredding). The protocol's sign rule does not cover this case.
4. **W2 landfill for waste brick / mortar.** The ecoinvent waste-brick and waste-cement datasets have no "landfill" route words (only `collection for final disposal`, `sorting plant`, `recycling`), so W1 = no and W2 gave `treatment of inert waste, inert material landfill` (CH).
5. **D1b test 1 for clay brick masonry.** "Same product and delivered state": ecoinvent has `clay brick` (a brick, no mortar); the input is masonry as laid with 20 % mortar. I answered no (different product and state). If the intended reading is "same main constituent is enough", the answer would be yes and the LCI would be 1 kg of brick without mortar. Please decide.
6. **D1 for structural steel.** `steel, structural, 100% scrap` (EAF) exists but is cast steel without hot rolling; `steel, low-alloyed, hot rolled` has rolling but a global mix (74 % converter). I answered D1 no, D1b yes (CHECK 2 failed: 4.07x the median), then built from scratch.
7. **Steps already inside a constituent dataset (P1, "blue path").** The input lists steps (brick: clay preparation to firing; steel: EAF melting; polyester: melt spinning) that the chosen constituent dataset already contains (documentation says so). I wrote no rows for them and logged it. For proxy constituents (wood chips for fibres) the rule does not apply, so all six MDF steps got rows; but then "green wood chips" plus a flash-drying step could double count a little drying. The input for brick is built so that every step is contained in the brick dataset; the step list then has no effect.
8. **Pairing "no energy" tag.** None of the four materials has a note starting with "no energy".

## Missing or unreachable data (P1, P2)

9. **Three machines with datasheets (power, throughput, mass) cannot be found for large process machines**: refiner, flash dryer, continuous press, pre-steaming bin, hot-rolling mill, air-jet loom, coating/gelling oven, lacquering line. Manufacturers do not publish all three. I logged the candidates found, and used:
   - EU BREF energy per tonne (WBP 2016 Table 3.2/3.3; FMP 2022 Tables 9.1/9.22), midpoint of the range, for steaming, refining, drying, pressing, hot rolling;
   - a machine mass from the nearest datasheet-like source where one exists (refiner: Andritz TX68 51.6 t; press: supplier line 32 t; chipper 7 t; sander 4.5 t), with throughput from BREF typical capacity (refiner 30 t/h), a 900 m3/day press report (27.6 t/h) or an assumed feed speed (sander 10.85 t/h);
   - for steaming, drying, hot rolling and weaving: no mass found, so no machine row (logged as unclear, lower-impact branch). Bounds (0.01-0.1 % of GWP) are in `decisions.csv`.
   The protocol does not say what to do when only energy (no mass) exists. All such rows carry TeR 4 and "proxy".
10. **Coating and gelling oven, lacquering (PVC-coated polyester):** no source with energy per kg or kW and kg/h was found. Following "unclear: lower-impact branch" I wrote no energy rows. The PVC LCI therefore leaves out the most energy-intensive step; its pass in CHECK 3 (0.83x) should not be read as validation.
11. **Weaving energy** is a vendor-blog range (1.2-6 kWh/kg, midpoint 3.6), the weakest source in the run.
12. **Machine life**: no source states a life. I used 20 years x 5000 h/y = 100 000 h (the protocol's 5000 h/y; 20 years is my assumption). Wear share is 0.012 % for MDF, so it does not matter.
13. **Values taken from search-result summaries.** Several machine values (chipper listings, Heesemann sander, Jiangsu press line weights, Siempelkamp 900 m3/day) come from search-result summaries and were not read on the original page. They should be spot-checked before use.
14. The **PDF of the BREF could not be read by WebFetch**; I extracted the text locally with pypdf from the downloaded file (reading the downloaded copy only).

## Checks against ÖKOBAUDAT

15. The workbook README says ÖKOBAUDAT is blocked from the workspace. The soda4LCA API (`/OEKOBAU.DAT/resource/processes`) was reachable by curl and gave GWP-fossil A1-A3 (A2 datasets). The dataset pages answer only with a login for some older versions.
16. **"Product's category" and "latest release" are not defined.** I used: MDF = uncoated/raw MDF, EN 15804+A2, one per EPD (the older duplicate version 8bd1172b of the German average left out; coated and A1-only datasets left out): 5 EPDs; brick = `Mauerziegel (ungefüllt)` A2 (filled and facing bricks left out): 1 EPD, brick only although our kg contains 20 % mortar; steel = `Baustahl: Profile und Stabstahl` A2 (galvanised and painted left out): 1 EPD; PVC-coated polyester has no category in ÖKOBAUDAT, I used `PVC-Dachbahnen` (roofing sheet, 1.5 kg/m2, A2): 1 EPD. Release label: the API default stock on 2026-11-19.
17. **Per m3 / per m2 EPDs need a density or area mass.** MDF densities come from the datasets (800, 736, 716.7, 637, 737.5 kg/m3). The Sonae Arauco density (800) is from the dataset page, not the XML.
18. **Exact match unit.** ecoinvent MDF is per m3; "amount = input amount in kg" does not apply, I used 1 kg = 1/684 m3 (wet mass property of the dataset).
19. **MDF check 1 and check 3 both fail** (1.89x and 1.77x), so the REVIEW keeps the built LCI (closer). Clay brick fails CHECK 3 (1.58x) with only one route tried; kept and flagged.

## Other

20. **T2 evidence.** Web search with a few queries rarely confirms plants in 3 of 5 countries. Found: MDF 3 (DE, IT, FR) = yes; steel 2, brick 2, PVC membranes about 2 = logged "unclear" and the national branch (150 km, lower impact) taken. A stricter evidence standard (e.g. a list of EPD owners per country) would make T2 reproducible.
21. **Piece weights** (I1, X1) rely on assumed formats: MDF board 2440 x 1220 x 18 mm (39 kg; the 2800 x 2070 mm board is 110 kg, which would flip I1 to yes), brick 365 x 248 x 249 mm, IPE 200 6 m, 50 m roll. These are assumptions, flagged in `decisions.csv`.
22. **Dataset name for diesel.** `fixed_settings` says `diesel, burned in building machine` (without "market for"); I used that activity (GLO, production), not the market.
23. **cff_inputs.csv** shares are written in % as in sheet `nmd_eol` (not fractions); the template has no unit.
24. **bioc moisture.** The input has no moisture field; MDF's note says "wood ~82 % + water 5-7 %". I wrote 0.073 (dry basis, 0.06/0.82) for the wood fibres and flagged it in the note; the archetype default is 0.12.
25. **Search tool.** `search_ecoinvent.py` only finds by words in the name. For waste datasets I used a read-only name-prefix match in bw2data (`treatment of waste <material>`), and bw2data to read documentation and exchanges (D1, D5, P1 documentation checks). Nothing was written to the Brightway project.
26. **TiR** is set to 1 (2020+) for all ecoinvent 3.12 datasets without reading each dataset's reference year.
27. **MDF wood proxy and moisture.** The chosen wood-chip dataset is per kg dry mass while the input amount (0.88) includes about 6 % water; the amount was kept as in the input (CHECK sums to 1.00).


# batch_7

# Protocol issues, batch_7 (glulam, CLT, soft wood fibre board, aluminium extrusion)

Run date 2026-11-19. Each note: step id, what was unclear, what I did.

## P1 · ENERGY (the main one)
- **Three complete datasheets per step were not findable.** For the 10 machine steps of the two built materials I searched for three machines per type with power, throughput and mass. Datasheets almost never give all three: refiners give motor power and capacity but weight only in tonnes; dryers and saws give kW or kg but no throughput in kg/h; ageing ovens and presses give no output. At most one candidate per step was complete (Andritz TX68 refiner). Throughput in kg/h is the missing value for nearly every machine type. The median-of-three rule could not be applied as written.
- **What I did:** used the protocol's own fallback (EU BREF, then studies): EU BREF Wood-based Panels 2016 Table 3.3 for refining and drying (midpoints of the ranges), BREF Table 3.2 MDF pressing for steam-air curing; aluminium-guide.com and an EU CORDIS project for gas billet heating (175–215 kWh/t) and ageing (75–85 kWh/t); the US DOE bandwidth study (2016) for extrusion electricity (derived: 0.196 kWh/kg). Where vendor kW existed (dosing 2.2 kW, saw 13.5 kW) I divided by the line capacity of a 6 t/h dry-process insulation line (Ziegler/Grenzebach). All these rows are marked proxy, TeR 4. For billet heating and ageing I applied the median rule on energy per kg across three sources (not three manufacturers' datasheets). Suggest: let the protocol say explicitly that "energy per tonne" from a BREF or study replaces power ÷ throughput, and that the three-machine rule applies only where datasheets exist.
- **Heat carrier for the aluminium steps.** The usual European billet furnace and ageing oven are gas-fired, so they got heat rows (natural gas, as fixed in the workbook). Induction billet heaters use electricity; both options are logged as candidates. P1 does not say how to choose the carrier when machines of one type use different ones.
- **Double counting risk (aluminium).** The DOE extrusion figure covers the whole plant (press, pumps, stretcher, saw). I used only its electricity share for "extrusion" and wrote no rows for "cutting". The protocol has no rule for a source that covers several steps. The DOE fuel figure (1.7 kWh/kg, US average) is six times the EU gas figures for billet heating plus ageing and was not used.
- **The "extrusion" step is marked "assumption" in the input** (and "drying fibres", "curing with steam-air mixture" for the fibre board). I treated it as any other step.
- **Hydrophobing and "adding resin, forming the mat"** (fibre board): no machine energy source exists for dosing and forming. I used a 2.2 kW dosing unit from a food-industry listing as the closest kind of machine. The forming station (fans) is missing, so these two steps are probably too low. Neither step is marked "no energy" in the input.

## P2 · WEAR
- **Machine mass with throughput found only for the refiner and the dryer** of the fibre board (Andritz TX68, 51.6 t, 1,500 admt/d; VetterTec tube bundle dryer, 36 t, 3,200 kg/h evaporation). The dryer figure is water evaporation, used as kg/h of fibre; a flash tube dryer would differ. All other steps have no wear row (logged). Wear share of the fibre board, 0.033 % of GWP-fossil A1–A3, below the 1–2 % limit in the protocol. For aluminium the share is "not computed" (no wear rows).
- **Machine life.** P2 gives a default of 5,000 h per year but no default for years. I assumed 20 years (100,000 h) and flagged it. Please add a default and a source.
- **Rule conflict.** P2 says never take M from a different machine than the one used for power and throughput. With BREF energy per tonne there is no machine, so the wear machine is by necessity a different one. Logged as proxy.

## D1 / D1b
- **Glulam, D1.** The ecoinvent "average glue mix" has 0.07 % phenolic resin besides MUF and PUR. Read strictly ("an extra constituent is not an exact match"), D1 would be no and D1b yes (same dataset, TeR 2). I answered D1 yes because the adhesive class matches the input (PUR/MUF) and the phenolic share is negligible. The check passes either way, but the answer decides TeR. Suggest a minimum share (e.g. 1 % of mass) below which an extra constituent is ignored.
- **CLT, D1.** Constituents match but the shares differ (ecoinvent MUF about 0.8 %, input MUF 0.03 %). The protocol asks for the same constituents, not shares, so D1 yes.
- **Aluminium, D1b.** The only candidate (section bar extrusion, aluminium) is a process that takes the metal as an input; test 2 ("main constituent of the dataset") has no clear answer. I answered no. A rule for process-only datasets would help.
- **Fibre board.** "Same delivered state" is not decidable for soft fibreboard: ecoinvent mixes wet and dry processes, the input is dry process.

## D2–D4 / D5
- **Units.** ecoinvent wood boards are in m³, the input is in kg. I wrote the amount in m³ = 1 kg ÷ wet mass (property of the dataset: 444, 443, 157.7 kg/m³). The protocol says "kg per kg"; it does not say how to convert. Please state it.
- **D3 and "market" at GLO.** The aluminium wrought-alloy market (GLO) is the only dataset of the alloy besides scrap-only RER datasets. D3 rule 5 gives GLO. This is the whole result for aluminium (12.8 kg CO₂e/kg) and it is far above EPD profiles with high scrap shares. The input has no scrap share for the alloy, so I did not apply the 70–80 % scrap in the EPD; nothing in the protocol says whether to.
- **"PUR resin".** The real binder of the fibre board is pMDI. The ecoinvent PUR dataset is "polyurethane adhesive" (GLO). No rule for choosing between an MDI precursor and the cured resin.
- **Moisture in the fibre amount.** "softwood fibres (fir/spruce) 0.945" has no moisture note while the datasets are "measured as dry mass". I took 0.945 as dry mass unchanged.

## Checks
- **Which EPDs are "in the category".** The OEKOBAU.DAT classes mix products: CLT is under 3.1.04 (BSH) and 3.1.05 (solid wood panel); the aluminium profile class holds façade systems, panels, coated and anodised profiles, and three EMERUS ultra-low-carbon entries with values of 14,277–42,401 (per kg; certainly a unit error). I kept plain profiles and the CLT-type panels and logged the exclusions. The fibre board class has two entries of the same EPD with identical values. Different readers will get different medians. Suggest listing the datasets of each category in the workbook.
- **Release.** The workbook says "latest release; to fill". I used the newest data stock listed by the API, OBD_2024_III. Datasets without EN 15804+A2 were not in that list for the picked classes, so no extra filtering was done (the compliance label was read from the list for each).
- **Review tie.** For the fibre board the two failed routes are 1.701 (built) and 1.704 (approximate) times the median. The built one is closer by 0.003, which is within the uncertainty of the BREF midpoints. The rule keeps the built LCI.
- **CLT ratio 1.44** is just inside the +50 % edge.

## A4 / A5 / C1
- **T2 evidence.** For ES, IT, NL the searches were not exhaustive; "3 of 5" was reached for all four materials with sourced manufacturers. Links are vendor and trade-press pages.
- **I1/X1 piece weights.** No datasheet gave typical piece dimensions: I used the sourced density with an assumed format (glulam, CLT, boards, profiles) and logged that. Outcomes do not depend on the exact format except for aluminium profiles (large structural sections can exceed 50 kg).
- **A5 loss rows.** The protocol says the lost kg gets a lorry row and end-of-life rows; it does not say which block carries them, nor the distance when the route is mixed. I put both in the A5 block, with the route-weighted C2 distance and the C3–C4 datasets, scaled by the loss.
- **X1 "bonded".** Glulam and CLT are not bonded on site, but both are over 50 kg per piece, so X1 is yes.

## C2 / C3–C4 / W1
- **Waste material of a single dataset.** For glulam and CLT the product itself is the waste material (protocol). No such waste dataset exists, so I used the Wood class of waste_fallback (W2) and marked it proxy.
- **Recycling dataset sign.** "treatment of waste wood, post-consumer, sorting and shredding" has a positive reference output (wood chips), so the amount is written positive. A negative amount would give a credit. The protocol says waste has a negative amount; this dataset does not follow that convention.
- **Location of waste datasets.** By the D3 order the Swiss datasets (CH) win over GLO and RoW; the "municipal incineration FAE" activities are Swiss-specific. Aluminium incineration has a Europe-without-Switzerland dataset, so that one was taken.
- **W1 "market for waste" only if it splits like NMD** — no such market was used.
- **"adhesive, PUR/MUF" and "PUR resin".** There is no "waste adhesive". For the fibre board PUR resin I used waste polyurethane (W1); for the glulam and CLT the waste is the whole product (above).
- **Reuse (5 % for glulam and CLT)** gets no row, as the protocol says.

## Module D files
- `bioc_inputs.csv` moisture: only where the input note gives it (glulam 11.5/86.9 = 0.1323, CLT 10.70/88.28 = 0.1212, dry basis). The glulam note says "atro 86.9 % + water 11.5 %"; the sum is 98.4 %, so moisture of dry basis is the ratio.
- For the fibre board the dataset (kept LCI is built) means the waste items are constituents, so wood fibre, PUR resin and paraffin are listed separately.
