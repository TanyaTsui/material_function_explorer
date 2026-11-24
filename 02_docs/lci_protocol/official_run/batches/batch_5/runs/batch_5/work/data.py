# Run data for batch_5 (hand-collected decisions + machine values). Every number is traced in the logs written by build.py.
DATE = "2026-11-19"
RUN = "batch_5"

ELEC = ("market group for electricity, medium voltage", "RER", "electricity, medium voltage")
HEAT = ("market for heat, district or industrial, natural gas", "Europe without Switzerland", "heat, district or industrial, natural gas")
MACH = ("market for industrial machine, heavy, unspecified", "RER", "industrial machine, heavy, unspecified")
LORRY = ("market for transport, freight, lorry, unspecified", "RER", "transport, freight, lorry, diesel, unspecified")
SEA = ("market for transport, freight, sea, container ship, heavy fuel oil", "GLO", "transport, freight, sea, container ship, heavy fuel oil")
DIESEL = ("diesel, burned in building machine", "GLO", "diesel, burned in building machine")

L_DEF = 75000  # h = assumed 15 years x 5000 h/yr (life in years not on any datasheet found)

# ---------------- machine library (values as found) ----------------
MIX_LINK = "https://www.indianyellowpages.com/ahmedabad/pan-mixer-machine.htm"
MIXER = dict(
    machine_type="pan / forced-action mixer (proxy for mixing)",
    candidates=("(1) 6 ft pan mixer, typical specs, 10-15 HP, 500-750 kg/batch, 1200-1800 kg [indianyellowpages.com]; "
                "(2) Liebherr R 1.0 ring-pan mixer, 37 kW, 1500 l, 4300 kg [liebherr.com/en-at/p/85732-5915835]; "
                "(3) Eirich R09 150 l / 240 kg max: no power or mass on the datasheet pages found, not used"),
    used="6 ft pan mixer (lower kWh/kg of the two complete candidates; only 2 of 3 complete)",
    power_kW=12.5 * 0.7457, throughput=625 / 0.05, M=1500.0, L=L_DEF,
    found="12.5 HP (mid of 10-15 HP); 625 kg/batch (mid of 500-750); 1500 kg (mid of 1200-1800); cycle time 3 min incl. loading = ASSUMPTION (not on datasheet)",
    link=MIX_LINK,
    conv="kW = 12.5 HP x 0.7457 = 9.32; kg/h = 625 kg / 0.05 h = 12,500; kWh/kg = 9.32/12,500",
    proxy=True,
)
PRESS = dict(
    machine_type="biomass block press (proxy for moulding and pressing of hemp-lime blocks)",
    candidates=("(1) WITECH BP-18 biomass block press, 27 kW (40 HP), 1200 kg/h, 7 t [slideshare.net/slideshow/biomass-block-press-witech-bp-18/17990693]; "
                "(2) Hydraform block machine 7.5 kW, 200 blocks/h: no kg/h or mass given, not used; "
                "(3) Hydraform 11 kW, 400 blocks/h: no kg/h or mass, not used"),
    used="WITECH BP-18 (only machine with kW, kg/h and mass)",
    power_kW=27.0, throughput=1200.0, M=7000.0, L=L_DEF,
    found="27 kW (40 HP); 1200 kg/h guaranteed; 7 tons", link="https://www.slideshare.net/slideshow/biomass-block-press-witech-bp-18/17990693",
    conv="kWh/kg = 27/1200 = 0.0225", proxy=True,
)
CALC = dict(
    machine_type="gypsum calcining kiln (vertical kiln / horizontal kiln / mill-calciner)",
    candidates=("(1) vertical kiln, <190 kcal/kg plaster, 6-18.5 t/h [alphaplatre-france.com/platre/?lang=en]; "
                "(2) horizontal two-tube kiln, 260 kcal/kg plaster, 14-16 t/h [same page]; "
                "(3) Grenzebach rotary kiln / roller mill / Claudius Peters horizontal impact calciner: capacities only (up to 100 t/h), no energy, no mass in sources found"),
    used="vertical kiln (lower heat per kg of the two with energy data)",
    power_kW=None, throughput=15000.0, M=50000.0, L=L_DEF,
    found="heat <190 kcal/kg plaster; mill drive 2.5-5.5 kWh/t (Pfeiffer, mid 4 kWh/t); throughput 14-16 t/h of the horizontal kiln (mid 15 t/h) used for P2; machine mass 50 t = ASSUMPTION (a supplier table lists rotary kilns ~47.5-52 t, garbled)",
    link="https://www.alphaplatre-france.com/platre/?lang=en",
    conv="190 kcal x 4.1868 = 795 kJ = 0.795 MJ/kg; 4 kWh/t = 0.004 kWh/kg",
    elec_per_kg=0.004, heat_per_kg=0.795, proxy=True, fallback="vendor/plant figures (no machine datasheet with kW)",
)
DRYER = dict(
    machine_type="plasterboard dryer (multi-deck belt dryer)",
    candidates=("(1) gas-fired gypsum board plants 5,275-10,550 MJ per t of board (whole-plant) [Watlow white paper, 2025]; "
                "no dryer datasheet with kW / kg/h / mass found for 2 further manufacturers"),
    used="Watlow low value minus the calcining share (benefit of the doubt)",
    power_kW=None, throughput=15000.0, M=200000.0, L=L_DEF,
    found="5,275 MJ/t board (low end); calcining share 0.93 x 0.795 = 0.739 MJ/kg removed to avoid double counting; dryer mass 200 t and throughput 15 t/h = ASSUMPTIONS",
    link="https://www.watlow.com/-/media/documents/white-papers/wp_-electrifying-gypsum_eu_0725.ashx",
    conv="5.275 - 0.739 = 4.536 MJ/kg board", heat_per_kg=4.536, elec_per_kg=0.0, proxy=True, fallback="study/industry figure",
)
CUT_GL = dict(
    machine_type="automatic CNC glass cutting line",
    candidates=("(1) EVOMATEC EVOGLAS QUADRO, up to 24 kW, 120 m/min, 8,500 kg (largest model) [evomatec.de]; "
                "(2) Toyocc CNC cutting line, 11.8 kW, 0-180 m/min, 3,000 kg [toyocc.en.made-in-china.com]; "
                "(3) Perfect Laser PEG-7015, 8 kW, 0-180 m/min, ~3 t [directindustry.com]"),
    used="Toyocc (median kWh/kg of the three)",
    power_kW=11.8, throughput=180 * 450.0, M=3000.0, L=L_DEF,
    found="11.8 kW installed; 180 m/min cutting speed; 3000 kg. Mass throughput = ASSUMPTION: 2 m of cut per m2 of glass, 6 mm glass = 15 kg/m2, so kg/h = m/min x 60 / 2 x 15 = 450 x m/min",
    link="https://toyocc.en.made-in-china.com/product/WwfAGaYlaeVb/China-Advanced-Smart-CNC-Glass-Cutting-Line-with-Automated-Loading-Cutting-and-Unloading.html",
    conv="kg/h = 180 x 450 = 81,000; kWh/kg = 11.8/81,000 (EVOMATEC 24/54,000 = 4.4e-4; PEG-7015 8/81,000 = 9.9e-5)",
    proxy=False,
)
CUT_GY = dict(CUT_GL)
CUT_GY.update(machine_type="board cutting (proxy: automatic cutting line, glass cutting machine data)",
              throughput=15000.0,
              found="11.8 kW installed, 3000 kg (Toyocc glass cutting line); throughput = plasterboard line 15 t/h = ASSUMPTION (cut at line speed)",
              conv="kWh/kg = 11.8/15,000", used="Toyocc glass cutting line as proxy for board cutting", proxy=True,
              candidates="no plasterboard cutter datasheet found; proxy = glass cutting line (see toughened glass)")
