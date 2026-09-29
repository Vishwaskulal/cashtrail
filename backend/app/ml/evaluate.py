import os
import sys
import json
import joblib
import pandas as pd

# Allow importing from backend
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(base_dir)

from backend.app.ml.train import load_data, split_by_case, calculate_regression_metrics, calculate_ranking_metrics, get_artifacts_dir

def main():
    print("Loading test data...")
    df = load_data()
    _, _, test_df = split_by_case(df)
    
    print(f"Test cases: {test_df['case_id'].nunique()} ({len(test_df)} rows)")
    
    artifacts_dir = get_artifacts_dir()
    model_path = os.path.join(artifacts_dir, 'model.pkl')
    metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
    
    if not os.path.exists(model_path) or not os.path.exists(metadata_path):
        print("Model artifacts not found. Please run train.py first.")
        return
        
    print("Loading model and metadata...")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    model_pipeline = joblib.load(model_path)
    
    print(f"Loaded Model: {metadata['model_name']} (Version {metadata['model_version']})")
    
    features = metadata['features']
    target = metadata['target_name']
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    print("Generating predictions...")
    preds = model_pipeline.predict(X_test)
    
    print("Calculating metrics...")
    reg_metrics = calculate_regression_metrics(y_test, preds)
    rank_metrics = calculate_ranking_metrics(test_df, preds)
    
    print("\n=== EVALUATION RESULTS ===")
    print(f"Model: {metadata['model_name']}")
    print(f"Version: {metadata['model_version']}")
    print(f"Test Set: {test_df['case_id'].nunique()} unique cases")
    print("\nRegression Metrics:")
    for k, v in reg_metrics.items():
        print(f"  {k}: {v:.4f}")
        
    print("\nRanking Metrics (Candidate Location Retrieval):")
    for k, v in rank_metrics.items():
        print(f"  {k}: {v:.4f}")
        
    print("\nSample Case Output:")
    # Show output conceptually as requested
    sample_case = test_df['case_id'].unique()[0]
    sample_rows = test_df[test_df['case_id'] == sample_case].copy()
    sample_preds = model_pipeline.predict(sample_rows[features])
    sample_rows['Predicted_Risk'] = sample_preds
    
    sample_rows = sample_rows.sort_values(by='Predicted_Risk', ascending=False)
    
    print(f"\nCase: {sample_case}")
    print("Candidate Locations:")
    for _, row in sample_rows.iterrows():
        print(f"\nLocation: {row['location_id']}")
        print(f"Predicted Risk Score: {row['Predicted_Risk']:.4f}")
        print(f"Actual Target Score: {row['target_risk']:.4f}")

if __name__ == "__main__":
    main()
