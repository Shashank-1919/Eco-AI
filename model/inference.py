import numpy as np
import os
import joblib
import skfuzzy as fuzz

# Load ML Model and Scaler
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, 'energy_model.joblib')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.joblib')

CLF = None
SCALER = None

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    try:
        CLF = joblib.load(MODEL_PATH)
        SCALER = joblib.load(SCALER_PATH)
    except Exception as e:
        import sys
        print(f"Error loading model: {e}", file=sys.stderr)


ENERGY_DETAILS = {
    "Solar": {
        "name_of_instrument": "Solar Photovoltaic (PV) System",
        "sub_type": "Rooftop Solar / Solar Farm",
        "advantage": "Highly scalable, rapidly declining costs, lowest maintenance of any renewable source. Available globally wherever sunlight reaches.",
        "payback_duration": "6 - 9 years",
        "precaution": "IMPORTANT: Ensure roof structure can support panel weight (~15kg/sq.m). Install proper lightning arrestors and surge protectors to prevent electrical damage during storms. Never walk directly on panels as it can cause micro-cracks.",
        "care": "Lush evergreen performance requires cleaning panels every 3-6 months to remove dust/pollen. Inspect mounts annually for rust or loose bolts. Check inverter health logs quarterly for any 'Arc Fault' or 'Ground Fault' warnings.",
        "installation_location": "South-facing rooftops (30-45 degree tilt) or open ground with no shading. Desert and sunny regions are optimal.",
        "area_required": "~300-400 sq. ft for a standard 5kW system. Rooftop or open land.",
        "estimated_cost": "Rs.2,00,000 - Rs.6,00,000",
        "environmental_impact": "Reduces CO2 by 3-4 tons/year per 5kW system. Zero operational emissions.",
        "roi": "15-25% annual energy savings. Eligible for PM-KUSUM and net metering subsidies in India.",
        "installation_guide": "**1. Site Assessment**\nEnsure a south-facing roof area with no shade from 9 AM to 4 PM.\n\n**2. Structural Check**\nVerify the roof can handle ~15kg/sq.m load capacity.\n\n**3. Rail Mounting**\nInstall aluminum rails and secure panels with heavy-duty clamps.\n\n**4. Wiring Connection**\nConnect panels in strings (series/parallel) to an inverter.\n\n**5. Grid Integration**\nConnect to the local grid with utility approval.",
        "safety_plan": "**Operational Safety**\n• Always wear a safety harness during roof installation.\n\n**Electrical Protection**\n• Use DC isolators to safely disconnect panels.\n\n**Grounding**\n• Ground every rack and the inverter to prevent surges.\n\n**Maintenance**\n• Clean panels only when cool to avoid thermal cracking.",
        "detailed_impact": "**Sustainability**\nReplaces 95,000 lbs of CO2 over 25 years.\n\n**Trees Equivalent**\nEqual to planting 2,000 trees.\n\n**Local Air Quality**\nEliminates SO2 and NOx emissions from coal usage.",
        "financial_roi": "**Initial Cost**\nInvestment of 3-5 Lakhs for standard systems.\n\n**Payback Period**\nTypically pays for itself in just 6-7 years.\n\n**Total Savings**\nExpected savings exceed 12 Lakhs over 25 years.",
        "government_subsidy": "Eligible for **PM-KUSUM** and **Surya Ghar Muft Bijli Yojana**. Provides 30-40% direct capital subsidy on rooftop solar installations.",
        "government_subsidy_detailed": "**1. PM-KUSUM Scheme**\nFarmers can install solar pumps and grid-connected solar power plants. Subsidy up to 60% is provided by central and state governments.\n\n**2. Rooftop Solar Subsidy (Surya Ghar)**\nResidential consumers receive Rs. 30,000 per kW for up to 2 kW, and Rs. 18,000 per kW for additional capacity up to 3 kW.\n\n**3. Net Metering**\nExcess power generated can be sold back to the grid, reducing monthly bills to zero or even earning revenue."
    },
    "Wind": {
        "name_of_instrument": "Residential / Small Wind Turbine",
        "sub_type": "Small Wind Turbine (1-10 kW)",
        "advantage": "Generates power continuously day and night as long as wind is sufficient. Excellent for coastal and open rural areas.",
        "payback_duration": "10 - 15 years",
        "precaution": "WARNING: Check local zoning laws for height limits and noise ordinances. Requires open, unobstructed land. Keep a safe distance from trees and buildings to avoid turbulence that can damage blades.",
        "care": "Maintain vibrant evergreen efficiency by inspecting blades, bearings, and rotor annually for wear or cracks. Lubricate moving joints every 6 months. Tighten guy-wire anchors regularly to prevent tower swaying.",
        "installation_location": "Open rural/coastal land on a tower at least 30 ft above anything within 300 ft radius.",
        "area_required": "Minimum 1 acre of open land for smooth, non-turbulent airflow.",
        "estimated_cost": "Rs.5,00,000 - Rs.12,00,000",
        "environmental_impact": "Zero emissions during operation. High lifetime energy yield.",
        "roi": "Strong ROI in high-wind coastal zones. MNRE wind incentives apply.",
        "installation_guide": "**1. Wind Survey**\nConduct a 6-month wind study to ensure average speeds >5m/s.\n\n**2. Foundation Setup**\nPour a heavy concrete pad with guy-wire anchors.\n\n**3. Tower Raising**\nAssemble the turbine on the ground and tilt up using a winch system.\n\n**4. Electrical Sync**\nConnect to a charge controller and deep-cycle battery bank.",
        "safety_plan": "**Mechanical Awareness**\n• Always engage the manual brake before approaching the tower.\n• Inspect guy-wires for tension annually to avoid collapse.\n• Use specialized climbing gear for all tower-top maintenance.\n\n**Storm Protection**\nIn case of high-wind warnings (>25m/s), ensure the turbine is furled or braked.",
        "detailed_impact": "**Clean Lifecycle**\nOver their 20-year life, wind turbines provide clean, emission-free power with 90% less land footprint than utility solar when factoring in agricultural dual-use under the tower.\n\n**Energy Density**\nSmall-scale wind turbines produce roughly 50-80% more energy per unit of swept area compared to solar in windy regions.",
        "financial_roi": "**Cost Efficiency**\nAt average speeds of 5.5 m/s, payback is roughly 11 years. Net-metering for wind can reduce electric costs to 20% of retail rates.\n\n**Property Value**\nProperty resale value often increases by 3-5% for energy-independent farms.",
        "government_subsidy": "Eligible for **Generation Based Incentive (GBI)** and **Accelerated Depreciation (AD)** benefits under MNRE small-wind wind schemes.",
        "government_subsidy_detailed": "**1. Generation Based Incentive (GBI)**\nIncentive of Re. 0.50 per unit of electricity fed into the grid, subject to a cap per MW.\n\n**2. Accelerated Depreciation**\nAllows companies to write off 40% of the project cost in the first year to reduce taxable income.\n\n**3. Customs Duty Concessions**\nReduced import duties on specific wind turbine components to lower the initial capital expenditure."
    },
    "Hydro": {
        "name_of_instrument": "Micro-Hydro Power Generator",
        "sub_type": "Micro Hydro (1-100 kW)",
        "advantage": "Most consistent 24/7 baseload renewable power. Unaffected by clouds or windless conditions.",
        "payback_duration": "5 - 10 years",
        "precaution": "CAUTION: Obtain water-use permits from local authorities. Ensure intake does not disrupt local aquatic life or downstream users. Only feasible near fast-flowing water with consistent 'head' or drop.",
        "care": "Keep the system evergreen by clearing the intake screen (penstock) of debris/leaves weekly. Inspect turbine blades for pitting or erosion every 6 months. Monitor pipe anchors for soil erosion after heavy rains.",
        "installation_location": "Alongside a consistent, fast-flowing stream or river with sufficient hydraulic head (vertical drop).",
        "area_required": "Minimal turbine footprint, but requires legal access to flowing water.",
        "estimated_cost": "Rs.8,00,000 - Rs.20,00,000",
        "environmental_impact": "Continuous clean energy. Very low footprint with run-of-river design.",
        "roi": "Exceptional value in mountain/riverine regions. Long operational life of 30+ years.",
        "installation_guide": "**1. Head Measurement**\nCalculate the vertical drop of the water source.\n\n**2. Weir Construction**\nBuild a small diversion to channel water into a pipe.\n\n**3. Penstock Layout**\nLay the high-pressure pipe down to the turbine house.\n\n**4. Powerhouse Setup**\nInstall the Pelton or Turgo turbine and alternator.\n\n**5. Tailrace Design**\nEnsure water returns to the stream without eroding slopes.",
        "safety_plan": "**Water Velocity Safety**\n• Check for penstock leaks or weak joints weekly.\n\n**Debris Management**\n• Install a screen to prevent blockages and pipe bursts.\n\n**Electrical Waterproofing**\n• All electronics must be elevated from potential flood levels.",
        "detailed_impact": "**Eco-Friendly Consistency**\nMost eco-friendly solution with constant 24/7 power.\n\n**Ecosystem Preservation**\nRun-of-river design preserves local riverine life.\n\n**Baseload Stability**\nReduces the need for large battery storage systems.",
        "financial_roi": "**Energy Yield**\nProduces more kWh per kW than any other source.\n\n**Fast Payback**\nPayback in 5-7 years in ideal riverine locations.\n\n**Long Lifecycle**\nOperational life exceeds 40 years with minimal investment.",
        "government_subsidy": "Eligible for the **Small Hydro Power (SHP)** program. Provides capital subsidies based on the Kilowatt (KW) capacity installed.",
        "government_subsidy_detailed": "**1. SHP Capital Subsidy**\nMNRE provides financial support ranging from Rs. 7,500 to Rs. 20,000 per kW depending on the project location (higher for North Eastern states).\n\n**2. State-Level Incentives**\nMany states offer 100% exemption from electricity duty for the first 5-10 years of operation.\n\n**3. Soft Loans**\nLow-interest financing options available through IREDA (Indian Renewable Energy Development Agency)."
    },
    "Biomass": {
        "name_of_instrument": "Biogas / Biomass Energy System",
        "sub_type": "Biogas Plant (family/community scale)",
        "advantage": "Converts agricultural and organic waste into cooking gas and electricity. Reduces waste and methane emissions from decomposition.",
        "payback_duration": "3 - 6 years",
        "precaution": "CRITICAL: Maintain an airtight digester to prevent methane leaks. Never feed the system with plastic, oil, or toxic chemicals as it kills the active bacteria. Provide adequate ventilation around the gas output.",
        "care": "Ensure evergreen performance by stirring the digester slurry daily to prevent crust formation. Check gas pipe integrity with soap-water test monthly. Remove slurry from the outlet tank regularly for use as fertilizer.",
        "installation_location": "Rural farms, forest edges, or agricultural land with abundant organic waste and animal dung.",
        "area_required": "10-50 sq. ft for a family-scale biogas unit. Larger for community biogas plants.",
        "estimated_cost": "Rs.30,000 - Rs.3,00,000",
        "environmental_impact": "Reduces solid waste, methane emissions, and dependence on firewood (deforestation).",
        "roi": "Very high ROI in rural India. Government MNRE biogas program provides direct subsidies.",
        "installation_guide": "**1. Pit Excavation**\nDig a circular pit for the brick or masonry digester dome.\n\n**2. Chamber Construction**\nBuild the mixing tank, digester, and outlet slurry tank.\n\n**3. Gas Holder**\nInstall an airtight floating or fixed dome unit.\n\n**4. Piping Layout**\nLayout GI or HDPE pipes to the kitchen or engine.\n\n**5. Leak Sealing**\nApply waterproof cement to ensure zero methane leaks.",
        "safety_plan": "**Flammable Management**\n• Never use open flames near the digester dome.\n\n**Leak Detection**\n• Check for 'hissing' sounds in pipes weekly.\n\n**H2S Filtration**\n• Use iron filings to scrub corrosive gases.\n\n**Ventilation**\n• Ensure well-ventilated space to prevent asphyxiation.",
        "detailed_impact": "**Methane Capture**\nCaptures potent greenhouse gases from rotting waste.\n\n**Clean Cooking Fuel**\nEliminates indoor pollution from firewood usage.\n\n**Organic Fertilizer**\nProduces high-quality nutrient-rich bio-slurry.",
        "financial_roi": "**Immediate Savings**\nReplaces expensive LPG cylinders immediately.\n\n**Waste disposal**\nReduces cost of agricultural waste management.\n\n**Secondary Revenue**\nSelling compressed biogas (CBG) is a lucrative option.",
        "government_subsidy": "Eligible for **National Biogas and Organic Manure Programme (NBOMP)**. Provides direct central financial assistance for plant construction.",
        "government_subsidy_detailed": "**1. NBOMP Subsidy**\nDirect financial assistance of Rs. 9,800 to Rs. 14,350 for small-scale (1-25 cubic meter) biogas plants.\n\n**2. SATAT Initiative**\nSustainable Alternative Towards Affordable Transportation (SATAT) provides a floor price for Compressed Bio-Gas (CBG) produced from waste.\n\n**3. Waste-to-Energy Grants**\nAdditional grants available for large-scale community biogas plants in urban and industrial sectors."
    },
    "Geothermal": {
        "name_of_instrument": "Geothermal Heat Pump (Ground-Source)",
        "sub_type": "Ground-Source Heat Pump (GSHP)",
        "advantage": "Achieves 300-500% efficiency by exploiting stable underground temperatures. Ideal for heating and cooling.",
        "payback_duration": "5 - 7 years",
        "precaution": "NOTE: Requires a professional geological survey before drilling to ensure soil thermal conductivity. Keep excavation areas clear of heavy structures to avoid pipe compression.",
        "care": "Evergreen stability is provided by underground loops which are virtually maintenance-free. Change indoor air filters every 3 months. Monitor the fluid pressure gauge annually to check for loop leaks.",
        "installation_location": "Buried in yard (horizontal loop) or drilled underground (vertical loop). Volcanic/mountainous regions ideal.",
        "area_required": "Large garden for horizontal loops or deep borehole access for vertical installation.",
        "estimated_cost": "Rs.10,00,000 - Rs.25,00,000",
        "environmental_impact": "Massively reduces HVAC emissions. Longest lifespan of any renewable system (50+ years).",
        "roi": "Very high long-term savings on heating/cooling bills. Limited Indian subsidies currently.",
        "installation_guide": "**1. Geological Survey**\nTest soil thermal conductivity and rock depth.\n\n**2. Loop Excavation**\nTrench 4-6ft deep or drill 200ft deep boreholes.\n\n**3. Pipe Layout**\nInstall HDPE piping and fill with transfer fluid.\n\n**4. Sealing/Grout**\nSeal pipes with high-conductive grout to ensure contact.\n\n**5. System Sync**\nConnect to the indoor compressor/heat-exchanger unit.",
        "safety_plan": "**Pressure Monitoring**\n• Ensure closed loops are purged of air bubbles weekly.\n\n**Machinery Protocol**\n• Deep boreholes require industrial-grade drilling safety.\n\n**Indoor Integrity**\n• Inspect heat pump compressor for electrical leaks quarterly.\n\n**Fluid Management**\n• Handle transfer fluids professionally during maintenance.",
        "detailed_impact": "**Visual Minimalism**\nLowest land-use and zero visual impact ('Invisible' energy).\n\n**Climate Versatility**\nGold standard for both extreme heat and extreme cold.\n\n**Silent Operation**\nOperates silently compared to air-source heat pumps.",
        "financial_roi": "**50-Year Investment**\nReduces heating/cooling bills by 50-70% indefinitely.\n\n**HVAC Replacement**\nReplaces both heater and central AC in one unit.\n\n**Inflation Hedge**\nProvides energy stability against fuel price hikes.",
        "government_subsidy": "Limited state-level incentives available. Currently eligible for **Income Tax benefits** under 'Green Building' energy-efficiency sections.",
        "government_subsidy_detailed": "**1. Green Building Certification**\nInstallations often help buildings achieve LEED or GRIHA ratings, leading to property tax rebates of 5-10% in several Indian states.\n\n**2. Section 32 Income Tax Act**\nBusinesses can claim depreciation on energy-efficient heat pump systems to reduce tax liability.\n\n**3. R&D Support**\nMNRE provides up to 50% funding for pilot geothermal projects in specific regions like Puga Valley and Tatapani."
    },
    "Tidal": {
        "name_of_instrument": "Tidal / Wave Energy Converter",
        "sub_type": "Tidal Stream Generator",
        "advantage": "Fully predictable, tide-driven power generation. Unaffected by weather or sunlight. Operates 24/7 with 100% predictability.",
        "payback_duration": "12 - 20 years",
        "precaution": "MARINE ADVISORY: Only viable in high tidal-range coastal zones. Requires specialized marine engineering and environmental permits. Watch for biofouling (barnacles/seaweed) which can reduce blade efficiency.",
        "care": "Ensure evergreen marine health by inspecting subsea components with ROVs/drones every 6-12 months. Apply anti-fouling coatings annually. Check subsea power cable protection after major maritime storms.",
        "installation_location": "Coastal areas with tidal range >5m or strong tidal streams. Ideal for India's Gujarat and West Bengal coasts.",
        "area_required": "Offshore marine installation. No land area required.",
        "estimated_cost": "Rs.50,00,000+",
        "environmental_impact": "Zero CO2 emissions. Minimal visual impact as installations are mostly submerged.",
        "roi": "Currently high cost but costs declining rapidly. Suitable for large coastal utility projects.",
        "installation_guide": "**1. Marine Survey**\nMap the seabed and calculate tidal velocities using acoustic Doppler current profilers.\n\n**2. Mooring/Gravity Base**\nInstall a heavy seafloor anchor or concrete gravity base for stability.\n\n**3. Turbine Deployment**\nLower the turbine unit from a specialized barge during 'slack water' (low current).\n\n**4. Power Cable**\nLay armored subsea power cables from the turbine to the shore station.\n\n**5. Grid Link**\nConnect to the coastal substation with high-voltage protection and sync equipment.",
        "safety_plan": "**Marine Operations**\n• Working in tidal currents is high-risk; all installation must be done during 'slack water'.\n\n**Subsea Integrity**\n• Subsea electrical cables are high-voltage; ensure robust armoring against anchors or fishing gear.\n\n**Environmental Monitoring**\n• Conduct regular underwater drone inspections to check for biofouling or corrosion.",
        "detailed_impact": "**Predictable Baseload**\nActs as a 100% predictable baseload, unlike the intermittency of solar and wind.\n\n**Energy Density**\nTidal energy provides massive power density (800x that of wind) in a small aquatic footprint.\n\n**Eco-Friendly Design**\nModern 'slow-turn' turbines are designed to be sea-life friendly to manage seabed impact.",
        "financial_roi": "**Long-term Stability**\nProvides a stable power supply that avoids the need for massive battery backups, creating deep value for long-term PPAs.\n\n**Infrastructure Value**\nHigh initial investment is offset by a long operational life (30+ years) in demanding marine environments.",
        "government_subsidy": "Eligible for strategic support under **MNRE's Ocean Energy scheme** for large-scale pilot projects and technology demonstration.",
        "government_subsidy_detailed": "**1. Ocean Energy Policy**\nGovernment of India has declared Tidal and Wave energy as 'Renewable Energy', making them eligible for Renewable Purchase Obligations (RPOs).\n\n**2. Viability Gap Funding (VGF)**\nStrategic support for early-stage commercial projects to bridge the gap between high capital cost and tariff expectations.\n\n**3. Demonstration Grants**\nFull funding available for research institutions and 50% for private players for technology demonstration in Indian waters."
    }

}