FORM = dict(MIXER)
FORM.update(machine_type="board forming line (proxy: pan mixer data, low-power conveying/forming)",
            used="6 ft pan mixer data as proxy (no forming-line datasheet found)",
            candidates="no gypsum board forming-line datasheet with kW, kg/h and mass found; proxy = mixer",
            proxy=True)
MELT = dict(
    machine_type="float glass melting furnace",
    candidates=("(1) BREF/IPPC figure for flat glass: 5-8.5 GJ/t melted glass (Beerkens & van Limpt 2001, via IPCC AR4 7.4.5.3); "
                "no manufacturer datasheets (kW, kg/h, mass) for furnaces found for further candidates"),
    used="low end of the BREF range (benefit of the doubt)",
    power_kW=None, throughput=650000 / 24.0, M=2000000.0, L=18 * 8760,
    found="5 GJ/t = 5 MJ/kg heat; throughput 650 t/day (average European float line, Glass for Europe); life 16-20 yr, 24/7 (mid 18 yr x 8760 h); machine mass 2,000 t = ASSUMPTION (furnace holds ~2,000 t of molten glass; refractory mass assumed of the same order)",
    link="https://archive.ipcc.ch/publications_and_data/ar4/wg3/ch7s7-4-5-3.html ; https://glassforeurope.com/?p=44721",
    conv="5 GJ/t / 1000 = 5 MJ/kg; kg/h = 650,000/24 = 27,083; L = 157,680 h",
    elec_per_kg=0.0, heat_per_kg=5.0, proxy=False, fallback="EU BREF / industry benchmark",
)
TEMPER = dict(
    machine_type="flat glass tempering furnace",
    candidates=("(1) Glaston HTF, 884 kW installed (464 heating+drive, 430 blowers), 112 m2/h at 6 mm [machineseeker listing]; "
                "(2) Liaoda YD-F-2436, 536 kW heating + 305 kW blowing = 841 kW, 114 m2/h [liaodaglassmachine.en.made-in-china.com]; "
                "(3) Liaoda 1584 kW heating + 235 kW blowing, 297 m2/h [same product range]. kWh/kg at 15 kg/m2: 0.526 / 0.492 / 0.408. None lists a net machine mass."),
    used="Liaoda YD-F-2436 (median kWh/kg)",
    power_kW=841.0, throughput=114 * 15.0, M=40000.0, L=L_DEF,
    found="841 kW installed (not running power); 114 m2/h, thickness basis 6 mm (15 kg/m2) = ASSUMPTION (not stated for this model); net mass NOT listed (package gross 999 kg) -> 40 t = ASSUMPTION (furnace length 19.7 m)",
    link="https://liaodaglassmachine.en.made-in-china.com/product/kJCUNnMAuQrG/China-Yd-F-2436-Window-Applicable-Convection-Type-Flat-Glass-Tempering-Machine.html",
    conv="kg/h = 114 m2/h x 15 kg/m2 = 1,710; kWh/kg = 841/1,710 = 0.492",
    proxy=False,
)
WEAVE = dict(
    machine_type="air-jet / rapier loom (weaving glass fabric)",
    candidates=("no loom datasheet with kW, kg/h and mass found (Rifa RFJA32/RFRL30, Itema R9500, Dornier P2, SMIT: width and speed only); "
                "study value: air-jet weaving 3.2 kWh/kg fabric [fibre2fashion.com/industry-article/7956]"),
    used="generic textile weaving energy (proxy)",
    power_kW=None, throughput=8.0, M=3000.0, L=L_DEF,
    found="3.2 kWh/kg fabric (generic air-jet, textile); loom mass 3,000 kg and throughput 8 kg/h of glass fabric = ASSUMPTIONS",
    link="https://www.fibre2fashion.com/industry-article/7956/submitArticleLink",
    conv="kWh/kg = 3.2 as published", elec_per_kg=3.2, heat_per_kg=0.0, proxy=True, fallback="study (generic textile)",
)
# dip coating & sintering: bottom-up calculation
_water = 0.65 * (0.4 / 0.6)
_heat_useful = _water * (4.19 * 80 + 2257) / 1000 + (0.65 * 1.0 + 0.35 * 0.8) * 360 / 1000  # MJ
COAT = dict(
    machine_type="dip-coating line with IR/gas sintering tower oven",
    candidates=("no oven/line datasheet with kW, kg/h and mass found (Radiant Energy Systems 21 ft gas-IR tower oven: dimensions only; Monforts: up to 320 C for PTFE); "
                "bottom-up heat balance used"),
    used="heat balance of the coating (proxy)",
    power_kW=None, throughput=50.0, M=5000.0, L=L_DEF,
    found=("PTFE dispersion assumed 60 %% solids -> 0.433 kg water per kg product; evaporate from 20 C: 0.433 x (4.19x80+2257) kJ = %.0f kJ; heat solids to 380 C: (0.65x1.0+0.35x0.8) kJ/kgK x 360 K = %.0f kJ; "
           "oven efficiency 60 %% (upper end of the 40-60 %% IR-oven claim); several passes ignored (lower impact); line mass 5 t and 50 kg/h = ASSUMPTIONS") % (_water * (4.19 * 80 + 2257), (0.65 * 1.0 + 0.35 * 0.8) * 360),
    link="https://www.textileworld.com/textile-world/new-products/2013/09/new-gas-infrared-tower-oven-for-ptfe-coatings-on-fiberglass/",
    conv="useful heat %.3f MJ / 0.60 = %.3f MJ per kg product (natural gas heat)" % (_heat_useful, _heat_useful / 0.6),
    elec_per_kg=0.0, heat_per_kg=_heat_useful / 0.6, proxy=True, fallback="calculation",
)

