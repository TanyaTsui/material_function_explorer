# Protocol issues, batch_7 (glulam, CLT, soft wood fibre board, aluminium extrusion)

Run date 2026-11-19. Each note: step id, what was unclear, what I did.

## P1 · ENERGY (the main one)
- **Three complete datasheets per step were not findable.** For the 10 machine steps of the two built materials I searched for three machines per type with power, throughput and mass. Datasheets almost never give all three: refiners give motor power and capacity but weight only in tonnes; dryers and saws give kW or kg but no throughput in kg/h; ageing ovens and presses give no output. At most one candidate per step was complete (Andritz TX68 refiner). Throughput in kg/h is the missing value for nearly every machine type. The median-of-three rule could not be applied as written.
- **What I did:** used the protocol's own fallback (EU BREF, then studies): EU BREF Wood-based Panels 2016 Table 3.3 for refining and drying (midpoints of the ranges), BREF Table 3.2 MDF pressing for steam-air curing; aluminium-guide.com and an EU CORDIS project for gas billet heating (175–215 kWh/t) and ageing (75–85 kWh/t); the US DOE bandwidth study (2016) for extrusion electricity (derived: 0.196 kWh/kg). Where vendor kW existed (dosing 2.2 kW, saw 13.5 kW) I divided by the line capacity of a 6 t/h dry-process insulation line (Ziegler/Grenzebach). All these rows are marked proxy, TeR 4. For billet heating and ageing I applied the median rule on energy per kg across three sources (not three manufacturers' datasheets). Suggest: let the protocol say explicitly that "energy per tonne" from a BREF or study replaces power ÷ throughput, and that the three-machine rule applies only where datasheets exist.
- **Heat carrier for the aluminium steps.** The usual European billet furnace and ageing oven are gas-fired, so they got heat rows (natural gas, as fixed in the workbook). Induction billet heaters use electricity; both options are logged as candidates. P1 does not say how to choose the carrier when machines of one type use different ones.
- **Double counting risk (aluminium).** The DOE extrusion figure covers the whole plant (press, pumps, stretcher, saw). I used only its electricity share for "extrusion" and wrote no rows for "cutting". The protocol has no rule for a source that covers several steps. The DOE fuel figure (1.7 kWh/kg, US average) is six times the EU gas figures for billet heating plus ageing and was not used.
- **The "extrusion" step is marked "assumption" in the input** (and "drying fibres", "curing with steam-air mixture" for the fibre board). I treated it as any other step.
- **Hydrophobing and "adding resin, forming the mat"** (fibre board): no machine energy source exists for dosing and forming. I used a 2.2 kW dosing unit from a food-industry listing as the closest kind of machine. The forming station (fans) is missing, so these two steps are probably too low. Neither step is marked "no energy" in the input.

## P2 · WEAR
- **Machine mass with throughput found only for the refiner and the dryer** of the fibre board (Andritz TX68, 51.6 t, 1,500 admt/d; VetterTec tube bundle dryer, 36 t, 3,200 kg/h evaporation). The dryer figure is water evaporation, used as kg/h of fibre; a flash tube dryer would differ. All other steps have no wear row (logged). Wear share of the fibre board, 0.033 % of GWP-fossil A1–A3, below the 1–2 % limit in the protocol. For aluminium the share is "not computed" (no wear rows).
- **Machine life.** P2 gives a default of 5,000 h per year but no default for years. I assumed 20 years (100,000 h) and flagged it. Please add a default and a source.
- **Rule conflict.** P2 says never take M from a different machine than the one used for power and throughput. With BREF energy per tonne there is no machine, so the wear machine is by necessity a different one. Logged as proxy.

## D1 / D1b
- **Glulam, D1.** The ecoinvent "average glue mix" has 0.07 % phenolic resin besides MUF and PUR. Read strictly ("an extra constituent is not an exact match"), D1 would be no and D1b yes (same dataset, TeR 2). I answered D1 yes because the adhesive class matches the input (PUR/MUF) and the phenolic share is negligible. The check passes either way, but the answer decides TeR. Suggest a minimum share (e.g. 1 % of mass) below which an extra constituent is ignored.
- **CLT, D1.** Constituents match but the shares differ (ecoinvent MUF about 0.8 %, input MUF 0.03 %). The protocol asks for the same constituents, not shares, so D1 yes.
- **Aluminium, D1b.** The only candidate (section bar extrusion, aluminium) is a process that takes the metal as an input; test 2 ("main constituent of the dataset") has no clear answer. I answered no. A rule for process-only datasets would help.
- **Fibre board.** "Same delivered state" is not decidable for soft fibreboard: ecoinvent mixes wet and dry processes, the input is dry process.

