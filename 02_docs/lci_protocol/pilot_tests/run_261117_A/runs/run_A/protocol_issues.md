# Protocol issues — run_A (17 Nov 2026)

Each entry gives the step id, what was unclear, and what I did. No material hit STOP.

## Input and workbook

1. **INPUT / input_definitions.** The sheet uses the material name (`OSB/3`), while `material_definitions.csv` uses the id `osb3`. The sheet is also in a different order (cork and hempcrete come before OSB/3), and its title says "30 materials" where the protocol says 28. The constituent and step values are the same, so I worked from the CSV.
2. **INPUT, hempcrete.** In `material_overview`, the note says IsoHemp's 80/9/11 shares "look like volume" and that the naturamater mass shares should be checked against the EPD. I used the input as given (0.342 / 0.108 / 0.422 / 0.128). The 53 % lime binder share is the main driver of the hempcrete result (see 19).
3. **INPUT, OSB/3 "drying strands".** The note is a formula, `0.885 × (0.80 − 0.03)`, but the amount is 1. This is irrelevant here because D1 = yes (no P1 rows), but the note should say what the formula is for.
4. **fixed_settings, release.** `ÖKOBAUDAT release` is marked "to fill". The ÖKOBAUDAT API lists `OBD_2024_III` as its newest data stock, so I used that for every check.
5. **fixed_settings, names marked "check name".** All of them exist under the stated names and locations. The electricity, heat (Europe without Switzerland) and machine datasets are as written. For diesel, ecoinvent has both `diesel, burned in building machine` (GLO) and `market for diesel, burned in building machine` (GLO). I used the first, which is the name in the sheet.

## A1–A3

