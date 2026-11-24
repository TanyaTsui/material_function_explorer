# Summary, run_C (2026-11-19)

Protocol 19 Nov 2026 (D1b without mass threshold), ecoinvent 3.12 cut-off, GWP-fossil = EF 3.1 climate change: fossil, per kg. ÖKOBAUDAT release OBD_2024_III. No material hit STOP.

| Material | Route kept | A1–A3 GWP-fossil (kg CO2e/kg) | ÖKOBAUDAT median (n) | Ratio | Check |
|---|---|---|---|---|---|
| OSB/3 | D1 exact: `market for oriented strand board`, RER | 0.407 | 0.457 (4) | 0.89 | CHECK 1 pass |
| Hempcrete | Built from scratch (no D1/D1b dataset) | 0.640 | 0.424 (2) | 1.51 | CHECK 3 fail, **flagged** |
| Cork | Built from scratch, after REVIEW | 0.117 | 0.512 (1) | 0.228 | CHECK 2 fail (1.87x), CHECK 3 fail, **flagged** |

## OSB/3
- D1 yes: ecoinvent OSB (EPF average) has strands, MDI (3.0 %) and paraffin (1.8 %); the input has PMDI/MUF (5.1 %). Counted as the same constituents (difference logged). D2 market, D3 RER. 1 kg = 1/607 m3.
- A4: T1 no, T2 yes (DE, IT, ES; weak evidence for ES and IT) -> 150 km. A5: I1 no (34 kg board), L1 no -> 3 %. C1: no diesel. C2: NMD 55 (5/85/10/0).
- C3–C4: W1 no (no waste OSB), W2 wood fallback (landfill CH, incineration CH, recycling CH).
- No machine rows (exact match). CFF: Wood panels. Bio-C: strands Wood (u = 0.0508 from the input), adhesive and wax non-biogenic.

## Hempcrete
- D1 no, D1b no (nothing in ecoinvent). Constituents all D5 yes: hemp hurd FR, hydrated lime RER (air lime), hydraulic lime RER (NHL), tap water RER. Rows sum to 1.000.
- Machines (median of three by kWh/kg, 10 y x 5,000 h life assumed): mixing CO-NELE CTS1500 (55 kW, 0.00286 kWh/kg); moulding and pressing Tengfei QT6-15 (31.25 kW, 0.00424 kWh/kg). Curing: no energy. Wear share 0.009 %.
- CHECK 3 fails by 0.9 % over the limit; hydraulic lime is 66 % of the total. REVIEW has one LCI; kept and flagged.
- A4: T2 yes (DE, FR, IT; borderline) -> 150 km. I1 no, L1 yes (5 %), C1 yes (bonded: diesel 0.036 MJ). C2: NMD 8 (1/0/99/0). C3–C4: all W1 no; W2 wood (hurd) and mineral (lime, water). CFF: Mineral, crushed to aggregate. Bio-C: hurd Cellulose, rest non-biogenic.

## Cork
- D1 no (ecoinvent slab has 0.14 kg/kg MF/PF/UF resin). D1b yes (`market for cork slab`, RER; main constituent cork; differences logged). CHECK 2 fails at 1.87x.
- Built: raw cork 1.06 kg (`market for cork, raw`, RoW by the D3 order). Machines: grinding UMP MM-2000 (45 kW, 0.018 kWh/kg, median of 3); autoclave Systec HX-200 2D (18 kW thermal, 1.41 MJ/kg, **proxy**, TeR 4); cooling: no energy; cutting Wood-Mizer HR120 (7.5 kW, 0.0026 kWh/kg, **proxy**, only two candidates). Wear share 0.69 %.
- CHECK 3 fails at 0.228x. REVIEW: built (distance 0.772) is closer than approximate (0.871), so built is kept and flagged.
- A4: T2 no (only Portugal found), T3 yes -> 1,500 km lorry + 100 km sea. I1 no, L1 no (3 %), C1 no. C2: NMD 52 (5/95/0/0). C3–C4: W2 wood. CFF: Other plant-based. Bio-C: Cork.

## What I am unsure about (details in protocol_issues.md)
- Machine data quality: several datasheet values come from search-engine excerpts; the mixer cycle time (90 s) and machine life (10 y) are assumptions; the cork autoclave and cutting machines are proxies, and the cutting machine mass is from a sister model.
- Hempcrete passes or fails on a 1 % margin and depends on how "hydraulic lime" is mapped.
- The cork result is 4x below the one generic EPD, driven by the low proxy autoclave energy.
- Borderline A4 · T2 answers (OSB, hempcrete) and the sign convention of the recycling row (wood chips dataset).
- Not computed: premise scenario results (applied by the model); module B and D (only `cff_inputs.csv` and `bioc_inputs.csv` written).

Files: `LCI_osb3.xlsx`, `LCI_hempcrete.xlsx`, `LCI_cork.xlsx`, `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`, `cff_inputs.csv`, `bioc_inputs.csv`, `protocol_issues.md`.