## D2–D4 / D5
- **Units.** ecoinvent wood boards are in m³, the input is in kg. I wrote the amount in m³ = 1 kg ÷ wet mass (property of the dataset: 444, 443, 157.7 kg/m³). The protocol says "kg per kg"; it does not say how to convert. Please state it.
- **D3 and "market" at GLO.** The aluminium wrought-alloy market (GLO) is the only dataset of the alloy besides scrap-only RER datasets. D3 rule 5 gives GLO. This is the whole result for aluminium (12.8 kg CO₂e/kg) and it is far above EPD profiles with high scrap shares. The input has no scrap share for the alloy, so I did not apply the 70–80 % scrap in the EPD; nothing in the protocol says whether to.
- **"PUR resin".** The real binder of the fibre board is pMDI. The ecoinvent PUR dataset is "polyurethane adhesive" (GLO). No rule for choosing between an MDI precursor and the cured resin.
- **Moisture in the fibre amount.** "softwood fibres (fir/spruce) 0.945" has no moisture note while the datasets are "measured as dry mass". I took 0.945 as dry mass unchanged.

## Checks
- **Which EPDs are "in the category".** The OEKOBAU.DAT classes mix products: CLT is under 3.1.04 (BSH) and 3.1.05 (solid wood panel); the aluminium profile class holds façade systems, panels, coated and anodised profiles, and three EMERUS ultra-low-carbon entries with values of 14,277–42,401 (per kg; certainly a unit error). I kept plain profiles and the CLT-type panels and logged the exclusions. The fibre board class has two entries of the same EPD with identical values. Different readers will get different medians. Suggest listing the datasets of each category in the workbook.
- **Release.** The workbook says "latest release; to fill". I used the newest data stock listed by the API, OBD_2024_III. Datasets without EN 15804+A2 were not in that list for the picked classes, so no extra filtering was done (the compliance label was read from the list for each).
- **Review tie.** For the fibre board the two failed routes are 1.701 (built) and 1.704 (approximate) times the median. The built one is closer by 0.003, which is within the uncertainty of the BREF midpoints. The rule keeps the built LCI.
- **CLT ratio 1.44** is just inside the +50 % edge.

## A4 / A5 / C1
- **T2 evidence.** For ES, IT, NL the searches were not exhaustive; "3 of 5" was reached for all four materials with sourced manufacturers. Links are vendor and trade-press pages.
- **I1/X1 piece weights.** No datasheet gave typical piece dimensions: I used the sourced density with an assumed format (glulam, CLT, boards, profiles) and logged that. Outcomes do not depend on the exact format except for aluminium profiles (large structural sections can exceed 50 kg).
- **A5 loss rows.** The protocol says the lost kg gets a lorry row and end-of-life rows; it does not say which block carries them, nor the distance when the route is mixed. I put both in the A5 block, with the route-weighted C2 distance and the C3–C4 datasets, scaled by the loss.
- **X1 "bonded".** Glulam and CLT are not bonded on site, but both are over 50 kg per piece, so X1 is yes.

## C2 / C3–C4 / W1
- **Waste material of a single dataset.** For glulam and CLT the product itself is the waste material (protocol). No such waste dataset exists, so I used the Wood class of waste_fallback (W2) and marked it proxy.
- **Recycling dataset sign.** "treatment of waste wood, post-consumer, sorting and shredding" has a positive reference output (wood chips), so the amount is written positive. A negative amount would give a credit. The protocol says waste has a negative amount; this dataset does not follow that convention.
- **Location of waste datasets.** By the D3 order the Swiss datasets (CH) win over GLO and RoW; the "municipal incineration FAE" activities are Swiss-specific. Aluminium incineration has a Europe-without-Switzerland dataset, so that one was taken.
- **W1 "market for waste" only if it splits like NMD** — no such market was used.
- **"adhesive, PUR/MUF" and "PUR resin".** There is no "waste adhesive". For the fibre board PUR resin I used waste polyurethane (W1); for the glulam and CLT the waste is the whole product (above).
- **Reuse (5 % for glulam and CLT)** gets no row, as the protocol says.

## Module D files
- `bioc_inputs.csv` moisture: only where the input note gives it (glulam 11.5/86.9 = 0.1323, CLT 10.70/88.28 = 0.1212, dry basis). The glulam note says "atro 86.9 % + water 11.5 %"; the sum is 98.4 %, so moisture of dry basis is the ratio.
- For the fibre board the dataset (kept LCI is built) means the waste items are constituents, so wood fibre, PUR resin and paraffin are listed separately.