6. **D1, OSB/3.** The ecoinvent OSB dataset lists MDI, paraffin, wood, and 5.2 kg/m³ of an unspecified "chemical, organic". I read MDI + "chemical, organic" as the input's "adhesive, PMDI/MUF" and answered **yes**. A stricter reader could call the organic chemical an extra constituent, answer no, and build from scratch. The D1 test should say how generic placeholder inputs are treated.
7. **ROW, D1 = yes.** The rule says "amount = the amount from the input", but for a finished product the input gives no product amount, and the dataset is in m³. I wrote 1 kg converted with the dataset's own property (wet mass 607 kg/m³), i.e. 0.00165 m³. The protocol should say this explicitly for datasets not in kg.
8. **D3, location list.** PT is not in the country list (DE, FR, IT, ES, NL, AT, SE, FI, PL, CH). For raw cork, which has only PT and RoW datasets, the literal order puts PT under "any other" (7), after RoW (6), so I took **RoW**. RoW is also the lower-impact branch (0.0305 vs 0.0626 kg CO₂e/kg). For a Portuguese product this is odd. Suggest adding "any other European country" before GLO.
9. **ROW, TeR for constituent rows.** In the TeR table, row 3 reads "built from constituents". It is unclear whether an exactly matched constituent row scores 1 or 3. I used TeR 1 for exact constituent matches, 3 for P1/P2 rows, and 4 for proxies.
10. **ROW, GeR for CH.** CH is in the D3 country list but is not an EU country. I scored CH datasets GeR 2 ("one EU country").
11. **ROW, TiR and DQR.** The Brightway import does not keep ecoinvent's time period. TiR could only be read where the comment text states a period: hemp hurd 2021–2023 → 1; raw cork 2012 yield table → 3. For everything else TiR is blank, so DQR cannot be computed. Suggest keeping the time period at import, or a lookup table.
12. **P1, ranges.** Many datasheets give ranges (power 45–55 kW, throughput 1.5–2 t/h, feed 3.5–35 m/min, steam 25–45 kg/cycle). The protocol does not say which operating point to use. I used the **midpoint** of every range, for power and throughput alike. For three-option lists (Weinig: 80/120/150 m/min; 45/55/75 kW) I used the middle option.
13. **P1, m³/h conversion for hempcrete.** The mixer and block press give m³/h or blocks/h, and P1 asks for the "density of the material as processed". I found no source for the density of fresh hemp-lime mix, so this is **unclear**. I used IsoHemp's bulk density at delivery, 355 kg/m³, which is the higher of the two IsoHemp values (dry density is 320) and so the lower-impact choice. Block machines were compared on the 400 × 200 × 200 mm hollow-block row (10 per mould), converted with the block envelope (0.016 m³) because hempcrete blocks are solid.
14. **P2, machine life.** No datasheet gives life, and the protocol names no source for L. I used the German BMF AfA depreciation tables (useful life in years) × 5,000 h/yr (the protocol's default):
    - Zwangsmischer: 6 y
    - Steinpressen: 10 y
    - Schlagkreuzmühlen: 7 y
    - Bandsägemaschinen: 6 y
    - autoclave proxy: 10 y (see 15)

    Suggest fixing one life source in the workbook.
15. **P1 "no machine found", cork autoclave expansion.** No datasheet, BREF or accessible study gives power and throughput for a cork autoclave. I applied the proxy rule with **EPS steam block moulding machines**, which do the same work (steam expansion and fusing of granules into a block in a mould) with the same carrier. Candidates: Epsole ESB200V, Milon ML-2000VS, Zhongji EPSSM2000. The median is **Milon ML-2000VS**, marked proxy, TeR 4. Further choices:
    - Steam kg was converted to MJ with the enthalpy of evaporation at 7 bar (2.065 MJ/kg). This is unclear: total enthalpy is 2.762 MJ/kg, and I took the lower-impact branch.
    - Life is unclear: 10 y (Härtekessel, autoclave) or 5 y (Schaumstoffverarbeitungsanlagen). I took 10 y, the lower-impact branch.
    - Cork density for throughput is unclear: 80 kg/m³ (ÖKOBAUDAT generic) or 115 kg/m³ (Amorim ICB EPD). I took 115, the lower-impact branch.

    **Sense check (P1 note):** our rows give 0.262 MJ heat and 0.036 kWh electricity per kg of board, against 4.92 MJ and 1 kWh in the ecoinvent cork slab. The EPS proxy (4-min cycles at about 110 °C steam) clearly understates a cork autoclave (300–370 °C superheated steam, 17–30 min, per APCOR). Per the rules, nothing was changed. The three-machine catalogue rule is weak for batch thermal processes.
16. **P1, band saw throughput.** Resaw datasheets give feed speed and maximum cutting section, not kg/h. I used feed × max height × max width × density, i.e. the machine's capacity rather than the actual block section, so it is an upper bound on throughput. The Weinig PowerSplit datasheet gives only a twin-version weight, so I used the twin (2 heads × 55 kW) consistently for that candidate. The Dom mixer datasheet says "35 m²/h", which I read as m³/h.
17. **P1, median with heat and electricity.** For the proxy autoclave I chose the median on total energy per kg (heat + electricity, both in kWh).

## Checks

18. **CHECK 1 / CHECK 2, ÖKOBAUDAT data errors.** The two Schönthaler hemp-block datasets declare a "Mass" flow property of 1.0 per m³ (an error). The "430 kg/m³" dataset also lists gross density 405 kg/m³ as a material property, while its name says "mittlere Ausgleichsdichte ca. 430 kg/m³". I converted each dataset with the as-delivered density in its name (405 and 430), decided before computing the result.
19. **CHECK 2, hempcrete.** Ratio **1.51**, so flagged. With 405 kg/m³ for both datasets the ratio would be 1.47 (pass). The outcome hinges on this density choice and on only 2 EPDs from 1 producer; it was not changed (the checks never change a number or a choice). Hydraulic lime carries about 66 % of A1–A3.
20. **CHECK 2, cork.** Ratio **0.12** (0.0593 vs 0.512 kg CO₂e/kg), so flagged. ÖKOBAUDAT has 1 generic dataset. Our value is low for the reasons in 15. For reference only (not in ÖKOBAUDAT), Amorim's ICB EPD gives 82.8 kg CO₂e/m³ ÷ 115 = 0.72 kg CO₂e/kg.
21. **P2 · Check, wear share.** Hempcrete 0.012 %, cork 0.49 % (OSB/3 has none, D1 = yes). Both are below 2 %, so no review was triggered.

## A4–C4 and module D

22. **A4 · T2, evidence quality.** Manufacturer checks rest on web sources and trade press, not registries.
    - OSB/3 (DE, FR, IT): solid.
    - Hempcrete (FR Vieille Matériaux, IT Equilibrium / Schönthaler, ES Cannabric): moderate.
    - Cork: only an unconfirmed French directory entry and a Spanish supplier → T2 **no**. T3 yes (Amorim, PT).
23. **A5 · L1, hempcrete blocks.** The examples list "blocks … placed dry" as prefab, but IsoHemp blocks are glued with a 3 mm adhesive mortar. I answered **yes** (in situ, 5 %) and C1 · X1 **yes** (bonded → diesel). The examples could name thin-joint glued blocks explicitly.
24. **A5 BLOCK, lorry for the lost kg.** The text says "C2 distance", but the example uses 50 km. I used the route-weighted C2 tkm per kg (OSB 0.0925, hempcrete 0.05, cork 0.0975) × loss.
25. **W1/W2, product as waste (D1 = yes).** `waste_fallback` is looked up by constituent, but for OSB/3 the product itself is the waste material, and it is not in the `constituents` column. I used the "Wood, wood-based" row, whose `materials` column lists OSB/3 and contains its main constituent. W1 was answered **no**, because "waste wood, untreated" does not describe a resin-bonded board.
26. **W2, recycling dataset sign.** `treatment of waste wood, post-consumer, sorting and shredding` has reference product *wood chips* (production +1), not a waste flow. A negative amount, as the C3–C4 rule says, would credit chips production. I wrote it as a **positive** amount (the burden of sorting/shredding). Its unit is kg dry mass; I used the wet mass share (no correction).
27. **W2, hempcrete composite.** NMD category 8 sends 99 % to recycling, but per constituent the sheet sends hemp shiv to wood sorting/shredding ("as wood") and lime and water to concrete recycling. In reality the composite is crushed as a mineral. Water is also in the Mineral class, so it gets a concrete-recycling and an inert-landfill row. I followed the sheet. Suggest treating composites as one waste material.
28. **C3–C4, constituent mass with production losses.** For cork, the input constituent is 1.06 kg/kg, including a 6 % production loss. Using it would send 1.06 kg to waste per kg of product. This is unclear: I used the product mass, 1.00 kg (lower impact, mass-consistent). bioc_inputs also uses 1.00 ("losses excluded").
29. **B2, OSB/3 moisture.** The input note gives wood 88.5 % + water 4.5 %. I recorded moisture as 0.045 ÷ 0.885 = 0.0508 (dry basis). The other constituents give no moisture, so the archetype default applies.

## Not used

`README.md` and `compare_runs.py` were not opened: the prompt lists the files to use, and they are not among them.
