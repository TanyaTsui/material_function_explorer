# Methods: unit impacts of the baseline and RAW materials (component 1)

What component 1 calculates, and how. Code: `03_model/1_unit_lcia/` (one script per step below). Result: the four
tables in `01_data/02_processed/`.

## 1. What is assessed

**35 cases**, each 1 kg of a construction material:

- 27 **baseline** materials (conventional and bio-based), one LCI each, written with the baseline LCI protocol
  (`02_docs/lci_protocol/`).
- 4 **RAW** products, each assessed twice: as built in the project (**prototype**) and at industrial scale
  (**scaled-up**). 8 cases, one LCI each.

**Functional unit of component 1:** 1 kg of the material, installed, over one life (cradle to grave plus module D). The
amount needed for a function, and how often it is repaired or replaced, come in component 2.

**Two scenarios:** *today* (ecoinvent 3.12 cut-off as it is) and *2050* (the same database rewritten by premise with the
IMAGE SSP2-L pathway for 2050). Only the background changes between them; the LCIs are the same.

**Impact method:** EF 3.1, all 25 categories as implemented in ecoinvent 3.12 (`ecoinvent-3.12 / EF v3.1` in Brightway).

**Deterministic:** each exchange is taken at its typical value (the `amount` column of the LCI sheet). The ranges in
the RAW sheets are not used here.

## 2. Life cycle modules (EN 15804)

| Module | Included | Where it comes from |
|---|---|---|
| A1–A3 product | yes | LCI sheet |
| A4 transport to site | yes | LCI sheet |
| A5 installation (incl. installation losses) | yes | LCI sheet |
| B1–B7 use | **no** | depends on the function: component 2 |
| C1 deconstruction | yes | LCI sheet |
| C2 transport to waste processing | yes | LCI sheet |
| C3–C4 waste processing and disposal | yes | LCI sheet |
| D benefits beyond the system boundary | yes | calculated (section 4) |
| Biogenic carbon stored in the product | reported separately | calculated (section 5) |

The RAW workbooks originally also held B3 (repair) and B4 (replacement) blocks. They were removed when the workbooks
were split per variant (24 Nov 2026), so that module B is counted once, in component 2. At typical values both were 0.

## 3. Modules A and C (steps 1a to 1c)

Each LCI sheet is a chain of blocks: A1–A3 → A4 → A5 → C1 → C2 → C3–C4. Each block's first input is the output of the
block before it, so the last activity of a block carries everything up to the end of that block.

1. **Impact of one unit of every ecoinvent dataset used** (step 1b, Brightway): for each background dataset of the LCIs
   and each avoided product of module D, the EF 3.1 score of one unit (1 kg, 1 kWh, 1 tkm, 1 MJ, ...), per scenario.
   A dataset missing in the 2050 database gets today's value (noted in the output table).
2. **Cumulative impact of an activity**, per unit of its output:

   `cumulative(activity) = Σ over its inputs of amount × cumulative(input) / amount produced`

   where `cumulative(input)` is the score from step 1 for an ecoinvent dataset, or the same calculation for an
   activity of the same LCI sheet.
3. **Impact of a module**: `impact(M) = cumulative(end of M) − cumulative(end of the module before M)`, with
   `cumulative(before A1–A3) = 0`. The modules therefore add up to the cradle-to-grave impact of 1 kg.

**Losses.** When A5 needs, for example, 1.03 kg delivered per kg installed, step 3 subtracts 1 kg (not 1.03 kg) of the
A4 cumulative impact, so the production and transport of the lost 0.03 kg are counted in A5, as EN 15804 asks.

**Check.** Step 1g recomputes the cradle-to-grave impact of every case with the matrix method (all foreground
activities of the sheet solved as one system of linear equations) and stops if it differs from the sum of the modules.

## 4. Module D: circular footprint formula (step 1d)

Module D follows the circular footprint formula (CFF) of the EU Environmental Footprint method. Each case belongs to one
CFF archetype (`cff_inputs.csv`). The archetype gives the parameters (`method_constants/cff_archetypes.csv`, values and
sources from the protocol workbook), and the case gives its end-of-life shares (the same shares as its C3–C4 block).
Per kg of product:

```
material credit = −(1 − A) × (R_recycling + R_reuse) × (Qsout / Qp) × E_avoided material
energy credit   = −(1 − B) × R_incineration × LHV × (X_heat × E_heat + X_el × E_el / 3.6)
module D        = material credit + energy credit
```

