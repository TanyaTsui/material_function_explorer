# Protocol issues, run_B (19 Nov 2026 protocol)

Each note: step id, what was unclear, what I did.

## Steps where I could not follow the protocol fully

1. **P1 · ENERGY / P2 · WEAR: three complete datasheets are rarely findable.**
   - Grinding (cork): three hammer mills from three manufacturers (Bruks Siwertell, Zorg, Rongda) have power, throughput and mass. Bruks gives ranges (midpoints used) and Rongda gives a t/h range (25 t/h used). All three are for wood or biomass, not cork. The DP Pulverizers brochure lacks kg/h and mass, so I dropped it.
   - Cork autoclave: no datasheet with thermal power, kg/h and mass. I used the "no machine found" route with a proxy: a pilot municipal-waste autoclave at 1.29 MJ/kg (TeR 4). I read that figure from a search-result summary; the paper itself would not open. No machine row was written for the autoclave. This is probably an underestimate for superheated steam at 300–350 °C, and it likely explains the cork CHECK 3 failure.
   - Cork cutting, hempcrete mixing, hempcrete moulding/pressing: partial data only (a 5.5 kW foam band saw without weight or throughput; mixers with litres but no cycle time; block presses in blocks/h for concrete blocks). I logged "unclear", wrote no rows, and took the lower-impact branch. **Hempcrete therefore has no energy or wear rows, and cork has only grinding plus the autoclave proxy.**
   - Suggestion: allow the protocol to say what to do when a step is "unclear" for a whole step. Today it silently removes the step's energy, which favours low impact. A fixed per-step fallback (for example an energy-per-kg range from the BREF) would make runs comparable.

2. **P2: machine life.** Datasheets give none. I took 25 years from the ecoinvent machine dataset documentation ("Service life declared by the producer: 25 years") × 5,000 h/y = 125,000 h, for every machine. The protocol says "from the source, else 5,000 h/y", but gives no default number of years.

3. **P1: electricity/heat from MJ vs kWh.** Fine. No issue, but the heat dataset (Europe without Switzerland, natural gas) is not the carrier of an autoclave heated with biomass (Amorim says over 90 % biomass energy). Noted as a limitation, as the protocol says.

## Ambiguities in the protocol

4. **D1 "same constituents".** The ecoinvent OSB has wood, MDI (3.0 %), an organic-chemicals input (0.9 %) and paraffin (1.8 %). The input has wood, PMDI/MUF (5.1 %) and paraffin (1.9 %). I said yes (the three constituents are present; the adhesive share differs, 3.9 % vs 5.1 %). Another run could read "PMDI/MUF" strictly and say no. D1b gives a measure (10 % of mass) but D1 gives none. Suggest a threshold for amount differences, or state that only the presence of constituents counts.

