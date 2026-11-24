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
| CFF correction for recycled input (part of A1–A3) | yes, on its own row | calculated (section 4) |
| Biogenic carbon stored in the product | reported separately | calculated (section 5) |

The RAW workbooks originally also held B3 (repair) and B4 (replacement) blocks. They were removed when the workbooks
were split per variant (24 Nov 2026), so that module B is counted once, in component 2. At typical values both were 0.

## 3. Modules A and C (steps 1a to 1c)

Each LCI sheet is a chain of blocks: A1–A3 → A4 → A5 → C1 → C2 → C3–C4. Each block's first input is the output of the
block before it, so the last activity of a block needs everything up to the end of that block.

1. **Impact of one unit of every ecoinvent dataset used** (step 1b, Brightway): for each background dataset of the LCIs
   and each dataset of the CFF (section 4), the EF 3.1 score of one unit (1 kg, 1 kWh, 1 tkm, 1 MJ, ...), per scenario.
   A dataset missing in the 2050 database gets today's value (noted in the output table).
2. **Cumulative inventory of an activity** (step 1c), per unit of its output: the amount of every ecoinvent dataset it
   needs, upstream included:

   `inventory(activity) = Σ over its inputs of amount × inventory(input) / amount produced`

   where the inventory of an ecoinvent input is just its own amount, and the inventory of an activity of the same LCI
   sheet is found the same way.
3. **Inventory of a module**: `inventory(M) = inventory(end of M) − inventory(end of the module before M)`, with nothing
   before A1–A3. The modules therefore add up to the cradle-to-grave inventory of 1 kg.
4. **Impact of a module** = Σ over its inventory of amount × impact of one unit (step 1).

The inventory per module (`unit_lcia_steps/1c_inventory_by_module.csv`) is the same in both scenarios and shows, for
every case, how much of each ecoinvent dataset each module uses.

**Losses.** When A5 needs, for example, 1.03 kg delivered per kg installed, step 3 subtracts 1 kg (not 1.03 kg) of the
A4 inventory, so the production and transport of the lost 0.03 kg are counted in A5, as EN 15804 asks.

**Check.** Step 1g recomputes the cradle-to-grave impact of every case with the matrix method (all foreground
activities of the sheet solved as one system of linear equations) and stops if it differs from the sum of the modules.

## 4. Circular footprint formula: recycled input and module D (step 1d)

**Principle.** The LCI sheets hold only physical flows: what goes in and out, in what amounts. The allocation of
recycling between the user and the supplier of recycled material is a method choice, applied by the model on both
sides with the circular footprint formula (CFF) of the EU Environmental Footprint method and one set of parameters.

Why both sides: ecoinvent's cut-off datasets give recycled material without the burden of the product it came from
(the user keeps the whole benefit, as if A = 1). The CFF gives the user the share A of the benefit and the supplier at
end of life the share 1 − A. Crediting the supplier in module D while the user also keeps the whole benefit in A1–A3
would count the share 1 − A twice (for metals, A = 0.2: 80 % of the benefit twice).

Each case belongs to one CFF archetype, or to one per part (`cff_inputs.csv`). The archetype gives the parameters and
the datasets (`method_constants/cff_archetypes.csv`; values and sources from the protocol workbook), the case gives
its end-of-life shares (the same shares as its C3–C4 block). Per kg of product:

```
recycled content (added to A1–A3) = m_recycled × (1 − A) × (Qsin/Qp × E_virgin − E_recycled)
material credit (D)               = −(1 − A) × (R_recycling + R_reuse) × (Qsout/Qp) × E_avoided product
energy credit (D)                 = −(1 − B) × R_incineration × LHV × (X_heat × E_heat + X_el × E_el / 3.6)
```

**Recycled content.** `m_recycled` is the kg of the archetype's recycled material in the A1–A3 inventory of the case
(step 1c), so the recycled content is read from the LCI itself, losses in production included. With the correction,
each kg of recycled input costs `A × E_recycled + (1 − A) × Qsin/Qp × E_virgin`, as the CFF asks. The correction is
reported on its own row, "A1–A3 recycled content (CFF)", next to A1–A3. Two cases have one:

| Case | Recycled material in the LCI | Virgin material it stands in for | A, Qsin/Qp |
|---|---|---|---|
| RAW timber (prototype and scaled-up) | reclaimed wood (waste wood market, as in v19), 1.25 kg per kg of product | virgin sawnwood | 0.8, 1 |
| Structural steel | steel, structural, 100 % scrap, 1 kg per kg | converter steel (to check) | 0.2, 1 |

