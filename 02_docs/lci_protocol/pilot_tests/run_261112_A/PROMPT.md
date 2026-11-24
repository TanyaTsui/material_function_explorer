# Prompt for the agent (paste this into a fresh session)

You are running the baseline LCI protocol for a life cycle assessment study. Work only from the files in this folder.

**Files**
- `protocol.md`: the protocol. Follow it step by step, from START to END, for each material.
- `inputs.csv`: the materials to run. For each material you get exactly these facts: name and class, standard,
  delivered state, element types, and the function it is screened for (function name, outdoor yes/no, service life).
- `search_ecoinvent.py`: searches ecoinvent 3.12 cut-off in the local Brightway project. Use it for every dataset
  search (D1 to D4), e.g. `python search_ecoinvent.py "oriented strand board"`; run `python search_ecoinvent.py -h`
  for the options. Record the queries you ran as the search terms in `dataset_choices.csv`. You may also use bw2data
  directly to read an activity's documentation or exchanges, read-only: never write to the Brightway project.
- `templates/`: the output files with their columns, and `lci_template.xlsx`, the layout of the LCI sheet.

**Your task**
1. Create the folder `runs/<run_id>/` (run_id given below) and copy the templates into it.
2. Run the protocol for each material in `inputs.csv`, one at a time.
3. Log every decision in `decisions.csv`, every dataset choice in `dataset_choices.csv`, each material definition in
   `material_definitions.csv`, and each EPD check in `epd_check.csv`. Put `<run_id>` in the run_id column.
   For `row_purpose` in `dataset_choices.csv`, use these fixed names so runs can be compared:
   `constituent: <name>`, `processing: <step>`, `A2 transport`, `A4 lorry`, `A4 ship`, `A5 energy`, `A5 lorry`,
   `A5 end of life: <treatment>`, `B2 coating`, `B3 lorry`, `B3 end of life: <treatment>`, `C1 diesel`,
   `C2 lorry`, `C3-C4: <treatment>`.
4. Write one LCI sheet per material, `runs/<run_id>/LCI_<material_id>.xlsx`, following `lci_template.xlsx`.
5. Use the web to look up EPDs (ÖKOBAUDAT, EPD International, EPD Norge, EPD Hub, IBU), manufacturer documents,
   standards and the NMD end-of-life values, as the protocol says. Give a link for every source.

**Rules**
- Do not use any other file on this computer, earlier results, or your own memory of what the answer "should" be.
  Every value must come from a step of the protocol and a cited source, a protocol default, or a calculation shown.
- When a test cannot be answered, log "unclear" with one sentence on why, take the more conservative branch, and continue.
- When the protocol itself seems ambiguous, note it in `runs/<run_id>/protocol_issues.md` (step id, what was unclear,
  what you did). These notes are as valuable as the results.
- At the end, write a short `runs/<run_id>/summary.md`: per material, the main choices and anything you were unsure about.

run_id: run_A
