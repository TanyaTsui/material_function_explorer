# Summary — run_A (19 Nov 2026)

- **Inputs:** ecoinvent 3.12 cut-off and the ÖKOBAUDAT release OBD_2024_III (13.11.2026).
- **Results:** GWP-fossil A1–A3 per kg, EF v3.1 "climate change: fossil", computed with Brightway (read-only).
- **Stopped materials:** none. All three materials passed the CHECK, mass balance.

| material | route kept | GWP-fossil A1–A3 | ÖKOBAUDAT median (n) | ratio | check |
|---|---|---|---|---|---|
| OSB/3 | approximate match | 0.407 | 0.457 (4) | 0.89 | CHECK 2 pass |
| hempcrete | built from scratch | 0.639 | 0.424 (2) | 1.51 | CHECK 3 fail → kept, flagged |
| cork | built from scratch | 0.0365 | 0.512 (1) | 0.07 | CHECK 3 fail → kept, flagged |

## OSB/3
- **D1 (no):** the ecoinvent OSB has MDI (3.0 %) instead of PMDI/MUF (5.1 %), plus an extra organic chemical (0.86 %).
- **D1b (yes):** the differing constituents add up to 5.96 % ≤ 10 %. Dataset: `market for oriented strand board` RER, 0.00165 m³ per kg (607 kg/m³).
- **Machines:** none (single dataset).
- **CHECK 2:** pass, ratio 0.89.
- **A4:** T2 unclear → national. DE and FR confirmed, ES not.
- **A5:** 3 % loss, no machine rows. **C1:** none.
- **End of life:** NMD category 55. All waste rows are W2 wood fallbacks.

## Hempcrete
- **D1 / D1b (no):** no hemp-lime product in ecoinvent.
- **Constituents (built):**
  - hemp hurd FR
  - hydrated lime, packed RER (air lime)
  - hydraulic lime RER
  - tap water RER
- **Machines:**
  - mixing: no complete datasheet → **unclear, no rows**
  - moulding and pressing: Nantong Hengda QT6-15 (36 kW, 10,834 kg/h, 10 t, 14 y), the only complete candidate → 0.00332 kWh/kg
  - air drying and curing: no energy
- **CHECK 3:** fail, ratio 1.505.
  - The hydraulic lime row is 66 % of the result.
  - The result hinges on the density used for one EPD: 430 kg/m³ from its name vs 405 kg/m³ in its metadata. With 405 it would pass. See protocol_issues.md, issue 3.
  - REVIEW: the built LCI was the only one tried, so it is kept and flagged.
- **A4:** T2 unclear → national. **A5:** 5 % (laid with adhesive mortar). **C1:** diesel (bonded).
- **End of life:** NMD category 8.

## Cork
- **D1 (no):** the ecoinvent cork slab contains 0.14 kg resin binder per kg.
- **D1b (no):** 14 % > 10 %.
- **Constituent (built):** `market for cork, raw` RoW, 1.06 kg. D3 was unclear: PT is not in the country list.
- **Machines:**
  - grinding: hammer mill, median of three (Bruks 0.031, Zorg 0.011, Rongda 0.005 kWh/kg) → Zorg 8 t/h
  - autoclave expansion: no datasheet or study with thermal power and throughput → **unclear, no rows**
  - cutting: no saw datasheet with throughput → **unclear, no rows**
- **CHECK 3:** fail, ratio 0.07. The missing autoclave heat is the likely cause. REVIEW keeps the built LCI (the only route) and flags it.
- **A4:** EU (made in PT; FR only among the five countries). **A5:** 3 %. **C1:** none (unclear).
- **End of life:** NMD category 52.

## Most unsure about
1. **The cork LCI is not credible as a baseline.** The lower-impact branch for a step with no machine data removed the dominant energy use.
2. **The hempcrete pass/fail depends on one EPD's density field.** Its mixing step also has no rows.
3. **A4 · T2 answers rest on unconfirmed plants** (Spain), so a second run may choose the EU archetype instead.
4. **Machine life comes from the German AfA table.** The protocol gives no default number of years.
5. **The wood-recycling fallback dataset is a production dataset.** I wrote it with a positive amount to avoid a credit.

- **Wear share of GWP-fossil A1–A3:** cork 0.09 %, hempcrete 0.005 %. OSB has no wear rows.
- **Not computed:** cradle-to-grave totals (not required).
