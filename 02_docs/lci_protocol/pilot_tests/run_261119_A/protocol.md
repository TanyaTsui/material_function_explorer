# Baseline LCI protocol

Version: 19 Nov 2026, exported from the "Baseline LCI Protocol" flowchart (artifact version 1795092172-ab01). Follow it step by step for one material at a time.

## How to use this protocol

- Work through the steps in order, from INPUT to END. Each step has an id (e.g. `A4 · T2`). Each step ends with **Go to**, the arrow(s) to follow.
- **The input** is `material_definitions.csv`: for each material, its name and delivered state, every constituent (kg per kg of product) and every manufacturing step (kg processed per kg of product), with sources. It was prepared by hand. Take it as it is and never change it.
- **The workbook** `protocol_predetermined_values.xlsx` holds the predetermined values. Where a step starts with "**Excel:** … sheet `x`", read that sheet and take the value from it unchanged. The flowchart does not repeat those values: the sheet is the only source. Never change the workbook.
- **Decisions** are yes/no questions. Apply the written test, answer yes or no, and follow the matching arrow.
- **Log every decision** as one row in `decisions.csv`: material_id, question_id, answer (yes/no), value, unit, evidence (one sentence), source_link, date. Where a step asks you to record a value, a choice or a derivation, log it in the same file with answer = the value.
- **Log every dataset you choose**, and every machine row (P1, P2), in `dataset_choices.csv`.
- **Never guess silently.** If a test cannot be answered, write "unclear" with a sentence on why, take the branch that gives the lower impact, and continue.
- The LCI describes 1 kg of material, whatever it is later used for. Modules B and D have no rows in the sheet: the model adds them. For D, you only write `cff_inputs.csv` and `bioc_inputs.csv`.
- The LCI is written as one Excel sheet per material in the Brightway Excel format, one block per module, chained: each block's first input is the previous block's output (see `templates/lci_template.xlsx`). The blocks are A1–A3, A4, A5, C1, C2 and C3–C4.

## Input: Prepared by hand, before the run

### INPUT: Prepared by hand beforehand: the name of the material, the mass of every constituent, and each manufacturing step

The flow runs once per baseline material: the 28 baseline materials, and any material added later.

#### The input, prepared by hand

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `input_definitions` (the content of `material_definitions.csv`: the constituents and steps of each material) and sheet `material_overview` (ÖKOBAUDAT dataset and link per material).

Before the run you write `material_definitions.csv`. The agent reads it and cannot change it, so two runs start from the same bill of materials and the same list of steps. It holds:

- **The name of the material**, with its delivered state (e.g. glulam, kiln dried, planed, untreated).
- **Every constituent**, in kg per kg of product, losses included, with a cited source. No cut-off: a small glue, binder or coating can carry a large part of the impact. Moisture counts with its constituent.
- **Every manufacturing step**, in order, with the kg processed per kg of product and a cited source. A step that uses no machine energy is marked in its note (see P1).

| Column | Constituent row | Step row |
| --- | --- | --- |
| `kind` | constituent | step |
| `name` | e.g. raw cork | e.g. autoclave expansion |
| `amount` | kg per kg of product | kg processed per kg of product |
| `source`, `link`, `note` | cited source; range or midpoint used | cited source; note on the step |

#### Suggested conventions

- Search order for constituents and steps: the EPD for this product (ÖKOBAUDAT, then the EPD registries; the same EPD for both), the manufacturer, the EU BREF or a handbook, then a peer-reviewed study.
- A composition range: the midpoint, rescaled so the shares sum to 1; several EPDs: the median share. Write the call in `note`. In the pilot the hempcrete binder range (45–80 %) drove most of the remaining gap to the EPD median.
- Packaging, palletising and storage are not steps.
- Check before the run: the constituent shares sum to 1 before losses, and every step has a kg-processed value.

> **Example.** Cork board, illustrative: constituent raw cork 1.06; steps grinding 1.06, autoclave expansion 1.00, cooling and stabilising 1.00, cutting 1.00.

#### What the run produces

- One Excel sheet in the Brightway format, with one block per module, chained: each block's first input is the previous block's output.
- `decisions.csv`, `dataset_choices.csv` and `epd_check.csv`.
- `cff_inputs.csv` (module D, F2) and `bioc_inputs.csv` (biogenic carbon, B2), read by the model's scripts.

#### Fixed settings

|  |  |
| --- | --- |
| Database | ecoinvent 3.12 cut-off |
| Scenario | premise IMAGE SSP2-L 2050, applied by the model; same LCI for both |
| Method | EF 3.1, 16 categories |
| Mass basis | as delivered, incl. moisture |
| Rounding | 3 significant figures |

#### Golden rule

Every decision in the run is a diamond in this chart, with a written test. Its answer and the evidence are recorded, so a second run can be compared answer by answer.

#### When a test cannot be answered

Log "unclear" with one sentence on why, take the branch that gives the lower impact, and continue. Baselines get the benefit of the doubt: a padded baseline would make the RAW materials look better than they are.

**Go to:** Next → `D1`


## A1–A3: Product stage · exact match, approximate match, or built from scratch

### D1: Is the finished product in ecoinvent, in its delivered state, with the constituents of the input?

*Decision: apply the test, answer yes or no, log it.*

**D1 Exact match.** Search ecoinvent 3.12 cut-off for the finished product: same name, same delivered state (dried, planed, hot rolled), and the same constituents as the input. A dataset with an extra constituent (e.g. a resin binder) or without one the input lists is not an exact match. Record search terms and candidates.

> **Example.** Cork board: the input lists cork granules only, bound by heat and steam. The ecoinvent dataset includes a resin binder → no.

**Yes** → pick that dataset (D2–D4), write one row, and go to check 1. Its steps and machines are already inside the dataset.

**No** → look for an approximate match (D1b).

> **Example.** Brick: "clay brick" exists with the same constituents → yes.

An exact match scores TeR = 1.

**Go to:** Yes → `YES · D2–D4 · DATASET`; No → `D1b`

### YES · D2–D4 · DATASET: Market dataset first, else production + an A2 transport row; then location and variant

The finished product has a dataset. Pick it with three rules in order, then write one row. No mass check is needed, because the LCI is not built from parts: go straight to check 1.

#### D2 Market or production

**D2 Market first.** Use `market for <product>`. It includes average transport to the buyer and market losses, so it already covers A2.

**Yes** → pick its location (D3). **No** → production dataset plus a transport row.

> **Example.** Brick: `market for clay brick`.

No market dataset: use the production activity and add one A2 row: lorry tkm with the material's A4 distance.

#### D3 Location

**D3 Geography.** Take the first location that exists:

