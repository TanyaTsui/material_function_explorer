# Baseline LCI protocol

Version: 13 Nov 2026, exported from the "Baseline LCI Protocol" flowchart. Follow it step by step for one material at a time.

## How to use this protocol

- Work through the steps in order, from START to END. Each step has an id (e.g. `A4 · T2`).
- **Decisions** are yes/no questions. Apply the written test, answer yes or no, and follow the matching arrow.
- **Log every decision** as one row in `decisions.csv`: material_id, question_id, answer (yes/no), evidence (one sentence), source_link, date. Where a step asks you to record a value, a source or a derivation, log it in the same file with answer = the value.
- **Log every ecoinvent dataset you choose** (rules D1 to D5) in `dataset_choices.csv`.
- Datasets for the rows written in A4 to C3–C4 (lorry, ship, diesel, waste treatment) are chosen with the same rules D1 to D4.
- Never guess silently. If a test cannot be answered, write "unclear" with a sentence on why, take the more conservative branch, and continue.
- The LCI describes 1 kg of material, whatever it is later used for. You are not told the function, and module B (use stage) has no rows in the sheet: the model adds it later, per function.
- The LCI is written as one Excel sheet per material in the Brightway Excel format, one block per module, chained: each block's first input is the previous block's output (see `templates/lci_template.xlsx`). The blocks are A1–A3, A4, A5, C1, C2 and C3–C4.

## START: Baseline material, one of the 30 on the list

The flow runs once per baseline material: the 30 on the proposed list, and any material added later.

#### What it produces

- One Excel sheet in the Brightway format, with one block per module, chained: each block's first input is the previous block's output.
- `decisions.csv`: one row per diamond answered, with the evidence.
- `dataset_choices.csv`, `material_definitions.csv` and `epd_check.csv`.

#### Fixed settings

|  |  |
| --- | --- |
| Database | ecoinvent 3.12 cut-off |
| Scenario | premise IMAGE SSP2-L 2050, applied by the model; same LCI for both |
| Method | EF 3.1, 16 categories |
| Mass basis | as delivered, incl. moisture |
| Unit conversion | with the dataset's own density or area mass |
| Rounding | 3 significant figures |

#### Golden rule

Every decision is a diamond in this chart, with a written test. Its answer and the evidence behind it are recorded, so a second run can be compared answer by answer. No material is assigned to a category in advance.

Next → **INPUT** (Start with two facts about the material: its name and its delivered state)

## Setup: Define the material

### INPUT: Start with two facts about the material: its name and its delivered state

*Step*

Nothing is decided here. The protocol starts from two pieces of information about the material, given as input:

| Input | Used for | Glulam |
| --- | --- | --- |
| Name | what the material is | glulam |
| Delivered state | the form it is installed in; decides the dataset (D1, D4), the mass basis, and any finishing steps added in D5 | kiln dried, planed, untreated |

Nothing else is passed to the agent, so a second run cannot copy an answer it should find itself.

#### Left out on purpose

- **Strength class and element type.** The protocol gives an impact per kg of material, whatever it is used for. Performance and function come in at the next step, where the Ashby archetypes turn kg of material into a product.
- **Product standard.** Not needed: the agent finds the manufacturing steps in open sources (S2). Standards are paywalled, so readers could not check them anyway.

#### Why the delivered state matters

ecoinvent has sawn softwood "raw" (green, rough, about half water) and "dried (u=10%), planed". With "kiln dried, planed" as input, the dataset rules pick the dried, planed dataset, and 1 kg means 1 kg of dry timber.

Next → **S1** (Find the mass share of every constituent, with a cited source: EPD › maker › handbook or standard › study)

### S1: Find the mass share of every constituent, with a cited source: EPD › maker › handbook or standard › study

*Step*

**S1.** Find the mass of **every** constituent per kg of material, with a cited source, however small its share. There is no cut-off: a small constituent such as a glue, binder or coating can carry a large part of the impact.

#### Search order

1. The composition table of EPDs for this product (ÖKOBAUDAT, then the EPD registries); median if several.
2. The manufacturer's datasheet.
3. A handbook or standard giving quantities per unit (e.g. bricks and mortar per m² of wall).
4. A peer-reviewed study.

Stop at the first step that gives shares. Convert to kg per kg, check that the shares sum to 1, and record each share, the source and link, and the conversion. Moisture counts with the constituent it is in.

*Example:* Glulam: from an EPD's composition table, e.g. about 0.98 kg spruce lamellas (incl. moisture) and 0.02 kg adhesive per kg (illustrative numbers). The adhesive is kept even though it is 2 %.

Log in `decisions.csv`: material, question id, answer, evidence (with link), date.

Next → **S2** (List each manufacturing step, with a cited source: EPD › BREF › study › maker)

