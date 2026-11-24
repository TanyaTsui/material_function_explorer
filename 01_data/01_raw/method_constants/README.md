# Method constants

| File | Used in | What it holds | Source |
|---|---|---|---|
| `cff_archetypes.csv` | step 1d | per CFF archetype: A, R1, Qsin/Qp, Qsout/Qp, LHV, heat and electricity efficiency, avoided product and energy, B, basis | sheet `cff_archetypes` of `02_docs/lci_protocol/protocol_predetermined_values.xlsx` (exported 24 Nov 2026; the avoided products are written as short keys of `avoided_datasets.csv`) |
| `avoided_datasets.csv` | steps 1b, 1d | the ecoinvent dataset (name, reference product, location, unit) behind each avoided product and energy of module D | written 24 Nov 2026; **locations to check** with `02_docs/lci_protocol/official_run/search_ecoinvent.py` |
| `carbon_archetypes.csv` | step 1e | per carbon archetype: carbon fraction of dry mass, default moisture (dry basis), the constituents that belong to it, basis | sheet `carbon_archetypes` of the protocol workbook (exported 24 Nov 2026) |
| `gwpbio_table.csv` | component 2 | GWP_bio factors of Guest et al. (2012) by rotation and storage period | bcic sheet snapshot of 16 Oct 2026 |
| `dcf_bern.csv` | component 2 | Bern carbon cycle coefficients for the dynamic characterisation factor (Levasseur et al. 2010) | bcic sheet snapshot of 16 Oct 2026 |

If a value changes in the protocol workbook, export it here again (the model reads only these CSVs).