1. European market group (RER or Europe without Switzerland): the production-weighted European average
2. RER
3. Europe without Switzerland
4. A single European country, in this order: DE, FR, IT, ES, NL, AT, SE, FI, PL, CH
5. GLO
6. RoW
7. any other

Global market groups are never used: they mix in supply from outside Europe. **Decided 12 Nov:** a single European country comes before GLO.

> **Example.** Brick: if no European dataset exists, a German one is taken before GLO.

#### D4 Variant

**D4 Variants.** Several datasets can remain for the same product and location: indoor or outdoor use, strength class, glue type.

Take the variant that matches the delivered state from step 1. When none matches better, take the one whose name comes first alphabetically, and record the others. A different variant of the same product scores TeR = 2.

**Go to:** Next → `ROW (Write one row)`

### ROW: Write one row: 1 kg of that dataset; record rule, TeR, GeR, TiR

One row in the A1–A3 block:

- **amount** = the amount from the input: kg per kg of product, losses and yield included.
- **rule** = the D rule that decided the dataset.
- **TeR, GeR, TiR** read from the rule and the dataset (table below).

|  | TeR | GeR | TiR |
| --- | --- | --- | --- |
| 1 | D1 exact | RER, Europe w/o CH | 2020+ |
| 2 | D4 variant; D1b approximate match | one EU country | 2015–19 |
| 3 | built from constituents; machine energy and wear (P1, P2) | GLO | 2010–14 |
| 4 | proxy: constituent or machine | RoW | 2005–09 |
| 5 | – | other | <2005 |

DQR = (TeR + GeR + TiR) ÷ 3, mass-weighted over the material rows (energy and wear rows carry their kg processed); above 3 is marked low quality.

> **Example.** market for clay brick · 0.8 kg · D2  
> market for lime mortar · 0.2 kg · D2

**Go to:** Next → `CHECK 1`

### CHECK 1: Is GWP-fossil A1–A3 within ±50 % of the ÖKOBAUDAT median?

*Decision: apply the test, answer yes or no, log it.*

**Check 1, for an exact match (D1).**

**Yes** → continue to the A1–A3 block. **No** → keep this LCI and its result for the review, and try an approximate match (D1b). Log why it failed.

#### The test

Take every EN 15804+A2 dataset in the product's category from the latest ÖKOBAUDAT release, convert to per kg, and compare GWP-fossil A1–A3 (fossil only, because biogenic carbon is treated differently). Pass when our value is between 0.5× and 1.5× the median of those EPDs. With one EPD, its value is the median. No EPD: log "no check possible" and continue.

Why ±50 %: EPDs within one category typically spread with a coefficient of variation of 33–80 % (Hoxha et al. 2024), and generic data such as ecoinvent tend to sit above EPDs, so a smaller gap is not evidence of an error.

The check never changes a number by itself.

**Log.** Log in `epd_check.csv`: our value, the median, the number of EPDs, pass or fail.

**Go to:** Yes → `A1–A3 BLOCK`; No → `D1b`

### D1b: Is the finished product in ecoinvent, in its delivered state, with nearly the same constituents?

*Decision: apply the test, answer yes or no, log it.*

**D1b Approximate match.** Reached when there is no exact match (D1 no), or when the exact match failed check 1. Search ecoinvent 3.12 cut-off for the finished product in its delivered state whose constituents differ only slightly from the input.

#### The test: all three must hold

1. **Same product and delivered state** as in D1 (same name, same state).
2. **Same main constituent**: the constituent with the largest mass share in the input is also the main constituent of the dataset.
3. **Small difference**: the constituents that differ (extra in the dataset, missing from it, or replaced by another) add up to at most **10 %** of the mass of the input. *Threshold is our assumption; to be settled.*

Read the constituents of the dataset from its inputs (technosphere exchanges) or its documentation. If its shares cannot be read, the test cannot be answered: log "unclear" and answer no.

If the exact-match dataset from D1 failed check 1, it cannot be picked again here: it would only fail again.

**Yes** → pick that dataset (D2–D4), write one row, and go to check 2. **No** → build the LCI from scratch.

> **Example.** Cork board: the ecoinvent cork board dataset has cork granules as its main constituent plus a resin binder. If the binder is under 10 % of the mass → yes, an approximate match.

**Log.** Log in `decisions.csv`: material, D1b, answer, the dataset, each constituent that differs with its mass share, the sum, evidence.

**Go to:** Yes → `YES · D2–D4 · DATASET (approximate match)`; No → `BUILD FROM SCRATCH`

### YES · D2–D4 · DATASET (approximate match): Same rules: market dataset first, else production + an A2 transport row; then location and variant

The approximate match is picked with the same three rules as an exact match. Pick it with three rules in order, then write one row. No mass check is needed, because the LCI is not built from parts: go straight to check 2.

#### D2 Market or production

**D2 Market first.** Use `market for <product>`. It includes average transport to the buyer and market losses, so it already covers A2.

**Yes** → pick its location (D3). **No** → production dataset plus a transport row.

> **Example.** Brick: `market for clay brick`.

No market dataset: use the production activity and add one A2 row: lorry tkm with the material's A4 distance.

#### D3 Location

**D3 Geography.** Take the first location that exists:

1. European market group (RER or Europe without Switzerland): the production-weighted European average
2. RER
3. Europe without Switzerland
4. A single European country, in this order: DE, FR, IT, ES, NL, AT, SE, FI, PL, CH
5. GLO
6. RoW
7. any other

Global market groups are never used: they mix in supply from outside Europe. **Decided 12 Nov:** a single European country comes before GLO.

> **Example.** Brick: if no European dataset exists, a German one is taken before GLO.

#### D4 Variant

**D4 Variants.** Several datasets can remain for the same product and location: indoor or outdoor use, strength class, glue type.

Take the variant that matches the delivered state from step 1. When none matches better, take the one whose name comes first alphabetically, and record the others. A different variant of the same product scores TeR = 2.

**Go to:** Next → `ROW (approximate match)`

### ROW (approximate match): Write one row: 1 kg of that dataset; log the constituents that differ

One row in the A1–A3 block: 1 kg of the approximate-match dataset. TeR = 2. Record in `dataset_choices.csv` the constituents that differ from the input and their mass shares, so the paper can show what the stand-in includes or leaves out. Otherwise as the ROW above.

**Go to:** Next → `CHECK 2`

### CHECK 2: Is GWP-fossil A1–A3 within ±50 % of the ÖKOBAUDAT median?

*Decision: apply the test, answer yes or no, log it.*

**Check 2, for an approximate match (D1b).**

**Yes** → continue to the A1–A3 block. **No** → keep this LCI and its result for the review, and build the LCI from scratch. Log why it failed.

#### The test

