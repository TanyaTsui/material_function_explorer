# Summary, run batch_6 (2026-11-19)

Database ecoinvent 3.12 cut-off, EF 3.1 climate change: fossil, ÖKOBAUDAT via API (A2 datasets). Machine/energy values partly from BREF and search summaries: see `protocol_issues.md` 9-14. All four materials went through; none stopped.

| material | route kept | GWP-fossil A1-A3, kg CO2e/kg | ÖKOBAUDAT median (n) | ratio | check |
| --- | --- | --- | --- | --- | --- |
| mdf | built from scratch (flagged) | 0.815 | 0.461 (5) | 1.77 | CHECK 1 fail (1.89), CHECK 3 fail, REVIEW keeps built |
| clay brick masonry | built from scratch (flagged) | 0.309 | 0.196 (1, brick only) | 1.58 | CHECK 3 fail (only one route), kept flagged |
| structural steel | built from scratch | 0.762 | 0.560 (1) | 1.36 | CHECK 2 fail (4.07), CHECK 3 pass |
| PVC-coated polyester | built from scratch | 3.44 | 4.13 (1, PVC roofing sheet) | 0.83 | CHECK 3 pass (energy of coating missing) |

Wear (P2 machine rows) share of GWP-fossil A1-A3: MDF 0.012 %; other materials have no machine rows.

## mdf
- D1 yes: `market for medium density fibreboard` RER (EPF average; UF 46.4 + MF 41.8 kg/m3 resin, paraffin, wood; 1 kg = 1/684 m3). CHECK 1 failed (0.872 vs 0.461). D1b no (the same dataset cannot be picked again; other fibreboards are other products). Built:
  wood fibres -> proxy `market for wood chips, green` (Europe w/o CH); UMF -> proxy UF resin RER; paraffin RER/GLO.
- Machines/energy: chipping = drum chipper, median of three datasheets (Liantai UTM, 110 kW, 15 t/h, 7 t; kWh 0.0073/kg). Steaming (3.28 MJ), refining (0.265 kWh), flash drying (0.125 kWh + 3.94 MJ), hot pressing (0.068 kWh + 1.03 MJ): EU BREF WBP midpoints, no datasheet had all three values; refiner, press, sander have machine rows (proxy mass), steaming and drying none. Sanding: Heesemann HSM 2 (13.4 kW, 4.5 t) with assumed throughput; saws not modelled.
- Both LCIs ~1.8-1.9x the median: natural-gas heat (0.446 of 0.815), electricity and UF resin; probably biomass heat in the EPDs (not checked).
- A4: T2 yes (DE, IT, FR) -> 150 km; I1 no (39 kg board, assumed format); L1 no (3 %); X1 no. EOL NMD 55 (5/85/10/0).

## clay brick masonry
- D1 no, D1b no (masonry with mortar is not `clay brick`; protocol issue 5). Built: `market for clay brick` RoW 0.8 (D2/D3 literal; RER production would be 0.250 instead of 0.332) + `market for cement mortar` CH 0.2.
- All five steps are inside the brick dataset (grinding, mixing, extrusion, drying, firing): no energy or machine rows.
- CHECK 3 1.58x (EPD is brick only, 1 EPD): flagged. A4: T2 unclear -> yes (DE, NL confirmed); I1 no; L1 yes 5 %; X1 yes. EOL NMD 32 (1/0/99/0).

## structural steel
- D1 no; D1b yes (`market for steel, low-alloyed, hot rolled` GLO, 74 % converter steel); CHECK 2 fail (2.28 vs 0.56). Built: `market for steel, structural, 100% scrap` (EAF, GLO) 1 kg + hot rolling from EU BREF 2022 (1.8 MJ heat, 0.056 kWh); EAF melting is inside the dataset; no machine row (no mass found). CHECK 3 pass (1.36).
- A4: T2 unclear -> yes (DE, IT confirmed); I1 yes (IPE 200, 134 kg; diesel 0.015 MJ); L1 no 3 %; X1 yes. EOL NMD 70 (1/0/94/5): only landfill gets a row.

## PVC-coated polyester
- D1 no, D1b no. Built: polyester filament (`market for fibre, polyester` GLO, includes melt spinning), PVC emulsion RER, plasticiser = proxy DOTP, flame retardant/fillers/stabilisers = proxy aluminium hydroxide, acrylic varnish RER.
- Only weaving has energy rows (vendor benchmark 3.6 kWh/kg x 0.2 kg); coating/gelling oven and lacquering: unclear, no rows (largest gap).
- A4: T2 unclear -> yes; I1 yes (roll 131 kg); L1 no 3 %; X1 yes. EOL NMD 62 (10/85/5/0).

## Unsure about
Machine values (protocol issues 9-14), the D2/D3 literal reading (RoW brick, GLO steel/polyester), brick D1b, T2 for steel/brick/PVC, assumed piece weights, the positive sign for wood sorting and shredding, and the PVC check (reference is a roofing sheet, coating energy missing).
