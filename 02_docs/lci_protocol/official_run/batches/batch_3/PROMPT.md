# Prompt for the agent (paste this into a fresh session)

You are running the baseline LCI protocol for a life cycle assessment study. Work only from the files in this folder.

**Files**
- `protocol.md`: the protocol. Follow it step by step, from INPUT to END, for each material.
- `material_definitions.csv`: the input, prepared by hand. For each material (`material_id`): its name, delivered
  state, every constituent (kg per kg of product) and every manufacturing step (kg processed per kg of product), with
  sources. A step whose `note` starts with "no energy" gets no machine rows. Take the input as it is; never change it.
  You are not told what the material will be used for: the LCI is per kg of material.
- `protocol_predetermined_values.xlsx`: the predetermined values. Where a step of the protocol says
  "**Excel:** … sheet `x`", read that sheet and take the value from it unchanged. Never change the workbook.
- `search_ecoinvent.py`: searches ecoinvent 3.12 cut-off in the local Brightway project. Use it for every dataset
  search (D1 to D5, W1), e.g. `python search_ecoinvent.py "oriented strand board"`; run
  `python search_ecoinvent.py -h` for the options. Record the queries you ran as `search_terms` in
  `dataset_choices.csv`. You may also use bw2data directly to read an activity's documentation or exchanges (D1 asks
  you to compare a dataset's inputs with the constituents of the input), read-only: never write to the Brightway project.
- `templates/`: the output files with their columns, and `lci_template.xlsx`, the layout of the LCI sheet.

**Your task**
1. Create the folder `runs/<run_id>/` (run_id given below) and copy the templates into it.
2. Run the protocol for each material in `material_definitions.csv`, one at a time, in the order of the file.
3. Log every decision in `decisions.csv`, every dataset choice and every machine row in `dataset_choices.csv`, each
   ÖKOBAUDAT check in `epd_check.csv`, and the module D inputs in `cff_inputs.csv` (F2) and `bioc_inputs.csv` (B2).
   Put `<run_id>` in the run_id column.
   - `question_id` in `decisions.csv`: the step id from `protocol.md` (e.g. `D1`, `CHECK 1`, `A4 · T2`, `C2 · ROUTE`,
     `D · CFF · F1`). For steps repeated per constituent, manufacturing step or waste item, add it after a colon, in the
     exact words of `material_definitions.csv`: `D5: lime`, `D3: lime`, `P1: grinding`, `P2: grinding`,
     `W1: lime × landfill`, `D · BIO-C · B1: lime`.
   - `check_id` in `epd_check.csv`: `CHECK 1` (exact match), `CHECK 2` (approximate match), `CHECK 3` (built from scratch) or `REVIEW` (the comparison when all checks failed). Also fill `route` (`exact`, `approximate`, `built`), `distance_to_median` (|our value ÷ median − 1|) and, on the REVIEW row, `lci_kept` (the route kept).
   - `row_purpose` in `dataset_choices.csv`, fixed names so runs can be compared:
     `finished product` (exact match), `finished product (approximate)` (D1b), `constituent: <name>`, `processing: <step> (electricity)`, `processing: <step> (heat)`,
     `machine: <step>`, `A2 transport`, `A4 lorry`, `A4 ship`, `A5 diesel`, `A5 lorry (loss)`,
     `A5 end of life: <constituent> × <route>`, `C1 diesel`, `C2 lorry`, `C3-C4: <constituent> × <route>`.
     For P1 and P2 rows, also fill the machine columns (machine type, the three candidates, the one used, power,
     throughput, mass, life, values as found, source, link, conversions, value per kg processed).
4. Write one LCI sheet per material, `runs/<run_id>/LCI_<material_id>.xlsx`, following `lci_template.xlsx`
   (blocks A1–A3, A4, A5, C1, C2, C3–C4).
5. Use the web to look up ÖKOBAUDAT EPDs, machine datasheets (P1, P2), manufacturers (A4 · T2, T3), piece weights
   (A5 · I1, C1 · X1), EU BREF documents and studies, as the protocol says. Give a link for every source.
6. For every check (CHECK 1, 2 and 3, and each LCI compared in the REVIEW), compute GWP-fossil A1–A3 of 1 kg with Brightway (EF 3.1, climate change: fossil),
   read-only. In the same calculation, record the share of the machine (P2) rows in `wear_share_of_gwp_fossil_a1a3`.
   If you cannot run the calculation, write "not computed" and continue.

**Rules**
- Do not use any other file on this computer, earlier results, or your own memory of what the answer "should" be.
  Every value must come from a step of the protocol and a cited source, the workbook, or a calculation shown.
- When a test cannot be answered, log "unclear" with one sentence on why, take the branch that gives the lower impact,
  and continue.
- The checks never change a number. Never change a choice because it brings the result closer to the EPD median.
- If the protocol says STOP for a material (the rows do not match the input), stop that material, record it in
  `protocol_issues.md` and `summary.md`, and go on to the next material.
- When the protocol itself seems ambiguous, or the workbook and the protocol disagree, note it in
  `runs/<run_id>/protocol_issues.md` (step id, what was unclear, what you did). These notes are as valuable as the
  results.
- At the end, write a short `runs/<run_id>/summary.md`: per material, the main choices (D1, the machines used per
  step), the CHECK outcomes, and anything you were unsure about.

run_id: batch_3
