# Protocol issues — run_A (19 Nov 2026)

Each note gives the step id, what was unclear, and what I did. The most consequential notes come first.

## 1. P1 / P2 — three complete datasheets are rarely available (affects hempcrete and cork)
- **What was unclear.** P1 asks for three machines from three manufacturers, each with power, throughput and mass on its datasheet. A machine missing one of the three "is not used". In practice:
  - **Twin-shaft mixers** (Liebherr DW, Co-Nele CHS): kW, batch volume and mass, but no cycle time, so no throughput.
  - **Band saws / resaws** (Cantek, Braun, HEMA, Fecken-Kirfel): kW and mass, but no throughput.
  - **Cork expansion autoclaves:** no public datasheet at all. There is no BREF for cork, and the peer-reviewed inventory (Demertzi et al. 2017) was not accessible. Industrial autoclave brochures (Akarmak) give no values.
  - **Block presses:** only one complete datasheet was found (Nantong Hengda QT6-15).
- **The gap in the protocol.** It says what to do with three candidates (take the median) and with no machine of the type (use a proxy machine type). It does not say what to do with one or two candidates, or when the proxy search also finds nothing.
- **What I did.**
  - **3 complete candidates:** median (cork grinding: Zorg 8 t/h hammer mill).
  - **1 complete candidate:** used it and logged that it was the only one (hempcrete moulding and pressing).
  - **0 complete candidates:** logged "unclear" and took the lower-impact branch, i.e. no rows. This applies to hempcrete mixing, cork autoclave expansion and cork cutting.
- **Consequence.** The cork LCI has no autoclave heat, which is the main energy use of expanded cork. Its GWP-fossil A1–A3 is 0.0365 kg CO₂e/kg against an EPD median of 0.512 (ratio 0.07). This is the "benefit of the doubt" rule working against completeness.
- **Suggestion.** Allow a measured or declared energy per kg from the sector (EPD background report, manufacturer, study) when no machine datasheet exists. Or give a library value for heating steps.

## 2. P2 — machine life: no default number of years
- **What was unclear.** P2 gives 5,000 h/yr when the source gives years but no hours. It gives no default when the source gives no life at all, and no datasheet did.
- **What I did.** I used the German BMF AfA table for general assets (AfA-Tabelle AV), × 5,000 h/yr:
  - hammer mill = "Shredder": 6 y
  - press = "Pressen und Stanzen": 14 y
  - (would have used: saws, stationary, 14 y; pressure vessels / boilers, 15 y)
- **Two caveats.**
  - The AfA lives assume one shift (its note 4 allows faster depreciation for two shifts), while the protocol assumes about two shifts. This mismatch shortens life slightly in hours.
  - There is no AfA entry for mixers other than "Betonkleinmischer" (6 y).
- **Suggestion.** Put one life table in the workbook.

## 3. CHECK 3 hempcrete — the result depends on which density converts an EPD
- **The data.** ÖKOBAUDAT dataset bcb212fe… is named "Hanfstein – 430 kg/m³ … mittlere Ausgleichsdichte ca. 430 kg/m³", but its material properties give 405 kg/m³ (copied from the 405 kg/m³ sibling dataset).
- **What I did.** I used 430, the declared product density.
  - With 430: median 0.424 kg CO₂e/kg, ratio 1.505, **fail**.
  - With 405: median 0.437, ratio 1.46, **pass**.
- I did not choose the density by its effect on the check.
- **Suggestion.** Specify which field is authoritative ("material properties: gross density" or the name/description).

## 4. D3 — Portugal (and other European countries) are not in the country list
- **What was unclear.** `market for cork, raw` exists only for PT and RoW. Rank 4 is "a single European country, in this order: DE, FR, IT, ES, NL, AT, SE, FI, PL, CH". It is unclear whether PT counts as rank 4 (it is a single European country) or as rank 7 ("any other", after RoW).
- **What I did.** Logged "unclear" and took RoW. That is both the literal order and the lower-impact choice (0.0305 vs 0.0626 kg CO₂e/kg).
- **Suggestion.** For cork, PT is clearly the representative geography. Consider "any other single European country" after CH and before GLO.

## 5. W2 fallback for wood recycling gives a credit if the sign rule is followed
- **The problem.** `treatment of waste wood, post-consumer, sorting and shredding` has *wood chips* as its reference product (it consumes waste wood as an input). Writing it with a negative amount, per the "waste to treatment is negative" convention, would *subtract* wood-chip production, which is a credit.
- **What I did.** Wrote it with a **positive** amount (the burden of sorting and chipping) for OSB recycling, hemp shiv recycling, and the matching A5 loss rows.
- **Also.** The dataset is in kg dry mass, while the waste mass includes moisture. I did not correct for this.
- **Suggestion.** Replace this dataset with a waste-treatment dataset, or state the sign rule.