# ─────────────────────────────────────────────────────────────────────────────
# CORE FIS BUILDER — Pure numpy/skfuzzy, no shared antecedent state
# ─────────────────────────────────────────────────────────────────────────────

def _trapmf(universe, abcd):
    return fuzz.trapmf(universe, abcd)


def _suitability_mf(universe):
    """Returns dict of membership functions for a [0,1] suitability output."""
    return {
        'very_low':  _trapmf(universe, [0.0,  0.0,  0.10, 0.25]),
        'low':       _trapmf(universe, [0.10, 0.25, 0.35, 0.50]),
        'medium':    _trapmf(universe, [0.35, 0.50, 0.60, 0.75]),
        'high':      _trapmf(universe, [0.60, 0.75, 0.85, 0.92]),
        'very_high': _trapmf(universe, [0.82, 0.92, 1.0,  1.0 ]),
    }


def _defuzz_centroid(universe, mf):
    """Centroid defuzzification with fallback."""
    try:
        result = fuzz.defuzz(universe, mf, 'centroid')
        return float(np.clip(result, 0.0, 1.0))
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL MAMDANI INFERENCE (avoids skfuzzy ControlSystem shared-state bugs)
# ─────────────────────────────────────────────────────────────────────────────

def _mamdani(output_mfs: dict, output_universe: np.ndarray, rules: list) -> float:
    """
    rules: list of (activation_strength, output_label) tuples.
    Performs Mamdani aggregation + centroid defuzzification.
    """
    aggregated = np.zeros_like(output_universe, dtype=float)
    for strength, label in rules:
        if strength > 0 and label in output_mfs:
            clipped = np.minimum(strength, output_mfs[label])
            aggregated = np.maximum(aggregated, clipped)
    return _defuzz_centroid(output_universe, aggregated)