| Symbol | Meaning | Source |
|---|---|---|
| A | allocation of burdens and credits between supplier and user of recycled material | archetype (JRC Annex C defaults where available) |
| R_recycling, R_reuse, R_incineration | end-of-life shares | `cff_inputs.csv` (NMD end-of-life defaults, as in C3–C4) |
| Qsout/Qp | quality of the recycled output relative to the primary material it replaces | archetype |
| B | allocation factor of energy recovery; 0 in the EF method | archetype |
| LHV | lower heating value, MJ per kg | archetype |
| X_heat, X_el | heat and electricity efficiency of the incinerator | archetype |
| E_avoided material, E_heat (per MJ), E_el (per kWh) | impact of the avoided product | step 1b; datasets in `method_constants/avoided_datasets.csv` |

**Choices and limitations**

- **Reuse is credited like recycling.** The RAW LCI sheets treat reuse as recycling under cut-off; module D does the same.
- **The recycled-content term (R1) of the CFF is not applied.** The LCI datasets already contain the product's recycled
  input under the cut-off rule (burden-free scrap). Applying the full CFF would add `(1 − A) × R1 × (E_v × Qsin/Qp − E_recycled)`
  to A1–A3. This matters most for structural steel (R1 = 1) and aluminium extrusion (R1 = 0.75), whose A1–A3 is lower
  here than under the full CFF. Open point.
- **The recycling process at end of life is counted in full in C3–C4** (as in the LCI sheet), not multiplied by (1 − A).
- **The RAW timber LCI already applies the CFF to its recycled input inside A1–A3** (A × waste wood + (1 − A) × Qs/Qp ×
  virgin sawnwood). The baselines do not; see the R1 point above.
- **The avoided datasets** (`avoided_datasets.csv`) were matched by name; their locations were chosen by us and are
  marked "check".
- EN 15804+A2 (behind the ÖKOBAUDAT EPDs used in the protocol check) uses a different module D rule; the CFF is used here
  because the impact method is the EF method.

## 5. Biogenic carbon stored in the product (step 1e)

Per constituent of the product (`bioc_inputs.csv`, losses excluded: only what ends up in the product):

```
CO2 stored = kg per kg of product ÷ (1 + u) × carbon fraction of dry mass × 44/12
```

with `u` the moisture content on a dry basis (from `bioc_inputs.csv` if given, otherwise the default of the carbon
archetype) and the carbon fraction from the constituent's carbon archetype (`method_constants/carbon_archetypes.csv`;
0 for mineral, metal and fossil constituents).

The result, in kg CO2 per kg of product, is the same in both scenarios and is **reported next to the impact categories,
not inside "climate change"**. How much credit the stored carbon deserves depends on how long it stays stored (the
service life), which depends on the function. Component 2 therefore applies the time-dependent credit: GWP_bio of
Guest et al. (2012) for virgin biomass and the dynamic characterisation factor of Levasseur et al. (2010) for
co-products and recycled biomass (tables in `method_constants/gwpbio_table.csv` and `dcf_bern.csv`), as in the bcic model.

**No double counting with EF 3.1 (to confirm).** The EF method's simplified approach to biogenic carbon is expected
to give biogenic CO2 uptake and emission a factor of 0 in "climate change", so that only biogenic methane counts. Step
1b prints the factors of `carbon dioxide, in air` and `carbon dioxide, non-fossil` in the database used: if they are
not 0, stored carbon would be counted twice and this section has to change.

Not included: CO2 taken up by lime binders as they carbonate (relevant for hempcrete).

## 6. The output tables

| File | Shape | Content |
|---|---|---|
| `unit_impacts_by_module_<scenario>.csv` | long: one row per case × module × impact category | modules A1–A3, A4, A5, C1, C2, C3–C4, D; plus one row per case with module `in product`, category `biogenic CO2 stored`, unit kg CO2 |
| `unit_impacts_total_<scenario>.csv` | wide: one row per case | one column per impact category (unit in the column name) = sum of all modules A1–A3 to C3–C4 and D; last column: biogenic CO2 stored (kg CO2) |

`case_type` is `baseline`, `RAW prototype` or `RAW scaled-up`. All values are per kg of product.

Intermediate tables of each step are in `01_data/02_processed/unit_lcia_steps/`, named after the step that writes them.

## 7. Inputs written by hand (to check)

- **RAW rows of `cff_inputs.csv` and `bioc_inputs.csv`** (source column: "written by hand from the RAW LCI"). Archetypes
  and constituents were read from the RAW LCI sheets. Where no archetype fits (seagrass, pea protein, glycerol,
  xanthan gum) the closest or the conservative one was taken (lower stored carbon for RAW) and flagged.
- **The two concrete baselines** (non-structural and reinforced structural) both use the `concrete` rows of the official
  protocol run, which had one concrete. For reinforced concrete the steel share would change the CFF archetype mix.
- **Locations of the avoided datasets** of module D.
