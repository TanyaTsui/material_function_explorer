# Component 2: function–material map (to do)

Planned scripts:

- `2a_calculate_kg_per_function.py`: from the material properties and the function requirements
  (`01_data/01_raw/function_material_map/`), the kg of each material needed for each function (Ashby sizing; the
  largest requirement governs), or ✗ (fails a screen) or ? (missing property).
- `2b_calculate_function_impacts.py`: kg per function × unit impacts of component 1
  (`01_data/02_processed/unit_impacts_*.csv`), plus module B (B2 recoating, B3 repair, B4 replacements over the study
  period) and the time-dependent credit for the stored biogenic carbon. One table per scenario and impact category,
  same shape as the kg table.

Reference: the "RAW Function–Material Map" artifact.
