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