### S2: List each manufacturing step, with a cited source: EPD › BREF › study › maker

*Step*

**S2.** List each step that turns the constituents from S1 into the material in its delivered state, e.g. sawing, kiln drying, planing, finger-jointing, gluing, pressing, mixing, firing, weaving, coating. Every material has at least one step.

#### Search order

1. The production process description of an EPD for this product (ÖKOBAUDAT, then the EPD registries). Use the same EPD as in S1 if there was one, so the composition and the steps describe the same product.
2. The EU Best Available Techniques reference document (BREF) for the sector, where one exists (e.g. wood-based panels, ceramics, cement and lime, glass, iron and steel, non-ferrous metals, textiles).
3. A peer-reviewed LCA or study of European production of this product.
4. The manufacturer's website or datasheet.

Stop at the first source that describes the process from constituents to delivered state. Product standards (EN) are not used: they are behind a paywall, so a reader could not check them.

*Example:* Glulam: from an EPD's process description: kiln drying, planing and finger-jointing of the lamellas, applying adhesive, pressing, curing, planing the beam.

Log in `decisions.csv`: material, S2, the list of steps, source (with link), search step, date.

Next → **S3** (Definition complete: write it to material_definitions.csv)

### S3: Definition complete: write it to material_definitions.csv

*Step*

**S3.** Write the definition to `material_definitions.csv` (one row per material): the two inputs, the constituents with mass shares and sources, and the manufacturing steps.

A1–A3 uses this definition. If ecoinvent has the finished product in its delivered state (D1 yes), its dataset already contains the steps, so they are not added again. If it does not (D5), each constituent and each step becomes its own row, and any finishing step needed to reach the delivered state is added there.

*Example:* Glulam: ecoinvent has "glued laminated timber, for indoor use" → D1 yes → one market row in A1–A3; the constituents and steps stay on record for checking and for the end-of-life route.

Next → **D1** (Is this product in ecoinvent, in its delivered state and with the constituents from S1?)

## A1–A3: Product stage · dataset choice

### D1: Is this product in ecoinvent, in its delivered state and with the constituents from S1?

*Decision*

**D1 Product match.** Search ecoinvent 3.12 cut-off for a reference product with the same name, in the same state (dried, planed, hot rolled). Record search terms and candidates.

A match also needs the same constituents as S1. Check the dataset's inputs: a dataset with an extra constituent (e.g. a resin binder) or without one that S1 lists is not a match, so the material is built instead (D5).

*Example:* Cork board: S1 (from an EPD) lists cork granules only, bound by heat and steam. The ecoinvent dataset includes a resin binder → not a match → D5.

**Yes** → D2. **No** → build it from its constituents and manufacturing steps (D5).

*Example:* Brick: "clay brick" exists. Mortar: "lime mortar" exists.

An exact match scores TeR = 1.

- **Yes** → **D2** (Is there a market dataset for this product?)
- **No** → **D5** (Build it: send each constituent (S1) and manufacturing step (S2) through D1. No dataset for a step: closest processing dataset, logged)

### D5: Build it: send each constituent (S1) and manufacturing step (S2) through D1. No dataset for a step: closest processing dataset, logged

*Step*

Each constituent (from S1) and each manufacturing step (from S2) becomes its own row. Send each one back to the top of the A1–A3 flow (connector 1) so it gets its own dataset by D1–D4.

#### Finishing steps

When D1 finds a constituent only in a less finished state than it has in the product (e.g. "sawnwood, softwood, raw" while the lamellas are kiln dried and planed), add one processing row per missing step (kiln drying, planing), each with its own dataset by D1–D4. Log the gap and the steps added in `decisions.csv`.

Processing datasets are per kg processed and usually exclude the material, so the material is a separate row.

#### When D1 finds nothing

A constituent with no dataset is broken down further into its own constituents and steps. A manufacturing step (or a raw material that cannot be broken down) with no dataset gets the closest processing dataset, in this order:

1. The same operation on another material (e.g. needle-punching of polyester fibre for hemp fibre mat).
2. A similar operation on the same material.

Log it in `dataset_choices.csv` as a proxy, with the step it stands in for and one sentence on why. TeR = 4.

Next → D1, with each constituent and step in turn

### D2: Is there a market dataset for this product?

*Decision*

**D2 Market first.** Use `market for <product>`. It includes average transport to the buyer and market losses, so it already covers A2.

**Yes** → pick its location (D3). **No** → production dataset plus a transport row.

*Example:* Brick: `market for clay brick`.

- **Yes** → **D3** (Pick the location: European market group › RER › Europe w/o CH › DE, FR, IT … CH › GLO › RoW › other)
- **No** → **D2** (Use the production dataset, and add an A2 transport row)

### D2: Use the production dataset, and add an A2 transport row

