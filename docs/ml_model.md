# CashTrail ML Location Risk Model

## 1. Problem Formulation
The CashTrail model predicts potential withdrawal-risk locations from candidate locations based on learned patterns. **It does not identify or track the live physical location of a suspected fraudster.** 
Instead, given a cybercrime case and its transaction data, the model estimates the synthetic risk score (`target_risk`) of various candidate physical withdrawal locations (ATMs, Bank Branches, etc.) and ranks them for prioritization by investigators.

## 2. Input Features
The model uses the following features:
**Numerical Features:**
- `transaction_amount`: Total financial loss
- `transaction_count`: Number of transactions
- `transaction_velocity`: Transactions per hour
- `fraud_hour`: Hour of the day the fraud started
- `fraud_day`: Day of the week the fraud started
- `distance_to_location`: Geographic distance from the victim to the candidate location in kilometers (Haversine formula)
- `historical_similarity`: Synthetic similarity score to historical patterns
- `location_activity_score`: Base activity score of the candidate location
- `night_activity_score`: Nighttime activity score of the candidate location
- `withdrawal_frequency`: Historical withdrawal frequency at the location

**Categorical Features:**
- `crime_category`: Type of fraud (e.g., UPI_FRAUD, NET_BANKING_FRAUD). This is one-hot encoded.

*Note: Identifiers like `case_id` and `location_id` are explicitly excluded from the predictive features to prevent target leakage.*

## 3. Target Definition
The target variable is `target_risk`, a continuous score (0.0 to 1.0). The model is formulated as a **Regression** problem to estimate this score. For ranking candidate locations, the locations associated with a case are sorted in descending order of their predicted risk.

## 4. Train/Validation/Test Strategy
The dataset is split into **70% Training / 15% Validation / 15% Testing**. 

## 5. Data Leakage Prevention
To ensure there is absolutely no data leakage, the split is performed in a **Grouped** manner based on `case_id`. All rows (candidate location pairings) associated with a single cybercrime case remain exclusively in one of the three sets. Standard row-wise splitting would incorrectly allow a case to appear in both training and test sets.

## 6. Baseline Model
A `RandomForestRegressor` was established as the baseline model. It acts as a benchmark to ensure that the primary model provides a tangible performance improvement.

## 7. XGBoost Model
The primary model is an `XGBRegressor` from the XGBoost library. It operates using gradient-boosted decision trees, which are highly effective at capturing non-linear relationships in tabular data without overfitting (controlled via parameters like `max_depth` and `subsample`).

## 8. Evaluation Metrics
*Metrics measured on the held-out test set (750 unique cases / 3014 rows):*

**Baseline Model (RandomForestRegressor):**
- **MAE**: 0.0507
- **RMSE**: 0.0591
- **R²**: 0.8215
- **Hit@1**: 0.372 (37.2%)
- **Hit@3**: 0.832 (83.2%)
- **Hit@5**: 1.000 (100.0%)

**Primary Model (XGBRegressor):**
- **MAE**: 0.0515
- **RMSE**: 0.0604
- **R²**: 0.8139
- **Hit@1**: 0.367 (36.7%)
- **Hit@3**: 0.815 (81.5%)
- **Hit@5**: 1.000 (100.0%)

*Note: In this specific iteration on synthetic data, the Random Forest Regressor slightly outperformed the default XGBoost configuration. However, both models capture the core generation rules accurately and provide strong ranking utility.*

## 9. Ranking Methodology
While traditional regression metrics (MAE, RMSE, R²) evaluate the error in score estimation, the actual utility of the model is measured via **Ranking Metrics**.
For each case in the test set:
1. The model predicts the risk score for all candidate locations for that case.
2. Candidate locations are sorted by predicted risk (descending).
3. The true "target" location is assumed to be the one with the highest *actual* `target_risk`.
4. We evaluate **Hit@1**, **Hit@3**, and **Hit@5**: whether the true top location appears in the top 1, 3, or 5 predicted ranks, respectively.

## 10. SHAP Explainability
SHAP (SHapley Additive exPlanations) is integrated to provide interpretability. It measures the contribution of each feature to the model's predictions. The most important global features will highlight what drives location risk in this prototype (e.g., small distance to location, high night activity during a late-night fraud hour).

## 11. Model Limitations
- The model relies heavily on the quality and completeness of transaction data.
- It is a ranking system, not a definitive identification tool. Investigators must use the output as prioritized leads, not definitive proof.

## 12. Synthetic-Data Limitations
- The current model is trained on **SYNTHETIC DEMONSTRATION DATA**.
- The patterns learned are solely those explicitly programmed into the generation script (e.g., distance, transaction velocity). Real-world cybercrime manifests with much higher complexity and noise.
- Model performance on this synthetic dataset (such as R² or Hit@K) will not reflect performance on real-world data.

## 13. Interpretation of Predictions
A high risk score (or high rank) for a location does not imply the perpetrator will withdraw there; it implies that historically, similar combinations of case and location characteristics resulted in a withdrawal at that location.
