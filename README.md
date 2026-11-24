# RAW material function explorer

Model behind the paper *(reference to be added)*: environmental impacts of conventional and RAW bio-based construction
materials, compared per building function instead of per kg. Part of Work Package 4 of the RAW project (Horizon Europe).

The repository is written to be read: one script per step, each script reads files and writes files, every
intermediate result is a CSV you can open in Excel. It runs once to produce the results; speed does not matter.

## The model in three components

| | Component | Question | Status |
|---|---|---|---|
| 1 | **Unit impacts** | What is the impact of 1 kg of each material (27 baselines, 4 RAW products as prototype and scaled-up), today and in 2050? | built |
| 2 | **Function–material map** | How many kg of each material does each function need, and what is its impact per function? | to do |
| 3 | **Function explorer** | How do the materials compare, function by function? (interactive page) | to do |

```
 LCI sheets ──► 1. unit impacts ──────────────┐
 (per kg)       per kg, per module, 2 scenarios │
                                                ▼
 material properties ──► 2. kg per function ──► impact per function ──► 3. function explorer
 function requirements    (Ashby sizing)         (+ module B, carbon credit)
```

## Folders

```
01_data/
  01_raw/
    LCIs/                      one LCI sheet per case (Brightway Excel format); see its README
    cff_and_carbon_inputs/     per case: CFF archetype and end-of-life shares; constituents and carbon archetypes
    method_constants/          CFF and carbon archetype tables, avoided datasets of module D, GWP_bio and Bern tables
    function_material_map/     [component 2] functions, Ashby archetypes, material properties
  02_processed/
    unit_impacts_by_module_<today|2050>.csv   ◀ result of component 1
    unit_impacts_total_<today|2050>.csv       ◀ result of component 1
    unit_lcia_steps/                          intermediate tables, one per script
02_docs/
  methods_unit_lcia.md         what component 1 calculates (equations, choices, limitations)
  lci_protocol/                how the 27 baseline LCIs were made with AI agents: protocol, pilot tests, official run
03_model/
  settings.py                  paths, Brightway project, scenarios, impact method
  1_unit_lcia/                 component 1, scripts 1a to 1g
  2_function_material_map/     [component 2]
  3_function_explorer/         [component 3]
04_results/
  tables/, figures/            for the paper
```

## Run component 1

```bash
conda env create -f environment.yml      # once
conda activate brightway_env
cd 03_model/1_unit_lcia
python 1a_import_lcis.py                  # LCI sheets -> one table of exchanges
python 1b_calculate_background_impacts.py # Brightway: impact of 1 unit of each ecoinvent dataset (today, 2050)
python 1c_calculate_lcia_modules.py       # modules A1–A3 ... C3–C4
python 1d_calculate_module_d.py           # module D (circular footprint formula)
python 1e_calculate_biogenic_carbon.py    # CO2 stored in the product
python 1f_combine_unit_impacts.py         # -> 01_data/02_processed/unit_impacts_*.csv
python 1g_check_unit_impacts.py           # checks and one figure
```

Each script is split into cells (`# %%`): in VS Code, click "Run Cell" to run one cell at a time and see its table
under it, or run the whole file as above. Only step 1b needs Brightway with ecoinvent 3.12 cut-off and the premise
database (an ecoinvent licence); all other steps only need pandas. To change a path, the Brightway project or a
database name, edit `03_model/settings.py`.

## Changing an input

| To change | Edit | Then run |
|---|---|---|
| an LCI | the sheet in `01_data/01_raw/LCIs/` | 1a to 1g |
| end-of-life shares or CFF archetype of a case | `cff_and_carbon_inputs/cff_inputs.csv` | 1d, 1f, 1g |
| the constituents of a case | `cff_and_carbon_inputs/bioc_inputs.csv` | 1e, 1f, 1g |
| a CFF or carbon parameter | `method_constants/*.csv` | 1d or 1e, then 1f, 1g |

## Origin

Component 1 replaces the per-kg part of the earlier repository `biobased_construction_impact_calculator` (bcic), whose
comparative LCA of the four RAW prototypes stays there. Moved on 24 Nov 2026: the LCI sheets, the protocol
documentation, the function–material map data and the carbon tables. The CFF and carbon-storage equations follow
the bcic methods; the code is new.

## Citation and licence

*(to be added)*