# ---------------- material definitions ----------------
# constituent: (input name, amount, activity name, location, reference product, rule, TeR, proxy flag/note, search terms, candidates)
# step: (input name, kg processed, machine dict, mode) mode: 'machine' | 'noenergy'
MATERIALS = {}

MATERIALS["hempcrete"] = dict(
    name="hempcrete",
    constituents=[
        ("hemp shiv", 0.342, "market for hemp hurd", "FR", "hemp hurd", "D5/PICK: market, only location FR", 1, "",
         "hemp; hemp hurd", "market for hemp hurd FR; hemp hurd production (decorticated fibre production, hemp FR)"),
        ("air lime", 0.108, "market for hydrated lime, packed", "RER", "hydrated lime, packed", "D5/PICK: market, RER (D3 rank 2)", 1, "",
         "hydrated lime; lime --field product", "market for hydrated lime, packed RER; hydrated lime, loose (CH, RoW only)"),
        ("natural hydraulic lime", 0.422, "market for hydraulic lime", "RER", "hydraulic lime", "D5/PICK: market, RER (D3 rank 2)", 1, "",
         "hydraulic lime", "market for hydraulic lime RER, RoW"),
        ("water", 0.128, "market group for tap water", "RER", "tap water", "D5/PICK: market group, RER (D3 rank 1)", 1, "",
         "tap water", "market group for tap water RER/GLO; market for tap water Europe without Switzerland; water, deionised"),
    ],
    steps=[("mixing", 1.0, MIXER, "machine"), ("moulding and pressing", 1.0, PRESS, "machine"),
           ("air drying and curing", 1.0, None, "noenergy")],
    t1=("no", "Blocks are discrete units (IsoHemp thin-joint blocks), not loose or ready-mixed.", "https://naturamater.eu/en/ecosystem/materials/hemp-block-isohemp"),
    t2=("unclear", "Hemp-lime blocks: IsoHemp is Belgian (Namur), Vicat Biosys hemp blocks are French; a market report lists further hemp firms in DE and IT but not as block makers. 3 of DE/FR/IT/ES/NL not shown -> unclear, lower-impact branch (national, 150 km).",
        "https://www.isohemp.com/en/our-story"),
    t3=None, archetype="national",
    i1=("unclear", "Piece weight not stated (no length/height on source); 36 cm block at 320 kg/m3, estimated 60 x 25 cm face = about 17 kg, well under 50 kg; not poured -> no row (unclear -> lower impact).",
        "https://naturamater.eu/en/ecosystem/materials/hemp-block-isohemp"),
    i1_yes=False,
    l1=("yes", "Blocks are laid as thin-joint masonry with 3 mm joints of lime-based IsoHemp adhesive mortar: in situ -> 5 %.", "https://naturamater.eu/en/ecosystem/materials/hemp-block-isohemp"),
    w=0.05,
    x1=("yes", "Blocks are bonded with adhesive mortar -> machine demolition, diesel row.", "https://naturamater.eu/en/ecosystem/materials/hemp-block-isohemp"),
    x1_yes=True,
    nmd_cat="8 concrete, masonry, reinforced concrete", shares=dict(landfill=1, incineration=0, recycling=99, reuse=0),
    cff="Mineral, crushed to aggregate", carbon={"hemp shiv": "Cellulose fibres and stalks", "air lime": "Non-biogenic", "natural hydraulic lime": "Non-biogenic", "water": "Non-biogenic"},
    d1=("no", "No hempcrete / hemp-lime block dataset in ecoinvent 3.12 cut-off (searches 'hempcrete', 'hemp': only hemp fibre, hurd and stem production).", ""),
    d1b=("no", "No dataset of the finished product exists, so no approximate match either.", ""),
    epd=None,
)