# ─────────────────────────────────────────────────────────────────────────────
# 1. SOLAR FIS
# ─────────────────────────────────────────────────────────────────────────────

def _score_solar(irradiance: float, temperature: float, humidity: float, budget: float) -> float:
    irr_u = np.arange(0, 101, 1)
    irr_low    = _trapmf(irr_u, [0,  0,  25, 45])
    irr_medium = _trapmf(irr_u, [30, 50, 65, 78])
    irr_high   = _trapmf(irr_u, [65, 80, 100, 100])

    # Temperature membership for solar efficiency vs practical reliability
    temp_u = np.arange(0, 51, 1)
    t_freezing = _trapmf(temp_u, [0,  0,  5,  12])
    t_cold     = _trapmf(temp_u, [8,  15, 22, 30])
    t_optimal  = _trapmf(temp_u, [20, 30, 40, 50])

    hum_u = np.arange(0, 101, 1)
    hum_low    = _trapmf(hum_u, [0,  0,  28, 42])
    hum_medium = _trapmf(hum_u, [30, 48, 62, 72])
    hum_high   = _trapmf(hum_u, [62, 75, 100, 100])

    bud_u = np.arange(0, 1000001, 5000)
    bud_low    = _trapmf(bud_u, [0,      0,      75000,  200000])
    bud_medium = _trapmf(bud_u, [75000,  200000, 500000, 700000])
    bud_high   = _trapmf(bud_u, [500000, 700000, 1000000, 1000000])

    # Clamp inputs
    irr = float(np.clip(irradiance, 0, 100))
    hum = float(np.clip(humidity, 0, 100))
    bud = float(np.clip(budget, 0, 1000000))

    i_low = float(fuzz.interp_membership(irr_u, irr_low,    irr))
    i_med = float(fuzz.interp_membership(irr_u, irr_medium, irr))
    i_hgh = float(fuzz.interp_membership(irr_u, irr_high,   irr))

    # Temperature interpolation
    tmp = float(np.clip(temperature, 0, 50))
    t_frz = float(fuzz.interp_membership(temp_u, t_freezing, tmp))
    t_cld = float(fuzz.interp_membership(temp_u, t_cold,     tmp))
    t_opt = float(fuzz.interp_membership(temp_u, t_optimal,  tmp))

    h_low = float(fuzz.interp_membership(hum_u, hum_low,    hum))
    h_med = float(fuzz.interp_membership(hum_u, hum_medium, hum))
    h_hgh = float(fuzz.interp_membership(hum_u, hum_high,   hum))

    b_low = float(fuzz.interp_membership(bud_u, bud_low,    bud))
    b_med = float(fuzz.interp_membership(bud_u, bud_medium, bud))
    b_hgh = float(fuzz.interp_membership(bud_u, bud_high,   bud))

    s_u = np.arange(0, 1.01, 0.01)
    s_mfs = _suitability_mf(s_u)

    rules = [
        (min(i_hgh, h_low, b_hgh, t_opt), 'very_high'),
        (min(i_hgh, h_low, b_hgh, t_frz), 'medium'), # Penalty for freezing
        (min(i_hgh, h_low, b_med, t_opt), 'high'),
        (min(i_hgh, h_med, b_hgh, t_opt), 'very_high'),
        (min(i_hgh, h_med, b_med, t_opt), 'high'),
        (min(i_hgh, h_hgh),               'medium'),
        (min(i_hgh, t_frz),               'low'),    # Strong penalty for icing/snow
        (min(i_med, h_low, b_med),        'medium'),
        (min(i_med, h_med),               'medium'),
        (min(i_med, h_hgh),               'low'),
        (min(i_low, h_hgh),               'very_low'),
        (min(i_low, h_med),               'low'),
        (min(i_low, b_low),               'very_low'),
        (min(i_hgh, b_low),               'medium'),
        (min(i_med, b_low),               'low'),
    ]

    return _mamdani(s_mfs, s_u, rules)


