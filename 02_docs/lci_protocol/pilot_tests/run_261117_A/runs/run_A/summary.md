# Summary — run_A (17 Nov 2026)

Database: ecoinvent 3.12 cut-off. Checks: EF 3.1 climate change: fossil, read-only Brightway. ÖKOBAUDAT release: OBD_2024_III. No material stopped; the full list of issues is in `protocol_issues.md`.

| material | D1 | A1–A3 GWP-fossil (kg CO₂e/kg) | ÖKOBAUDAT median (n) | ratio | check | wear share |
|---|---|---|---|---|---|---|
| osb3 | yes: market for oriented strand board, RER (0.00165 m³ = 1 kg at 607 kg/m³) | 0.408 | 0.457 (4) | 0.89 | CHECK 1 pass | – (no P2 rows) |
| hempcrete | no → built from scratch | 0.640 | 0.424 (2) | 1.51 | CHECK 2 fail → **flagged** | 0.012 % |
| cork | no (ecoinvent cork slab has MF/PF/UF resins) → built from scratch | 0.0593 | 0.512 (1) | 0.12 | CHECK 2 fail → **flagged** | 0.49 % |

## OSB/3

- **D1–D4.** market for oriented strand board, RER (rules D2, D3; one variant).
- **A4.** T1 no; T2 yes: DE EGGER Wismar, FR SWISS KRONO Sully-sur-Loire, IT I-PAN. National: lorry 0.15 tkm.
- **A5 and C1.** I1 no (board 2500 × 1250 × 18 mm ≈ 33.8 kg). L1 no (3 %). X1 no.
- **C2–C4.** NMD category 55 (5/85/10/0).
- **Waste rows.** W1 no → W2 wood class (waste wood landfill CH, incineration GLO, sorting/shredding CH).
- **Module D.** CFF archetype: Wood panels.

## Hempcrete

**Constituents (D5 yes for all):**
- hemp shiv → market for hemp hurd, FR
- air lime → market for hydrated lime, packed, RER
- natural hydraulic lime → market for hydraulic lime, RER
- water → market group for tap water, RER

**Machines (median of three):**

| step | machine used | power | throughput | mass | life | other candidates |
|---|---|---|---|---|---|---|
| mixing | Zhengzhou Focus MP1000 planetary mixer | 37 kW | 13,135 kg/h | 5,500 kg | 6 y | CO-NELE CMP1000, Dom MP1000 |
| moulding and pressing | Tancheng Hongbaoyuan QT10-15 block machine | 55.5 kW | 13,632 kg/h | 12,000 kg | 10 y | Queen QT10-15, Henry QT10-15 |

Air drying and curing: no energy.

**A4–C4:**
- A4: T2 yes (FR Vieille Matériaux, IT Equilibrium / Schönthaler, ES Cannabric) → lorry 0.15 tkm.
- A5: I1 no (block about 11.5 kg). L1 yes (glued with thin-joint mortar) → 5 %.
- C1: X1 yes (bonded) → diesel 0.036 MJ.
- C2: NMD category 8 (1/0/99/0).
- Waste rows: W2 for every item.
- Module D: CFF archetype Mineral, crushed to aggregate.

**Flag.** The ratio of 1.51 is just outside the band. Hydraulic lime carries about 66 % of A1–A3, and the EPDs come from one producer. The result hinges on the per-kg density used for one ÖKOBAUDAT dataset: 430 (from its name) gives 1.51; 405 (its material property) would give 1.47.

## Cork

**Constituent.** raw cork granules → market for cork, raw, **RoW**. PT is not in the D3 country list, so it ranks after RoW; RoW is also the lower-impact option.

**Machines (median of three):**

| step | machine used | power | throughput | mass | life | other candidates |
|---|---|---|---|---|---|---|
| grinding | BIOMAC KD 110-550 hammer mill | 50 kW | 1,750 kg/h | 5,185 kg | 7 y | Bruks HH 300x850, Zorg 8 t/h |
| autoclave expansion | **PROXY**: Milon ML-2000VS EPS steam block moulder | 301 kW thermal + 19.75 kW | 4,140 kg/h | 5,000 kg | 10 y | Epsole ESB200V, Zhongji EPSSM2000 |
| cutting blocks into boards | Centauro Supercut 80 band resaw | 15 kW | 16,560 kg/h | 880 kg | 6 y | Felder FB 940 RS, Weinig PowerSplit 1250 |

Cooling and stabilising: no energy. No cork-autoclave datasheet exists, so the autoclave rows use the proxy rule (TeR 4).

**A4–C4:**
- A4: T2 no; T3 yes (Amorim, PT) → lorry 1.5 tkm + ship 0.1 tkm.
- A5: I1 no (board ≤ 17.3 kg). L1 no (screwed, dry) → 3 %.
- C1: X1 no.
- C2: NMD category 52 (5/95/0/0).
- Waste rows: W2 "as wood".
- Module D: CFF archetype Other plant-based.

**Flag.** Our value is about 1/9 of the single generic EPD. The proxy autoclave gives 0.26 MJ heat and 0.036 kWh electricity per kg; the ecoinvent cork slab uses 4.92 MJ and 1 kWh. So the P1 machine-rating method almost certainly understates the cork autoclave.

## Things I was unsure about

- **D1 for OSB.** I read ecoinvent's unspecified "chemical, organic" as part of the PMDI/MUF adhesive.
- **Machine life.** The protocol has no life source. I used the German BMF AfA tables × 5,000 h/yr.
- **Ranges in datasheets.** I took the midpoint.
- **Density as processed.** Hempcrete 355 kg/m³ (bulk at delivery; no fresh-mix value found). Cork 115 kg/m³ (Amorim).
- **Sign of the wood recycling dataset.** It produces wood chips, so I wrote it as a positive amount.
- **Waste mass for cork.** I used 1.00 kg, not 1.06 kg.
- **TiR and DQR.** They are mostly blank: the Brightway import has no time period.
