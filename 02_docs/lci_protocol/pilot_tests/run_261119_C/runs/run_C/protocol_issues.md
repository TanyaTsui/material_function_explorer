# Protocol issues and unclear points, run_C (2026-11-19)

Each note: step id, what was unclear, what I did. Nothing in the input or the workbook was changed.

## Cross-cutting

1. **P1 · three machines with all three values.** Datasheets of industrial batch machines (mixers, autoclaves, saws) rarely give throughput in kg/h.
   - *Mixers:* MEKA and CO-NELE list batch volume, power and weight, but no cycle time. The Sicoma datasheet (90 s cycle, 40 batches/h) was used for all three. This is an assumption; the protocol does not say where a missing cycle time comes from.
   - *Presses:* output is in blocks/h of concrete blocks. I converted with the hemp block density (320 kg/m3, IsoHemp via naturamater) and a solid 400x200x200 mm block, which is not what the machine presses. Should the protocol say which block size and density to use?
   - *Ranges:* where a datasheet gives a range (Bruks hammer mill 2–4 t/h and 75–110 kW; UMP 37/45/55 kW; Hongfa 15–20 s) I took the midpoint.
2. **P2 · machine life.** No datasheet gives life. The protocol only says how to convert years to hours, not what to do when neither years nor hours are given. I assumed 10 years x 5,000 h = 50,000 h for every machine. The wear rows come to 0.009 % (hempcrete) and 0.69 % (cork) of GWP-fossil A1–A3, so this does not matter for the outcome, but a default life in `fixed_settings` would make runs comparable.
3. **P1 · tie in the median.** Autoclave candidates Systec HX-200 and ConductScience BIO-0153 have identical energy per kg (0.391 kWh/kg). I took the first (Systec). The rule has no tie-break.
4. **P1 · "no machine found" for the cork autoclave and the cutting step.** Cork autoclaves are not sold with datasheets. I took the closest type (steam autoclave, but sterilisation autoclaves; band resaw) and marked both proxy, TeR 4. Cycle 20 min (literature, APCOR/Springer) + 10 min load/unload (assumption), load = chamber volume x 115 kg/m3 (Amorim EPD). Result 1.41 MJ/kg heat, far below the 4.92 MJ/kg in the ecoinvent slab. The protocol's "sense check" figure suggests the proxy is too low, but nothing was changed because of it.
5. **P2 · cutting machine mass.** The Wood-Mizer HR120 datasheet has no weight. I used 832 kg from the HR115 (same family), which breaks the rule "never take M from a different machine". The alternative was to write no wear row, which breaks the rule that every step with energy rows has one. Effect on GWP: 1.5e-5 kg CO2e/kg. Only two candidates (not three) had power and feed, so I took the one with lower energy per kg (benefit of the doubt).
6. **P1 · datasheet sources not readable.** Several PDFs (Priorclave, ConductScience, Liebherr) were not machine-readable here, and two directindustry pages returned 403. For UMP MM-2000, Priorclave 700 L, Systec HX-200 2D and ConductScience BIO-0153 the values come from search-engine excerpts of the datasheet. They are marked as such in `values_as_found`. Please check them before the paper.
7. **W1 · sign convention.** The protocol says waste to treatment has a negative amount. That holds for datasets whose reference product is a waste (production exchange −1). The W2 fallback for wood recycling, `treatment of waste wood, post-consumer, sorting and shredding`, has a *positive* production exchange (wood chips), so a negative amount would give a credit. I used a positive amount for it. Its only waste input is −0.0015 kg of chrome-preserved building wood per kg, so the dataset hardly "takes" the waste; its burden is for producing chips. Please confirm that this is the dataset you meant.
8. **C2 / W1 · what mass is a waste item?** The protocol says "constituent mass x route share". For cork the constituent is 1.06 kg (6 % loss in manufacturing), but 1 kg reaches end of life. I used 1.0 kg (the amount in `bioc_inputs.csv`). For hempcrete, water (0.128 kg/kg) is a waste item through the Mineral class of `waste_fallback`, which lists "water". Treating the water as inert waste is unphysical; I followed the sheet.
9. **A5 · distance for lost kg.** The example uses 50 km. I used the share-weighted C2 distance (e.g. 92.5 km for OSB, mostly incinerated), since the lost kg follows the same route. Tell me if the example (50 km) is meant literally.
10. **A5 block · EoL rows of the lost kg.** The protocol says "end of life as in C3–C4" for the lost kg. Written as `A5 end of life: <constituent> × <route>` rows, amount = loss x constituent mass x share. Reuse and metal/plastic recycling have no rows.
11. **D3 · locations not in the list.** `market for cork, raw` exists for PT and RoW. PT is a European country but not in the D3 country list (DE, FR, IT, ES, NL, AT, SE, FI, PL, CH), so literally RoW (rank 6) comes before "any other" (rank 7). I took RoW. This is the lower-impact choice here (0.030 vs 0.063 kg CO2e/kg raw cork), but a Portuguese cork supply chain is better described by PT. Also for waste: CH (a listed country) is taken before GLO, and "Europe without Switzerland" before CH.
12. **D3 · European market group vs RER.** Rank 1 (market group) and rank 2 (RER) overlap; for tap water the RER market group exists and also a Europe-without-CH market. I took the RER market group (rank 1).
13. **TeR for constituent rows (ROW).** The table has "3 = built from constituents". I gave constituent rows found by D5 TeR 1 (a direct dataset match) and only machine rows TeR 3. Unclear which was intended.
14. **TiR.** Not defined per dataset in ecoinvent; I gave all ecoinvent 3.12 rows TiR 1 (2020+), including waste datasets that are older in substance.
15. **fixed_settings · diesel.** `diesel, burned in building machine` exists as an activity and as a market (both GLO). I used the activity named in the sheet. The other fixed datasets (electricity RER group, heat Europe w/o CH, machine RER, lorry RER, sea GLO) exist with the names written.
16. **ÖKOBAUDAT access.** README says the site is blocked; the ÖKOBAUDAT service API worked (datastock OBD_2024_III, 4,322 processes, accessed 2026-11-19), so the medians use the actual release and values, not search snippets. Per-kg conversion uses the mass in the unit or description (OSB 607/630/601/600 kg/m3; Hanfstein 405/430; cork 80).
17. **Check scope.** "Every EN 15804+A2 dataset in the product's category": I used the ÖKOBAUDAT classification (OSB-Platte 4 datasets; Hanfsteine 2; Expandierter Kork 1). I did not add EPDs from other registries (e.g. the Amorim cork board EPD, 0.72 kg CO2e/kg, EPD Hub, is not in that category in ÖKOBAUDAT).
18. **Moisture in bioc_inputs.** The input note for OSB strands gives water 4.5 % and wood 88.5 %, so I wrote u = 0.0508 (dry basis) instead of the archetype default 0.12. Other rows have no moisture in the input.
19. **Brightway runs.** pypardiso is not installed (slow solves, same results). Scores: ecoinvent-3.12 `EF v3.1 / climate change: fossil / GWP100`, cut-off database, no premise scenario.

