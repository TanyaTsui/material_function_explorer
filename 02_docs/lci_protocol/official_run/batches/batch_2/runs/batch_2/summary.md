# Summary, batch_2 (run date 19 Nov 2026)

GWP-fossil A1–A3 per kg: EF 3.1 "climate change: fossil", ecoinvent 3.12 cut-off, computed with Brightway (read-only). Wear = share of machine (P2) rows. No material was stopped.

| Material | Route kept | GWP-fossil A1–A3 (kg CO2e/kg) | EPD median | Ratio | Check | Wear share |
| --- | --- | --- | --- | --- | --- | --- |
| sawn hardwood (oak) | D1 exact: market for sawnwood, hardwood, raw, dried (u=10%), RER | 0.133 | 0.139 (n=1) | 0.953 | CHECK 1 pass | 0 (no machine rows) |
| cotton canvas | built from scratch | 5.87 | none | – | CHECK 3: no check possible | 1.45e-4 |
| ceramic tile | D1b approximate: ceramic tile production, CH + A2 lorry 150 km | 0.432 | 0.694 (n=1) | 0.623 | CHECK 2 pass | 0 |
| PVC-U | built from scratch | 2.40 | 4.18 (n=2, not ÖKOBAUDAT) | 0.574 | CHECK 3 pass | 1.96e-4 |

## Per material

**Sawn hardwood (oak).** D1 yes (market, RER; moisture u=10 % vs 12 % and generic hardwood vs oak noted). Check 1 passes (ratio 0.95, one EPD). A4: made in DE/FR/NL → 150 km. A5: no machine, prefab → 3 %. No C1 row. Route 34 (5/80/10/5). CFF: Solid wood; biogenic: Wood, u = 0.12.

**Cotton canvas.** D1 no and D1b no: ecoinvent only has greige woven cotton (finishing is a separate dataset). Built: cotton fibre market GLO (1.1 kg). Machines: carding = Rieter C 81 (only 1 of 3 candidates complete); spinning = EDIPTEX study, ring Ne 16, 2.10 kWh/kg (proxy); weaving = industry-article value 3.2 kWh/kg (proxy, low confidence); wet finishing = stenter drying heat only, 2.58 MJ/kg (proxy). No ÖKOBAUDAT dataset, so no check. A4: T2 no (only NL found), T3 yes → EU (1.5 tkm lorry + 0.1 tkm ship). Route 52 (5/95/0/0), waste via W2 (wood datasets, CH).

**Ceramic tile.** D1 no (extra TiO2, stucco, metals; no kaolin). D1b yes (clay main constituent), check 2 passes. D2 was unclear (market only GLO): took production CH + A2 (lower impact; market GLO would give 0.796, ratio 1.15, also a pass). A4 national 150 km. L1 yes (set in adhesive) → 5 %; X1 yes (bonded) → diesel 0.036 MJ. Route 25 (15/0/80/5); waste via W2 mineral datasets.

**PVC-U.** D1 and D1b no (no PVC profile dataset; "window frame" is a whole frame with metal). Built: PVC resin, chalk (limestone, milled), TiO2 from datasets; impact modifier (PMMA) and Ca-Zn stabiliser (organic chemical) are proxies (TeR 4). Machines: dry blending = Jwell hot/cold mixer (median of three, 0.094 kWh/kg, no weight); profile extrusion = Jwell SJZ65/132 (37 kW, 215 kg/h, 4,000 kg; only two of three complete, lower-energy used); cutting = no data, no rows. Check 3 passes only against two non-ÖKOBAUDAT EPDs. Route 63 (10/10/80/0).

## Things I am unsure about

1. EPD medians rest on 0 to 2 EPDs each (ÖKOBAUDAT could not be searched by category). Oak and tile rest on a single EPD.
2. Machine data are the weakest part: for 6 of 7 built steps I could not get three complete datasheets; three steps use study values, one has no rows (PVC cutting). Wear shares are far below 2 % but several machines have no wear row. The Jwell values come from a search summary (page returned 403).
3. Cotton canvas is dominated by cotton fibre (3.81 of 5.87), but spinning and weaving energy values are low-confidence.
4. Open protocol questions (D2 vs D3 market GLO, FAE variants, sign of wood recycling, T2 "unclear") are in `protocol_issues.md`.
5. TiR = 1 for all datasets; the ceramic tile dataset is old (v2).

Files: `decisions.csv` (106 rows), `dataset_choices.csv` (65), `epd_check.csv` (4), `cff_inputs.csv`, `bioc_inputs.csv`, `LCI_<material_id>.xlsx` ×4, `protocol_issues.md`. The build script is `scripts/build_run.py` in the working folder.