MATERIALS["gypsum_board"] = dict(
    name="gypsum board",
    constituents=[
        ("gypsum (calcined, from natural / FGD gypsum)", 0.93, "market for gypsum, mineral", "RER", "gypsum, mineral",
         "D5/PICK: market, RER; calcining is a listed step so gypsum enters as mineral gypsum", 1, "", "gypsum --field product; stucco",
         "market for gypsum, mineral RER/IN/RoW/ZA; market for stucco GLO (already calcined, would double count the calcining step)"),
        ("recycled paper liner", 0.035, "market for waste paper, sorted", "GLO", "waste paper, sorted", "D5/PICK: market, only location GLO", 1, "",
         "waste paper; paper", "market for waste paper, sorted GLO (used by ecoinvent gypsum fibreboard); market for paper, newsprint/woodfree (virgin)"),
        ("mineral additives and chemicals (starch, foaming agent)", 0.035, "market for potato starch", "GLO", "potato starch",
         "PROXY: closest listed additive (starch); no dataset for the mixed additive", 4, "proxy",
         "starch; foaming agent; alkylbenzene sulfonate", "market for potato starch GLO (starch part); market for alkylbenzene sulfonate (foaming agent, not chosen)"),
    ],
    steps=[("calcining gypsum to stucco", 0.93, CALC, "machine"), ("mixing slurry", 1.0, MIXER, "machine"),
           ("forming on the line", 1.0, FORM, "machine"), ("drying boards", 1.0, DRYER, "machine"),
           ("cutting", 1.0, CUT_GY, "machine")],
    t1=("no", "Plasterboard is delivered as boards (discrete pieces).", "https://www.knauf.com/de-DE/p/produkt/bauplatte-lowr-gkb-12-5-33696_0010"),
    t2=("yes", "Plasterboard plants in FR (Saint-Gobain Placo, Vaujours), DE (Siniat Hartershofen; BV Gips EPD covers Danogips/Knauf/Rigips products) and ES (Saint-Gobain Placo, Ebro Gelsa).",
        "https://globalgypsum.com/magazine/articles/805-gypsum-in-north-west-europe"),
    t3=None, archetype="national",
    i1=("no", "12.5 mm board 8.9-10 kg/m2 (Knauf LOWR 8.9; BVG EPD 10 kg/m2); a 2.5 x 1.25 m board is about 28 kg, under 50 kg.", "https://knauf.com/de-DE/p/produkt/bauplatte-lowr-gkb-12-5-33696_0010"),
    i1_yes=False,
    l1=("no", "Prefab boards fixed dry with screws; joint filler is an auxiliary and not the board itself -> 3 %.", ""),
    w=0.03,
    x1=("no", "Boards are screwed to studs, not cast or bonded, and under 50 kg per piece -> taken apart by hand.", ""),
    x1_yes=False,
    nmd_cat="27 gypsum", shares=dict(landfill=95, incineration=0, recycling=5, reuse=0),
    cff="Gypsum", carbon={"gypsum (calcined, from natural / FGD gypsum)": "Non-biogenic", "recycled paper liner": "Cellulose fibres and stalks",
                          "mineral additives and chemicals (starch, foaming agent)": "Non-biogenic"},
    d1=("no", "ecoinvent 'gypsum plasterboard' (market GLO; production CH/RoW) contains stucco 0.811 plus corrugated board, glass fibre 1.6e-4, silicone 1.3e-4, starch, alkylbenzene sulfonate, tap water: extra constituents (glass fibre, silicone) that the input does not list -> not an exact match.", ""),
    d1b=("yes", "Same product and delivered state (gypsum plasterboard); main constituent stucco/gypsum in both. Differences: dataset has extra glass fibre (0.016 %), silicone (0.013 %), surfactant (1e-5), corrugated board 4.8 % instead of recycled paper 3.5 %, starch 0.29 % vs additives 3.5 %.", ""),
    approx=("market for gypsum plasterboard", "GLO", "gypsum plasterboard"),
    epd=dict(release="not verified (ÖKOBAUDAT blocked; EPD read from PDF)", category="Gypsum plasterboard (DIN EN 520 / DIN 18180)",
             ids="EPD-BVG-20210344-IBE1-EN (BV Gips, IBU, EN 15804+A2, valid to 3 Apr 2027)", n=1, median=1.57 / 10.0,
             note="GWP-fossil A1-A3 1.57 kg CO2e per m2 = 10 kg -> 0.157 per kg; only this one EPD read; other board EPDs (Knauf, Siniat, Rigips) not read",
             link="https://www.sentinel-holding.eu/Kunden/Danogips%20GmbH%20%26%20Co.%20KG/Produktunterlagen/DANO%C2%AE%20Bauplatten%20%28A-GKB%29/EPD%20DANO%20A-GKB_2022-04-en.pdf"),
)