*Step*

Use the production activity. It has no transport to the buyer, so add one A2 row: lorry tkm with the material's A4 transport category distance.

Next → **D3** (Pick the location: European market group › RER › Europe w/o CH › DE, FR, IT … CH › GLO › RoW › other)

### D3: Pick the location: European market group › RER › Europe w/o CH › DE, FR, IT … CH › GLO › RoW › other

*Step*

**D3 Geography.** Take the first location that exists:

1. European market group (RER or Europe without Switzerland): the production-weighted European average
2. RER
3. Europe without Switzerland
4. A single European country, in this order: DE, FR, IT, ES, NL, AT, SE, FI, PL, CH
5. GLO
6. RoW
7. any other

Global market groups are never used: they mix in supply from outside Europe. **Decided 12 Nov:** a single European country comes before GLO.

*Example:* Brick: if no European dataset exists, a German one is taken before GLO.

Next → **D4** (Is more than one dataset still left?)

### D4: Is more than one dataset still left?

*Decision*

**D4 Variants.** Several datasets can remain for the same product and location: indoor or outdoor use, strength class, glue type.

- **Yes** → **D4** (Take the variant that matches the delivered state; else the first A–Z)
- **No** → **ROW** (Write the row: amount = mass share; record rule, TeR, GeR, TiR)

### D4: Take the variant that matches the delivered state; else the first A–Z

*Step*

Take the variant that matches the delivered state from step 1. When none matches better, take the one whose name comes first alphabetically, and record the others. A different variant of the same product scores TeR = 2.

Next → **ROW** (Write the row: amount = mass share; record rule, TeR, GeR, TiR)

### ROW: Write the row: amount = mass share; record rule, TeR, GeR, TiR

*Step*

One row in the A1–A3 block:

- **amount** = the mass share from step 1 (kg per kg). When a processing dataset states a yield below 1, the material row becomes share ÷ yield.
- **rule** = the D rule that decided the dataset.
- **TeR, GeR, TiR** read from the rule and the dataset (table below).

|  | TeR | GeR | TiR |
| --- | --- | --- | --- |
| 1 | D1 exact | RER, Europe w/o CH | 2020+ |
| 2 | D4 variant | one EU country | 2015–19 |
| 3 | D5 built | GLO | 2010–14 |
| 4 | D5 step proxy | RoW | 2005–09 |
| 5 | – | other | <2005 |

DQR = (TeR + GeR + TiR) ÷ 3, mass-weighted over the rows; above 3 is marked low quality.

*Example:* market for clay brick · 0.8 kg · D2  
market for lime mortar · 0.2 kg · D2

Next → **LOOP** (Any constituent or processing step left?)

### LOOP: Any constituent or processing step left?

*Decision*

Repeat D1 to the row for every constituent and processing step from step 1. **Yes** → connector 1, back to D1. **No** → mass balance check.

- **Yes** → back to D1 (next constituent or step)
- **No** → **CHECK** (Do the rows sum to 1 kg (or 1 ÷ yield)?)

### CHECK: Do the rows sum to 1 kg (or 1 ÷ yield)?

*Decision*

The material rows must sum to 1 kg, or to 1 ÷ yield where a processing yield applies. An LCI that fails is not used.

*Example:* 0.8 + 0.2 = 1 kg → passes.

- **Yes** → **STEP 3** (Is GWP-fossil A1–A3 within ±50 % of the ÖKOBAUDAT median?)
- **No** → **FIX** (Correct the shares or yields)

### FIX: Correct the shares or yields

*Step*

Correct the shares in step 1 or the yields, then check again.

Next → back to **CHECK** (Do the rows sum to 1 kg (or 1 ÷ yield)?)

### STEP 3: Is GWP-fossil A1–A3 within ±50 % of the ÖKOBAUDAT median?

*Decision*

**Step 3, ÖKOBAUDAT check.** Take every EN 15804+A2 dataset in the product's category from the latest ÖKOBAUDAT release, convert to per kg, and compare GWP-fossil A1–A3 (fossil only, because biogenic carbon is treated differently).

Pass when our value is within ±50 % of the median of those EPDs: between 0.5× and 1.5× the median. With one EPD, its value is the median. No EPD: "no check possible", continue.

Why ±50 %: EPDs within one category typically spread with a coefficient of variation of 33–80 % (Hoxha et al. 2024), and generic data such as ecoinvent tend to sit above EPDs, so a gap below 50 % is not evidence of an error. In the pilot (3 materials), both failures traced to items on the targeted checklist: dry mass counted twice, and an extra resin binder in the ecoinvent dataset.

Yes → pass. No → targeted check.

The check never changes a number by itself. **Rule revised 13 Nov.**

