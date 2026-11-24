# Protocol issues: run_B (12 Nov 2026)

These are the places where the protocol's wording allowed more than one reading. For each: the step id, what was unclear, and what this run did.

## General

1. **TiR (ROW table), every dataset.** The ecoinvent 3.12 import in the Brightway project has no "time period" field, so TiR cannot be read from the dataset. The protocol gives no conservative default for a score.
   *Did:* logged TiR = "unclear"; left TiR blank in the sheets; wrote DQR as "n/a". *Suggest:* read the time period from the ecospold files (or ecoQuery) when the database is imported, or set a default TiR.

2. **Rounding (Fixed settings: 3 significant figures) vs the A5 input "1 + loss".** At 3 s.f., 1.0309 and 1.0526 become 1.03 and 1.05, which changes the loss by up to 5 %. The protocol's own example writes 1.053.
   *Did:* wrote 1 + loss to 3 decimals (1.031 and 1.053); all other amounts use 3 s.f.

3. **D2 "no market → add an A2 transport row" for service rows.** For waste treatments, transport services and diesel this makes no sense, and C2 already covers transport to treatment.
   *Did:* added no A2 rows for service datasets. No material row needed A2, since all three found a market.

4. **D3 for treatment rows: a single country (CH) before GLO.** For waste wood incineration this picks the Swiss "municipal incineration FAE" (fly-ash extraction) dataset over the generic GLO "municipal incineration". The result follows the rule literally but may not be what was intended.
   *Did:* followed the rule (CH FAE). Sanitary landfill is also CH, chosen over RoW.

5. **D3 "global market groups are never used" vs GLO markets.** The ship, diesel and wood-chipping datasets exist only as GLO *markets*, not market groups.
   *Did:* treated GLO markets as allowed (rank 5). The lorry market group (GLO) was excluded.

6. **D4 for lorry: "else the first A–Z".** At RER there are 17 lorry markets. The first alphabetically would be "16-32 metric ton, EURO 3", an arbitrary choice.
   *Did:* chose "market for transport, freight, lorry, unspecified" RER as the variant that matches the protocol's unspecified "lorry". *Suggest:* name the lorry and ship datasets in the protocol.

7. **Recycling share in C3–C4 under cut-off.** The protocol asks for "one treatment row per share", but ecoinvent cut-off has no per-kg "recycling" treatment for wood or board. The waste-wood market (post-consumer) adds its own transport, which would double-count C2.
   *Did:* for OSB recycling, used a shredding service ("wood chipping, industrial residual wood, stationary electric chipper", +amount) as the C3 processing. The material then leaves without burden. The sign is positive, unlike the waste rows.

8. **Sign convention.** "Waste sent to treatment has a negative amount" fits waste-treatment datasets but not service inputs such as chipping.
   *Did:* treatment rows are negative and service rows are positive.

9. **S1 "median if several", across sources that differ in kind.** EPDs report water separately (Egger, Sonae) or inside the wood (Kronospan); some give ranges (Sonae, Schönthaler). Kronospan's shares add up to 100.5 %. The medians do not sum to 1.
   *Did:* merged water into the wood ("moisture counts with the constituent it is in"), used range midpoints, normalised Kronospan, then normalised the medians (sum 1.0029 → 1).

10. **STEP 3 "every EN 15804+A2 dataset in the category".** It is unclear whether generic or representative ÖKOBAUDAT datasets (Thünen OSB average, the generic expanded cork) count as "EPDs", and whether two density variants of one EPD count as 1 EPD or 2.
    *Did:* included the generic datasets and counted datasets. Hemp stone: 2 datasets from 1 EPD, so the ±50 % rule applied.

11. **TeR for rows of a built material (D5).** "Built materials score TeR = 3", but the ROW step says TeR is "read from the rule and the dataset" per row.
    *Did:* gave each constituent row the TeR of its own D1 to D4 path (1 for exact matches) and logged the material-level TeR = 3 in decisions.csv.

## OSB/3

12. **A4 · T2, "made in" a country.** Spain: Kronospan has announced an OSB line at Tortosa for 2026, but no start-up was confirmed. Italy: one poplar OSB plant (I-PAN, Coniolo); the latest evidence of production is a 2020 study.
    *Did:* counted IT and not ES (3 of 5 → yes). *Suggest:* define a recency requirement for the evidence.

13. **A5 · I1, typical piece.** The input says "standard thickness" without a value.
    *Did:* used 2500 × 1250 × 18 mm (SINTEF certificate for EGGER OSB 3), which gives 34.1 kg. Even 25 mm boards (47 kg) stay under 50 kg.

