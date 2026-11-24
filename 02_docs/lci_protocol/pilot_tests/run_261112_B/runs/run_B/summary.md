# Summary: run_B (12 Nov 2026)

Database: ecoinvent 3.12 cut-off (local Brightway project, read only). ÖKOBAUDAT release OBD_2024_II (22.07.2026). GWP-fossil uses EF v3.1 "climate change: fossil". All values are per 1 kg installed. TiR could not be read from the Brightway import, so DQR is not computed (protocol_issues #1).

## OSB/3 (osb3)

| Step | Choice |
| --- | --- |
| S1 | wood incl. moisture 0.951 / pMDI 0.0339 / paraffin and additives 0.0149: median of 3 ÖKOBAUDAT EPDs (Egger, Sonae Arauco, Kronospan) |
| A1–A3 | D1 yes: `market for oriented strand board` RER, 0.00165 m³ (1/607 kg/m³). TeR 1, GeR 1 |
| STEP 3 | 0.407 kg CO₂e/kg, inside the range 0.282–0.579 (4 datasets) → pass |
| A4 | T2 yes (DE Egger/Sonae, FR Swiss Krono, IT I-PAN) → 150 km lorry |
| A5 | board 34.1 kg → no machine row; prefab 3 % |
| B2 / B3 | indoor; no repair share |
| C1 | none (mechanically fixed) |
| End of life | NMD cat. 55: 5/85/10/0. Waste wood (untreated) incineration CH FAE and landfill CH as proxies; recycling = chipping service |

Unsure about:
- Whether Italy and Spain count for T2: only one Italian plant, and the Spanish line isn't confirmed. If Italy dropped out, transport would change to 1,500 km + 100 km.
- The CH FAE incinerator chosen by D3.
- Glued tongue-and-groove joints in floor decks, which could make C1 = yes.

## Hempcrete blocks (hempcrete)

| Step | Choice |
| --- | --- |
| S1 | hemp shiv 0.291 / hydraulic-lime binder 0.547 / water 0.162. The single EPD (Schönthaler, IT) gives only ranges; shares were derived from its biogenic carbon and densities |
| A1–A3 | D1 no → D5 built (TeR 3): `market for hemp hurd` FR, `market for hydraulic lime` RER, `market group for tap water` RER |
| Processing | mixing and pressing as a D6 proxy: energy of ecoinvent concrete block production DE (0.002 kWh electricity + 0.0216 MJ diesel per kg). TeR 5 |
| STEP 3 | 0.649 kg CO₂e/kg vs band 0.212–0.636 → flagged. Lime gives 84 % of the result. Reason recorded; nothing changed |
| A4 | T2 yes (IT Schönthaler, FR Biosys, ES Cannabric) → 150 km |
| A5 | blocks under 21 kg; laid with mortar → in situ 5 % |
| C1 | bonded → diesel 0.036 MJ/kg |
| End of life | no direct NMD match → heaviest constituent (lime) → cat. 40, 1/0/99/0. Unreinforced concrete recycling and inert landfill as proxies |

Unsure about (this is the least robust of the three materials):
- The S1 shares. The range midpoints would give binder 0.625.
- The processing energy proxy (per-kg versus per-volume basis).
- The end-of-life category. The EPD itself says incineration; cat. 52 would give 95 % incineration.
- Whether the Spanish (Cannabric) and German producers are current.

## Cork board (cork)

| Step | Choice |
| --- | --- |
| S1 | 100 % cork (Amorim ICB EPD HUB-0281). ÖKOBAUDAT has only a generic dataset without composition |
| A1–A3 | `market for cork slab` RER. It is resin-bonded (UF/MF/PF 14 %), unlike binder-free EN 13170 board, so it was treated as a glue-type variant: TeR 2 |
| STEP 3 | 0.959 kg CO₂e/kg vs band 0.256–0.768 (generic expanded cork 0.512) → flagged. The gap is expected from the resins; the Amorim EPD gives 0.720 |
| A4 | T2 no (production concentrated in Portugal) → T3 yes → 1,500 km lorry + 100 km ship |
| A5 | board ≤ 14 kg. Glued or screwed is "unclear", so the conservative branch was taken: in situ 5 % |
| B2 | outdoor, but no recoating prescribed → no rows |
| B3 | no repair share |
| C1 | unclear → conservative: diesel 0.036 MJ/kg |
| End of life | NMD cat. 52 (organic insulation): 5/95/0/0, with waste wood proxies. Cat. 55 (cladding board) would also fit |

Unsure about:
- D1. Answering "no" and building the board from `cork, raw` plus processing (D5) would avoid the resin and is the most likely difference between runs.
- Both "unclear" fixing answers (L1, C1).
- Cat. 52 vs 55.

## Files

`decisions.csv` (102 rows), `dataset_choices.csv`, `material_definitions.csv`, `epd_check.csv`, `LCI_osb3.xlsx`, `LCI_hempcrete.xlsx`, `LCI_cork.xlsx`, `protocol_issues.md` (26 items).