# ─────────────────────────────────────────────────────────────────────────────
# 2. WIND FIS
# ─────────────────────────────────────────────────────────────────────────────

def _score_wind(wind_speed: float, loc_factor: float, humidity: float, budget: float) -> float:
    ws_u = np.arange(0, 15.1, 0.1)
    ws_vlow   = _trapmf(ws_u, [0,   0,   2,   4  ])
    ws_low    = _trapmf(ws_u, [2,   3,   5,   6  ])
    ws_mod    = _trapmf(ws_u, [5,   6,   8,   9  ])
    ws_high   = _trapmf(ws_u, [7,   9,   11,  12 ])
    ws_vhigh  = _trapmf(ws_u, [10,  11,  15,  15 ])

    # loc_factor: 0.0 = worst (urban/desert), 1.0 = best (coastal)
    loc_u = np.arange(0, 1.01, 0.01)
    loc_poor = _trapmf(loc_u, [0,   0,   0.25, 0.4 ])
    loc_mod  = _trapmf(loc_u, [0.3, 0.5, 0.65, 0.8 ])
    loc_good = _trapmf(loc_u, [0.7, 0.85, 1.0, 1.0 ])

    bud_u = np.arange(0, 1000001, 5000)
    bud_low  = _trapmf(bud_u, [0,      0,      100000, 300000])
    bud_med  = _trapmf(bud_u, [100000, 300000, 600000, 800000])
    bud_high = _trapmf(bud_u, [600000, 800000, 1000000, 1000000])

    ws  = float(np.clip(wind_speed, 0, 15))
    loc = float(np.clip(loc_factor, 0, 1))
    bud = float(np.clip(budget, 0, 1000000))

    w_vl = float(fuzz.interp_membership(ws_u, ws_vlow,  ws))
    w_l  = float(fuzz.interp_membership(ws_u, ws_low,   ws))
    w_m  = float(fuzz.interp_membership(ws_u, ws_mod,   ws))
    w_h  = float(fuzz.interp_membership(ws_u, ws_high,  ws))
    w_vh = float(fuzz.interp_membership(ws_u, ws_vhigh, ws))

    l_p  = float(fuzz.interp_membership(loc_u, loc_poor, loc))
    l_m  = float(fuzz.interp_membership(loc_u, loc_mod,  loc))
    l_g  = float(fuzz.interp_membership(loc_u, loc_good, loc))

    b_l  = float(fuzz.interp_membership(bud_u, bud_low,  bud))
    b_m  = float(fuzz.interp_membership(bud_u, bud_med,  bud))
    b_h  = float(fuzz.interp_membership(bud_u, bud_high, bud))

    s_u = np.arange(0, 1.01, 0.01)
    s_mfs = _suitability_mf(s_u)

    rules = [
        (min(w_vh, l_g, b_h),  'very_high'),
        (min(w_vh, l_g, b_m),  'high'),
        (min(w_vh, l_m, b_m),  'high'),
        (min(w_h,  l_g, b_h),  'very_high'),
        (min(w_h,  l_g, b_m),  'high'),
        (min(w_h,  l_m, b_m),  'high'),
        (min(w_h,  l_m, b_l),  'medium'),
        (min(w_m,  l_g, b_m),  'high'),
        (min(w_m,  l_g, b_l),  'medium'),
        (min(w_m,  l_m),       'medium'),
        (min(w_l,  l_g),       'medium'),
        (min(w_l,  l_m),       'low'),
        (min(w_l,  l_p),       'very_low'),
        (w_vl,                 'very_low'),
        (min(b_l,  w_h),       'medium'),
        (min(b_l,  w_m),       'low'),
    ]

    return _mamdani(s_mfs, s_u, rules)


