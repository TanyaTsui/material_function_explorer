# LCI sheets

One Excel file per case, in the Brightway Excel format: one block per activity, chained A1–A3 → A4 → A5 → C1 → C2 →
C3–C4, per kg of product. The file name is the case id used everywhere in the model.

| Files | Cases | Made by |
|---|---|---|
| `baseline_<material>.xlsx` | 27 baseline materials | the baseline LCI protocol, official run of 19 Nov 2026 (`02_docs/lci_protocol/`), then checked by hand |
| `raw_<product>_prototype.xlsx`, `raw_<product>_scaled_up.xlsx` | 4 RAW products × 2 variants | Tanya, from the partners' data (`RAW_LCA_inputs_v19`), in the same format |

## Changes on 24 Nov 2026 (move to this repository)

- Each RAW workbook (`raw_<product>.xlsx`, with a prototype and a scaled-up sheet) was split into two files, one per
  variant, so that every case has its own LCI. Shared sheets (the pea protein isolate of biopol) are in both files.
- Module B (the B3 repair and B4 replacement blocks) was removed from the RAW files: it depends on the function and is
  added in component 2. C1 now takes the A5 output directly. At typical values both blocks were 0, so modules A and C do
  not change.
- Each split file got its own database name (`raw_<product>_<variant>`). A note at the bottom of its README sheet says
  what was done.
- The original workbooks are in `archive/`, with `baseline_straw_bale` and `baseline_soft_wood_fibre_board` (dropped
  from the material list) and the commented biopol workbook of 19 Nov.

The model only reads the `amount` column (the typical value); formulas and ranges stay in the sheets for later use.
