# Summary — run_B (17 Nov 2026)

Three materials were run in the order of `material_definitions.csv`: osb3, hempcrete, cork. None stopped: the mass CHECK passed for all three. D1 was **no** for all three, so each LCI was built from scratch and checked against ÖKOBAUDAT with CHECK 2 (release OBD_2024_III, 13 Nov 2026). GWP-fossil A1–A3 was computed in Brightway (ecoinvent 3.12 cut-off, EF 3.1 climate change: fossil), read-only.

| material | D1 | GWP-fossil A1–A3 (kg CO₂e/kg) | ÖKOBAUDAT median (n) | ratio | CHECK 2 | machine (P2) share |
|---|---|---|---|---|---|---|
| osb3 | no | 0.416 | 0.457 (4) | 0.91 | pass | 0.08 % |
| hempcrete | no | 0.639 | 0.424 (2) | 1.51 | **fail → flagged** | 0.01 % |
| cork | no | 0.070 | 0.512 (1) | 0.14 | **fail → flagged** | 0.54 % |

The wear rows are under 1 % for every material, so no machine review was triggered (threshold 2 %).

## osb3 (OSB/3, board, unsanded)

- **D1 no.** The ecoinvent OSB (EPF average) has an extra 0.86 % of "unspecified additives, dyes, flame retardants" and no MUF.
- **Constituents:**
  - wood strands → `market for pulpwood, softwood, with bark…` (Europe without Switzerland), 0.00196 m³
  - PMDI/MUF → `market for methylene diphenyl diisocyanate` (RER), chosen by D3 over the MUF adhesive, which exists only as GLO
  - paraffin → `market for paraffin` (GLO)
- **Machines per step:**
  - debarking: roller debarker, Leabon LB-Z700S (median of 3)
  - flaking: knife ring flaker, Suzhou Yiweite BX4614/5 (median of 3)
  - drying: rotary drum dryer, Fote Φ3.6×28 for electricity and mass (median of 3); heat from the EU BREF (OSB drying, 1.50 MJ/kg)
  - blending: Henan Pallet BS450 ring blender (energy only; no mass, so no wear row)
  - continuous pressing: EU BREF energy only; heat uses the particleboard proxy; no wear row
  - cutting to size: Mingding DD saw (the only complete datasheet)
  - cooling, stacking: no energy
- **A4:** T1 no, T2 no (DE and FR only), T3 yes → EU transport.
- **A5:** 3 % loss (33.6 kg sheets, prefab).
- **C1:** no diesel.
- **End of life:** NMD category 55; wood to W1 datasets, glue and wax to the W2 plastic fallback.
- **CHECK 2 passes.** The MDI glue is half of the result.

## hempcrete (IsoHemp-type block)

- **D1 no.** There is no hemp-lime dataset in ecoinvent.
- **Constituents:**
  - hemp shiv → `market for hemp hurd` (FR)
  - air lime → `market for hydrated lime, packed` (RER)
  - natural hydraulic lime → `market for hydraulic lime` (RER)
  - water → `market group for tap water` (RER)
- **Machines per step:**
  - mixing: twin-shaft mixer Camelway JS3500 (the only complete datasheet)
  - moulding and pressing: block press, Jiangsu Huawei QT10-15 (lower of 2)
  - air drying: no energy
- **A4:** T2 yes (FR, IT, ES) → 150 km.
- **A5:** 5 % loss (laid with adhesive mortar).
- **C1:** diesel, because the blocks are bonded.
- **End of life:** NMD category 8; all items go to W2 fallbacks.
- **CHECK 2 fails by a hair (1.51).** The lime binders, which are 53 % of the mass at about 1 kg CO₂e/kg, dominate. Both EPDs come from one Italian producer. The material is flagged; the numbers are unchanged.

## cork (expanded cork board, pure)

- **D1 no.** The ecoinvent cork slab contains MF, UF and phenolic resins.
- **Constituent:** raw cork granules → `market for cork, raw` **RoW**. PT ranks after RoW under a literal reading of D3, and RoW is also the lower-impact option.
- **Machines per step:**
  - grinding: hammer mill, Bruks HH 600×2000 (median of 3)
  - autoclave expansion: **proxy** EPS block moulding machine, Epsole ESB600V (TeR 4); there is no cork-autoclave data anywhere
  - cutting: band resaw, Fill speedliner 710
  - cooling and stabilising: no energy
- **A4:** T3 → EU (PT).
- **A5:** 3 % loss (unclear: bonded in ETICS?).
- **C1:** no diesel (unclear).
- **End of life:** NMD category 52; cork goes to "as wood" W2 fallbacks. 1.00 kg was used, not 1.06.
- **CHECK 2 fails (0.14).** There is a single Sphera generic dataset, and the autoclave heat comes from a proxy that is likely far too low (0.40 MJ/kg against 4.92 MJ/kg in the ecoinvent cork slab). The material is flagged.

## What I am unsure about

- **D1 for OSB:** a strict reading of a < 1 % additive.
- **D3 for countries outside the list:** PT and GB.
- **Machine data:**
  - The model chosen within each range (largest model).
  - Steps where fewer than three complete datasheets exist.
  - The BREF and proxy values for dryer heat, press and autoclave.
  - Machine lives from the German AfA tax tables.
- **Missing data quality scores:** TiR and DQR are missing (no time period in the Brightway import).
- **Cork:** the autoclave proxy is the weakest number in this run and the main reason for the cork check failure.

Details: `protocol_issues.md` (30 notes), `decisions.csv`, `dataset_choices.csv`, `epd_check.csv`.
