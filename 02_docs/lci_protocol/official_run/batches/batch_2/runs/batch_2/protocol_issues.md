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