# ─────────────────────────────────────────────────────────────────────────────
# 3. HYDRO FIS
# ─────────────────────────────────────────────────────────────────────────────

def _score_hydro(water_avail: float, loc_factor: float, budget: float) -> float:
    wa_u = np.arange(0, 101, 1)
    wa_none = _trapmf(wa_u, [0,  0,  5,  15 ])
    wa_low  = _trapmf(wa_u, [5,  15, 25, 38 ])
    wa_mod  = _trapmf(wa_u, [28, 42, 55, 65 ])
    wa_high = _trapmf(wa_u, [55, 68, 80, 88 ])
    wa_abun = _trapmf(wa_u, [78, 88, 100, 100])

    loc_u = np.arange(0, 1.01, 0.01)
    loc_poor = _trapmf(loc_u, [0,   0,   0.25, 0.4])
    loc_mod  = _trapmf(loc_u, [0.3, 0.5, 0.65, 0.8])
    loc_good = _trapmf(loc_u, [0.7, 0.85, 1.0, 1.0])

    bud_u = np.arange(0, 1000001, 5000)
    bud_low  = _trapmf(bud_u, [0,      0,      100000, 300000])
    bud_med  = _trapmf(bud_u, [100000, 300000, 600000, 800000])
    bud_high = _trapmf(bud_u, [600000, 800000, 1000000, 1000000])

    wa  = float(np.clip(water_avail, 0, 100))
    loc = float(np.clip(loc_factor, 0, 1))
    bud = float(np.clip(budget, 0, 1000000))

    wa_n = float(fuzz.interp_membership(wa_u, wa_none, wa))
    wa_l = float(fuzz.interp_membership(wa_u, wa_low,  wa))
    wa_m = float(fuzz.interp_membership(wa_u, wa_mod,  wa))
    wa_h = float(fuzz.interp_membership(wa_u, wa_high, wa))
    wa_a = float(fuzz.interp_membership(wa_u, wa_abun, wa))

    l_p = float(fuzz.interp_membership(loc_u, loc_poor, loc))
    l_m = float(fuzz.interp_membership(loc_u, loc_mod,  loc))
    l_g = float(fuzz.interp_membership(loc_u, loc_good, loc))

    b_l = float(fuzz.interp_membership(bud_u, bud_low,  bud))
    b_m = float(fuzz.interp_membership(bud_u, bud_med,  bud))
    b_h = float(fuzz.interp_membership(bud_u, bud_high, bud))

    s_u = np.arange(0, 1.01, 0.01)
    s_mfs = _suitability_mf(s_u)

    rules = [
        (min(wa_a, l_g, b_h),  'very_high'),
        (min(wa_a, l_g, b_m),  'high'),
        (min(wa_a, l_m, b_m),  'high'),
        (min(wa_h, l_g, b_h),  'very_high'),
        (min(wa_h, l_g, b_m),  'high'),
        (min(wa_h, l_m),       'medium'),
        (min(wa_m, l_g, b_m),  'medium'),
        (min(wa_m, l_m),       'low'),
        (wa_l,                 'low'),
        (wa_n,                 'very_low'),
        (min(b_l, wa_h),       'medium'),
        (min(l_p, wa_a),       'low'),
        (l_p,                  'very_low'),
    ]

    return _mamdani(s_mfs, s_u, rules)


