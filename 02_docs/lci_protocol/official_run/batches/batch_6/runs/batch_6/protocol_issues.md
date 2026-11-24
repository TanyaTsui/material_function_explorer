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
