# Summary, run batch_5

GWP-fossil A1–A3 per kg (EF 3.1, climate change: fossil, Brightway, read-only). Wear (P2 machine) share is below 0.4 % everywhere (limit 2 %). No material was stopped. All files are in `runs/batch_5/`; calculation scripts in `work/`.

**Big caveat:** no machine had a complete datasheet (kW, kg/h, mass) from three manufacturers; most machine values are proxies or assumptions, all marked in `dataset_choices.csv` and `protocol_issues.md`. ÖKOBAUDAT could not be queried, so each median rests on the one EPD PDF I could read.

| Material | Route kept | GWP-fossil A1–A3 | CHECK |
| --- | --- | --- | --- |
| hempcrete | built | 0.646 | no check possible (no ÖKOBAUDAT dataset) |
| gypsum board | built, flagged | 0.352 (approx. match 0.360) | CHECK 2 fail (2.29× median 0.157), CHECK 3 fail (2.24×); REVIEW keeps built |
| toughened glass | built, flagged | 0.547 | CHECK 3 fail (0.40× median 1.384); REVIEW: only route tried |
| PTFE-coated glass fabric | built | 99.7 | no check possible |

## hempcrete
D1 no, D1b no (nothing in ecoinvent). Constituents: hemp hurd (market FR), hydrated lime packed (RER), hydraulic lime (RER), tap water (market group RER). Machines: mixing = 6 ft pan mixer (proxy, 2 of 3 candidates complete); moulding and pressing = WITECH BP-18 biomass press (proxy, TeR 4); air drying: no energy. A4 national 150 km (T2 unclear, lower-impact branch); A5 no machine (piece weight unclear), in situ 5 %; C1 diesel (bonded); NMD category 8. Lime and hemp dominate (hydraulic lime 0.42 of 0.65).

## gypsum board
D1 no (ecoinvent board has extra glass fibre, silicone), D1b yes (market for gypsum plasterboard GLO), CHECK 2 fail → built. Built: mineral gypsum, waste paper, starch as proxy for additives (TeR 4). Steps: calcining (vertical kiln, 190 kcal/kg, vendor figure), mixing and forming (mixer proxy), drying (Watlow low value minus calcining, 4.5 MJ/kg; 0.25 of 0.35 total), cutting (glass cutter proxy). Unsure: dryer mass and throughput are assumptions; one EPD only for the median. A4 national 150 km, 3 % loss, NMD 27 (95 % landfill).

## toughened glass
D1 no, D1b no (no toughened dataset). Built from six batch constituents (all ecoinvent markets). Melting heat 5 MJ/kg (low end of the BREF-type range), tempering furnace Liaoda YD-F-2436 at 0.49 kWh/kg (median of 3, mass not listed → assumed), cutting Toyocc (median of 3), batch mixing mixer proxy. CHECK 3 fails low: no carbonate process CO₂ row exists in the protocol (about 0.17 kg CO₂/kg missing). The EPD is EN 15804+A1, GWP total. A4 national (T2 unclear).

## PTFE-coated glass fabric
D1 no, D1b no. Glass fibre (market GLO) 0.35 and PTFE (market GLO) 0.65. Weaving = generic textile 3.2 kWh/kg (proxy); dip coating and sintering = heat balance (about 2.4 MJ/kg, proxy). A4 EU (T2 no, T3 yes): lorry 1.5 + ship 0.1 tkm. NMD 62 (85 % incineration). 99.7 kg CO₂e/kg is almost all PTFE: please check the input shares.