14. **C1 · X1.** OSB floor decks often have glued tongue-and-groove joints. The EPDs assume mechanical fixing and manual deconstruction.
    *Did:* answered no.

## Hempcrete

15. **S1, EPD gives only ranges** (hemp shiv 20–55 %, binder 45–80 %).
    *Did:* pinned the hemp share from the EPD's biogenic carbon (56.1 and 54.4 kg C/m³) divided by the ecoinvent hemp hurd carbon content (0.4548). Binder = dry density − dry hurd; water = equilibrium density − dry density. This is a calculation, not a stated share, and another run may take the range midpoints (0.375 / 0.625) instead. The undisclosed "hardener" in the binder is not separated.

16. **S1, "moisture counts with the constituent it is in".** The EPD footnote puts the moisture in the hemp shiv. The ecoinvent hurd dataset is at 2 % moisture, so the extra equilibrium water was written as a separate "water" row (tap water) to keep the mass balance.

17. **D5, processing steps with no dataset.** Mixing and pressing have no ecoinvent processing dataset, and D5/D6 are written for products, not steps.
    *Did:* D6 proxy. Took the energy inputs of "concrete block production" DE (0.002 kWh electricity + 0.0216 MJ diesel per kg; the EPD says the blocks are made on a concrete-block moulding machine), with TeR 5 because the main raw material differs. These are per kg of concrete block (density about 2,380 kg/m³). If the machine's energy is per batch volume, as the EPD suggests, per kg of hempcrete (405 kg/m³) it would be about 6 times higher. Air drying: no energy row.

18. **A5 · L1.** The example list has "blocks … placed dry" as prefab and "masonry laid with mortar" as in situ. Schönthaler blocks are laid with mortar.
    *Did:* in situ, 5 %. C1 · X1 follows (bonded → diesel).

19. **C2 · E1, "product type it is used as".** Hempcrete blocks are masonry ("metselwerk"), and that word appears in NMD categories 8, 32 and 40, but each of those is tied to a material.
    *Did:* no direct match → heaviest constituent (lime binder) → same main raw material → cat. 40 (calcium silicate, lime-bound units), 1/0/99/0. Categories 8, 32 and 76 give the same split. This conflicts with the EPD, which says hemp stones cannot be landfilled and go to incineration. Treatment datasets are D6 proxies (unreinforced concrete). Another run could also pick 52 (organic), which gives 5/95/0/0: a large difference.

20. **STEP 3 flag.** 0.649 against a band of 0.212–0.636 kg CO₂e/kg. Hydraulic lime dominates the result. No choice was changed (the check flags only).

## Cork board

21. **D1 "same product in the same state".** The input class is "expanded / agglomerated" and the standard is EN 13170 (binder-free expanded cork, ICB). The only ecoinvent dataset, "cork slab", is resin-bonded agglomerated cork (UF, MF and PF 14 %).
    *Did:* treated it as the same product in a glue-type variant (the protocol lists "glue type" under D4), giving TeR 2. Another run could answer D1 = no and build the board from "cork, raw" plus processing (D5). That route would remove the resins and probably land closer to the EPDs. STEP 3 flagged the gap (0.959 vs 0.256–0.768).

22. **A4 · T2 for a two-class name.** If "agglomerated" (resin-bonded) cork boards count, ES, IT and FR producers may exist. This run tested the EN 13170 product (expanded cork) → at most FR → no → EU (PT).

23. **A5 · L1 and C1 · X1 when the maker offers two fixing systems.** Amorim's MD Facade can be glued (adhesive mortar) or fixed mechanically.
    *Did:* logged "unclear" for both and took the conservative branch (5 % loss; diesel row).

24. **C2 · E1, two categories match.** Cat. 52 (organic insulation) names the material; cat. 55 (board material, e.g. cladding) names the use.
    *Did:* chose 52 (95 % incineration). *Suggest:* say whether the material or the use decides first.

25. **Waste dataset for cork.** No cork waste treatment exists in ecoinvent. Used waste wood, untreated (D6) with TeR 4, treating cork bark and wood as the same lignocellulosic raw material. That is debatable; TeR 5 is also defensible.

26. **B2 · M2.** No source prescribes recoating. The protocol's default (2 coats of 0.15 kg/m² every 10 years) only applies on a "yes", so no B2 rows were written. A coated cork-cladding variant could be a sensitivity case.

## Not checked

- NMD revised scenarios (Nov 2026, valid from 1 Jan 2027): not read (the protocol notes this).
- The full text of EN 300 (paywalled). S2 steps were taken from the EPD process descriptions instead.
