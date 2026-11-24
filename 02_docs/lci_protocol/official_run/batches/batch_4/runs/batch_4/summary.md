# Summary, batch_4 (ÖKOBAUDAT release OBD_2024_III, 13.11.2026; ecoinvent 3.12 cut-off)

GWP-fossil A1–A3 per kg, EF 3.1, computed read-only in Brightway.

| Material | Route kept | Dataset / machines | Ours (kg CO2e/kg) | EPD median (n) | Ratio | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| plywood | exact (D1 yes) | market for plywood, RER (m3, 823 kg/m3) | 0.496 | 0.405 (3) | 1.22 | CHECK 1 pass; no machine rows |
| mycelium | built (D1 no, D1b no) | hemp hurd FR 0.85, wheat flour RoW 0.05, rye grain CH (proxy for spawn) 0.10; autoclave (Rootlab, proxy), paddle mixer (Magaldi 700), belt dryer (STELA, proxy) | 0.656 | none | – | CHECK 3 no check possible; wear share 0.002 % |
| AAC | approximate (D1 no, D1b yes) | market for AAC block, CH | 0.359 | 0.461 (11) | 0.78 | CHECK 2 pass; no machine rows |
| concrete | built, flagged | gravel crushed CH (proxy) 0.769, cement Europe w/o CH 0.145, tap water RER 0.087; mixer Sicoma MAO3000/2000 | 0.118 | 0.0728 (63, C30/37) | 1.62 | CHECK 2 fail (1.62), CHECK 3 fail (1.62); REVIEW kept built (distance 0.620 vs 0.621), flagged; wear share 0.002 % |

Transport and end of life: plywood A4 150 km, 3 % loss, route 55; AAC A4 150 km, 5 % loss, diesel C1, route 9; mycelium A4 EU (1.5 tkm lorry + 0.1 sea), 3 % loss, route 52; concrete A4 bulk 50 km, 5 % loss, diesel A5 and C1, route 8.

Unsure about (details in protocol_issues.md):
- D1 for concrete and AAC hinges on how strictly "extra constituent" is read; the dataset is the same either way.
- Mycelium has no complete three-machine sets: incubation and moulding have no rows, pasteurising and drying are proxies, and the drying values come from a search summary of a PDF I could not read. The result is under- or over-stated by an unknown amount; the heat row is 36 % of it.
- Concrete fails by the same ratio on both routes: the EPD set is mostly low-clinker ECOPact mixes; cement carries ~95 % of our result.
- TiR = 1 for all datasets (time period unreadable); machine life 40,000 h is an assumption.
- W2 for plywood, AAC and mycelium uses fallback classes; the wood recycling dataset is entered with a positive amount.

Files: decisions.csv, dataset_choices.csv, epd_check.csv, cff_inputs.csv, bioc_inputs.csv, LCI_<material>.xlsx; scripts/ holds the code that produced them (read-only on Brightway and ÖKOBAUDAT).
