import os
import pandas as pd

def get_data_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_dir, 'data', 'synthetic')

def load_cases():
    """Load the synthetic cases dataset."""
    path = os.path.join(get_data_dir(), 'cashtrail_cases.csv')
    return pd.read_csv(path)

def load_transactions():
    """Load the synthetic transactions dataset."""
    path = os.path.join(get_data_dir(), 'cashtrail_transactions.csv')
    return pd.read_csv(path)

def load_withdrawal_locations():
    """Load the synthetic withdrawal locations dataset."""
    path = os.path.join(get_data_dir(), 'withdrawal_locations.csv')
    return pd.read_csv(path)

def load_training_dataset():
    """Load the case-location pairs training dataset."""
    path = os.path.join(get_data_dir(), 'cashtrail_training_dataset.csv')
    return pd.read_csv(path)

def validate_data(df, name="Dataset"):
    """Basic validation checks for loaded datasets."""
    report = [f"--- Validation Report for {name} ---"]
    report.append(f"Total rows: {len(df)}")
    
    missing_vals = df.isnull().sum()
    if missing_vals.sum() > 0:
        report.append(f"Missing values found:\n{missing_vals[missing_vals > 0]}")
    else:
        report.append("No missing values.")
        
    # Check duplicates if id columns exist
    id_cols = [col for col in df.columns if col.endswith('_id')]
    for id_col in id_cols:
        if id_col != 'location_id' or 'case_id' not in df.columns: # Skip composite check for training set here
            dupes = df[id_col].duplicated().sum()
            report.append(f"Duplicate {id_col}s: {dupes}")
            
    return "\n".join(report)
