# Inputs of module D and of the stored biogenic carbon

Two tables, one or more rows per case (all 35 cases). Read by steps 1d and 1e.

| File | One row per | Columns |
|---|---|---|
| `cff_inputs.csv` | case, or part of a case | `cff_archetype` (a row of `method_constants/cff_archetypes.csv`), `mass_share` (share of the case's mass in this archetype; 1 for a case with one row; the rows of a case add up to 1), end-of-life shares (recycling, reuse, incineration, landfill; they add up to 1 and match the C3–C4 block of the LCI). Only reinforced concrete has two rows: concrete 0.955, steel 0.045 |
| `bioc_inputs.csv` | constituent of a case | `kg_per_kg_product` (losses excluded: only what ends up in the product), `carbon_archetype` (a row of `method_constants/carbon_archetypes.csv`), `moisture_content` (dry basis; empty = archetype default) |

Both have `source`, `flag` and `note` columns:

- **Baselines**: written by the protocol agents in the official run (`02_docs/lci_protocol/official_run/results/`),
  copied unchanged. The official run had one concrete; its rows are used for both concrete files (noted), plus a
  steel row for reinforced concrete (added by hand).
- **RAW cases**: written by hand on 24 Nov 2026 from the RAW LCI sheets (same rows for prototype and scaled-up).
  To check, especially the rows flagged "closest archetype" or "conservative".
