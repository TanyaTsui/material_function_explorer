# Protocol issues: run_B (13 Nov 2026)

Each note gives the step id, what was unclear, and what this run did.

## Setup and A1–A3

**S1: median of several EPDs, per constituent or per EPD?** (OSB, hempcrete)
Medians taken per constituent do not sum to 1. For OSB they summed to 1.003. The run took the median per constituent and normalised to 1. The protocol should say whether to take the median EPD instead, or to normalise.

**S1: compositions given as ranges.** (hempcrete, OSB/Sonae)
Both hemp-block EPDs give only ranges: Schönthaler gives 20–55 % shiv and 45–80 % binder, IsoHemp gives 35–45 / 8–15 / 40–55 kg. The run used range midpoints, so the binder share (0.569) rests on that choice. The protocol could say "midpoint of a range", or move to the next source in the search order when an EPD gives only ranges.

**S1: where does residual water go?** (hempcrete)
"Moisture counts with the constituent it is in" does not say which constituent holds the water in a hemp-lime block. Schönthaler puts it in the shives, so the run did the same for IsoHemp's 16.2 kg remainder. The water then carries the hemp-hurd burden (about 0.06 kg CO₂e/kg).

**S1: different binder detail across EPDs.** (hempcrete)
Schönthaler gives one "lime-containing binder" with an unquantified hardener. IsoHemp gives air lime and NHL separately. The run split the binder using IsoHemp's ratio, the only source that splits it.

**S1: the ÖKOBAUDAT dataset has no composition table.** (cork, and the Thünen OSB dataset)
The run went on to the next registry (EPD Hub, Amorim HUB-0281). For OSB it did not open the Thünen Excel annex.

**D1: matching for a finished product.** (OSB)
The test was applied at the level of constituent classes: wood, resin binder, wax/additives. EGGER uses pMDI+MUF while ecoinvent uses MDI only, which was judged "same constituents". If D1 has to match the binder chemistry, the answer would flip to D5.

**D3: Portugal is not in the country list.** (cork, raw cork PT)
The single-country list (DE, FR, IT, ES, NL, AT, SE, FI, PL, CH) leaves out PT, so a strict reading puts RoW before PT. The run took PT as "a single European country", following the intent of "a single European country comes before GLO". Please add PT, or make the rule "any European country".

**D2/D3: the only market is GLO and almost all non-European.** (plaster mixing, wood chipping)
`market for plaster mixing` GLO is 99 % RoW supply and scores 0.055 kg CO₂e/kg, against 0.0022 for the CH production. D2 (market first) and then D3 (location of the market) lead to the GLO market. That respects "never use global market *groups*" but breaks its spirit. The run used the GLO market, which is also the conservative choice. Should D3 compare locations across market *and* production datasets?

**D2: some markets carry no transport.** (hydraulic lime)
`market for hydraulic lime` RER says transport is "considered irrelevant" and has no transport exchange. Because D2 = yes, no A2 row was added, and A2 is effectively zero for that row.

**D4: A–Z gives an odd lorry.** (A4/A5/C2 lorry)
RER has 16 size-class × EURO-class lorry markets plus `unspecified`. A–Z would pick "16–32 t, EURO 3". The run treated `transport, freight, lorry, diesel, unspecified` as the exact D1 match for "lorry" (no size or EURO class), so D4 was not needed. Please name the lorry dataset in the protocol.

**D5: no processing dataset, and the alternatives include material.** (hempcrete pressing, cork autoclave expansion)
- *Hempcrete pressing:* candidates were rejected because they include the material (`concrete block production`) or are hot, per-cycle processes (`compression of sheet moulding compound`, `stamping …`). The run logged "unclear" and took the conservative branch: a second `plaster mixing` row.
- *Cork autoclave/steam:* no dataset or source gives steam per kg. The run applied rule 2 (similar operation, same material) by copying the processing-energy exchanges of `cork slab production`: 4.92 MJ wood-chip heat and 1 kWh electricity per kg, leaving out its cork and resin inputs. The protocol does not say whether "closest processing dataset" may be the energy exchanges of a product dataset.
- *Yield:* the yield (1.06 kg raw cork per kg) was taken from that same dataset.