Until 24 Nov 2026 the RAW timber LCI applied this correction in its own sheet (with Qsin/Qp = 0.9); it now holds the
plain flows (0.99 kg reclaimed wood and 0.01 kg virgin sawnwood per kg entering the first step) and the model applies the
correction with the archetype's values.

**Module D.** Material credit + energy credit. A case whose parts belong to different archetypes has one row per part,
each with its mass share, and module D is `Σ mass share × (material credit + energy credit)` over its parts. Only
reinforced concrete has two parts so far: concrete (95.5 %, mineral archetype) and reinforcing steel (4.5 %, steel
archetype), both with the shares of its C3–C4 block (99 % to reinforced concrete recycling, where the rebar is recovered,
1 % landfill).

| Symbol | Meaning | Source |
|---|---|---|
| A | allocation of the benefit of recycling between the user (A) and the supplier (1 − A) of recycled material | archetype (JRC Annex C defaults where available) |
| m_recycled | kg of recycled input per kg of product (the CFF's R1, as an amount) | the LCI, through the inventory of step 1c |
| Qsin/Qp, Qsout/Qp | quality of the recycled input / output relative to the primary material | archetype (JRC defaults for glass and metals; otherwise assumptions) |
| E_virgin, E_recycled | impact of 1 kg of the virgin material and of the recycled material as the LCI uses it | step 1b; datasets in `method_constants/cff_datasets.csv` |
| mass share | share of the case's mass that belongs to this archetype (1 unless the case has parts) | `cff_inputs.csv` |
| R_recycling, R_reuse, R_incineration | end-of-life shares | `cff_inputs.csv` (NMD end-of-life defaults, as in C3–C4) |
| B | allocation factor of energy recovery; 0 in the EF method | archetype |
| LHV | lower heating value, MJ per kg | archetype |
| X_heat, X_el | heat and electricity efficiency of the incinerator | archetype |
| E_avoided product, E_heat (per MJ), E_el (per kWh) | impact of the avoided product and energy | step 1b; datasets in `cff_datasets.csv` |

**Choices and limitations**

- **Recycled content is only corrected where the LCI shows it as its own flow** (the archetype's recycled material).
  Datasets that mix primary and recycled material inside ecoinvent are not corrected, because the model cannot see their
  recycled share: the aluminium market used for aluminium extrusion, the reinforcing steel of reinforced concrete, flat
  glass (cullet), and possibly wood panels and gypsum board. For aluminium this matters most (module D credits 94 %
  recycling). The fix, in the spirit of the principle above, is to write such an LCI as explicit primary and recycled
  flows, as for RAW timber. Open point.
- **Reuse is credited like recycling.** The RAW LCI sheets treat reuse as recycling under cut-off; module D does the same.
- **The recycling process at end of life is counted in full in C3–C4** (as in the LCI sheet), not multiplied by (1 − A).
- **The datasets of `cff_datasets.csv`** were matched by name; those marked "check" (e.g. converter steel as the virgin
  counterpart of scrap-based structural steel, at a different processing stage) need confirming.
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
| `unit_impacts_by_module_<scenario>.csv` | long: one row per case × module × impact category | A1–A3, A1–A3 recycled content (CFF), A4, A5, C1, C2, C3–C4, D; plus one row per case with module `in product`, category `biogenic CO2 stored`, unit kg CO2 |
| `unit_impacts_total_<scenario>.csv` | wide: one row per case | one column per impact category (unit in the column name) = sum of all these rows; last column: biogenic CO2 stored (kg CO2) |

`case_type` is `baseline`, `RAW prototype` or `RAW scaled-up`. All values are per kg of product.

Intermediate tables of each step are in `01_data/02_processed/unit_lcia_steps/`, named after the step that writes them.

## 7. Inputs written by hand (to check)

- **RAW rows of `cff_inputs.csv` and `bioc_inputs.csv`** (source column: "written by hand from the RAW LCI"). Archetypes
  and constituents were read from the RAW LCI sheets. Where no archetype fits (seagrass, pea protein, glycerol,
  xanthan gum) the closest or the conservative one was taken (lower stored carbon for RAW) and flagged.
- **The two concrete baselines** (non-structural and reinforced structural) both use the `concrete` rows of the official
  protocol run, which had one (unreinforced) concrete. Reinforced concrete has an extra steel row in `cff_inputs.csv`
  (4.5 % of the mass, from its A1–A3); its constituent list in `bioc_inputs.csv` lacks the steel, which holds no
  biogenic carbon, so the stored CO2 (0) is unaffected.
- **The datasets of `cff_datasets.csv`** marked "check" (locations, and the virgin counterpart of scrap steel).
