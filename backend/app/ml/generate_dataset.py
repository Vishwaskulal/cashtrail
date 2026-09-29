import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Fixed Random Seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate geographic distance using Haversine formula in km."""
    R = 6371.0 # Earth radius in km
    
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def create_directories():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    directories = [
        'data/raw',
        'data/processed',
        'data/synthetic'
    ]
    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)
    return base_dir

def generate_withdrawal_locations(n_locations=300):
    states = ["Karnataka", "Maharashtra", "Delhi", "Tamil Nadu", "Kerala", "Telangana", "Andhra Pradesh", "Gujarat", "West Bengal", "Uttar Pradesh"]
    types = ["ATM", "BANK_BRANCH", "CASH_POINT"]
    
    # Approx bounding box for India
    lat_min, lat_max = 8.0, 37.0
    lon_min, lon_max = 68.0, 97.0
    
    locations = []
    for i in range(n_locations):
        loc = {
            "location_id": f"LOC_{str(i+1).zfill(4)}",
            "location_code": f"CASH_{random.randint(1000, 9999)}",
            "location_name": f"Synthetic Location {i+1}",
            "location_type": random.choice(types),
            "city": f"Synthetic_City_{random.randint(1, 50)}",
            "district": f"Synthetic_District_{random.randint(1, 50)}",
            "state": random.choice(states),
            "latitude": round(random.uniform(lat_min, lat_max), 6),
            "longitude": round(random.uniform(lon_min, lon_max), 6),
            "location_activity_score": round(random.uniform(0.1, 10.0), 2),
            "historical_withdrawal_frequency": random.randint(0, 500),
            "night_activity_score": round(random.uniform(0.1, 10.0), 2)
        }
        locations.append(loc)
    
    return pd.DataFrame(locations)

def generate_cases(n_cases=5000):
    categories = ["UPI_FRAUD", "PHISHING", "CARD_FRAUD", "NET_BANKING_FRAUD", "INVESTMENT_SCAM", "IMPERSONATION", "OTHER"]
    states = ["Karnataka", "Maharashtra", "Delhi", "Tamil Nadu", "Kerala", "Telangana", "Andhra Pradesh", "Gujarat", "West Bengal", "Uttar Pradesh"]
    
    lat_min, lat_max = 8.0, 37.0
    lon_min, lon_max = 68.0, 97.0
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)
    
    cases = []
    for i in range(n_cases):
        date = start_date + timedelta(days=random.randint(0, 730), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        crime_cat = random.choice(categories)
        
        # Base transaction amount depends on crime
        if crime_cat in ["INVESTMENT_SCAM"]:
            amount = round(random.uniform(50000, 1000000), 2)
        elif crime_cat in ["UPI_FRAUD"]:
            amount = round(random.uniform(100, 50000), 2)
        else:
            amount = round(random.uniform(1000, 200000), 2)
            
        case = {
            "case_id": f"CASE_{str(i+1).zfill(5)}",
            "case_number": f"FIR/{date.year}/{random.randint(100,999)}",
            "complaint_date": date.strftime('%Y-%m-%d %H:%M:%S'),
            "crime_category": crime_cat,
            "victim_state": random.choice(states),
            "victim_district": f"Synthetic_District_{random.randint(1, 50)}",
            "victim_latitude": round(random.uniform(lat_min, lat_max), 6),
            "victim_longitude": round(random.uniform(lon_min, lon_max), 6),
            "total_amount": amount,
            "transaction_count": random.randint(1, 20),
            "transaction_velocity": round(random.uniform(0.1, 5.0), 2), # transactions per hour
            "fraud_hour": date.hour,
            "fraud_day": date.weekday(),
            "historical_similarity": round(random.uniform(0.0, 1.0), 3),
            "created_at": (date + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S')
        }
        cases.append(case)
        
    return pd.DataFrame(cases)

def generate_transactions(cases_df):
    transactions = []
    tx_id_counter = 1
    
    for _, case in cases_df.iterrows():
        n_tx = case['transaction_count']
        total_amt = case['total_amount']
        
        # Split total amount into n_tx parts
        if n_tx == 1:
            amts = [total_amt]
        else:
            amts = np.random.dirichlet(np.ones(n_tx), size=1)[0] * total_amt
        
        case_date = datetime.strptime(case['complaint_date'], '%Y-%m-%d %H:%M:%S')
        
        for i in range(n_tx):
            tx = {
                "transaction_id": f"TXN_{str(tx_id_counter).zfill(7)}",
                "case_id": case['case_id'],
                "amount": round(amts[i], 2),
                "timestamp": (case_date - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S'),
                "sender_account": f"ACC_{random.randint(1000000, 9999999)}",
                "receiver_account": f"ACC_{random.randint(1000000, 9999999)}",
                "payment_mode": random.choice(["UPI", "IMPS", "NEFT", "RTGS", "CARD"])
            }
            transactions.append(tx)
            tx_id_counter += 1
            
    return pd.DataFrame(transactions)

def generate_training_dataset(cases_df, locations_df):
    training_data = []
    
    # We won't cross-join 5000 cases with 300 locations (1.5M rows) for a simple synthetic dataset.
    # Instead, we will generate ~3 candidate locations per case to evaluate.
    
    for _, case in cases_df.iterrows():
        # Sample 3-5 candidate locations for this case
        n_candidates = random.randint(3, 5)
        candidates = locations_df.sample(n_candidates)
        
        for _, loc in candidates.iterrows():
            dist = haversine_distance(
                case['victim_latitude'], case['victim_longitude'],
                loc['latitude'], loc['longitude']
            )
            
            # Pattern Generation for Target Risk
            # Higher risk if:
            # - distance is small (though cybercrime can be remote, some have local cashout)
            # - high activity score & night activity
            # - high transaction velocity & high amount
            # - high historical similarity
            
            base_risk = 0.1
            
            if dist < 100:
                base_risk += 0.2
            if loc['night_activity_score'] > 7.0 and case['fraud_hour'] in [22, 23, 0, 1, 2, 3, 4]:
                base_risk += 0.3
            if case['transaction_velocity'] > 3.0:
                base_risk += 0.1
            if case['historical_similarity'] > 0.8:
                base_risk += 0.2
                
            # Add some noise
            noise = random.uniform(-0.1, 0.1)
            target_risk = max(0.0, min(1.0, base_risk + noise))
            
            row = {
                "case_id": case['case_id'],
                "location_id": loc['location_id'],
                "transaction_amount": case['total_amount'],
                "transaction_count": case['transaction_count'],
                "transaction_velocity": case['transaction_velocity'],
                "fraud_hour": case['fraud_hour'],
                "fraud_day": case['fraud_day'],
                "crime_category": case['crime_category'],
                "victim_latitude": case['victim_latitude'],
                "victim_longitude": case['victim_longitude'],
                "location_latitude": loc['latitude'],
                "location_longitude": loc['longitude'],
                "distance_to_location": round(dist, 2),
                "historical_similarity": case['historical_similarity'],
                "location_activity_score": loc['location_activity_score'],
                "night_activity_score": loc['night_activity_score'],
                "withdrawal_frequency": loc['historical_withdrawal_frequency'],
                "target_risk": round(target_risk, 4)
            }
            training_data.append(row)
            
    return pd.DataFrame(training_data)

def main():
    print("Initializing Synthetic Dataset Generation...")
    base_dir = create_directories()
    
    print("Generating Withdrawal Locations...")
    locations_df = generate_withdrawal_locations(300)
    
    print("Generating Cases...")
    cases_df = generate_cases(5000)
    
    print("Generating Transactions...")
    transactions_df = generate_transactions(cases_df)
    
    print("Generating Training Dataset (Case-Location pairs)...")
    training_df = generate_training_dataset(cases_df, locations_df)
    
    # Save to CSV
    synth_dir = os.path.join(base_dir, 'data', 'synthetic')
    locations_df.to_csv(os.path.join(synth_dir, 'withdrawal_locations.csv'), index=False)
    cases_df.to_csv(os.path.join(synth_dir, 'cashtrail_cases.csv'), index=False)
    transactions_df.to_csv(os.path.join(synth_dir, 'cashtrail_transactions.csv'), index=False)
    training_df.to_csv(os.path.join(synth_dir, 'cashtrail_training_dataset.csv'), index=False)
    
    print(f"Generated {len(cases_df)} synthetic cases.")
    print(f"Generated {len(transactions_df)} synthetic transactions.")
    print(f"Generated {len(locations_df)} synthetic withdrawal locations.")
    print(f"Generated {len(training_df)} case-location training rows.")
    print("DATA GENERATION COMPLETE. (ALL DATA IS SYNTHETIC DEMONSTRATION DATA)")

if __name__ == "__main__":
    main()