# ─────────────────────────────────────────────────────────────────────────────
# 4. BIOMASS FIS
# ─────────────────────────────────────────────────────────────────────────────

def _score_biomass(bio_avail: float, loc_factor: float, humidity: float, budget: float) -> float:
    ba_u = np.arange(0, 101, 1)
    ba_none = _trapmf(ba_u, [0,  0,  5,  15 ])
    ba_low  = _trapmf(ba_u, [5,  15, 25, 38 ])
    ba_mod  = _trapmf(ba_u, [28, 42, 55, 65 ])
    ba_high = _trapmf(ba_u, [55, 68, 80, 88 ])
    ba_vh   = _trapmf(ba_u, [78, 88, 100, 100])

    hum_u = np.arange(0, 101, 1)
    hum_low = _trapmf(hum_u, [0,  0,  30, 45])
    hum_med = _trapmf(hum_u, [35, 50, 65, 75])
    hum_hgh = _trapmf(hum_u, [65, 78, 100, 100])

    loc_u = np.arange(0, 1.01, 0.01)
    loc_poor = _trapmf(loc_u, [0,   0,   0.25, 0.4])
    loc_mod  = _trapmf(loc_u, [0.3, 0.5, 0.65, 0.8])
    loc_good = _trapmf(loc_u, [0.7, 0.85, 1.0, 1.0])

    ba  = float(np.clip(bio_avail, 0, 100))
    loc = float(np.clip(loc_factor, 0, 1))
    hum = float(np.clip(humidity, 0, 100))

    b_n = float(fuzz.interp_membership(ba_u, ba_none, ba))
    b_l = float(fuzz.interp_membership(ba_u, ba_low,  ba))
    b_m = float(fuzz.interp_membership(ba_u, ba_mod,  ba))
    b_h = float(fuzz.interp_membership(ba_u, ba_high, ba))
    b_v = float(fuzz.interp_membership(ba_u, ba_vh,   ba))

    h_l = float(fuzz.interp_membership(hum_u, hum_low, hum))
    h_m = float(fuzz.interp_membership(hum_u, hum_med, hum))
    h_h = float(fuzz.interp_membership(hum_u, hum_hgh, hum))

    l_p = float(fuzz.interp_membership(loc_u, loc_poor, loc))
    l_m = float(fuzz.interp_membership(loc_u, loc_mod,  loc))
    l_g = float(fuzz.interp_membership(loc_u, loc_good, loc))

    s_u = np.arange(0, 1.01, 0.01)
    s_mfs = _suitability_mf(s_u)

    rules = [
        (min(b_v, l_g, h_h),  'very_high'),
        (min(b_v, l_g, h_m),  'very_high'),
        (min(b_v, l_m, h_m),  'high'),
        (min(b_h, l_g, h_h),  'high'),
        (min(b_h, l_g),       'high'),
        (min(b_h, l_m, h_m),  'medium'),
        (min(b_m, l_g),       'medium'),
        (min(b_m, l_m),       'low'),
        (b_l,                 'low'),
        (b_n,                 'very_low'),
        (min(l_p, b_v),       'low'),
        (l_p,                 'very_low'),
    ]

    return _mamdani(s_mfs, s_u, rules)