**D5: steps with no energy input.** (air drying, stabilisation, cooling, palletising/packing)
The rule says every step gets a dataset, but some steps use no energy: hemp blocks are air dried, and cork stabilisation is stated to need no energy. The run wrote no row and logged each one. Packaging was left out for all three materials; for OSB it sits inside the ecoinvent dataset, which is inconsistent.

**ROW: what TeR do constituent rows of a built material get?** (hempcrete, cork)
The table gives "D5 built = 3", but each constituent also passes D1 as an exact match (1). The run gave constituent rows TeR 3 and step proxies TeR 4.

**ROW: TiR cannot be read from Brightway.** (all)
The Brightway import keeps no `time period` field. The run used the "Time period:" text in the dataset or main supplier comment if present. Otherwise it used the latest year cited in the documentation, and if there was none it logged "unclear" and gave TiR 5 (conservative). This makes TiR noisy and probably too pessimistic, for example for RER electricity. A fixed lookup or the ecoSpold time period would be better.

**CHECK: units of the material rows.**
For cork, the 1.06 kg row is 1 ÷ yield. For OSB the row is in m³, and the check used the dataset's wet density (0.00165 m³ × 607 = 1.00 kg). Rounding to 3 significant figures leaves a 0.16 % mass error on the OSB row.

## STEP 3

**Which density for the EPD?** (hempcrete)
The ÖKOBAUDAT flow of the 430 kg/m³ Schönthaler dataset lists 405 kg/m³, which looks like a data error. The run used 430, from the declared unit. It does not change the result.

**Targeted check: what counts as "shown wrong"?** (hempcrete)
None of the four items found a provable error, so the material is flagged. The two largest uncertainties are not on the checklist: the binder share chosen within the EPD's 45–80 % range, and the GLO mixing proxy. Neither could be corrected without "moving toward the median".

**Only one or two datasets per category.**
Hempcrete has one producer (2 datasets) and cork has one generic dataset (expanded cork, described as "cork flour" production, which may not be board). With one producer the ±50 % band says little.

## A4, A5, C

**A4 · T2: how strong must the evidence be?**
Several manufacturer findings come from search-result excerpts, not from opened pages: Swiss Krono FR, I-PAN IT, Vieille Matériaux FR, Cannabric ES, Agglolux FR. Cannabric's current production was not confirmed. The protocol could ask for an EPD or a manufacturer page per country.

**A5 · L1 and C1 · X1: the same product can be glued or dry-fixed.** (cork)
Cork boards are screwed in the EPD scenario but glued in ETICS. The run followed the EPD scenario (no / no).

**C2 · E1: does "masonry" name hemp blocks?** (hempcrete)
Category 8 names "masonry", and hemp blocks are used as masonry. The category is concrete masonry, though. The run logged "unclear"; both branches lead to 1/0/99/0 (via the heaviest constituent, lime → category 8 or 40). The EPD says the blocks cannot be landfilled and models incineration, so NMD's 99 % recycling as concrete aggregate is doubtful for a 43 % organic material.

**C3–C4: D2 for waste rows.** (all)
Waste "markets" in ecoinvent mix treatment routes, which conflicts with using NMD shares. The run used the route-specific treatment datasets (D2 = no) and logged this on every waste row.

**C3–C4: recycling of wood under cut-off.** (OSB)
There is no "treatment of waste wood, recycling". The run used `market for waste wood, post-consumer, measured as dry mass` RER, which is a zero-burden cut-off pass-through plus its own transport. That transport double-counts the C2 lorry, and the dataset is per kg *dry* mass (the run converted with 581.7/607).

**C3–C4: D3 picks CH "FAE" incineration over the GLO dataset.** (OSB, cork)
`treatment of waste wood, untreated, municipal incineration` exists only as GLO and as CH "FAE". D3 puts CH first.

**C1 default and NMD revision.**
The NMD Nov 2026 revised end-of-life scenarios were not read; the protocol says to check them before freezing.
