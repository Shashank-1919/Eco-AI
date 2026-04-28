import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=5000):
    np.random.seed(42)
    
    # 0=coastal, 1=mountainous, 2=desert, 3=forest, 4=rural, 5=urban
    loc_types = ['coastal', 'mountainous', 'desert', 'forest', 'rural', 'urban']
    
    data = []
    
    # Use a quota-based approach to ensure balance
    counts = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    quota = num_samples // 6
    
    while len(data) < num_samples:
        # Features
        temp      = np.random.uniform(0, 50)
        hum       = np.random.uniform(0, 100)
        wind      = np.random.uniform(0, 15)
        solar_irr = np.random.uniform(0, 100)
        water     = np.random.uniform(0, 100)
        biomass   = np.random.uniform(0, 100)
        budget    = np.random.uniform(30000, 1000000)
        loc_type_idx = np.random.randint(0, 6)
        loc_type = loc_types[loc_type_idx]
        
        # Scoring logic (Target)
        scores = {}
        
        # Solar: Needs high irr, prefers moderate/hot temp (but efficiency drops slightly at extreme hot)
        solar_score = (solar_irr / 100.0) * 0.9
        solar_score += (1.0 - abs(temp - 25)/35) * 0.2
        if hum > 80: solar_score *= 0.8 # Humidity/Cloud factor
        scores['Solar'] = solar_score
        
        # Wind: Needs wind speed, favors coastal/mountains
        wind_score = (wind / 15.0) * 0.9
        if loc_type in ['coastal', 'mountainous']: wind_score += 0.3
        if budget < 150000: wind_score *= 0.2 # Turbines are expensive
        scores['Wind'] = wind_score
        
        # Hydro: Needs water, favors mountains/forest
        hydro_score = (water / 100.0) * 0.9
        if loc_type in ['mountainous', 'forest']: hydro_score += 0.4
        if budget < 400000: hydro_score *= 0.1 # Micro-hydro is high cap-ex
        scores['Hydro'] = hydro_score
        
        # Biomass: Needs biomass source, favors rural/forest
        biomass_score = (biomass / 100.0) * 0.8
        if loc_type in ['rural', 'forest']: biomass_score += 0.3
        if hum > 60: biomass_score += 0.1 # Wet waste processing
        scores['Biomass'] = biomass_score
        
        # Geothermal: High budget, favors mountains, extreme temps (cold/hot)
        geo_score = 0
        if budget > 500000:
            geo_score = (abs(temp - 25) / 25.0) * 0.7 + 0.2
            if loc_type == 'mountainous': geo_score += 0.3
        scores['Geothermal'] = geo_score
        
        # Tidal: Coastal ONLY, needs high budget
        tidal_score = 0
        if loc_type == 'coastal':
            tidal_score = (water / 100.0) * 0.6 + (budget / 1000000.0) * 0.6
            if budget < 600000: tidal_score = 0
        scores['Tidal'] = tidal_score
        
        # Determine best source
        best_source = max(scores, key=scores.get)
        mapping = {'Solar': 0, 'Wind': 1, 'Hydro': 2, 'Biomass': 3, 'Geothermal': 4, 'Tidal': 5}
        target = mapping[best_source]
        
        # Balance distribution
        if counts[target] < quota or np.random.random() < 0.05:
            counts[target] += 1
            data.append([temp, hum, wind, solar_irr, water, biomass, budget, loc_type_idx, target])
        
    columns = ['temp', 'hum', 'wind', 'solar_irr', 'water', 'biomass', 'budget', 'loc_type', 'target']
    df = pd.DataFrame(data, columns=columns)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), 'energy_dataset.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} samples and saved to {output_path}")
    print("Class distribution:")
    print(df['target'].value_counts())

if __name__ == '__main__':
    generate_synthetic_data()
