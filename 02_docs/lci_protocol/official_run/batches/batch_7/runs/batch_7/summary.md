# Summary, batch_7 (run 2026-11-19)

Four materials, none stopped. Values are GWP-fossil A1–A3 per kg (EF 3.1, climate change: fossil, ecoinvent 3.12 cut-off), compared with the median of EN 15804+A2 EPDs in the latest OEKOBAU.DAT data stock listed by its API (OBD_2024_III, read per EPD with the API; per-EPD values are converted to kg with each EPD's gross density).

| Material | Route kept | Ours | EPD median (n) | Ratio | Check |
| --- | --- | --- | --- | --- | --- |
| glulam | exact (D1) | 0.340 | 0.291 (7) | 1.17 | CHECK 1 pass |
| CLT | exact (D1) | 0.349 | 0.242 (4) | 1.44 | CHECK 1 pass (near +50 % edge) |
| soft wood fibre board | built, flagged | 0.919 | 0.540 (4) | 1.70 | CHECK 2 fail (1.70), CHECK 3 fail (1.70), REVIEW |
| aluminium extrusion | built, flagged | 13.0 | 4.17 (10) | 3.11 | CHECK 3 fail, REVIEW (only one LCI) |

## glulam
- D1 yes: `market for glued laminated timber, average glue mix`, Europe without Switzerland (D2 market, D3 rule 1, D4 only variant there). Unsure: the dataset has 0.07 % phenolic resin besides PUR/MUF (see protocol_issues).
- A4: T2 yes (DE, FR, IT, ES), lorry 0.15 tkm. A5: I1 yes (beam about 124 kg), L1 no, 3 % loss. C1: X1 yes. Route 34 (5/80/10/5). CFF: Solid wood. Waste via Wood class of waste_fallback (proxy).

## CLT
- D1 yes: `market for cross-laminated timber`, RER. ecoinvent glue shares differ from the input (MUF), same constituents.
- A4: T2 yes (DE, FR, IT, ES). I1 yes, X1 yes, route 34. Ratio 1.44, only just inside the limit.

## soft wood fibre board
- D1 no (extra binders in every candidate). D1b yes: `market for fibreboard, soft`, RER (differences logged: MDI 0.18 %, phenolic, latex, starch, vinyl acetate, nylon, Al sulfate). CHECK 2 fails (1.70).
- Built: wood chips (RER market) 0.945, polyurethane adhesive (GLO) 0.04, paraffin (GLO) 0.015; mass check passes.
- Machines (all proxy, TeR 4, see protocol_issues): refining and drying energy from BREF Table 3.3 midpoints (refining 0.265 kWh/kg electricity + 0.91 kWh/kg heat; drying 0.125 + 1.095), curing from BREF MDF pressing, dosing and saw from vendor kW over a 6 t/h line. Wear rows only for refiner (Andritz TX68) and dryer (VetterTec); wear share 0.033 %.
- CHECK 3 fails (1.70). REVIEW: built 1.701 vs approximate 1.704 times the median; built kept and flagged (a tie in practice). Heat from natural gas is half of the built result.
- A4: T2 yes (DE, FR, IT), 0.15 tkm. I1 no (boards below 50 kg), X1 no. Route 55 (5/85/10/0). CFF: Wood panels.

## aluminium extrusion
- D1 and D1b no (ecoinvent has only the extrusion process, not the profile). D5: `market for aluminium, wrought alloy` GLO (no European dataset; D3 rule 5).
- Steps: billet heating gas 0.195 kWh/kg (0.702 MJ), extrusion electricity 0.196 kWh/kg (US DOE bandwidth study, derived), ageing oven gas 0.080 kWh/kg (0.288 MJ), cutting: no separate row (inside the DOE plant electricity). No wear rows (no mass with throughput found), so the wear share is "not computed".
- CHECK 3 fails: 12.96 vs 4.17 (3.1x). The alloy market alone is 12.84; the energy rows are 1 %. The EPD median is pulled down by low-carbon and recycled profiles; the GDA EPD named in the input sheet has 1.92. Flagged, kept.
- A4: T2 yes (DE, FR, IT, ES). I1 no, X1 no. Route 4 (3/3/94/0). CFF: Aluminium. Landfill and incineration rows only (recycling has no row, cut-off).

## Biggest uncertainties
1. Machine values (P1/P2) are fallback figures, not three-machine medians; see protocol_issues.md.
2. Median of the aluminium category depends on which EPDs count as "profiles".
3. Piece weights (I1/X1) rest on assumed formats; the A4 category for all four is "national" (150 km).
4. Amounts of wood products are in m³ (kg ÷ wet mass of the dataset).

Files: `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material>.xlsx`, `protocol_issues.md`; the scripts that wrote them are in `work/` (read-only use of Brightway; no database or workbook was changed).
