# Method constants

| File | Used in | What it holds | Source |
|---|---|---|---|
| `cff_archetypes.csv` | step 1d | per CFF archetype: A, Qsin/Qp, Qsout/Qp, LHV, heat and electricity efficiency, B, and the names of its datasets: virgin material and recycled material (for recycled input), avoided product and energy (for module D); basis and status of each value | sheet `cff_archetypes` of `02_docs/lci_protocol/protocol_predetermined_values.xlsx` (exported 24 Nov 2026). Changed on 24 Nov 2026: the dataset names are short keys of `cff_datasets.csv`; the R1 column was removed (recycled content is read from the LCI, see `02_docs/methods_unit_lcia.md`, section 4); virgin and recycled material added for solid wood and steel |
| `cff_datasets.csv` | steps 1b, 1d | the ecoinvent dataset (name, reference product, location, unit) behind each name in `cff_archetypes.csv`, with its role | written 24 Nov 2026 (was `avoided_datasets.csv`); rows marked **check** to confirm with `02_docs/lci_protocol/official_run/search_ecoinvent.py` |
| `carbon_archetypes.csv` | step 1e | per carbon archetype: carbon fraction of dry mass, default moisture (dry basis), the constituents that belong to it, basis | sheet `carbon_archetypes` of the protocol workbook (exported 24 Nov 2026) |
| `gwpbio_table.csv` | component 2 | GWP_bio factors of Guest et al. (2012) by rotation and storage period | bcic sheet snapshot of 16 Oct 2026 |
| `dcf_bern.csv` | component 2 | Bern carbon cycle coefficients for the dynamic characterisation factor (Levasseur et al. 2010) | bcic sheet snapshot of 16 Oct 2026 |

If a value changes in the protocol workbook, export it here again (the model reads only these CSVs).
