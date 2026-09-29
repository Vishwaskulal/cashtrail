# CashTrail Synthetic Dataset Documentation

**DISCLAIMER: THIS IS SYNTHETIC DEMONSTRATION DATA**

All data described here is completely synthetic and generated exclusively for demonstration and development purposes of the CashTrail prototype. It does not represent real cybercrime statistics, actual hotspots, or real victim identities. Real deployment would require authorized and validated data.

## 1. Purpose of Synthetic Data
The purpose of this synthetic dataset is to establish a robust data processing pipeline and train an initial prototype prediction model. It allows the development of machine learning algorithms to learn plausible patterns without relying on sensitive or real-world restricted data.

## 2. Dataset Overview
The synthetic dataset is composed of four main files stored in `data/synthetic/`:
- `cashtrail_cases.csv`: Contains metadata for ~5,000 synthetic cybercrime cases.
- `cashtrail_transactions.csv`: Contains individual transaction details linked to cases.
- `withdrawal_locations.csv`: Contains ~300 candidate ATM/bank locations.
- `cashtrail_training_dataset.csv`: Case-location pairs with synthetic target risk for model training.

## 3. Features
Important features across the datasets:

### Cases
- `case_id`: Unique identifier for the case.
- `crime_category`: Type of cybercrime (e.g., UPI_FRAUD, PHISHING).
- `total_amount`: Total financial loss.
- `transaction_count`: Number of transactions involved.
- `transaction_velocity`: Transactions per hour.
- `victim_latitude`, `victim_longitude`: Synthetic victim location.
- `fraud_hour`, `fraud_day`: Temporal features of the fraud.
- `historical_similarity`: A synthetic score representing similarity to known past cases.

### Candidate Withdrawal Locations
- `location_id`: Unique location identifier.
- `location_type`: ATM, BANK_BRANCH, or CASH_POINT.
- `latitude`, `longitude`: Geographic coordinates.
- `location_activity_score`: General activity score.
- `night_activity_score`: Activity specifically during nighttime hours.

### Case-Location Training Pairs
- `distance_to_location`: Geographic distance (Haversine formula in km) between the victim and candidate location.
- `target_risk`: A continuous synthetic target indicating the relative likelihood/risk of that candidate location for the case.

## 4. Synthetic Pattern Generation
The dataset contains learnable relationships generated deliberately so that a machine learning model can learn them:
- **Geographic Influence**: Closer candidate locations generally have slightly higher risk, representing local cashout operations.
- **Time-of-Day Influence**: Locations with high `night_activity_score` receive a higher risk target if the fraud occurred during late hours (e.g., 10 PM - 4 AM).
- **Transaction Patterns**: High `transaction_velocity` boosts risk scores.
- **Historical Similarity**: Cases with high historical similarity increase the likelihood of matching locations.
- **Noise**: Reasonable uniform noise was introduced to prevent the relationships from being perfectly deterministic, making the ML task realistic.

## 5. Train/Validation/Test Split Strategy
Data splitting is performed at the **Case ID** level to prevent data leakage. If multiple rows belong to the same case (e.g., multiple candidate locations evaluated), they will all be placed in either the training, validation, or test set.
- 70% Training
- 15% Validation
- 15% Testing

## 6. Limitations
Synthetic data cannot perfectly capture the complex, evolving nuances of real cybercriminal networks. Patterns learned by models trained on this data will be purely reflective of the rules embedded in the generation script. It is strictly a prototype.
