# Function–material map data

The three tables behind the RAW Function–Material Map artifact (tabs: Function library, Ashby archetypes, Materials).
They replace `data/materials/` and `data/screening/` (built 20 Nov 2026). All three are long or one-row-per-item
tables with identifying columns repeated, so each file is self-contained.

| File | One row per | Rows | What it holds |
|---|---|---|---|
| `functions.csv` | function × requirement | 66 (20 functions) | Function id, name, element type, `ashby_archetype`, functional unit, reference service life, reference product, and each requirement: `kind` = `screen` (pass/fail: property, `op`, `threshold`) or `sizing` / `sizing_fixed` (Ashby: `property`, `exponent`, anchor `m_ref_kg`, `rho_ref_kg_m3`, `p_ref`). The largest sizing mass governs. `old_function_id` is the id in the pre-Nov-2026 library (F01–F25). |
| `archetypes.csv` | Ashby archetype | 8 | Geometry assumption, derivation, material index, properties used, the functions that use it, and warnings. Formula for every sizing row: m = m_ref × (ρ/ρ_ref) × (P_ref/P)^n. |
| `materials.csv` | material × property | 161 (27 baseline + 4 RAW materials) | Material fields (`group` = `baseline` or `raw`, family, kind, element types, the three screening checks `flexible`, `max_length_m`, `outdoor`, and `lci_file` in `data/LCI/`), then one property row with `low`, `high`, `unit`, `basis`, `status`, `sources` and `source_urls` (baselines) or `low_factor`, `high_factor`, `orientation` (RAW). |

Properties: `rho` kg/m³, `E` GPa, `sigma_f` / `sigma_c` / `sigma_t` MPa (bending, compression, tension), `alpha_w` (sound
absorption). RAW rows also carry `phi`, `min_thickness`, `lambda` and `moisture_resistant`. Baseline values are typical
mean values: characteristic standard values were converted (timber ÷ 0.7, glulam and panels ÷ 0.8).

Notes
- The CSVs are UTF-8 with a byte-order mark so Excel shows ρ, σ and ⅔ correctly. Read them in Python with `encoding="utf-8-sig"` (pandas does this by default).
- Exponents 1/3 and 2/3 are stored as 0.3333 and 0.6667, as in the artifact, so results reproduce it exactly.
- Baselines are the 27 materials with a final LCI `data/LCI/baseline_*.xlsx`. Reinforced concrete σf and σt are derived
  estimates for the whole section including rebar (1.4 vol % × fy 500–550 MPa); see its `property_note`.
- RAW rows have one value (`low` = `high`), as in the artifact. The bands from the old `properties.csv` are kept as
  `low_factor` / `high_factor` for the uncertainty step. Their `max_length`, `flexible` and `outdoor_durable` values are
  in the material columns; their status and rationale are in `material_note`.
- Sources are written out in `materials.csv`, so there is no separate sources file.
- `data/screening/` was deleted: the old screening code (`raw_lca/screening/`, `pipeline/08_function_screen.py`,
  `pipeline/09_background_additions.py`, `tests/test_screening.py`) read it and has to be rewritten for these tables.
  The old files are in git history (last commit before 20 Nov 2026).