- **Yes** → **PASS** (Record the check and continue)
- **No** → **TARGETED CHECK** (Units and mass basis, dataset state, indicator, composition. Correct proven errors only, once)

### PASS: Record the check and continue

*Step*

Record our value, the median and the number of EPDs in `epd_check.csv`, and continue to the A1–A3 block.

Next → **A1–A3 BLOCK** (Output: 1 kg at the factory gate)

### TARGETED CHECK: Units and mass basis, dataset state, indicator, composition. Correct proven errors only, once

*Step*

**Targeted check.** Go through these four items in order, once:

1. **Units and mass basis.** Per m³ or per m² values converted to per kg with the right density or area mass; moisture counted once (not dry mass plus water on top of a dataset that already includes it).
2. **Dataset state.** Each dataset matches the delivered state (e.g. dried and planed, not raw).
3. **Indicator.** Only GWP-fossil is compared, on both sides; no biogenic or land-use carbon mixed in.
4. **Composition.** The datasets used contain the same constituents as S1: no extra ingredient (e.g. a resin binder inside an ecoinvent product dataset) and none missing. A mismatch means D1 should not have matched: rebuild the material from its S1 constituents through D5.

#### Rules

- Change something only when it is shown to be wrong, and log the evidence.
- Never change a choice because it brings the result closer to the EPD median.
- One round only.

Log in `epd_check.csv`: each item, what was found, what was changed and why.

Next → **STEP 3 · RECHECK** (Now within ±50 % of the median?)

### STEP 3 · RECHECK: Now within ±50 % of the median?

*Decision*

Recalculate GWP-fossil A1–A3 after the corrections and apply the same test: within ±50 % of the ÖKOBAUDAT median?

Yes → pass, with the corrections recorded. No → flag.

- **Yes** → **PASS** (Record the correction and continue)
- **No** → **FLAG** (Flag the material; record what was checked and changed)

### PASS: Record the correction and continue

*Step*

Record the value before and after, the median, and the corrections made in `epd_check.csv`, and continue to the A1–A3 block.

Next → **A1–A3 BLOCK** (Output: 1 kg at the factory gate)

### FLAG: Flag the material; record what was checked and changed

*Step*

The material still fails after one round of corrections. Keep the LCI as it is, mark it as flagged in `epd_check.csv`, and record: our value, the median and number of EPDs, each checklist item with what was found, any corrections made, and one sentence on the likely reason for the remaining gap (e.g. EPDs from one producer only, or a different production route).

Flagged materials stay in the model and are reported as such in the paper.

Next → **A1–A3 BLOCK** (Output: 1 kg at the factory gate)

### A1–A3 BLOCK: Output: 1 kg at the factory gate

*Step*

The first block of the sheet. Output (production row): 1 kg of the material at the factory gate. Inputs: the rows written above.

A1, A2 and A3 stay one module because ecoinvent datasets bundle raw materials, transport to the manufacturer and manufacturing.

*Example:* clay brick masonry, A1–A3 → 1 kg  
market for clay brick · 0.8 kg  
market for lime mortar · 0.2 kg

Next → **A4 · T1** (Is it delivered in bulk: loose or ready-mixed?)

## A4: Transport to site

### A4 · T1: Is it delivered in bulk: loose or ready-mixed?

*Decision*

**Question A4 · T1.** Is the material delivered to site in bulk: loose or ready-mixed by truck, rather than as discrete products (units, boards, sections, rolls)?

- Yes: ready-mixed concrete, aggregate, sand, earth, loose fill.
- No: anything delivered as pieces, boards, rolls or bales.

Yes → bulk, 50 km ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), bulk material). No → T2.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **BULK** (50 km by lorry)
- **No** → **A4 · T2** (Is it made in at least 3 of DE, FR, IT, ES, NL?)

### BULK: 50 km by lorry

*Step*

Bulk material: one row, lorry 50 km one way ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), bulk material).

Next → **A4 BLOCK** (1 kg of A1–A3 in, plus the transport rows of its category)

### A4 · T2: Is it made in at least 3 of DE, FR, IT, ES, NL?

*Decision*

**Question A4 · T2.** Is the product made in at least 3 of the 5 countries DE, FR, IT, ES, NL (the first five of the D3 country list)?

**How to check:** look for a manufacturer of this product in each country, in this order: the product's EPDs in ÖKOBAUDAT or the EPD programme registries, then the national manufacturers' association, then a web search for "<product> manufacturer <country>". Record one manufacturer name and link per country found.

Yes → nationally manufactured, 150 km. No → T3.

Why these countries: production spread over the large European markets means a building usually gets the product from within its own country.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **NATIONAL** (150 km by lorry)
- **No** → **A4 · T3** (Is it made anywhere in Europe?)

### NATIONAL: 150 km by lorry

*Step*