MATERIALS["toughened_glass"] = dict(
    name="toughened glass",
    constituents=[
        ("silica sand", 0.577, "market for silica sand", "GLO", "silica sand", "D5/PICK: market, only location GLO", 1, "", "silica sand", "market for silica sand GLO"),
        ("soda ash", 0.177, "market for soda ash, light", "RER", "soda ash, light", "D5/PICK: market, RER; D4 light before dense (GLO)", 2, "", "soda ash", "market for soda ash, light RER/RoW; market for soda ash, dense GLO"),
        ("dolomite", 0.151, "market for dolomite", "RER", "dolomite", "D5/PICK: market, RER", 1, "", "dolomite", "market for dolomite RER/RoW"),
        ("chalk (limestone)", 0.047, "market for limestone, crushed, for mill", "CH", "limestone, crushed, for mill", "D5/PICK: market, CH (D3 rank 4, before RoW)", 1, "",
         "limestone, crushed; chalk", "market for limestone, crushed, for mill CH/CA/IN/RoW; limestone, milled (production Europe w/o CH)"),
        ("cullet", 0.035, "market for glass cullet, sorted", "RER", "glass cullet, sorted", "D5/PICK: market, RER", 1, "", "cullet; waste glass", "market for glass cullet, sorted RER/RoW"),
        ("sulphate", 0.009, "market for sodium sulfate, anhydrite", "RER", "sodium sulfate, anhydrite", "D5/PICK: market, RER (sulphate taken as sodium sulphate)", 2, "", "sodium sulfate", "market for sodium sulfate, anhydrite RER/RoW"),
    ],
    steps=[("batch mixing", 1.2, MIXER, "machine"), ("float glass melting", 1.0, MELT, "machine"),
           ("cutting", 1.0, CUT_GL, "machine"), ("tempering", 1.0, TEMPER, "machine")],
    t1=("no", "Glass panes are discrete pieces.", ""),
    t2=("unclear", "Float/tempering sites named: DE (Schollglas; AGC SGT Oelsnitz) and ES (Tvitec/Cricursa); an Italian tempering firm is mentioned but not named; FR and NL not shown. Unclear -> lower-impact branch (national, 150 km).",
        "https://www.glassonweb.com/directory/cat/glass-fabricators-flat-glass-processing/tempered-safety-glass?page=28"),
    t3=None, archetype="national",
    i1=("no", "Typical architectural pane 1-3 m2 x 15 kg/m2 (6 mm) = 15-45 kg, under 50 kg (large panes exist; typical piece used).", ""),
    i1_yes=False,
    l1=("no", "Prefab glazing placed in frames, not made in situ -> 3 %.", ""),
    w=0.03,
    x1=("no", "Glazing is removed by hand per pane (typical pane under 50 kg).", ""),
    x1_yes=False,
    nmd_cat="28 flat glass", shares=dict(landfill=30, incineration=0, recycling=70, reuse=0),
    cff="Flat glass", carbon={k: "Non-biogenic" for k in ["silica sand", "soda ash", "dolomite", "chalk (limestone)", "cullet", "sulphate"]},
    d1=("no", "ecoinvent has 'flat glass, uncoated' and a separate 'tempering, flat glass' process but no toughened safety glass product.", ""),
    d1b=("no", "No finished-product dataset in the toughened delivered state (uncoated flat glass is not tempered): delivered state differs.", ""),
    epd=dict(release="not verified (ÖKOBAUDAT blocked; EPD read from PDF)", category="Flat glass, toughened safety glass (ESG)",
             ids="M-EPD-FEV-002000 (BV Flachglas, 18 Dec 2017; EN 15804+A1, not A2)", n=1, median=3.46 / 2.5,
             note="GWP total A1-A3 3.46 kg CO2e per m2 per mm; 2.5 kg/m2/mm (density 2500) -> 1.384 per kg; EPD gives GWP total, no fossil split (biogenic assumed ~0)",
             link="https://www.oekobaudat.de/OEKOBAU.DAT/resource/sources/104410c7-6ed5-441a-8735-14b8d8cc0fbd/2020-07-16_BV-FG_M-EPD_FG_ESG_VSG.pdf?version=00.00.010"),
)