Take every EN 15804+A2 dataset in the product's category from the latest ÖKOBAUDAT release, convert to per kg, and compare GWP-fossil A1–A3 (fossil only, because biogenic carbon is treated differently). Pass when our value is between 0.5× and 1.5× the median of those EPDs. With one EPD, its value is the median. No EPD: log "no check possible" and continue.

Why ±50 %: EPDs within one category typically spread with a coefficient of variation of 33–80 % (Hoxha et al. 2024), and generic data such as ecoinvent tend to sit above EPDs, so a smaller gap is not evidence of an error.

The check never changes a number by itself.

**Log.** Log in `epd_check.csv`: our value, the median, the number of EPDs, pass or fail.

**Go to:** Yes → `A1–A3 BLOCK`; No → `BUILD FROM SCRATCH`

### BUILD FROM SCRATCH: Go through every constituent (left) and every manufacturing step (right) of the input

Reached when there is no approximate match (D1b no), or when the approximate match failed check 2. The LCI is built from the input:

- **Every constituent** (left) gets a dataset and becomes a material row.
- **Every manufacturing step** (right) gets the power and throughput, and the life and mass, of its machine (P1, P2), and becomes energy rows and a machine row.

The agent takes the input as it is and does not change it.

**Note.** Changed 13 Nov: steps are no longer searched for in ecoinvent. That search is what made the two pilot runs differ (compression of sheet moulding compound, plaster mixing, drying of grass).

**Go to:** For each constituent → `D5`; For each manufacturing step → `P1 · ENERGY`

### D5: Is this constituent in ecoinvent?

*Decision: apply the test, answer yes or no, log it.*

**D5 Constituent match.** Search ecoinvent 3.12 cut-off for the constituent, in the state it enters the factory. Record search terms and candidates.

**Yes** → pick it with the same rules as D2–D4. **No** → a similar material, flagged.

**Log.** Log in `decisions.csv`: material, question id, constituent, answer, evidence.

**Go to:** Yes → `PICK`; No → `PROXY`

### PICK: Market first, else production; then location and variant, as D2–D4

Same rules as for a finished product (D2–D4): market dataset first, else the production dataset plus an A2 lorry row; then the location in the D3 order; then the variant that matches the state, else the first A–Z.

**Go to:** Next → `ROW (Write the material row)`

### PROXY: Pick a similar material and flag it (TeR 4)

Take the closest dataset of the same raw-material class (e.g. another plant fibre for hemp shiv). Log it in `dataset_choices.csv` as a proxy with one sentence on why. TeR = 4. Flagged constituents are listed in the paper.

**Go to:** Next → `ROW (Write the material row)`

### ROW: Write the material row: kg from the input; rule, TeR, GeR, TiR

One row in the A1–A3 block:

- **amount** = the amount from the input: kg per kg of product, losses and yield included.
- **rule** = the D rule that decided the dataset.
- **TeR, GeR, TiR** read from the rule and the dataset (table below).

|  | TeR | GeR | TiR |
| --- | --- | --- | --- |
| 1 | D1 exact | RER, Europe w/o CH | 2020+ |
| 2 | D4 variant; D1b approximate match | one EU country | 2015–19 |
| 3 | built from constituents; machine energy and wear (P1, P2) | GLO | 2010–14 |
| 4 | proxy: constituent or machine | RoW | 2005–09 |
| 5 | – | other | <2005 |

DQR = (TeR + GeR + TiR) ÷ 3, mass-weighted over the material rows (energy and wear rows carry their kg processed); above 3 is marked low quality.

> **Example.** market for clay brick · 0.8 kg · D2  
> market for lime mortar · 0.2 kg · D2

**Go to:** Next constituent → `D5`; After the last constituent and step → `CHECK`

### P1 · ENERGY: Machine power (kW) ÷ throughput (kg/h) = kWh per kg; one row per carrier

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `fixed_settings` (the electricity and heat datasets) and sheet `input_definitions` (the note of each step, where "no energy" is marked). Power and throughput come from the machine's datasheet, not from the workbook.

**P1 · Energy.** Only for a product built from scratch (no exact or approximate match passed). Take the next manufacturing step of the input, in order.

- The note of the step in `input_definitions` starts with "no energy": write no rows for the step (and no machine row in P2), and log it. The tag is set by hand in the sheet; the agent never sets it.
- A constituent dataset chosen on the blue path already contains the step (its name or documentation says so, e.g. "dried", "planed"): write no row for the step, and log it.

#### The two values

For the machine that does the step, find:

1. **Power draw**, in kW. Electrical power gives the electricity row. Thermal power (the heat the machine takes in, not its electrical rating) gives the heat row. A machine that uses both gets one value for each.
2. **Throughput**, in kg of material processed per hour, at the same operating point as the power.

#### Which machine

The usual industrial machine for the step; the step name says which (grinding: a grinder or hammer mill; hot pressing: a hot press). Log the choice. Find three machines of that type from three manufacturers (industrial machines, not laboratory or craft scale), with power, throughput and machine mass from their datasheets (a machine whose datasheet lacks one of the three is not used). Use the one whose energy per kg is the median of the three, and take every value for the step from that one machine, here and in P2. If the datasheets lack a value, the next sources are the EU BREF for the sector, then a peer-reviewed study of the operation. Log all three candidates.

#### Calculation

`energy per kg processed (kWh/kg) = power (kW) ÷ throughput (kg/h)`

`row amount = kg processed per kg of product (input) × energy per kg processed`

Unit check: kW ÷ (kg/h) = kWh/kg. The electricity row is in kWh. The heat dataset is in MJ, so the heat amount is multiplied by 3.6 (1 kWh = 3.6 MJ).

| The source gives | Convert |
| --- | --- |
| power in MJ/h | kW = MJ/h ÷ 3.6 |
| power in horsepower | kW = hp × 0.7457 (metric PS: × 0.7355) |
| throughput in kg/min or t/h | kg/h = kg/min × 60, or t/h × 1,000 |
| throughput in m³/h | kg/h = m³/h × density of the material as processed (kg/m³) |
| batch machine (autoclave, press, kiln) | kg/h = kg per batch ÷ cycle time in hours, loading and unloading included |
| energy per tonne | kWh/kg = kWh/t ÷ 1,000 |

#### Datasets (fixed, no search)

Take the electricity dataset from the row `Electricity carrier` and the heat dataset from the row `Heat carrier` of sheet `fixed_settings`, with the name and location written there. The flowchart does not repeat them, so the sheet is the only place to change. Electricity rows are in kWh, heat rows in MJ.

Electricity rows follow the premise scenario. As far as I know, heat rows stay on natural gas unless the model swaps the carrier; note that as a limitation.

#### Rows