# ─────────────────────────────────────────────────────────────────────────────
# 5. GEOTHERMAL FIS
# ─────────────────────────────────────────────────────────────────────────────

def _score_geothermal(temperature: float, budget: float, location_type: str) -> float:
    temp_u = np.arange(0, 51, 1)
    t_extreme = _trapmf(temp_u, [0,  0,  8,  15])   # very cold = high heat pump value
    t_mod     = _trapmf(temp_u, [10, 18, 28, 36])
    t_hot     = _trapmf(temp_u, [30, 40, 50, 50])

    bud_u = np.arange(0, 1000001, 5000)
    bud_low  = _trapmf(bud_u, [0,      0,      200000, 400000])
    bud_med  = _trapmf(bud_u, [200000, 400000, 700000, 900000])
    bud_high = _trapmf(bud_u, [700000, 900000, 1000000, 1000000])

    tmp = float(np.clip(temperature, 0, 50))
    bud = float(np.clip(budget, 0, 1000000))

    te = float(fuzz.interp_membership(temp_u, t_extreme, tmp))
    tm = float(fuzz.interp_membership(temp_u, t_mod,     tmp))
    th = float(fuzz.interp_membership(temp_u, t_hot,     tmp))

    bl = float(fuzz.interp_membership(bud_u, bud_low,  bud))
    bm = float(fuzz.interp_membership(bud_u, bud_med,  bud))
    bh = float(fuzz.interp_membership(bud_u, bud_high, bud))

    s_u = np.arange(0, 1.01, 0.01)
    s_mfs = _suitability_mf(s_u)

    rules = [
        (min(bh, te),  'very_high'),
        (min(bh, tm),  'high'),
        (min(bh, th),  'medium'),
        (min(bm, te),  'high'),
        (min(bm, tm),  'medium'),
        (min(bm, th),  'low'),
        (bl,           'very_low'),
    ]

    score = _mamdani(s_mfs, s_u, rules)

    # Climate and Location bonus
    if tmp < 12: # Cold climate boost
        score = min(1.0, score * 1.45)
    
    if location_type == 'mountainous':
        score = min(1.0, score * 1.3)
    elif location_type in ('urban', 'desert'):
        score *= 0.65

    return score


# ─────────────────────────────────────────────────────────────────────────────
# 6. TIDAL — Rule-based (purely location-dependent)
# ─────────────────────────────────────────────────────────────────────────────

def _score_tidal(location_type: str, budget: float, water_proximity: float) -> float:
    if location_type != 'coastal':
        return 0.03
    score = 0.40
    if budget >= 800000:
        score += 0.30
    elif budget >= 400000:
        score += 0.15
    if water_proximity >= 70:
        score += 0.20
    elif water_proximity >= 40:
        score += 0.10
    return float(np.clip(score, 0.0, 1.0))


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION TYPE → FACTOR MAPPINGS
# ─────────────────────────────────────────────────────────────────────────────

