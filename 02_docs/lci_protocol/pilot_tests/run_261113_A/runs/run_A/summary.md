# Summary, run_A (13 Nov 2026)

GWP-fossil = EF 3.1 "climate change: fossil", ecoinvent 3.12 cut-off, computed read-only in Brightway. ÖKOBAUDAT release OBD_2024_III (13 Nov 2026). Values are per kg.

| Material | A1–A3 (first) | ÖKOBAUDAT median (n) | Ratio | STEP 3 outcome | A1–A3 after check | Cradle-to-grave (A1–C4) | A1–A3 DQR |
|---|---|---|---|---|---|---|---|
| osb3 | 0.407 | 0.457 (4) | 0.89 | pass | – | 0.682 | 2.33 |
| hempcrete | 2.37 | 0.424 (2) | 5.58 | fail → corrected → **flag** (2.03) | 0.863 | 0.948 | 3.32 (low) |
| cork | 1.65 | 0.512 (1) | 3.22 | fail → corrected → pass (1.25) | 0.640 | 0.922 | 3.50 (low) |

DQR is above 3 mostly because TiR = 5 wherever the ecoinvent time period was not available in Brightway (protocol_issues #14).

## OSB/3 (osb3)
- **S1:** median of 3 EPD composition tables: wood incl. moisture 0.951, pMDI 0.0339, paraffin/additives 0.0149. **S2:** Egger EPD process steps.
- **D1 yes:** ecoinvent OSB has wood + MDI + paraffin, the same constituents. Row: `market for oriented strand board` RER, 1/607 m³.
- **A4:** T2 unclear (DE, FR confirmed; IT only from 2013 reports; ES planned) → conservative no → EU: 1,500 km lorry + 100 km ship. This is the most fragile decision: it adds 0.23 kg CO₂-eq/kg, 34 % of the total.
- **A5:** I1 no (≈34 kg board), L1 no → 3 %. **C1:** by hand. **E1:** NMD 55 (5/85/10/0); untreated waste wood datasets (CH) as variant.
- **STEP 3:** pass at 0.89× the median; no change.

## Hempcrete blocks (hempcrete)
- **S1:** Schönthaler EPD (only one): shives 20–55 %, lime binder 45–80 % → midpoints 0.375 / 0.625. **S2:** mixing, pressing in a block machine, air drying.
- **D1 no → D5:** hemp hurd FR 0.375 kg; hydraulic lime RER 0.625 kg; mixing → plaster mixing (proxy); pressing → first compression of SMC, then plaster mixing; air drying → no row.
- **STEP 3:** 2.37 (5.6×). Targeted check item 4 found the SMC proxy carries polymers, steel castings and plastic waste → replaced → 0.863 (2.0×) → **flagged**. The remaining gap is mostly the binder: 0.625 kg of ecoinvent hydraulic lime alone gives 0.62. The share is a midpoint of a 45–80 % range, and the EPD's binder is unspecified ("calcareous mineral binder" with a hardener).
- **A4:** T2 yes (FR, IT, ES) → 150 km. **A5:** L1 yes (laid with mortar) → 5 %. **C1:** X1 yes (bonded) → 0.036 MJ diesel.
- **E1:** unclear (masonry vs insulation categories) → heaviest constituent (lime) → NMD 40 (1/0/99/0); concrete waste datasets as proxies.

## Cork board (cork)
- **S1:** EPD Hub HUB-0281 (Amorim): 100 % cork, no binder. **D1 no:** ecoinvent `cork slab production` contains MF, UF and phenolic resins (0.14 kg/kg), which are not in S1.
- **D5:** raw cork PT 1.0 kg; grinding and cutting → wood chipping (proxy); autoclave → first compression of SMC, then `drying of grass` (1 L per kg, assumed).
- **STEP 3:** 1.65 (3.2×) → item 4 → 0.640 (1.25×) → pass after correction. Caveat: the autoclave row (0.55 of 0.64) rests on an assumed amount (1 L water evaporated per kg) and on a proxy chosen after the failing result was seen.
- **A4:** T2 no (no plants confirmed in 3 of 5), T3 yes (PT) → EU 1,500 km + 100 km ship. **A5:** 3 %. **C1:** by hand (screwed per EPD). **E1:** NMD 52 (5/95/0/0), waste wood proxies.

## What I was unsure about
- The STEP 3 corrections for hempcrete and cork were made after seeing the gap. I justified them only by checklist item 4 (extra ingredients in the proxy), but the choice of replacement was mine. A blind second run is the real test.
- Range midpoints (hemp), the A4 evidence standard (OSB), GLO markets for processing proxies, PT in the D3 list, and TiR are the decisions most likely to differ between runs (see protocol_issues.md).
- The ÖKOBAUDAT reference for cork is one generic dataset at 80 kg/m³, not an ICB board EPD.
