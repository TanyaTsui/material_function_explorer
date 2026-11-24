# Summary, run_B

Protocol of 19 Nov 2026, ecoinvent 3.12 cut-off, EF 3.1 climate change: fossil (Brightway, read-only), ÖKOBAUDAT release OBD_2024_III (13 Nov 2026). No material stopped (the CHECK on mass passed for cork and hempcrete).

| Material | Route kept | Our GWP-fossil A1–A3 (kg CO2e/kg) | ÖKOBAUDAT median (n) | Ratio | Result |
|---|---|---|---|---|---|
| OSB/3 | D1 exact match | 0.407 | 0.457 (4) | 0.89 | CHECK 1 pass |
| hempcrete | built from scratch | 0.636 | 0.424 (2) | 1.4995 | CHECK 3 pass, borderline (limit 1.5) |
| cork | built from scratch | 0.106 | 0.512 (1) | 0.21 | CHECK 3 fail → REVIEW, flagged |

## OSB/3
- D1 yes (a judgement call, see issues 4): `market for oriented strand board` RER, 1/607 m³ per kg (wet mass 607 kg/m³). TeR 1, GeR 1. D1b, build and machines not needed.
- A4: T1 no, T2 no (DE and FR only), T3 yes → lorry 1.5 tkm + sea 0.1 tkm. A5: I1 no (34 kg board), L1 no → 3 % (loss 0.0309). C1: no diesel. C2: NMD 55 (5/85/10/0), 92.5 km weighted. C3–C4: wood fallback (W2) for landfill, incineration, recycling.
- CHECK 1: EPDs EGGER 0.282, Kronospan 0.345, AGEPAN 0.568, Thünen 0.579 → median 0.457.

## Hempcrete
- D1 no, D1b no (nothing in ecoinvent). Built from four constituents: hemp hurd FR (0.342), hydrated lime loose CH (0.108), hydraulic lime RER (0.422), tap water RER (0.128). Mass check passes (1.000).
- Machines: **none.** Mixing and moulding/pressing: unclear (no complete datasheet), curing: no energy. So the A1–A3 block holds constituents only; the energy and wear of the factory are missing.
- CHECK 3 compares with two Schönthaler hemp-stone EPDs (the workbook says none exist). Passes by 0.04 %; the result depends on every choice above (issue 19).
- A4: EU (T2 no, T3 yes: IsoHemp, Belgium). A5: I1 no (≤16.5 kg), L1 yes (mortar) → 5 % (loss 0.0526). C1: X1 yes → 0.036 MJ diesel. C2: NMD 8 (1/0/99/0), 50 km. C3–C4: wood fallback for shiv, mineral fallback for lime and water.

## Cork
- D1 no (ecoinvent cork slab has 0.140 kg resin per kg). D1b no (14 % > 10 %). Built: raw cork `market for cork, raw` RoW 1.06 kg (PT is "any other" in D3, issue 6).
- Machines: grinding = hammer mill, median of 3 (Bruks 0.0308, **Zorg 0.01125**, Rongda 0.00528 kWh/kg): 90 kW, 8,000 kg/h, 3,000 kg, life 125,000 h → 0.0119 kWh and 3.2e-6 kg of machine per kg of board. Autoclave: **proxy**, 1.29 MJ heat per kg from a waste autoclave study (TeR 4), no machine row. Cooling: no energy. Cutting: unclear, no rows.
- CHECK 3 fails (0.21× the one EPD, Sphera "Expanded cork; 80 kg/m³"). REVIEW: only one LCI exists (D1/D1b answered no before any LCI), so the built LCI is kept and flagged. For information, ecoinvent cork slab (not allowed, binder 14 %) gives 0.959, 1.9× the EPD.
- Wear share of GWP-fossil A1–A3: 7.6e-5 (0.0076 %, far below 2 %).
- A4: EU (T2 no; Amorim PT, Barnacork ES). A5: I1 no, L1 no → 3 %. C1: unclear → no diesel. C2: NMD 52 (5/95/0/0), 97.5 km. C3–C4: wood fallback (landfill 0.053 kg, incineration 1.007 kg, using 1.06 kg constituent mass, issue 10).

## Wear share (P2 rows) in GWP-fossil A1–A3
OSB 0 (no machine rows), hempcrete 0 (no machine rows), cork 7.6e-5.

## What I am unsure about
- The missing machines: the hempcrete result and the cork failure both reflect incomplete energy data, not product facts. The cork autoclave proxy is the weakest number.
- OSB D1 yes vs no (issue 4); hempcrete borderline pass (issues 19 and 20).
- The positive sign of the wood "sorting and shredding" recycling row (issue 13), water as a waste item (issue 12), and the 1.06 kg waste mass for cork (issue 10).
- TiR defaulted to 1 for all ecoinvent rows (issue 16).
- Modules B and D have no rows, as the protocol says; `cff_inputs.csv` and `bioc_inputs.csv` hold the module D inputs.

Files: `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_osb3.xlsx`, `LCI_hempcrete.xlsx`, `LCI_cork.xlsx`, `protocol_issues.md`.