## OSB/3

- **D1.** The dataset has MDI only (3.0 %); the input has PMDI/MUF at 5.1 %. I counted the adhesive as the same constituent (isocyanate-bonded OSB) and logged the difference. A strict reading (MUF is missing) would send OSB to D1b; the check passed anyway (0.89x).
- **D1 unsanded/delivered state.** The ecoinvent product is the uncoated board at factory gate; no sanding step is mentioned. Accepted as the same delivered state.
- **A4 · T2.** DE (EGGER Wismar), IT (I-PAN, Coniolo; current operation not verified) and ES (Kronospan, Burgos; evidence is a product page) give 3 of 5. FR (EGGER Rion-des-Landes makes particleboard) and NL: none found. Borderline; the unclear-rule would also give "yes" (lower impact).
- **W1.** There is no waste dataset for OSB (glued board). `waste wood, untreated` is solid untreated wood, so I answered W1 no and used W2 (same datasets, proxy TeR 4).

## Hempcrete

- **D1 / D1b.** No dataset at all (0 hits), so both are no without comparing constituents.
- **Air lime** is mapped to `hydrated lime, packed` (RER) and **natural hydraulic lime** to `hydraulic lime` (RER). The ecoinvent hydraulic lime is limestone + clay fired in a coal-fed kiln, not necessarily a natural hydraulic lime (NHL). It is 66 % of the GWP, so this choice drives the result.
- **CHECK 3 fails at 1.509x** (limit 1.5). This is a knife-edge: a 1 % change in any large item flips the answer. The two EPDs are from one producer (Schönthaler, IT). `material_overview` marks the hempcrete shares "to be sourced" (maybe volume, not mass); I took them as given.
- **Density 320 kg/m3** (IsoHemp, naturamater) is used only for machine throughput; the ÖKOBAUDAT EPDs are 405/430 kg/m3 at equilibrium moisture.
- **A4 · T2.** DE evidence is a distributor entry (von Hanf, Itzehoe) plus a DIBt approval; FR Vielle Matériaux (BIOSYS); IT Schönthaler. ES, NL not found. Borderline.
- **A5 · I1 / C1 · X1.** Block weight needs a face height (not on the page); 600 x 300 mm assumed. Max 20.7 kg either way.

## Cork

- **D1 no, D1b yes, CHECK 2 fail (1.87x), CHECK 3 fail (0.228x), REVIEW keeps the built LCI** (distance 0.772 vs 0.871). With no exact-match LCI the review compared two LCIs.
- **D1b.** The "same main constituent" test is satisfied trivially (raw cork 1.06 of 1.20 kg inputs). The dataset binder is 0.14 kg/kg (14 %); with the old 10 % limit it would have been rejected.
- **CHECK 2 / 3 against one EPD.** The only ÖKOBAUDAT dataset in "Expandierter Kork" is the Sphera generic (0.512 kg CO2e/kg, 80 kg/m3). It is generic data, so the ±50 % band around it is not very informative.
- **The built LCI sits far below the median** mainly because the proxy autoclave gives 1.41 MJ/kg of heat (see 4 above) and raw cork from the RoW market is low. Not changed (rule: checks never change a number).
- **A4 · T2 / T3.** No producer found in DE, FR, IT, ES, NL (only Portugal), so EU transport (1,500 km lorry + 100 km sea). Absence of evidence only.
- **C1 · X1.** Cork boards are sometimes glued; I assumed dry/mechanical fixing (no diesel row).
