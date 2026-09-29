import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def haversine_distance(lat1, lon1, lat2, lon2):
    """Reusable geographic-distance calculation in km."""
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

def prepare_features(df):
    """
    Handle missing values, encode categorical features, scale numerical features.
    """
    df_processed = df.copy()
    
    # Fill missing values if any
    df_processed.fillna(0, inplace=True)
    
    # Scale numerical features
    num_cols = ['transaction_amount', 'transaction_count', 'transaction_velocity', 
                'distance_to_location', 'historical_similarity', 
                'location_activity_score', 'night_activity_score', 'withdrawal_frequency']
    
    # Only scale if columns exist
    existing_num_cols = [c for c in num_cols if c in df_processed.columns]
    if existing_num_cols:
        scaler = StandardScaler()
        df_processed[existing_num_cols] = scaler.fit_transform(df_processed[existing_num_cols])
        
    # One-hot encode categorical features (like crime_category)
    cat_cols = ['crime_category']
    existing_cat_cols = [c for c in cat_cols if c in df_processed.columns]
    if existing_cat_cols:
        df_processed = pd.get_dummies(df_processed, columns=existing_cat_cols, drop_first=True)
        
    return df_processed

def split_dataset(df, test_size=0.3, val_size=0.5, random_seed=42):
    """
    Prepare a reproducible train/validation/test split.
    Recommended overall: 70% training, 15% validation, 15% testing.
    
    IMPORTANT: To avoid data leakage, we split by case_id, not by row.
    """
    # Get unique cases
    unique_cases = df['case_id'].unique()
    
    # Split cases into train and temp (val+test)
    cases_train, cases_temp = train_test_split(
        unique_cases, test_size=test_size, random_state=random_seed
    )
    
    # Split temp into val and test (50/50 of the 30% -> 15% each)
    cases_val, cases_test = train_test_split(
        cases_temp, test_size=val_size, random_state=random_seed
    )
    
    # Create final dataframes
    train_df = df[df['case_id'].isin(cases_train)].copy()
    val_df = df[df['case_id'].isin(cases_val)].copy()
    test_df = df[df['case_id'].isin(cases_test)].copy()
    
    return train_df, val_df, test_df
