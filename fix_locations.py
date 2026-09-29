import pandas as pd
import random

# Karnataka cities and their approximate bounding boxes or random coords within Karnataka
karnataka_cities = [
    "Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Dharwad", "Belagavi",
    "Shivamogga", "Tumakuru", "Davanagere", "Ballari", "Kalaburagi", "Vijayapura",
    "Udupi", "Hassan", "Mandya", "Kodagu", "Chikkamagaluru", "Raichur", "Kolar"
]

def get_random_karnataka_coords():
    # Karnataka bounding box: lat ~ 11.5 to 18.5, lon ~ 74.0 to 78.5
    lat = random.uniform(11.5, 18.5)
    lon = random.uniform(74.0, 78.5)
    return lat, lon

def fix_locations_dataset():
    df = pd.read_csv('data/synthetic/withdrawal_locations.csv')
    
    # Update states, cities, and districts to Karnataka ones
    df['state'] = 'Karnataka'
    df['city'] = [random.choice(karnataka_cities) for _ in range(len(df))]
    df['district'] = df['city'] + "_District"
    
    # Update latitudes and longitudes
    coords = [get_random_karnataka_coords() for _ in range(len(df))]
    df['latitude'] = [c[0] for c in coords]
    df['longitude'] = [c[1] for c in coords]
    
    df.to_csv('data/synthetic/withdrawal_locations.csv', index=False)
    print("Fixed withdrawal_locations.csv")

def fix_training_dataset():
    df = pd.read_csv('data/synthetic/cashtrail_training_dataset.csv')
    
    # We also need to update the location_latitude and location_longitude in training data
    # Let's map location_id to the new coords
    loc_df = pd.read_csv('data/synthetic/withdrawal_locations.csv')
    loc_map = loc_df.set_index('location_id')[['latitude', 'longitude']].to_dict('index')
    
    def get_lat(loc_id):
        return loc_map.get(loc_id, {'latitude': 12.9716})['latitude']
        
    def get_lon(loc_id):
        return loc_map.get(loc_id, {'longitude': 77.5946})['longitude']

    df['location_latitude'] = df['location_id'].apply(get_lat)
    df['location_longitude'] = df['location_id'].apply(get_lon)
    
    # Let's also fix victim coordinates to be in Karnataka just in case, though the requirement says "ALL withdrawal candidate locations"
    # But it might be good. Requirement: "Find every location where state != Karnataka or coordinates are outside Karnataka"
    # The requirement specifically mentions "candidate withdrawal-risk locations".
    
    df.to_csv('data/synthetic/cashtrail_training_dataset.csv', index=False)
    print("Fixed cashtrail_training_dataset.csv")

if __name__ == '__main__':
    fix_locations_dataset()
    fix_training_dataset()