MATERIALS["ptfe_coated_glass_fabric"] = dict(
    name="PTFE-coated glass fabric",
    constituents=[
        ("glass fibre yarn", 0.35, "market for glass fibre", "GLO", "glass fibre", "D5/PICK: market, only location GLO", 1, "", "glass fibre; glass fabric", "market for glass fibre GLO; glass fibre production RER/RoW"),
        ("PTFE dispersion (solids)", 0.65, "market for polytetrafluoroethylene", "GLO", "polytetrafluoroethylene",
         "D5/PICK: market, only location GLO (solids taken as PTFE polymer)", 1, "", "polytetrafluoroethylene; ptfe", "market for polytetrafluoroethylene GLO; production, emulsion polymerization GLO"),
    ],
    steps=[("weaving glass fabric", 0.35, WEAVE, "machine"), ("dip coating and sintering", 1.0, COAT, "machine")],
    t1=("no", "Delivered as rolls/panels, not in bulk.", ""),
    t2=("no", "Only Germany shown as a producer/fabricator (Verseidag-Indutex membranes, Ceno Tec Greven); FR/IT/ES/NL not found.", "https://www.archiexpo.com/prod/verseidag-indutex/product-61073-922390.html"),
    t3=("yes", "Verseidag-Indutex (Germany) makes PTFE-glass architectural membrane B 18039; Fiberflon AS (Norway, EFTA) is a PTFE glass-fabric maker.", "https://archiexpo.com/prod/verseidag-indutex/product-61073-922390.html"),
    archetype="eu",
    i1=("unclear", "Roll dimensions not found; 1.31 kg/m2 (Sheerfill II) -> a 50 m x 2.5 m roll would be ~160 kg, but typical piece not verified: unclear -> lower impact, no row.",
        "https://materials.oneclicklca.com/en/material/woven-fiberglass-membrane-with-ptfe-coating-catenary-clamping-installation/5e24b19e8e202b056bbf487a"),
    i1_yes=False,
    l1=("no", "Prefab membrane panels, tensioned and clamped, not made in situ -> 3 %.", ""),
    w=0.03,
    x1=("no", "Clamped / mechanically fixed, not cast or bonded; taken apart by hand.", ""),
    x1_yes=False,
    nmd_cat="62 PVC films, roofing", shares=dict(landfill=10, incineration=85, recycling=5, reuse=0),
    cff="Coated fabrics and composites", carbon={"glass fibre yarn": "Non-biogenic", "PTFE dispersion (solids)": "Non-biogenic"},
    d1=("no", "No PTFE-coated glass fabric / architectural membrane in ecoinvent 3.12 cut-off (searches: glass fabric, ptfe, polytetrafluoroethylene, fabric --field product).", ""),
    d1b=("no", "No finished-product dataset, so no approximate match.", ""),
    epd=None,
)