5. **D1b "differing constituents add up to at most 10 % of the mass of the input".** For cork the resins are 0.140 kg per kg of output (14.0 % of the input mass; 11.7 % of the dataset's own 1.20 kg input). Both readings are above 10 %, so the answer is the same, but the base of the percentage should be stated.

6. **D3 and countries outside the list.** Raw cork exists as PT and RoW markets only. PT is not in the D3 country list, so "any other" (tier 7) comes after RoW (tier 6), and I took RoW (0.030 kg CO2e/kg vs 0.063 for PT). That looks like the opposite of what the rule intends (a Portuguese market is closer to the real origin of the cork). Suggest adding PT to the list or saying that a country inside Europe comes before RoW.

7. **D3 and CH vs RoW/GLO.** CH is in the country list, so CH datasets come before GLO or RoW (hydrated lime loose CH, wood waste datasets CH). Several ecoinvent waste datasets exist only for CH and RoW. I followed the rule, but CH-specific waste datasets (e.g. incineration FAE) are Swiss technology, not European average.

8. **D3 "market group" vs "market".** "market for hydraulic lime" is RER (a market, not a market group); tap water has a market group RER. I treated RER as rule 1/2 in both cases.

9. **Unit of the dataset is not kg.** The OSB market dataset is per m³. The row amount is 1 ÷ 607 m³ per kg, using the wet mass property of the dataset. The protocol says "amount = kg per kg of product". Suggest saying "converted to the dataset's unit with the density in the dataset".

10. **Constituents with losses at end of life (cork 1.06 kg).** C2 says mass of the waste item = constituent mass × route share. Cork's constituent mass is 1.06 kg, so C3–C4 treats 1.06 kg of waste per kg of product, although only 1.0 kg is demolished (the 6 % loss happened in manufacture). Same for the A5 end of life of the lost kg. I followed the rule literally (0.053 + 1.007 kg). Suggest scaling constituents to the 1 kg that arrives at C2.

11. **Waste item for a single-dataset product (OSB).** W1 says the waste material must match the constituent, but for D1 matches the product is the waste material ("OSB/3"). There is no ecoinvent waste-OSB dataset and sheet `waste_fallback` is keyed by constituent ("wood strands, incl. moisture"), not by product. I used the class "Wood, wood-based", which lists OSB/3 under `materials` (it is also listed under "Plastic, resin, binder, coating"; I did not split by mass). Suggest keying W2 by product for D1/D1b matches.

12. **W2 and water as a constituent (hempcrete).** The workbook lists "water" in class Mineral, so 0.128 kg of "waste water" goes to inert landfill (1 %) and reinforced-concrete recycling (99 %). Physically the water evaporated during curing. The effect is tiny for GWP, but the mass is wrong. Suggest "no row" for water.

13. **W2 recycling dataset with positive reference product.** "treatment of waste wood, post-consumer, sorting and shredding" has a positive reference product (wood chips, +1 kg), unlike the other treatment datasets (waste, −1 kg). The protocol says waste to treatment has a negative amount. A negative amount here would give a credit. I used a **positive** amount for this dataset (burden of sorting and shredding; the chips leave burden-free under cut-off). Please confirm.

14. **W2 recycling for minerals.** "treatment of waste reinforced concrete, recycling" is used for lime and water (workbook text). It is a different waste (reinforced concrete). Location: Europe without Switzerland (D3 tier 3) ahead of CH.

15. **Fixed dataset names.** The workbook says `diesel, burned in building machine`. ecoinvent has both an activity of that name (GLO) and a market of it. I used the activity named exactly as in the sheet. The sheet name `market for industrial machine, heavy, unspecified (kg) - RER` matches ecoinvent RER; the `market group` for electricity is RER. All "check name" cells in `fixed_settings` matched.

16. **TiR can't be read.** bw2data does not expose the time period of ecoinvent 3.12 activities, so I set TiR = 1 for every ecoinvent row. Some datasets (e.g. cork slab) are old, but they were not used. GeR for CH/FR/DE = 2, RoW = 4.

17. **DQR "mass-weighted".** The sheet shows DQR per row (mean of TeR, GeR, TiR). I did not write the mass-weighted total anywhere because the template has no cell for it.

18. **CHECK 1/2/3 category.** "Every EN 15804+A2 dataset in the product's category": ÖKOBAUDAT categories are not exposed by the name search, so I selected datasets by name search (OSB: 4 EPDs; cork: 1; hemp stone: 2). Other cork EPDs in the release are flooring or other products and were left out. The workbook says hempcrete has "no ÖKOBAUDAT dataset found", but the latest release (OBD_2024_III, 13 Nov 2026) has two Schönthaler "Hanfstein" EPDs (hemp-lime blocks). I used them as the hempcrete comparison. The input's own composition comes from IsoHemp, a different producer.
    - Thünen OSB (aab0ed28) lists modules A1, A2, A3 separately; I summed them for A1–A3.
    - EGGER's EPD text states 611 kg/m³ while its flow label says 607; I used 611 (declared unit).
    - The hemp-stone EPDs use "equilibrium density" 405 and 430 kg/m³, which I took as the as-delivered mass basis.

19. **Hempcrete passes CHECK 3 by 0.04 %** (ratio 1.4995 vs 1.5). Any other choice (hydrated lime RoW instead of CH, a mixing row, the water row) flips the result. Noted as a borderline pass; nothing was changed.

20. **Hempcrete shares may be volume shares.** Workbook note on `material_overview` says IsoHemp's 80/9/11 might be volume shares. I took the input as given. Lime is 53 % of the mass and drives the result.

21. **A4 · T2 evidence.** The protocol asks for a manufacturer per country. For OSB, cork and hempcrete I could find manufacturers in at most two of DE/FR/IT/ES/NL, so T2 = no and T3 = yes (EU transport: 1.5 tkm lorry + 0.1 tkm sea). Web search is thin for IT and NL and only in English; a native-language search could change the result (cork: Italy and France sell Amorim products but do not manufacture).

22. **C1 · X1 for cork.** Whether boards are bonded depends on the use. Treated as "unclear" and the lower-impact branch (no diesel). OSB: no. Hempcrete: yes (bonded in mortar).

23. **A5 end of life of the loss.** The protocol says "end of life of the lost kg as in C3–C4". I used loss × constituent mass × route share, with the same datasets. The lorry row uses the route-weighted C2 distance (92.5 km OSB, 97.5 km cork, 50 km hempcrete).

24. **Rounding.** Amounts in the sheets are rounded to 3 significant figures (for example A4→A5 1.0309 shows as 1.03). GWP checks use unrounded values.

25. **Search tool.** I ran the same matching as `search_ecoinvent.py` with a batch wrapper that loads the database once (the script takes about a minute per call). The search terms I used are in `dataset_choices.csv` and `decisions.csv`.

26. **Web tools.** The ÖKOBAUDAT API (www.oekobaudat.de/OEKOBAU.DAT/resource) answered, so the EPD values are read directly from the datasets. Several manufacturer PDFs would not open (Andritz, MDPI, Amorim EPD), and `WebFetch` returned binary for others; I installed `pypdf` in a separate virtual environment in the scratchpad to read one brochure. Nothing in the Brightway project or the workbook was changed.