LOCATION_WIND_FACTOR = {
    'coastal': 1.0, 'mountainous': 0.75, 'rural': 0.65,
    'forest': 0.50, 'urban': 0.30, 'desert': 0.45
}
LOCATION_HYDRO_FACTOR = {
    'mountainous': 1.0, 'forest': 0.75, 'rural': 0.65,
    'coastal': 0.55, 'urban': 0.15, 'desert': 0.05
}
LOCATION_BIOMASS_FACTOR = {
    'forest': 1.0, 'rural': 0.90, 'mountainous': 0.60,
    'coastal': 0.45, 'urban': 0.20, 'desert': 0.10
}


# ─────────────────────────────────────────────────────────────────────────────
# DETERMINE HYBRID RECOMMENDATION
# ─────────────────────────────────────────────────────────────────────────────

def _recommend_hybrid(scores: dict, budget: float, location_type: str) -> str:
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_types = [r[0] for r in ranked[:3]]

    if 'Solar' in top_types and 'Wind' in top_types and budget >= 500000:
        return 'Hybrid (Solar + Wind)'
    if 'Solar' in top_types and 'Biomass' in top_types:
        return 'Solar + Biomass'
    if location_type == 'coastal' and budget >= 500000:
        return 'Hybrid (Solar + Wind)'
    return 'Hybrid (Solar + Wind)'


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def predict_renewable_energy(
    description_text: str = '',
    user_budget: float = None,
    user_temp: float = None,
    user_hum: float = None,
    user_wind_speed: float = None,
    user_solar_irradiance: float = None,
    user_water_availability: float = None,
    user_biomass_availability: float = None,
    user_location_type: str = 'rural'
) -> dict:

    # ── Defaults ─────────────────────────────────────────────────────────────
    budget               = float(np.clip(user_budget               if user_budget               is not None else 300000, 0, 1000000))
    temperature          = float(np.clip(user_temp                 if user_temp                 is not None else 25,     0, 50))
    humidity             = float(np.clip(user_hum                  if user_hum                  is not None else 50,     0, 100))
    wind_speed           = float(np.clip(user_wind_speed           if user_wind_speed           is not None else 5,      0, 15))
    solar_irradiance     = float(np.clip(user_solar_irradiance     if user_solar_irradiance     is not None else 60,     0, 100))
    water_availability   = float(np.clip(user_water_availability   if user_water_availability   is not None else 30,     0, 100))
    biomass_availability = float(np.clip(user_biomass_availability if user_biomass_availability is not None else 25,     0, 100))

    location_type = (user_location_type or 'rural').lower().strip()
    loc_mapping = {'coastal': 0, 'mountainous': 1, 'desert': 2, 'forest': 3, 'rural': 4, 'urban': 5}
    loc_idx = loc_mapping.get(location_type, 4)

    # ── Inference ────────────────────────────────────────────────────────────
    if CLF and SCALER:
        # Features: [temp, hum, wind, solar_irr, water, biomass, budget, loc_type]
        features = np.array([[temperature, humidity, wind_speed, solar_irradiance, 
                              water_availability, biomass_availability, budget, loc_idx]])
        features_scaled = SCALER.transform(features)
        
        # Get Class Probabilities
        probs = CLF.predict_proba(features_scaled)[0]
        
        # Mapping to names
        idx_to_name = {0: 'Solar', 1: 'Wind', 2: 'Hydro', 3: 'Biomass', 4: 'Geothermal', 5: 'Tidal'}
        scores = {idx_to_name[i]: float(probs[i]) for i in range(len(probs))}
    else:
        # Fallback to simple heuristic if model loading failed
        scores = {
            'Solar': 0.6 if solar_irradiance > 50 else 0.2,
            'Wind':  0.6 if wind_speed > 8 else 0.1,
            'Hydro': 0.6 if water_availability > 70 else 0.05,
            'Biomass': 0.6 if biomass_availability > 60 else 0.1,
            'Geothermal': 0.4 if budget > 500000 else 0.05,
            'Tidal': 0.5 if location_type == 'coastal' and budget > 600000 else 0.01
        }

    # ── Rank ─────────────────────────────────────────────────────────────────
    ranked           = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type        = ranked[0][0]
    second_best_type = ranked[1][0]
    
    # Simple hybrid logic
    hybrid_type = f"{best_type} + {second_best_type}" if scores[second_best_type] > 0.2 else best_type

    best_details        = dict(ENERGY_DETAILS.get(best_type, {}))
    second_best_details = dict(ENERGY_DETAILS.get(second_best_type, {}))

    hybrid_details      = dict(ENERGY_DETAILS.get(hybrid_type, {}))

    all_pct = {k: round(v * 100, 1) for k, v in scores.items()}

    return {
        'best': {
            'type':       best_type,
            'score':      round(scores[best_type], 3),
            'confidence': round(scores[best_type] * 100, 1),
            'details':    best_details
        },
        'second_best': {
            'type':       second_best_type,
            'score':      round(scores[second_best_type], 3),
            'confidence': round(scores[second_best_type] * 100, 1),
            'details':    second_best_details
        },
        'hybrid': {
            'type':    hybrid_type,
            'details': hybrid_details
        },
        'all_scores':  all_pct,
        'inputs_used': {
            'budget':               budget,
            'temperature':          temperature,
            'humidity':             humidity,
            'wind_speed':           wind_speed,
            'solar_irradiance':     solar_irradiance,
            'water_availability':   water_availability,
            'biomass_availability': biomass_availability,
            'location_type':        location_type
        }
    }