Nationally manufactured: one row, lorry 150 km one way ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), other materials, products and elements).

Next → **A4 BLOCK** (1 kg of A1–A3 in, plus the transport rows of its category)

### A4 · T3: Is it made anywhere in Europe?

*Decision*

**Question A4 · T3.** Is the product made anywhere in Europe (EU, EFTA or UK)?

**How to check:** as in T2, but any European country counts. Record one manufacturer name, country and link.

Yes → EU manufactured. No → globally manufactured.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **EU** (1,500 km lorry + 100 km sea)
- **No** → **GLOBAL** (500 km lorry + 10,000 km sea)

### EU: 1,500 km lorry + 100 km sea

*Step*

EU manufactured: lorry 1,500 km plus container ship 100 km ([RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17, European manufactured).

Next → **A4 BLOCK** (1 kg of A1–A3 in, plus the transport rows of its category)

### GLOBAL: 500 km lorry + 10,000 km sea

*Step*

Globally manufactured: lorry 500 km plus container ship 10,000 km ([RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17, globally manufactured).

Next → **A4 BLOCK** (1 kg of A1–A3 in, plus the transport rows of its category)

### A4 BLOCK: 1 kg of A1–A3 in, plus the transport rows of its category

*Step*

Output: 1 kg delivered to site. Inputs: 1 kg from the A1–A3 block, plus one transport row per mode of the category reached in T1–T3: tkm = 1 kg × distance ÷ 1000.

| Category | Road | Sea | Source |
| --- | --- | --- | --- |
| Bulk | 50 km | – | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| Nationally manufactured | 150 km | – | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| EU manufactured | 1,500 km | 100 km | [RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17 |
| Globally manufactured | 500 km | 10,000 km | [RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf), Table 17 |

Do not add empty return trips: the ecoinvent transport datasets already include average load factors and empty trips.

*Example:* Clay brick masonry: T1 no (delivered as units); T2 yes (brick makers in all five countries) → 150 km.  
lorry · 1 × 150 ÷ 1000 = 0.15 tkm

Next → **A5 · I1** (Is it poured or pumped, or over 50 kg per piece?)

## A5: Installation

### A5 · I1: Is it poured or pumped, or over 50 kg per piece?

*Decision*

**Question A5 · I1.** Is the material poured or pumped on site, or does a typical delivered piece weigh more than 50 kg?

- "Piece" = one unit as handled on site: a brick, a board, a beam, a panel, a bale, a roll.
- Take the typical piece weight from the product's datasheet or EPD (dimensions × density if only those are given) and record it.
- 50 kg = two people at 25 kg each, the reference mass in manual handling guidance (ISO 11228-1). Threshold is our assumption.

Yes → look up and add a machine energy row. No → no row (installed by hand). Hand tools, fixings and site huts are left out for every material.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **A5** (Look up the installation energy per kg; add a row and log value, source and derivation)
- **No** → **A5 · L1** (Is it made in situ on the building site?)

### A5: Look up the installation energy per kg; add a row and log value, source and derivation

*Step*

Look up the energy needed to install this product by machine (crane, pump, lifting equipment), as MJ per kg, and add one row with the value found. No default value is given: the agent finds and documents it, so a second run can check the same search.

#### Search order

1. The A5 scenario of EPDs for this product in ÖKOBAUDAT, then in the EPD programme registries (EPD International, EPD Norge, EPD Hub, IBU).
2. The manufacturer's installation guidance (equipment, power, time per element).
3. A peer-reviewed study of installation of this product type.

Stop at the first step that gives a value.

#### Rules for the value

- Convert to MJ per kg installed: kWh × 3.6 = MJ; per m² or per element ÷ its mass. Diesel row: `diesel, burned in building machine`; electricity row: the D3 location's market for electricity, low voltage.
- Several EPDs in the same step: take the median, and record all values.
- Nothing found in all three steps: use the **fallback value of 0.015 MJ diesel per kg**, and log "fallback". The fallback is the crane energy of a precast timber-concrete slab EPD (88 kW crane, 10 minutes per 3.4 t element = 4.3 kWh/t; [EPD Hub 0135, precast TCC slab (2022)](https://manage.epdhub.com/declarations/file/download/epdSigned/158/)). It rests on one EPD; replace it if a better general source turns up.

#### Log in decisions.csv

Value, unit, source and link, the derivation in one line (e.g. "88 kW crane × 10 min per 3.4 t element = 4.3 kWh/t = 0.015 MJ/kg"), and the search step it came from.

*Example:* Example of a logged derivation (also the fallback): EPD Hub 0135, precast timber-concrete slab: 88 kW crane, 10 minutes per 3.4 t element → 4.3 kWh per tonne → 0.015 MJ/kg ([EPD Hub 0135, precast TCC slab (2022)](https://manage.epdhub.com/declarations/file/download/epdSigned/158/)). EPDs vary widely: an insulated-panel EPD assumes about 0.18 kWh/kg ([EPD Hub 0289, Kingspan panel (2025)](https://manage.epdhub.com/declarations/file/download/epdSigned/373/)), which is why the value is looked up per product.

Next → **A5 · L1** (Is it made in situ on the building site?)

### A5 · L1: Is it made in situ on the building site?

*Decision*

**Question A5 · L1.** Is the material made in situ on the building site (cast, mixed, sprayed, or laid from small units with mortar or adhesive), rather than delivered as a finished product that is only fixed in place?

- Yes, in situ: cast concrete, masonry laid with mortar, cast or sprayed hempcrete, tiles set in adhesive.
- No, prefab: boards, panels, beams, profiles, glazing, mats, fabrics, blocks or bales placed dry.

Yes → 5 % waste. No → 3 % waste ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf), §2.6.3.6, building-site losses). NMD's third class, 15 % for auxiliary and finishing materials (sealants, adhesives, paints), does not apply to the 30 materials.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **LOSS** (5 % (NMD, in situ))
- **No** → **LOSS** (3 % (NMD, prefab))

### LOSS: 5 % (NMD, in situ)

*Step*

In-situ products: waste rate 5 % ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf)).

Next → **A5 BLOCK** ((1 + loss) kg of A4 in, plus any energy row; the lost kg goes to waste)

### LOSS: 3 % (NMD, prefab)

*Step*

Prefab products: waste rate 3 % ([NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf)).

Next → **A5 BLOCK** ((1 + loss) kg of A4 in, plus any energy row; the lost kg goes to waste)

### A5 BLOCK: (1 + loss) kg of A4 in, plus any energy row; the lost kg goes to waste

*Step*

Output: 1 kg installed. Inputs: (1 + loss) kg from the A4 block, plus the machine energy row if I1 was yes. The waste rate w comes from L1: 5 % in situ, 3 % prefab (NMD). To install 1 kg, 1 + loss kg must be delivered, so the loss scales the whole chain above it. The lost kg goes to waste: a lorry row (C2 distance) and its end-of-life rows (C3–C4).

NMD gives the waste rate w as a share of the material delivered. In the sheet: loss = kg lost per kg installed = w ÷ (1 − w).

*Example:* Clay brick masonry: I1 no (bricks under 50 kg); L1 yes (laid with mortar on site) → 5 % → 0.05 ÷ 0.95 = 0.053.  
clay brick masonry, A4 · 1.053 kg  
lorry to recycling · 0.053 × 50 ÷ 1000 tkm  
end of life of 0.053 kg as in C3–C4

Next → **B1** (No rows. Not modelled; concrete carbonation noted as a limitation)

## B1–B7: Use stage. Depends on the function, so the model handles it after the Ashby step. No rows here

### B1: No rows. Not modelled; concrete carbonation noted as a limitation

*No rows*

No rows. All of module B depends on the function the material is used for (indoor or outdoor, exposure, service life), so it is handled by the model after the Ashby step, not in this per-kg sheet.

B1 use emissions are not modelled. Concrete carbonation uptake is noted as a limitation.

Next → **B2** (No rows. The model adds recoating for outdoor functions)

### B2: No rows. The model adds recoating for outdoor functions

*Computed by the model (no rows)*

No rows in the sheet. Maintenance depends on the function (indoor or outdoor) and its service life, not on the material, so the model adds it at the product level, like B4.

For outdoor functions with a coated material, the model adds paint per kg of material = coats × coating mass per coat ÷ product mass per m² × recoatings, with recoatings = ceil(service life ÷ interval) − 1.

Defaults: 2 coats × 0.15 kg/m² every 10 years ([Moelven cladding EPD NEPD-310-180 (2015)](https://www.moelven.com/globalassets/inriver/documents/epd-moelvenwood-kledning-2-str-nepd-310-180-en-exterior-cladding-with-waterborne-paint-gk.pdf), B2 scenario; [Flügger Wood Tex EPD NEPD-3504-2097 (2022)](https://epd-global.com/getfile.php/1323835-1652271462/EPDer/Utenlandsk%20registrerte%20EPD/NEPD-3504-2097_Flugger-07-Wood-Tex-Matt.pdf) agrees on 0.15 kg/m²). Product mass per m² comes from the Ashby step.

Next → **B3** (No rows. The model adds repair per function)

### B3: No rows. The model adds repair per function

*Computed by the model (no rows)*

No rows in the sheet. Repair depends on the function and its service life, so the model adds it at the product level, like B4.

Where a source gives a repair share r (kg renewed over the service life per kg installed), the model adds r kg of the material's A1–A5 chain and r kg of its end of life (C1–C4). r of 1 or more is a replacement, counted in B4. No default.

Next → **B4** (No rows. The model repeats the chain for each replacement)

### B4: No rows. The model repeats the chain for each replacement

*Computed by the model (no rows)*

No rows in the sheet. The model counts replacements over the study period from the function's reference service life:

`replacements = ceil(study period ÷ service life) − 1`

Each replacement repeats the chain for the same mass. Applied in the ranking step.

Next → **B5 · B6 · B7** (No rows. Not modelled)

### B5 · B6 · B7: No rows. Not modelled

*No rows*

No rows. B5 refurbishment, B6 operational energy and B7 operational water depend on the function and the building, and are not modelled.

Next → **C1 · X1** (Is it cast, bonded, or over 50 kg per piece?)

## C1: Deconstruction

### C1 · X1: Is it cast, bonded, or over 50 kg per piece?

*Decision*

**Question C1 · X1.** Is the material cast in place, bonded (mortar, adhesive, welding), or does a typical piece weigh more than 50 kg?

Yes → demolished by machine: one diesel row. No → taken apart by hand: no row. Same piece weight and 50 kg threshold as A5 · I1 (assumption).

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **C1** (Add a diesel row: 0.036 MJ per kg)
- **No** → **C1** (No diesel row (taken apart by hand))

### C1: No diesel row (taken apart by hand)

*Step*

No C1 rows: taken apart by hand.

Next → **C1 BLOCK** (1 kg of A5 in, plus any diesel row)

### C1: Add a diesel row: 0.036 MJ per kg

*Step*

One row: `diesel, burned in building machine`, 0.036 MJ per kg.

Derivation: 10 kWh of diesel per m² of demolished building (Bozdağ & Seçer 2007) ÷ about 1,000 kg of building per m² = 0.01 kWh/kg = 0.036 MJ/kg. This is the default in EPDs made with One Click LCA ([Bozdağ & Seçer 2007 (EPD Hub 1675)](https://skarbyggsystem.se/wp-content/uploads/sites/3/2026/08/epd_hub-1675_column-beam.pdf)).

Caveat: the figure comes from reinforced-concrete buildings and is spread over all machine-demolished materials. Light materials such as timber may need less energy per kg.

Next → **C1 BLOCK** (1 kg of A5 in, plus any diesel row)

### C1 BLOCK: 1 kg of A5 in, plus any diesel row

*Step*

Output: 1 kg demolished. Inputs: 1 kg from the A5 block, plus the diesel row if any.

Next → **C2 · E1** (Does it match an NMD end-of-life category?)

## C2: End-of-life route, then transport to waste

### C2 · E1: Does it match an NMD end-of-life category?

*Decision*

**Question C2 · E1.** Does the material match one of the NMD end-of-life categories ([NMD end-of-life defaults 2024](https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/))? Record the category number. This route is decided before C2, because C2 transport depends on it.

| No. | NMD category | Landfill / incin. / recycl. / reuse (%) |
| --- | --- | --- |
| 34 | Wood, untreated: beams, planks | 5 / 80 / 10 / 5 |
| 36 | Wood, painted or preserved | 5 / 95 / 0 / 0 |
| 55 | Board material, clean, large pieces | 5 / 85 / 10 / 0 |
| 56 | Board material, contaminated | 5 / 95 / 0 / 0 |
| 52 | Organic / bio-based insulation, other | 5 / 95 / 0 / 0 |
| 8 | Concrete elements, masonry, reinforced concrete | 1 / 0 / 99 / 0 |
| 9 | Aerated concrete | 1 / 0 / 99 / 0 |
| 32 | Coarse ceramics: masonry, roof tiles | 1 / 0 / 99 / 0 |
| 40 | Calcium silicate units | 1 / 0 / 99 / 0 |
| 25 | Fine ceramics, sanitary | 15 / 0 / 80 / 5 |
| 27 | Gypsum blocks, boards | 95 / 0 / 5 / 0 |
| 28 | Flat glass | 30 / 0 / 70 / 0 |
| 78 | Stone wool | 85 / 5 / 10 / 0 |
| 30 | Glass wool | 85 / 5 / 10 / 0 |
| 70 | Steel, structural sections | 1 / 0 / 94 / 5 |
| 73 | Steel, light profiles, sheets | 1 / 0 / 87 / 12 |
| 4 | Aluminium profiles, sheets | 3 / 3 / 94 / 0 |
| 63 | PVC window profiles | 10 / 10 / 80 / 0 |
| 62 | PVC films, roofing | 10 / 85 / 5 / 0 |
| 45 | Plastics, other: profiles, sheets | 0 / 90 / 10 / 0 |
| 46 | Plastics, fibre-reinforced | 0 / 100 / 0 / 0 |
| 57 | Polyolefins: pipes, films | 10 / 85 / 5 / 0 |

A match = the material, or the product type it is used as, is named in the category. Yes → use its shares. No → use the category of its heaviest constituent.

Log the answer in `decisions.csv`: material, question id, yes or no, evidence (with link), date.

- **Yes** → **ROUTE** (Use that category's end-of-life shares; record its number)
- **No** → **ROUTE** (Use the category of its heaviest constituent; record why)

### ROUTE: Use the category of its heaviest constituent; record why

*Step*

No direct match: take the category of the heaviest constituent (from step 1). If that also has no match, take the category with the same main raw material, and record the reasoning in one sentence. Such cases are the ones most likely to differ between runs.

Next → **C2 BLOCK** (1 kg of C1 in, plus lorry tkm per share: 50 km recycling or landfill, 100 km incineration)

### ROUTE: Use that category's end-of-life shares; record its number

*Step*

Use the matched category's shares ([NMD end-of-life defaults 2024](https://milieudatabase.nl/en/downloads/download/appendix-default-values-for-end-of-life-processing-scenarios/)), and record its number. Under the cut-off rule, reuse is treated like recycling: the material leaves the system without burden after C3, and its benefit goes to D.

Next → **C2 BLOCK** (1 kg of C1 in, plus lorry tkm per share: 50 km recycling or landfill, 100 km incineration)

### C2 BLOCK: 1 kg of C1 in, plus lorry tkm per share: 50 km recycling or landfill, 100 km incineration

*Step*

Output: 1 kg at the waste site. Inputs: 1 kg from the C1 block, and lorry tkm to each treatment in the route chosen at E1, weighted by its shares.

| Treatment | Distance (one way) | Source |
| --- | --- | --- |
| Recycling (sorting, crushing) | 50 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| Reuse | 50 km | assumption: as recycling |
| Landfill | 50 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |
| Incineration | 100 km | [NMD method 2020 §2.6.3.6](https://milieudatabase.nl/media/filer_public/08/97/08978af7-15a0-4412-a782-28aee7a91b83/bepalingsmethode-milieuprestatie-bouwwerken-juli-2020.pdf) |

*Example:* Clay brick masonry: E1 yes, category 32 (1 / 0 / 99 / 0) → all 50 km → 0.05 tkm

Next → **C3–C4 BLOCK** (1 kg of C2 in, plus one treatment row per end-of-life share. This block is the cradle-to-grave total)

## C3–C4: Waste processing and disposal

### C3–C4 BLOCK: 1 kg of C2 in, plus one treatment row per end-of-life share. This block is the cradle-to-grave total

*Step*

The last block. Output: 1 kg, cradle to grave. Inputs: 1 kg from the C2 block, and one treatment row per share of the route chosen at E1. Waste sent to treatment has a negative amount (ecoinvent convention).

RICS Table 23 ([RICS WLCA 2023](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf)) gives UK end-of-life defaults that can serve as a sensitivity case.

NMD has published revised scenarios (Nov 2026), usable from 1 Jan 2027, in an Excel file not yet read. Check them before freezing these values.

*Example:* clay brick masonry, C2 · 1 kg  
treatment of waste brick, recycling · −0.99 kg  
inert waste to landfill · −0.01 kg

Score this block for the total. A contribution analysis by activity gives each module.

Next → **D** (No rows. The model applies the circular footprint formula to the end-of-life route)

## D: Beyond the system boundary

### D: No rows. The model applies the circular footprint formula to the end-of-life route

*Computed by the model (no rows)*

No rows in the sheet. The model applies the circular footprint formula to the material's end-of-life route: credits for recycled material and for energy recovered at incineration.

Next → **BIO-C** (Biogenic carbon is reported separately by the model)

### BIO-C: Biogenic carbon is reported separately by the model

*Computed by the model (no rows)*

Biogenic carbon storage is reported separately for every material containing plant-based carbon, and kept out of the GWP-fossil EPD comparison.

Next → **END** (Sheet complete: save the records; 5 random materials are rebuilt by a separate AI session)

## END: Sheet complete: save the records; 5 random materials are rebuilt by a separate AI session

Save the sheet and the records in `data/baseline_recipes/` under git:

- `decisions.csv`: one row per diamond answered (material, question id, answer, evidence, link, date)
- `dataset_choices.csv`: one row per dataset choice (D1–D5), with search terms, candidates, scores, version and date
- `material_definitions.csv`, `epd_check.csv`

#### Reproducibility test

A separate AI session gets only this protocol and the two inputs for each material, rebuilds 5 materials picked at random, and both runs are compared question by question: `decisions.csv` (categories, thresholds, routes) and `dataset_choices.csv` (datasets). Every difference is fixed by sharpening the test of the diamond that allowed it. **Decided 12 Nov.**