## 6. W1 / W2 — the hempcrete end of life splits a composite into wood and mineral routes
- **The problem.** The NMD route is 99 % recycling (category 8, mineral). The per-constituent rule then sends 0.339 kg of hemp shiv to *wood chipping* and the lime and water to *concrete recycling*. Physically the block is crushed as one mineral material.
- **What I did.** Followed the sheet as written and logged it as a proxy (TeR 4).

## 7. C2 / W1 — waste mass when the input includes production losses (cork 1.06 kg)
- **What was unclear.** "Each constituent of the input, with its mass per kg" would give 1.06 kg of cork waste per 1 kg of product.
- **What I did.** Used the mass in the product (1.00 kg), which is the lower impact and consistent with B2 ("losses excluded").

## 8. W2 — a single-dataset product (OSB/3) is not in the column `constituents`
- **What was unclear.** For a matched dataset "the product itself is the one waste material", but W2 says to look the name up in the column `constituents`. OSB/3 is only in the column `materials`.
- **What I did.** Used the row whose `materials` column lists OSB/3 (Wood, wood-based).

## 9. ROW — "1 kg of that dataset" when the dataset is per m³
- **The problem.** ecoinvent OSB is per m³.
- **What I did.** amount = 1 kg ÷ 607 kg/m³ (ecoinvent "wet mass" property) = 0.00165 m³.
- **Suggestion.** State the rule: use the dataset's own density property.

## 10. TiR cannot be read
- **The problem.** The Brightway import of ecoinvent 3.12 does not keep the dataset time period.
- **What I did.** Set TiR to "n/a". DQR in the LCI sheets is the mean of TeR and GeR only.

## 11. GeR for CH
- **The problem.** The GeR table has "one EU country" (2) and "other" (5). CH is not in the EU but is in the D3 list.
- **What I did.** Scored CH as 2.

## 12. A4 · T2 — answers depend on how far the manufacturer search goes
- **OSB:** DE (EGGER) and FR (SWISS KRONO Sully) confirmed. ES (Kronospan Tortosa OSB line, announced for 2026) unconfirmed.
- **Hemp blocks:** FR (Vieille Matériaux / BIOSYS) and IT (Tecnocanapa) confirmed. ES (Cannabric) unconfirmed.
- **What I did.** Both logged "unclear" and took the lower-impact branch (national, 150 km).
- **Risk.** Another run may count these countries differently and switch to the EU archetype (1.5 tkm lorry plus sea).
- **Suggestion.** Define what counts as evidence: an EPD, or a production site named on the manufacturer's site.

## 13. C1 · X1 / A5 · L1 — depend on the application, which the per-kg LCI does not know
- **Cork boards** can be glued (ETICS) or fixed mechanically. I logged C1 · X1 as unclear and took no diesel row.
- **Hemp blocks** are laid with adhesive mortar. I answered yes for both L1 (5 %) and X1 (diesel).

## 14. P1 throughput in m³/h needs "density of the material as processed"; for a block press that is the fresh mix
- **The problem.** No source was found for the fresh hemp-lime density.
- **What I did.**
  - Used the EPD block density, 405 kg/m³ (Schönthaler).
  - Used the gross volume of the hollow concrete block the press datasheet quotes (390×190×190 mm, 1,900 pcs/h).
- Both are assumptions.

## 15. OSB input — note on "drying strands"
- **The note.** "0.885 × (0.80 − 0.03); assumption", while the amount is 1 kg processed.
- **What is unclear.** Whether the note is the water evaporated per kg (for a heat row) or just an explanation.
- **Impact.** Not used in this run, because OSB took the approximate-match route.

## 16. Other notes
- **Fixed datasets.** All datasets marked "check name" in `fixed_settings` exist under those names in ecoinvent 3.12. "diesel, burned in building machine" exists both as a production activity and as a market. I used the activity with the exact name (GLO).
- **Air lime.** Interpreted as hydrated lime (CL 90-S). The RER market exists only for the "packed" variant. D3 (location) was applied before D4 (variant).
- **ÖKOBAUDAT access.** The website is reachable through the soda4LCA API. Release used: **OBD_2024_III (13.11.2026)**, EN 15804+A2 datasets only. The workbook cell "ÖKOBAUDAT release" is still marked "to fill".
- **Wear share (P2 check).** Cork 0.09 %, hempcrete 0.005 % of GWP-fossil A1–A3. Both are well under 1 %, as estimated.
- **Files not opened.** `README.md`, `PROMPT.md` and `compare_runs.py` are in the run folder but are not among the files the task lists, so I did not open them.