# ---------------- waste treatment mapping (W1 / W2) ----------------
# key: (constituent, route) -> (rule, activity name, ref product)
W = {
 "wood_landfill": ("W2", "treatment of waste wood, untreated, sanitary landfill", "waste wood, untreated"),
 "wood_recycling": ("W2", "treatment of waste wood, post-consumer, sorting and shredding", "wood chips, from post-consumer wood, dry, measured as dry mass"),
 "min_landfill": ("W2", "treatment of inert waste, inert material landfill", "inert waste, for final disposal"),
 "min_recycling": ("W2", "treatment of waste reinforced concrete, recycling", "waste reinforced concrete"),
 "gyp_landfill": ("W1", "treatment of waste gypsum, sanitary landfill", "waste gypsum"),
 "paper_landfill": ("W1", "treatment of waste paperboard, inert material landfill", "waste paperboard"),
 "paper_recycling": ("W1", "treatment of waste paper, unsorted, sorting", "waste paper, sorted"),
 "glass_landfill": ("W1", "treatment of waste glass, inert material landfill", "waste glass"),
 "glass_recycling": ("W1", "treatment of waste glass from unsorted public collection, sorting", "glass cullet, sorted"),
 "plastic_landfill": ("W2", "treatment of waste plastic, mixture, sanitary landfill", "waste plastic, mixture"),
 "plastic_incin": ("W2", "treatment of waste plastic, mixture, municipal incineration", "waste plastic, mixture"),
}
# (material, constituent) -> {route: key or None (no row) }
WMAP = {
 "hempcrete": {"hemp shiv": {"landfill": "wood_landfill", "recycling": "wood_recycling"},
               "air lime": {"landfill": "min_landfill", "recycling": "min_recycling"},
               "natural hydraulic lime": {"landfill": "min_landfill", "recycling": "min_recycling"},
               "water": {"landfill": "min_landfill", "recycling": "min_recycling"}},
 "gypsum_board": {"gypsum (calcined, from natural / FGD gypsum)": {"landfill": "gyp_landfill", "recycling": "min_recycling"},
                  "recycled paper liner": {"landfill": "paper_landfill", "recycling": "paper_recycling"},
                  "mineral additives and chemicals (starch, foaming agent)": {"landfill": "min_landfill", "recycling": "min_recycling"}},
 "toughened_glass": {"silica sand": {"landfill": "min_landfill", "recycling": "min_recycling"},
                     "soda ash": {"landfill": "min_landfill", "recycling": "min_recycling"},
                     "dolomite": {"landfill": "min_landfill", "recycling": "min_recycling"},
                     "chalk (limestone)": {"landfill": "min_landfill", "recycling": "min_recycling"},
                     "cullet": {"landfill": "glass_landfill", "recycling": "glass_recycling"},
                     "sulphate": {"landfill": "min_landfill", "recycling": "min_recycling"}},
 "ptfe_coated_glass_fabric": {"glass fibre yarn": {"landfill": "min_landfill", "incineration": None, "recycling": "min_recycling"},
                              "PTFE dispersion (solids)": {"landfill": "plastic_landfill", "incineration": "plastic_incin", "recycling": None}},
}
