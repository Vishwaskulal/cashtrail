import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import shap

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def get_data_path():
    return os.path.join(get_base_dir(), 'data', 'synthetic', 'cashtrail_training_dataset.csv')

def get_artifacts_dir():
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    return artifacts_dir

def load_data():
    path = get_data_path()
    df = pd.read_csv(path)
    return df

def split_by_case(df, test_val_size=0.3, random_seed=RANDOM_SEED):
    unique_cases = df['case_id'].unique()
    
    cases_train, cases_temp = train_test_split(unique_cases, test_size=test_val_size, random_state=random_seed)
    cases_val, cases_test = train_test_split(cases_temp, test_size=0.5, random_state=random_seed)
    
    train_df = df[df['case_id'].isin(cases_train)].copy()
    val_df = df[df['case_id'].isin(cases_val)].copy()
    test_df = df[df['case_id'].isin(cases_test)].copy()
    
    return train_df, val_df, test_df

def calculate_ranking_metrics(df, predictions, k_values=[1, 3, 5]):
    """
    Calculate Hit@K.
    For each case, we identify the candidate with the highest actual target_risk as the 'ground truth'.
    Then we check if this ground truth location is in the top K highest predicted risk locations.
    """
    df_eval = df[['case_id', 'location_id', 'target_risk']].copy()
    df_eval['predicted_risk'] = predictions
    
    hits = {k: 0 for k in k_values}
    total_cases = 0
    
    for case_id, group in df_eval.groupby('case_id'):
        if len(group) == 0:
            continue
            
        # Ground truth: location with the max target_risk
        true_best_loc = group.loc[group['target_risk'].idxmax(), 'location_id']
        
        # Predicted best locations
        sorted_group = group.sort_values(by='predicted_risk', ascending=False)
        top_k_locations = sorted_group['location_id'].tolist()
        
        for k in k_values:
            if true_best_loc in top_k_locations[:k]:
                hits[k] += 1
                
        total_cases += 1
        
    metrics = {f'Hit@{k}': hits[k] / total_cases for k in k_values}
    return metrics

def calculate_regression_metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R2': r2_score(y_true, y_pred)
    }

def main():
    print("Loading data...")
    df = load_data()
    
    print("Splitting data by case_id...")
    train_df, val_df, test_df = split_by_case(df)
    
    print(f"Train cases: {train_df['case_id'].nunique()} ({len(train_df)} rows)")
    print(f"Val cases: {val_df['case_id'].nunique()} ({len(val_df)} rows)")
    print(f"Test cases: {test_df['case_id'].nunique()} ({len(test_df)} rows)")
    
    # Define features and target
    target = 'target_risk'
    num_features = [
        'transaction_amount', 'transaction_count', 'transaction_velocity', 
        'fraud_hour', 'fraud_day', 'distance_to_location', 
        'historical_similarity', 'location_activity_score', 
        'night_activity_score', 'withdrawal_frequency'
    ]
    cat_features = ['crime_category']
    features = num_features + cat_features
    
    X_train, y_train = train_df[features], train_df[target]
    X_val, y_val = val_df[features], val_df[target]
    X_test, y_test = test_df[features], test_df[target]
    
    # Build Preprocessing Pipeline
    print("Building preprocessing pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ])
    
    # Train Baseline (Random Forest)
    print("Training Baseline Model (RandomForestRegressor)...")
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(n_estimators=100, max_depth=10, random_state=RANDOM_SEED))
    ])
    rf_pipeline.fit(X_train, y_train)
    
    rf_preds = rf_pipeline.predict(X_test)
    rf_metrics = calculate_regression_metrics(y_test, rf_preds)
    rf_ranking = calculate_ranking_metrics(test_df, rf_preds)
    print("Baseline Metrics:", {**rf_metrics, **rf_ranking})
    
    # Train Primary Model (XGBoost)
    print("Training Primary Model (XGBRegressor)...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=100, 
        max_depth=6, 
        learning_rate=0.1, 
        subsample=0.8,
        colsample_bytree=0.8,
        base_score=0.5,
        random_state=RANDOM_SEED
    )
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', xgb_model)
    ])
    
    # Fit XGBoost (using validation set for early stopping requires some manual handling with pipelines, 
    # we'll just fit it directly with the preprocessor for simplicity since this is a demonstration)
    xgb_pipeline.fit(X_train, y_train)
    
    xgb_preds = xgb_pipeline.predict(X_test)
    xgb_metrics = calculate_regression_metrics(y_test, xgb_preds)
    xgb_ranking = calculate_ranking_metrics(test_df, xgb_preds)
    print("XGBoost Metrics:", {**xgb_metrics, **xgb_ranking})
    
    # SHAP Explainability
    print("Generating SHAP feature importance...")
    # Transform training data to pass to SHAP
    X_train_transformed = preprocessor.transform(X_train)
    
    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_['cat']
    cat_feature_names = cat_encoder.get_feature_names_out(cat_features)
    all_feature_names = num_features + list(cat_feature_names)
    
    # Create explainer (using generic Explainer instead of TreeExplainer due to XGB 3.x parser bug)
    sample_size = min(100, X_train_transformed.shape[0])
    background = X_train_transformed[:sample_size]
    
    # Use exact/permutation explainer
    explainer = shap.Explainer(xgb_pipeline.named_steps['model'].predict, background)
    
    # Calculate shap values for the sample
    shap_values = explainer(background)
    
    # Mean absolute SHAP values for feature importance
    mean_shap = np.abs(shap_values.values).mean(axis=0)
    shap_importance = pd.DataFrame({'feature': all_feature_names, 'importance': mean_shap})
    shap_importance = shap_importance.sort_values(by='importance', ascending=False)
    
    print("\nTop 5 Important Features (SHAP):")
    print(shap_importance.head(5).to_string(index=False))
    
    # Save Models and Metadata
    print("\nSaving artifacts...")
    artifacts_dir = get_artifacts_dir()
    
    joblib.dump(xgb_pipeline, os.path.join(artifacts_dir, 'model.pkl'))
    
    metadata = {
        'model_name': 'CashTrail XGBoost Location Risk Model',
        'model_version': '1.0.0',
        'training_date': datetime.now().isoformat(),
        'dataset_version': 'synthetic_v1',
        'features': features,
        'target_name': target,
        'training_case_count': int(train_df['case_id'].nunique()),
        'validation_case_count': int(val_df['case_id'].nunique()),
        'test_case_count': int(test_df['case_id'].nunique()),
        'random_seed': RANDOM_SEED,
        'evaluation_metrics': {
            'Baseline': {**rf_metrics, **rf_ranking},
            'XGBoost': {**xgb_metrics, **xgb_ranking}
        },
        'top_features_shap': shap_importance.head(10).to_dict(orient='records')
    }
    
    with open(os.path.join(artifacts_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("Training complete. Artifacts saved in", artifacts_dir)

if __name__ == "__main__":
    main()