One row per carrier in the A1–A3 block: `processing: <step> (electricity)` in kWh and `processing: <step> (heat)` in MJ. The datasets are fixed (the sheet), so they skip D1 to D4. TeR 3 (calculated from a machine of the step's own type, with the exact carrier dataset); GeR and TiR come from the carrier dataset, as in ROW.

**No machine found.** If no source gives both values for the machine type, take the closest machine type that does the same kind of work with the same energy carrier (cutting, grinding, mixing, heating, pressing). Write the rows as above, mark them "proxy", TeR 4, with one sentence on why. Do not search ecoinvent for a processing dataset.

**Log.** Log in `dataset_choices.csv`: step, machine type, the three candidates and the one used, power and throughput with units as found, source and link, conversions, kWh per kg.

#### How far to trust the numbers

Rated power and throughput are catalogue values. A machine running below its rating uses less power than rated, and idle and start-up time is not counted, so the result can be off either way. Estimating energy bottom-up from machine power and run time can be far off: one machining study found a standard unit-process model overestimating by 286–499 % until it was adjusted to the machine ([Krogshave et al. 2021: machine-specific energy with the UPLCI model](https://next.sciencegate.app/document/10.1115/1.0002180v)). The ÖKOBAUDAT check shows whether the total is plausible. If a step ever needs a measured value, [Kellens et al.: CO2PE! UPLCI methodology, part 2](https://lirias.kuleuven.be/retrieve/167362), the CO2PE! method is the route.

> **Example.** Cork board, with invented numbers to show the arithmetic (input: grinding 1.06 kg processed per kg of board, autoclave 1.00):  
> grinding, hammer mill: 30 kW ÷ 1,000 kg/h = 0.030 kWh/kg; 1.06 × 0.030 = 0.0318 kWh of electricity  
> autoclave, 200 kW thermal ÷ 500 kg/h = 0.40 kWh/kg; 1.00 × 0.40 × 3.6 = 1.44 MJ of heat  
> Sense check only (pilot, 13 Nov): the ecoinvent cork slab dataset uses 4.92 MJ of heat and 1 kWh of electricity per kg. Compare the sum of the rows with it; the agent changes nothing because of it.

**Note.** Changed 17 Nov: the archetype library (AR0 to AR13) is gone, because the machines vary too much for one value per step. The agent now looks up the machine's power, throughput, life and mass. Two runs can pick different machines; the three-machine median rule is there to limit that.

**Go to:** Next → `P2 · WEAR`

### P2 · WEAR: Machine mass × h per kg ÷ machine life in h = kg of machine per kg

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `fixed_settings` (the machine dataset).

**P2 · Wear.** One machine row for each step that got energy rows in P1, for the same machine. A step with no energy rows has none.

#### The three values

1. **Machine life**, in hours of operation (L). If the source gives years, multiply by the operating hours per year in the source; if it gives none, 5,000 h per year (assumption: about two shifts).
2. **Time to process 1 kg**, in h per kg (t). This is 1 ÷ the throughput from P1 (kg/h), so the energy row and the wear row cannot disagree. If a source gives minutes per kg, divide by 60.
3. **Machine mass**, in kg (M): the net weight of the machine itself, from the datasheet of the same machine as in P1. Packaging, crates, foundations and ancillary equipment are not counted. The ecoinvent machine dataset is per kg of machine, so M is what scales it to this machine. If the datasheet gives only a shipping weight, use it and log that. Never take M from a different machine than the one used for power and throughput.

#### Calculation

`machine per kg processed (kg/kg) = M (kg) × t (h/kg) ÷ L (h) = M ÷ (throughput × L)`

`row amount = kg processed per kg of product (input) × machine per kg processed`

Unit check: kg × (h/kg) ÷ h = kg of machine per kg processed.

#### Dataset (fixed, no search)

Take the machine dataset from the row `Machine dataset` of sheet `fixed_settings`, with the name, location and unit written there ([ecoinvent machine dataset, as named in fixed\_settings (via Climatiq)](https://www.climatiq.io/data/emission-factor/dda80c06-3224-4e5f-a77d-cf0bd1ce67b0)). The flowchart does not repeat the name. The dataset is per kg of machine, so the row amount is in kg of machine: the share of the machine used up by this kg of product.

TeR 3 (a machine of the step's own type); TeR 4 if P1 used a proxy machine. GeR and TiR come from the dataset.

**Log.** Log in `dataset_choices.csv`: step, machine, M, L and t with units as found, source and link, conversions, kg of machine per kg processed.

#### Why include it

As far as I know, ecoinvent datasets include the infrastructure of their plants. A material built from constituents with no machine rows would then look lighter than one taken from a dataset, for no real reason. EPDs often leave capital goods out for simple factory products ([One Click LCA: modelling machinery and equipment](https://help.oneclicklca.com/en/articles/275815-modeling-machinery-and-equipment-in-one-click-lca)), so the choice can be argued the other way: the check below shows whether it matters.

#### Check

After the sheet is built, log the share of the wear rows in GWP-fossil A1–A3. My estimate, not yet run: well under 1 %. Above 2 %, review the machine values before accepting the sheet. For metal and mineral resource use the share may be larger; look at it once on the five test materials.

> **Example.** Cork board, with invented numbers (same machines as in P1):  
> grinding: M 2,000 kg, L 40,000 h, t = 1 ÷ 1,000 = 0.001 h/kg → 2,000 × 0.001 ÷ 40,000 = 5.0 × 10⁻⁵ kg per kg processed; × 1.06 = 5.3 × 10⁻⁵ kg  
> autoclave: M 8,000 kg, L 100,000 h, t = 1 ÷ 500 = 0.002 h/kg → 8,000 × 0.002 ÷ 100,000 = 1.6 × 10⁻⁴ kg; × 1.00 = 1.6 × 10⁻⁴ kg  
> Total about 2.1 × 10⁻⁴ kg of machine per kg of board.

**Go to:** Next manufacturing step → `P1 · ENERGY`; After the last constituent and step → `CHECK`

### CHECK: Do the material rows sum to the masses in the input?

*Decision: apply the test, answer yes or no, log it.*

Only for LCIs built from scratch. The material rows must sum to the constituent masses in the input: 1 kg, or more where the input states losses (e.g. 1.06 kg raw cork per kg of board). Energy and machine rows are not mass and are left out.

**Yes** → check 3. **No** → stop.

**Go to:** Yes → `CHECK 3`; No → `STOP`

### STOP: Report it to you: the input needs correcting

The rows do not match the input: most likely a unit or moisture slip. The agent does not change the input. It stops this material and reports the gap to you.

### CHECK 3: Is GWP-fossil A1–A3 within ±50 % of the ÖKOBAUDAT median?

*Decision: apply the test, answer yes or no, log it.*

**Check 3, for an LCI built from scratch.**

**Yes** → continue to the A1–A3 block. **No** → review every LCI tried and keep the closest.

#### The test

Take every EN 15804+A2 dataset in the product's category from the latest ÖKOBAUDAT release, convert to per kg, and compare GWP-fossil A1–A3 (fossil only, because biogenic carbon is treated differently). Pass when our value is between 0.5× and 1.5× the median of those EPDs. With one EPD, its value is the median. No EPD: log "no check possible" and continue.

Why ±50 %: EPDs within one category typically spread with a coefficient of variation of 33–80 % (Hoxha et al. 2024), and generic data such as ecoinvent tend to sit above EPDs, so a smaller gap is not evidence of an error.

The check never changes a number by itself.

**Log.** Log in `epd_check.csv`: our value, the median, the number of EPDs, pass or fail.

> **Example.** Pilot (13 Nov): in cork, the ecoinvent dataset contained a resin binder that the EPDs do not. Under this rule it is not an exact match; it can be an approximate match (D1b, check 2), and if that fails it is built from scratch (check 3).

**Go to:** Yes → `A1–A3 BLOCK`; No → `REVIEW · FLAG`

### REVIEW · FLAG: Compare the LCIs of every route tried; keep the one closest to the median and flag it

Every route tried has failed its check. Compare the LCIs kept from each route that was tried, up to three:

1. the exact match (D1, check 1), if there was one;
2. the approximate match (D1b, check 2), if there was one;
3. the LCI built from scratch (check 3).

#### The rule

Keep the LCI whose GWP-fossil A1–A3 is closest to the ÖKOBAUDAT median, measured as the distance |our value ÷ median − 1|, the same measure as the ±50 % test. In a tie, keep the one with the lower value (baselines get the benefit of the doubt). Use it for the A1–A3 block and flag the material in `epd_check.csv`. Flagged materials stay in the model and are reported as such in the paper.

> **Example.** Illustrative: exact match 1.9× the median (distance 0.9), approximate match 1.7× (0.7), built 0.4× (0.6) → keep the built LCI, flagged.

#### Record, for each LCI compared

- Our value, the median, the number of EPDs, the distance.
- **Units and mass basis.** Per m³ or per m² values converted with the right density or area mass; moisture counted once.
- **Dataset state.** Each dataset matches the state of the product or constituent.
- **Indicator.** Only GWP-fossil on both sides; no biogenic or land-use carbon mixed in.
- **Composition.** For a matched dataset: the constituents that differ from the input. For a built LCI: which steps carry most of the energy, the machine for each, and any proxy.

Then which LCI was kept and one sentence on the likely reason for the gap (e.g. EPDs from one producer only, or a different production route). The agent changes nothing: a proven error is reported to you, and fixed in the input or the protocol.

**Go to:** Next → `A1–A3 BLOCK`

### A1–A3 BLOCK: Output: 1 kg at the factory gate

The first block of the sheet. Output (production row): 1 kg of the material at the factory gate. Inputs: the rows written above.

A1, A2 and A3 stay one module because ecoinvent datasets bundle raw materials, transport to the manufacturer and manufacturing.

> **Example.** clay brick masonry, A1–A3 → 1 kg  
> market for clay brick · 0.8 kg  
> market for lime mortar · 0.2 kg

**Go to:** Next → `A4 · T1`


## A4: Transport to site

### A4 · T1: Is it delivered in bulk: loose or ready-mixed?

*Decision: apply the test, answer yes or no, log it.*

**Question A4 · T1.** Is the material delivered to site in bulk: loose or ready-mixed by truck, rather than as discrete products (units, boards, sections, rolls)?

- Yes: ready-mixed concrete, aggregate, sand, earth, loose fill.
- No: anything delivered as pieces, boards, rolls or bales.

Yes → bulk, 50 km ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), bulk material). No → T2.

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `TRANSPORT · BULK`; No → `A4 · T2`

### TRANSPORT · BULK: Lorry 50 km: 0.05 tkm per kg

Bulk material: lorry 50 km one way ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), bulk material).

Transport archetype: fixed datasets, no search (they skip D1–D4).

- Lorry: `market for transport, freight, lorry, unspecified`, RER
- Sea: `market for transport, freight, sea, container ship, heavy fuel oil`, GLO

**Units:** both datasets are in tonne-kilometres (tkm), so amount = mass in kg × 0.001 × distance in km. 1 kg over 50 km is 0.05 tkm of lorry. Do not add empty return trips: the datasets already include average load factors and empty trips.

> **Example.** lorry · 0.05 tkm

**Go to:** Next → `A4 BLOCK`

### A4 · T2: Is it made in at least 3 of DE, FR, IT, ES, NL?

*Decision: apply the test, answer yes or no, log it.*

**Question A4 · T2.** Is the product made in at least 3 of the 5 countries DE, FR, IT, ES, NL (the first five of the D3 country list)?

**How to check:** look for a manufacturer of this product in each country, in this order: the product's EPDs in ÖKOBAUDAT or the EPD programme registries, then the national manufacturers' association, then a web search for "<product> manufacturer <country>". Record one manufacturer name and link per country found.

Yes → nationally manufactured, 150 km. No → T3.

Why these countries: production spread over the large European markets means a building usually gets the product from within its own country.

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `TRANSPORT · NATIONAL`; No → `A4 · T3`

### TRANSPORT · NATIONAL: Lorry 150 km: 0.15 tkm per kg

Nationally manufactured: lorry 150 km one way ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), other materials, products and elements).

Transport archetype: fixed datasets, no search (they skip D1–D4).

- Lorry: `market for transport, freight, lorry, unspecified`, RER
- Sea: `market for transport, freight, sea, container ship, heavy fuel oil`, GLO

**Units:** both datasets are in tonne-kilometres (tkm), so amount = mass in kg × 0.001 × distance in km. 1 kg over 50 km is 0.05 tkm of lorry. Do not add empty return trips: the datasets already include average load factors and empty trips.

> **Example.** Clay brick masonry: lorry · 0.15 tkm

**Go to:** Next → `A4 BLOCK`

### A4 · T3: Is it made anywhere in Europe?

*Decision: apply the test, answer yes or no, log it.*

**Question A4 · T3.** Is the product made anywhere in Europe (EU, EFTA or UK)?

**How to check:** as in T2, but any European country counts. Record one manufacturer name, country and link.

Yes → EU manufactured. No → globally manufactured.

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `TRANSPORT · EU`; No → `TRANSPORT · GLOBAL`

### TRANSPORT · EU: Lorry 1.5 tkm + sea 0.1 tkm per kg

EU manufactured: lorry 1,500 km plus container ship 100 km ([RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17, European manufactured).

Transport archetype: fixed datasets, no search (they skip D1–D4).

- Lorry: `market for transport, freight, lorry, unspecified`, RER
- Sea: `market for transport, freight, sea, container ship, heavy fuel oil`, GLO

**Units:** both datasets are in tonne-kilometres (tkm), so amount = mass in kg × 0.001 × distance in km. 1 kg over 50 km is 0.05 tkm of lorry. Do not add empty return trips: the datasets already include average load factors and empty trips.

> **Example.** lorry · 1.5 tkm; container ship · 0.1 tkm

**Go to:** Next → `A4 BLOCK`

### TRANSPORT · GLOBAL: Lorry 0.5 tkm + sea 10 tkm per kg

Globally manufactured: lorry 500 km plus container ship 10,000 km ([RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17, globally manufactured).

Transport archetype: fixed datasets, no search (they skip D1–D4).

- Lorry: `market for transport, freight, lorry, unspecified`, RER
- Sea: `market for transport, freight, sea, container ship, heavy fuel oil`, GLO

**Units:** both datasets are in tonne-kilometres (tkm), so amount = mass in kg × 0.001 × distance in km. 1 kg over 50 km is 0.05 tkm of lorry. Do not add empty return trips: the datasets already include average load factors and empty trips.

> **Example.** lorry · 0.5 tkm; container ship · 10 tkm

**Go to:** Next → `A4 BLOCK`

### A4 BLOCK: 1 kg of A1–A3 in, plus the transport rows of its category

Output: 1 kg delivered to site. Inputs: 1 kg from the A1–A3 block, plus the transport rows of the archetype reached in T1–T3. The datasets are in tonne-kilometres: tkm = kg × 0.001 × km.

| Archetype | Lorry | Sea | Source |
| --- | --- | --- | --- |
| Bulk | 50 km | – | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| National | 150 km | – | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| EU | 1,500 km | 100 km | [RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17 |
| Global | 500 km | 10,000 km | [RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17 |

- Lorry: `market for transport, freight, lorry, unspecified`, RER
- Sea: `market for transport, freight, sea, container ship, heavy fuel oil`, GLO

The same lorry dataset is used for the A2 row (D2) and for transport to waste (C2).

> **Example.** Clay brick masonry: T1 no, T2 yes → national.  
> clay brick masonry, A1–A3 · 1 kg  
> lorry · 0.15 tkm

**Go to:** Next → `A5 · I1`


## A5: Installation

### A5 · I1: Is it poured or pumped, or over 50 kg per piece?

*Decision: apply the test, answer yes or no, log it.*

**Question A5 · I1.** Is the material poured or pumped on site, or does a typical delivered piece weigh more than 50 kg?

- "Piece" = one unit as handled on site: a brick, a board, a beam, a panel, a bale, a roll.
- Take the typical piece weight from the product's datasheet or EPD (dimensions × density if only those are given) and record it.
- 50 kg = two people at 25 kg each, the reference mass in manual handling guidance (ISO 11228-1). Threshold is our assumption.

Yes → look up and add a machine energy row. No → no row (installed by hand). Hand tools, fixings and site huts are left out for every material.

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `A5`; No → `A5 · L1`

### A5: Add a diesel row: diesel, burned in building machine, 0.015 MJ per kg

One row: `diesel, burned in building machine`, 0.015 MJ per kg installed. No lookup: the same value for every material installed by machine.

Source: the crane energy of a precast timber-concrete slab EPD, 88 kW crane, 10 minutes per 3.4 t element = 4.3 kWh/t = 0.015 MJ/kg ([EPD Hub 0135, precast TCC slab (2022)](https://manage.epdhub.com/declarations/file/download/epdSigned/158/)). It rests on one EPD. EPDs vary widely: an insulated-panel EPD assumes about 0.18 kWh/kg ([EPD Hub 0289, Kingspan panel (2025)](https://manage.epdhub.com/declarations/file/download/epdSigned/373/)); a sensitivity case can use that.

**Go to:** Next → `A5 · L1`

### A5 · L1: Is it made in situ on the building site?

*Decision: apply the test, answer yes or no, log it.*

**Question A5 · L1.** Is the material made in situ on the building site (cast, mixed, sprayed, or laid from small units with mortar or adhesive), rather than delivered as a finished product that is only fixed in place?

- Yes, in situ: cast concrete, masonry laid with mortar, cast or sprayed hempcrete, tiles set in adhesive.
- No, prefab: boards, panels, beams, profiles, glazing, mats, fabrics, blocks or bales placed dry.

Yes → 5 % waste. No → 3 % waste ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), §2.6.3.6, building-site losses). NMD's third class, 15 % for auxiliary and finishing materials (sealants, adhesives, paints), does not apply to the 28 materials.

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `LOSS (5 % (NMD, in situ))`; No → `LOSS (3 % (NMD, prefab))`

### LOSS: 5 % (NMD, in situ)

In-situ products: waste rate 5 % ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf)).

**Go to:** Next → `A5 BLOCK`

### LOSS: 3 % (NMD, prefab)

Prefab products: waste rate 3 % ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf)).

**Go to:** Next → `A5 BLOCK`

### A5 BLOCK: (1 + loss) kg of A4 in, plus any energy row; the lost kg goes to waste

Output: 1 kg installed. Inputs: (1 + loss) kg from the A4 block, plus the machine energy row if I1 was yes. The waste rate w comes from L1: 5 % in situ, 3 % prefab (NMD). To install 1 kg, 1 + loss kg must be delivered, so the loss scales the whole chain above it. The lost kg goes to waste: a lorry row (C2 distance) and its end-of-life rows (C3–C4).

NMD gives the waste rate w as a share of the material delivered. In the sheet: loss = kg lost per kg installed = w ÷ (1 − w).

> **Example.** Clay brick masonry: I1 no (bricks under 50 kg); L1 yes (laid with mortar on site) → 5 % → 0.05 ÷ 0.95 = 0.053.  
> clay brick masonry, A4 · 1.053 kg  
> lorry to recycling · 0.053 × 50 ÷ 1000 tkm  
> end of life of 0.053 kg as in C3–C4

**Go to:** Next → `B1`


## B1–B7: Use stage. Depends on the function, so the model handles it after the Ashby step. No rows here

### B1: No rows. Not modelled; concrete carbonation noted as a limitation

No rows. All of module B depends on the function the material is used for (indoor or outdoor, exposure, service life), so it is handled by the model after the Ashby step, not in this per-kg sheet.

B1 use emissions are not modelled. Concrete carbonation uptake is noted as a limitation.

**Go to:** Next → `B2`

### B2: No rows. The model adds recoating for outdoor functions

No rows in the sheet. Maintenance depends on the function (indoor or outdoor) and its service life, not on the material, so the model adds it at the product level, like B4.

For outdoor functions with a coated material, the model adds paint per kg of material = coats × coating mass per coat ÷ product mass per m² × recoatings, with recoatings = ceil(service life ÷ interval) − 1.

Defaults: 2 coats × 0.15 kg/m² every 10 years ([Moelven cladding EPD NEPD-310-180 (2015)](https://www.moelven.com/globalassets/inriver/documents/epd-moelvenwood-kledning-2-str-nepd-310-180-en-exterior-cladding-with-waterborne-paint-gk.pdf), B2 scenario; [Flügger Wood Tex EPD NEPD-3504-2097 (2022)](https://epd-global.com/getfile.php/1323835-1652271462/EPDer/Utenlandsk%20registrerte%20EPD/NEPD-3504-2097_Flugger-07-Wood-Tex-Matt.pdf) agrees on 0.15 kg/m²). Product mass per m² comes from the Ashby step.

**Go to:** Next → `B3`

### B3: No rows. The model adds repair per function

No rows in the sheet. Repair depends on the function and its service life, so the model adds it at the product level, like B4.

Where a source gives a repair share r (kg renewed over the service life per kg installed), the model adds r kg of the material's A1–A5 chain and r kg of its end of life (C1–C4). r of 1 or more is a replacement, counted in B4. No default.

**Go to:** Next → `B4`

### B4: No rows. The model repeats the chain for each replacement

No rows in the sheet. The model counts replacements over the study period from the function's reference service life:

`replacements = ceil(study period ÷ service life) − 1`

Each replacement repeats the chain for the same mass. Applied in the ranking step.

**Go to:** Next → `B5 · B6 · B7`

### B5 · B6 · B7: No rows. Not modelled

No rows. B5 refurbishment, B6 operational energy and B7 operational water depend on the function and the building, and are not modelled.

**Go to:** Next → `C1 · X1`


## C1: Deconstruction

### C1 · X1: Is it cast, bonded, or over 50 kg per piece?

*Decision: apply the test, answer yes or no, log it.*

**Question C1 · X1.** Is the material cast in place, bonded (mortar, adhesive, welding), or does a typical piece weigh more than 50 kg?

Yes → demolished by machine: one diesel row. No → taken apart by hand: no row. Same piece weight and 50 kg threshold as A5 · I1 (assumption).

**Log.** Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

**Go to:** Yes → `C1`; No → `C1 BLOCK`

### C1: Add a diesel row: 0.036 MJ per kg

One row: `diesel, burned in building machine`, 0.036 MJ per kg.

Derivation: 10 kWh of diesel per m² of demolished building (Bozdağ & Seçer 2007) ÷ about 1,000 kg of building per m² = 0.01 kWh/kg = 0.036 MJ/kg. This is the default in EPDs made with One Click LCA ([Bozdağ & Seçer 2007 (EPD Hub 1675)](https://skarbyggsystem.se/wp-content/uploads/sites/3/2026/08/epd_hub-1675_column-beam.pdf)).

**Note.** Caveat: the figure comes from reinforced-concrete buildings and is spread over all machine-demolished materials. Light materials such as timber may need less energy per kg.

**Go to:** Next → `C1 BLOCK`

### C1 BLOCK: 1 kg of A5 in, plus any diesel row

Output: 1 kg demolished. Inputs: 1 kg from the A5 block, plus the diesel row if any.

**Go to:** Next → `C2 · ROUTE`


## C2: End-of-life route, then transport to waste

### C2 · ROUTE: Assign the material to its NMD end-of-life category with the key; take its shares

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `nmd_eol`: the NMD category of each material and its shares.

Find the material in the column `materials` of the sheet. That row gives its NMD end-of-life category and the shares for landfill, incineration, recycling and reuse (NMD end-of-life defaults 2024, [NMD end-of-life defaults 2024](https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/)); take them from the sheet unchanged. There is no decision. The flowchart does not repeat the key. A material not in the sheet is added there by you before its run.

**Log.** Log in `decisions.csv`: material, C2, category number.

**Go to:** Next → `C2 BLOCK`

### C2 BLOCK: 1 kg of C1 in, plus lorry tkm per route share: 50 km recycling or landfill, 100 km incineration

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `nmd_eol`: transport to treatment (lorry, km one way, per route), in the table below the categories.

Output: 1 kg at the waste site. Inputs: 1 kg from the C1 block, and lorry tkm to each treatment in the route from C2 · ROUTE, weighted by its shares.

| Treatment | Distance (one way) | Source |
| --- | --- | --- |
| Recycling (sorting, crushing) | 50 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| Reuse | 50 km | assumption: as recycling |
| Landfill | 50 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| Incineration | 100 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |

> **Example.** Clay brick masonry: category 32 (1 / 0 / 99 / 0) → all 50 km → 0.05 tkm

#### Waste items for C3–C4

The end-of-life shares come from the NMD end-of-life defaults 2024 ([NMD end-of-life defaults 2024](https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/)), as taken in C2 · ROUTE. The treatment dataset depends on both the waste material and the route, so each pair is one waste item:

- **Waste material:** each constituent of the input, with its mass per kg. If the LCI kept for A1–A3 is a single ecoinvent dataset (an exact or approximate match), the product itself is the one waste material.
- **Route:** each non-zero share: landfill, incineration, recycling, reuse.

Mass of the item = constituent mass × route share.

> **Example.** Hempcrete, route 1 / 0 / 99 / 0: hemp shiv × landfill, hemp shiv × recycling, lime × landfill, lime × recycling.

**Go to:** For each waste item (constituent × end-of-life route) → `W1`


## C3–C4: Waste processing and disposal

### W1: Is there a treatment dataset for this waste material and this route?

*Decision: apply the test, answer yes or no, log it.*

**Question W1.** For each end-of-life route from C2 and each constituent (one waste item):

Search ecoinvent 3.12 cut-off for a waste treatment activity named for this waste material and this route, in this order:

1. `market for waste <material>` only if it splits into routes the same way as NMD; else
2. `treatment of waste <material>, <route>`, where the route words are: *sanitary landfill* or *inert material landfill* (landfill); *municipal incineration* (incineration); *recycling*, *sorting* or *crushing* (recycling).

Location by the D3 order. The waste material must match the constituent (e.g. waste gypsum for gypsum, waste brick for clay brick).

#### No search needed

- **Reuse:** no row. Under the cut-off rule the material leaves without burden; its benefit goes to D.
- **Recycling of metals and plastics:** no row, for the same reason.

**Yes** → use it. **No** → fallback by material class.

**Log.** Log in `dataset_choices.csv`: waste item, route, dataset, rule W1 or W2.

**Go to:** No → `W2 · FALLBACK`; Yes: write the row; next waste item → `W1`; After the last waste item → `C3–C4 BLOCK`

### W2 · FALLBACK: Use the dataset for its material class and route (table); log it as proxy

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `waste_fallback`: the treatment dataset per material class and route.

No dataset for this waste material and route (W1 no): take the fallback from the sheet. Find the constituent in the column `constituents`; that row gives its class and the dataset for each route. Log it as a proxy, TeR 4.

- A dataset name: use it.
- `as wood` or `as mineral`: use the dataset in that row of the sheet.
- `no row (cut-off)`: write no row.
- `—`: the class has no dataset for this route; write no row, and log it.

The names are in the sheet only; the flowchart does not repeat them.

**Go to:** Next waste item → `W1`; After the last waste item → `C3–C4 BLOCK`

### C3–C4 BLOCK: 1 kg of C2 in, plus one treatment row per waste item. This block is the cradle-to-grave total

The last block. Output: 1 kg, cradle to grave. Inputs: 1 kg from the C2 block, and one treatment row per waste item (W1 or W2). Waste sent to treatment has a negative amount (ecoinvent convention).

End-of-life shares: the NMD end-of-life defaults 2024 ([NMD end-of-life defaults 2024](https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/)), as in C2.

> **Example.** clay brick masonry, C2 · 1 kg  
> treatment of waste brick, recycling · −0.792 kg  
> treatment of waste mortar (or inert waste), recycling · −0.198 kg  
> treatment of inert waste, inert material landfill · −0.010 kg

Score this block for the total. A contribution analysis by activity gives each module.

**Go to:** Next → `D · CFF · F1`


## D · CFF: Module D: circular footprint formula. Archetype assigned here, calculated by the model

### D · CFF · F1: Assign the material to its CFF archetype with the key

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `cff_archetypes`: the materials of each archetype and its parameters (A, R1, Qsin/Qp, Qsout/Qp, heating value, efficiencies, avoided datasets, B).

**Division of work.** You pre-make the CFF archetypes and the key; the agent assigns the material to its archetype with the key and writes the file; the model's script calculates module D with the circular footprint formula (CFF) of the EU Environmental Footprint method.

#### Key

Find the material in the column `materials` of the sheet; that row is its archetype. The flowchart does not repeat the key.

Each archetype holds every parameter the formula needs: A (from the JRC default parameter list, Annex C of the EF method), R1, Qsin/Qp, Qsout/Qp, lower heating value, heat and electricity efficiencies of energy recovery, the avoided primary material and energy (ecoinvent datasets), and B = 0. Suggested grouping, your call: hempcrete sits with the minerals because its NMD route is mineral recycling; the coated fabrics and composites may need splitting if their A values differ in the JRC list. Parameters: to be carried over from the end-of-life templates of the earlier model versions.

A material not in the sheet is added there by you before its run.

**Go to:** Next → `F2 · RECORD`

### F2 · RECORD: Write cff_inputs.csv: material, CFF archetype, route shares from C2, flag

**F2.** Write one row to `cff_inputs.csv`: material, CFF archetype, the end-of-life shares from C2 (recycling, reuse, incineration, landfill) and the flag. No numbers are looked up or calculated here.

**Go to:** Next → `D · CFF`

### D · CFF: The model's script calculates module D from cff_inputs.csv

The model's script reads `cff_inputs.csv` and the archetype table and calculates module D with the CFF, per kg of material: credits for recycled material (recycling share, A, quality ratio, avoided primary material) and for energy recovered at incineration (incineration share, heating value, efficiencies, avoided energy).

D is linear in mass, so it becomes a third column of the unit impact table (D per kg), next to A and C.

**Note.** Note for the paper: the CFF is the EU Environmental Footprint rule; EN 15804+A2, behind the ÖKOBAUDAT EPDs, uses a different module D rule. Say which one is used and why.

**Go to:** Next → `D · BIO-C · B1`


## D · BIO-C: Module D: biogenic carbon. Archetype assigned here, calculated by the model

### D · BIO-C · B1: Assign each constituent to its carbon archetype with the key

> **Excel:** `protocol_predetermined_values.xlsx`, sheet `carbon_archetypes`: the constituents of each archetype, its carbon fraction of dry mass and its default moisture.

Assign each constituent of the input to its carbon archetype. Look the constituent up by name in the column `constituents` of the sheet and take that row's archetype. Every constituent is listed once, biogenic or not: mineral, metal and fossil constituents are in the non-biogenic row (carbon fraction 0). Per constituent, not per material, because one material can mix both (hempcrete: hemp shiv and lime).

A constituent whose name is not in the sheet: take the closest row, log it with one sentence on why, and flag it.

The values and their basis are in the sheet only; the flowchart does not repeat them.

**Go to:** Next → `B2 · RECORD`

### B2 · RECORD: Write bioc_inputs.csv: per constituent, kg and carbon archetype

**B2.** Write one row per constituent to `bioc_inputs.csv`: constituent, kg per kg of product (losses excluded: only what ends up in the product), carbon archetype, and a moisture content only if the input gives one (otherwise the archetype default is used). No numbers are calculated here.

**Go to:** Next → `D · BIO-C`

### D · BIO-C: The model's script calculates CO₂ stored and its release at end of life

The model's script calculates the CO₂ stored per kg:

`Σ mᵢ ÷ (1 + uᵢ) × cfᵢ × 44/12`

It reports it separately from GWP-fossil, as uptake in A1–A3, and applies its release where the end-of-life route burns or landfills the material.

> **Example.** Glulam, illustrative: 0.98 kg lamellas at 12 % moisture → 0.98 ÷ 1.12 × 0.50 × 3.67 = 1.60 kg CO₂ per kg.

**Note.** Not included: CO₂ taken up by lime binders as they carbonate (relevant for hempcrete). Open.

**Go to:** Next → `END`


## END

### END: Sheet complete: save the records; 5 random materials are rebuilt by a separate AI session

Save the sheet and the records in `data/baseline_recipes/` under git:

- `decisions.csv`: one row per diamond answered (material, question id, answer, evidence, link, date)
- `dataset_choices.csv`: one row per dataset choice (D1–D4) and per machine row (P1, P2), with the values found, units, source and link, scores and date
- `epd_check.csv`: one row per check (CHECK 1, 2, 3), with which LCI was kept and, if all failed, the review
- `cff_inputs.csv` and `bioc_inputs.csv`: the inputs of the model's scripts for module D and biogenic carbon

`material_definitions.csv` is your input and is kept unchanged.

#### Reproducibility test

A separate AI session gets only this protocol and the `material_definitions.csv` of 5 materials picked at random, and both runs are compared question by question (`decisions.csv`: categories, thresholds, routes, machine per step) and dataset by dataset (`dataset_choices.csv`). The input is not part of the test: it is yours. Every difference is fixed by sharpening the test of the diamond that allowed it, or the library.
