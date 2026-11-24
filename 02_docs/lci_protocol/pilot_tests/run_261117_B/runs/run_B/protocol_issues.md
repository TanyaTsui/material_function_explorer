# Protocol issues — run_B (17 Nov 2026)

No material reached STOP (the mass CHECK passed for all three). Each note gives the step id, what was unclear, and what I did.

## A1–A3: dataset choice

1. **D1 (osb3): no tolerance for small extra inputs.** The ecoinvent `oriented strand board production` RER matches on wood, MDI and paraffin. It also has 5.2 kg/m³ of "chemical, organic" (0.86 % of mass), documented as "unspecified additives, dyes, flame retardants", and it has no MUF. Read strictly ("a dataset with an extra constituent … is not a match"), the answer is **no**, so I built OSB from scratch. A materiality threshold (e.g. < 1 % of mass) would make this diamond reproducible.
2. **D3: European countries that are not in the list.** The list is DE, FR, IT, ES, NL, AT, SE, FI, PL, CH. PT (cork) and GB (plastic incineration) are not in it. Read literally, they fall under "7 any other", which ranks *after* RoW. I applied it literally: `market for cork, raw` RoW instead of PT, and `treatment of waste plastic, mixture, municipal incineration` RoW instead of GB. For cork, RoW is also the lower-impact branch (0.030 vs 0.063 kg CO₂e/kg). Suggest: "any other single European country" as rank 4b, before GLO.
3. **D3 before D4 when the variants have different locations (osb3, "adhesive, PMDI/MUF").** MDI exists as a RER market, while MUF adhesive exists only as GLO. Applying D3 first leaves only MDI (4.18 kg CO₂e/kg; MUF is 2.91). A blended constituent ("PMDI/MUF") with no split has no rule. I took MDI for the whole 0.051 kg; it is half of the OSB result.
4. **D2 "market first" when the only market is GLO (paraffin).** `market for paraffin` GLO was taken over `paraffin production` RER, because D2 comes before D3. "Global market groups are never used" was read as applying to *market groups* only, not to GLO markets.
5. **TeR table for constituent rows.** The table gives 1 for D1 exact, 2 for D4 variant and 3 for "built from constituents". It is unclear whether an exactly matching constituent dataset gets 1 or 3. I used TeR 3 for all non-proxy rows of a from-scratch LCI and TeR 4 for proxies.
6. **TiR and DQR cannot be computed.** The Brightway import of ecoinvent 3.12 holds no time-period field (there are no `.spold` files locally). TiR and DQR are written as "n/a".
7. **Datasets not in kg (pulpwood, m³).** The input amount is in kg, so I converted it: 0.93 kg wood strands = 0.885 kg dry wood + 0.045 kg water (from the input note); 0.885 kg ÷ 451.04 kg dry mass per m³ (the dataset's `dry mass` property) = 0.00196 m³. The mass CHECK uses the kg equivalent. The protocol should say which property to use for the conversion.

## P1 / P2: machines

8. **A complete datasheet (power, throughput and mass) rarely exists for large panel-line machines.** Glue blenders, continuous presses and the thermal input of dryers are not published with all three values. What I did:
   - **drying strands:** electricity and mass from datasheets (median rule); heat from EU BREF WBP 2016 Table 3.2 (OSB drying, 0.1–0.4 MWh/m³; midpoint ÷ 600 kg/m³). This breaks "take every value for the step from that one machine".
   - **continuous hot pressing:** both rows from the BREF (OSB pressing power 0.01–0.06 MWh/m³). OSB pressing heat is "ND" in the BREF, so I used particleboard pressing heat (0.05–0.14 MWh/m³) as a proxy (TeR 4). There is no machine mass, so no P2 row.
   - **blending with resin:** the only data are power and throughput (Henan Pallet BS450). Strictly, the machine "is not used", and the BREF has no blending energy. I used its energy anyway and wrote no P2 row ("unclear": M must not come from another machine).
   - **autoclave expansion (cork):** no datasheet, no BREF and no study with an autoclave energy figure. Under "No machine found" I used a proxy that does the same kind of work with the same carrier: an EPS block moulding machine (steam expansion and fusing of granules into blocks), TeR 4. The resulting 0.40 MJ heat per kg is far below the ecoinvent cork slab sense-check value (4.92 MJ/kg).
9. **Which model of a manufacturer's range?** The protocol does not say. I took the largest model of each table, as industrial scale, and the midpoint of any range. This pushes energy and wear per kg down for small plants (e.g. the hempcrete mixer at 57.6 t/h). A rule is needed, such as "the model closest to X t/h" or "the median model".
10. **Fewer than three complete datasheets.** Only one was found for OSB cutting (Mingding DD saw), the autoclave proxy (Epsole ESB600V), the cork band saw (Fill speedliner 710) and the hempcrete mixer (Camelway JS3500); two for the block press. With two candidates the "median" is undefined, so I took the lower-energy one (the "unclear" rule). How many search attempts are enough before falling back should be defined.
11. **The dryer tables are probably mineral capacities.** Fote and CITICHL publish identical rotary-dryer tables (60.8–76 t/h for a 3.6 × 28 m drum); these look like coal or mineral throughputs. The wood-specific Jiutian dryer gives 8 times more kWh per kg. The median rule picked the low one. Electricity of drying is small next to heat, so the effect on the result is minor.
12. **Throughput conversions need assumptions the protocol does not give:**
    - t bone-dry/h (knife ring flaker) was taken as kg processed per hour.
    - Saws are rated by feed speed. I needed a cross-section: an 18 mm × 1.22 m OSB board, and a cork board of 0.30 m × 0.06 m (the saw's maximum).
    - m³/h for the mixer was multiplied by the product density (320 kg/m³, IsoHemp), not by the fresh-mix density.
    - For the dryer, output (dried) capacity counts as "kg processed".
13. **Machine life L has no source order.** I used the German AfA depreciation tables (BMF, sector tables): years × 5,000 h/yr. Mapping to entries is a judgement call (e.g. flaker → "Holzzerhacker" 4 y; autoclave → "Autoklaven" 10 y from the fish-processing table). Tax lives are probably shorter than physical lives. A fixed life table in the workbook would remove this variation between runs.
14. **The BREF values need a density.** I used 600 kg/m³ for OSB, from the input's source (Thünen ÖKOBAUDAT dataset), because material_overview gives no OSB density.

## A4, A5, C1

15. **A4 · T2: absence of evidence.** For OSB, manufacturers were found in DE and FR only. Plants in IT and ES could not be confirmed (Kronospan Italia is a sales address; no Spanish OSB plant was found). I answered **no**, giving EU transport (1.5 tkm lorry + 0.1 tkm sea), rather than "unclear", which would have given the lower-impact national 150 km. The test should say whether "not found" means no or unclear.
16. **A5 · L1 and C1 · X1 for insulation boards.** Cork boards are prefab but are often bonded with adhesive in ETICS. L1 lists "boards" as prefab but "tiles set in adhesive" as in situ. I logged both as unclear and took the lower-impact branch (3 %, no diesel).
17. **A5 lorry (loss) distance.** The protocol example uses 50 km. I used the route-weighted C2 distance of the material (OSB 92.5 km, cork 97.5 km, hempcrete 50 km), as A5 BLOCK says "C2 distance".

## C2–C4

18. **The mass of a waste item is unclear for constituents that include losses.** The cork input has 1.06 kg raw cork per kg, including 6 % production loss. Only 1.00 kg reaches end of life. C3–C4 says "constituent mass × route share", but the C3–C4 block only has 1 kg in. I used 1.00 kg (mass balance, and the lower-impact branch). bioc_inputs also uses 1.00 kg, as B2 asks.
19. **Recycling datasets with a product as reference.** `treatment of waste wood, post-consumer, sorting and shredding` produces wood chips (positive reference product), unlike the treatment datasets with −1 kg waste. A negative amount would subtract its burden, so I entered it as a positive amount. It also includes 50 km transport to the chipper, which double-counts C2.
20. **W1 and the "FAE" variants.** `… municipal incineration FAE` (CH) has a different name from the route words, so I treated it as not matching and used the GLO `… municipal incineration`.
21. **Water in hempcrete.** The fallback sheet puts water in the Mineral class, so 0.128 kg goes to inert landfill or concrete recycling. Physically, much of it has left as vapour.
22. **Adhesive and PU waste.** W1 found `treatment of waste polyurethane` but not "waste adhesive". I did not count a PMDI/MUF glue line as polyurethane, so it went to the W2 plastic fallback.

## Workbook and fixed settings

23. Names marked "check name" in fixed_settings (electricity, heat, machine) all exist exactly in ecoinvent 3.12. "diesel, burned in building machine" exists both as a production activity and as a market (GLO); I used the market (D2).
24. fixed_settings "ÖKOBAUDAT release" was "to fill": OBD_2024_III (ÖBD-Release vom 13.11.2026) was used. The ÖKOBAUDAT soda4LCA API was reachable from this machine, although the README says the site is blocked.

## ÖKOBAUDAT checks

25. **Hanfsteine (hempcrete):** the flow "Masse" property is 1.0 (a placeholder). I converted with the densities in the dataset names (equilibrium densities 405 and 430 kg/m³). Both EPDs come from one producer (Schönthaler, IT).
26. **EGGER OSB:** the flow name says 607 kg/m³ and the declared-unit text says 611 kg/m³. I used 611.
27. **Expanded cork:** the category holds one generic dataset (Sphera, 80 kg/m³), valid until 2026. A comparison against a single generic dataset is weak.
28. **CHECK 1** was not applicable to any material (D1 no for all).

## Run hygiene

29. I did not open README.md, PROMPT.md or compare_runs.py in the folder, so as not to read earlier results.
30. `search_ecoinvent.py` loads the full database for each query (about 7 s each). All searches were run with it in the `brightway_env` conda environment. The GWP calculation and dataset reads were read-only (`bw2calc.LCA` on an in-memory demand; nothing written to the project).
