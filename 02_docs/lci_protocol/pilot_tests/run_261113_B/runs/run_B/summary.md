# Summary: run_B (baseline LCI protocol, 13 Nov 2026 version)

Database: ecoinvent 3.12 cut-off (Brightway project `biobased_construction_impact_calculator`, read-only).
EPD check: ÖKOBAUDAT OBD_2024_III (release of 13.11.2026), EF 3.1 "climate change: fossil".

| Material | A1–A3 route | GWP-fossil A1–A3 (kg CO₂e/kg) | ÖKOBAUDAT median (n) | Ratio | STEP 3 | Cradle to grave (A1–C4) | DQR A1–A3 |
|---|---|---|---|---|---|---|---|
| OSB/3 | D1 yes → market for OSB, RER | 0.408 | 0.457 (4) | 0.89 | pass | 0.469 | 1.67 |
| Hempcrete blocks | D5 built | 0.817 | 0.424 (2) | 1.93 | **flagged** | 0.900 | 2.00 |
| Cork board (ICB) | D5 built (ecoinvent cork slab has resin) | 0.452 | 0.512 (1) | 0.88 | pass | 0.728 | 2.67 |

## OSB/3

**Composition (S1).** The median of three EPD composition tables (EGGER, Kronospan, Sonae Arauco), normalised to 1:
- wood incl. moisture: 0.951
- pMDI/MUF binder: 0.0339
- wax/additives: 0.0149

**A1–A3.** The ecoinvent OSB RER dataset holds the same constituent classes: MDI 3.0 %, paraffin 1.8 % and organic chemicals. D1 = yes, so the sheet uses `market for oriented strand board` RER at 0.00165 m³/kg (wet density 607 kg/m³).

**Downstream.**
- A4: T2 yes (DE, FR, IT), 150 km.
- A5: no machine energy (28.5 kg board), 3 % loss.
- C1: no diesel.
- End of life: NMD category 55 (5/85/10/0), with waste-wood datasets as variants.

**STEP 3.** Pass at 0.89× the median. The dry-mass trap the pilot found was avoided by using the dataset's wet density.

**Unsure about:**
- D1 counts MDI-only ecoinvent as the same constituents as EGGER's pMDI+MUF.
- The recycling row (dry-mass market) double-counts some transport.

## Hempcrete (hemp-lime blocks)

**Composition (S1).** Both EPDs give only ranges (Schönthaler in ÖKOBAUDAT, IsoHemp B-EPD). From range midpoints and their median:
- hemp shiv incl. moisture: 0.431
- air lime: 0.111
- natural hydraulic lime: 0.458

**A1–A3.** Not in ecoinvent, so D5: hemp hurd FR, hydrated lime RER and hydraulic lime RER. There are two processing proxies, each `market for plaster mixing` GLO:
- one for mixing;
- one for pressing, where the answer was "unclear" and the conservative branch was taken.

Air drying has no energy and gets no row.

**Downstream.**
- A4: T2 yes (IT, FR, ES), 150 km.
- A5: laid with mortar, 5 % loss.
- C1: bonded, so 0.036 MJ diesel.
- End of life: E1 unclear; via the heaviest constituent (lime) to category 8 (1/0/99/0), with waste concrete as a proxy.

**STEP 3.** 0.817 against a median of 0.424 (ratio 1.93) → fail. The targeted check (units, state, indicator, composition) found no provable error, so nothing was changed and the material is **flagged**. Likely reasons:
- The lime binder is about 80 % of the result, at ecoinvent's 0.9–1.0 kg CO₂e/kg, while its share sits in a 45–80 % range.
- There is only one producer, which uses a proprietary binder and PV power.
- The GLO plaster-mixing proxies add 0.11.

**Unsure about:**
- binder share and split;
- the pressing proxy;
- the end-of-life category (the EPD says the blocks cannot be landfilled and models incineration);
- the T2 evidence for ES (Cannabric's current production was not confirmed).

## Cork board (expanded insulation corkboard)

**Composition (S1).** 100 % cork, from the Amorim EPD HUB-0281 (bio-based 100 %, no adhesives).

**A1–A3.** D1 = no: ecoinvent `cork slab production` contains MF, PF and UF resins (0.14 kg/kg), which is the test case. Built with D5:
- raw cork PT: 1.06 kg (yield 0.943);
- grinding: wood-chipping proxy, GLO market;
- autoclave/steam expansion and cutting: the processing energy of ecoinvent cork slab production (4.92 MJ wood-chip heat + 1 kWh RER electricity per kg), without its cork and resins (rule 2).

**Downstream.**
- A4: T2 no, T3 yes (Portugal), so 1,500 km lorry + 100 km sea. This is 0.23 kg CO₂e/kg, half of A1–A3.
- A5: 3 % loss, no machine energy.
- C1: no diesel.
- End of life: category 52 (5/95/0/0), with waste wood as a proxy.

**STEP 3.** Pass at 0.88×, against a single generic dataset ("expanded cork", which may describe granulate rather than board). For reference, the resin-bound ecoinvent cork slab would score 0.93 (1.8×), so the D1 constituent test mattered.

**Unsure about:**
- the steam-step proxy (no published steam quantity was found);
- PT vs RoW in D3, since PT is not in the list;
- T2 for ES and FR, based on search excerpts only.

## General

- TiR could not be read from Brightway (no time period stored). The run scored it from the years cited in the documentation and used TiR 5 when none was cited, so DQRs are conservative.
- All protocol ambiguities are listed in `protocol_issues.md`.
- Outputs:
  - `decisions.csv` (183 rows)
  - `dataset_choices.csv` (35 rows)
  - `material_definitions.csv`
  - `epd_check.csv`
  - `LCI_osb3.xlsx`, `LCI_hempcrete.xlsx`, `LCI_cork.xlsx`
