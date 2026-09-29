import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.case import Case
from app.models.withdrawal_location import WithdrawalLocation
from app.models.prediction import Prediction, PredictionLocation

class PredictionService:
    def __init__(self):
        self.model_pipeline = None
        self.metadata = None
        self.features = []
        self._load_model()
        
    def _load_model(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        artifacts_dir = os.path.join(base_dir, 'app', 'ml', 'artifacts')
        
        model_path = os.path.join(artifacts_dir, 'model.pkl')
        metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
        
        if os.path.exists(model_path) and os.path.exists(metadata_path):
            try:
                self.model_pipeline = joblib.load(model_path)
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                self.features = self.metadata.get('features', [])
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print("Model artifacts not found.")

    def get_model_status(self):
        if self.model_pipeline and self.metadata:
            return {
                "model_loaded": True,
                "model_name": self.metadata.get('model_name', 'Unknown'),
                "model_version": self.metadata.get('model_version', 'Unknown'),
                "feature_count": len(self.features),
                "status": "ready"
            }
        return {
            "model_loaded": False,
            "model_name": "",
            "model_version": "",
            "feature_count": 0,
            "status": "unavailable"
        }

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1 = float(lat1), float(lon1)
        lat2, lon2 = float(lat2), float(lon2)
        R = 6371.0 # Earth radius in km
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c

    def _get_risk_level(self, score):
        # Prototype decision thresholds based on synthetic output distribution
        if score < 0.25:
            return "LOW"
        elif score < 0.50:
            return "MEDIUM"
        elif score < 0.75:
            return "HIGH"
        else:
            return "CRITICAL"

    def analyze_case(self, db: Session, request, top_k: int = 5):
        if not self.model_pipeline:
            raise HTTPException(status_code=503, detail="Model is currently unavailable")
            
        case = db.query(Case).filter(Case.case_number == request.case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
            
        locations = db.query(WithdrawalLocation).filter(WithdrawalLocation.state == 'Karnataka').all()
        if not locations:
            raise HTTPException(status_code=500, detail="No candidate withdrawal locations found in Karnataka")
            
        # Construct feature dataset
        records = []
        for loc in locations:
            dist = self._haversine_distance(
                request.victim_latitude, request.victim_longitude,
                loc.latitude, loc.longitude
            )
            
            # Reconstruct the feature dict as expected by the model pipeline
            record = {
                'transaction_amount': request.transaction_amount,
                'transaction_count': request.transaction_count,
                'transaction_velocity': request.transaction_velocity,
                'fraud_hour': request.fraud_hour,
                'fraud_day': request.fraud_day,
                'distance_to_location': float(dist),
                'historical_similarity': request.historical_similarity,
                'location_activity_score': loc.location_activity_score,
                'night_activity_score': loc.night_activity_score,
                'withdrawal_frequency': loc.historical_withdrawal_frequency,
                'crime_category': request.crime_category
            }
            records.append(record)
            
        df = pd.DataFrame(records)
        
        # Ensure only model features are passed, in correct order
        if self.features:
            df = df[self.features]
            
        # Run Inference
        preds = self.model_pipeline.predict(df)
        
        # Zip predictions with locations
        results = []
        for loc, score in zip(locations, preds):
            score = float(score)
            results.append({
                "location": loc,
                "risk_score": score,
                "risk_level": self._get_risk_level(score)
            })
            
        # Rank locations
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        top_results = results[:top_k]
        
        overall_risk_level = top_results[0]["risk_level"] if top_results else "LOW"
        
        # Save Prediction to DB
        prediction = Prediction(
            case_number=case.case_number,
            model_version=self.metadata.get('model_version', 'Unknown'),
            overall_risk_level=overall_risk_level
        )
        db.add(prediction)
        db.flush()
        
        # Save Risk Factors from model metadata SHAP values
        from app.models.risk_factor import RiskFactor
        top_features = self.metadata.get('top_features_shap', [])
        response_risk_factors = []
        for feature in top_features:
            rf = RiskFactor(
                prediction_id=prediction.id,
                factor_name=feature['feature'],
                importance_score=feature['importance'],
                impact_direction="POSITIVE" # Or determine based on feature value
            )
            db.add(rf)
            response_risk_factors.append({
                "factor_name": feature['feature'],
                "importance_score": feature['importance'],
                "impact_direction": "POSITIVE"
            })
        
        response_locations = []
        for res in top_results:
            loc = res["location"]
            pred_loc = PredictionLocation(
                prediction_id=prediction.id,
                location_code=loc.location_code,
                risk_score=res["risk_score"],
                confidence_score=res["risk_score"], # Prototype uses score as confidence proxy
                risk_level=res["risk_level"]
            )
            db.add(pred_loc)
            
            response_locations.append({
                "location_id": loc.location_code,
                "location_name": loc.location_name,
                "city": loc.city,
                "district": loc.district,
                "state": loc.state,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "risk_score": res["risk_score"],
                "confidence_score": res["risk_score"],
                "risk_level": res["risk_level"]
            })
            
        db.commit()
        
        # Evaluate for alerts
        from app.services.alert_service import alert_service
        alerts_generated = alert_service.evaluate_prediction_for_alerts(db, case, prediction.id, response_locations)
        
        return {
            "case_id": case.case_number,
            "model_version": prediction.model_version,
            "prediction_timestamp": prediction.prediction_timestamp,
            "overall_risk_level": overall_risk_level,
            "locations": response_locations,
            "risk_factors": response_risk_factors,
            "alerts_generated": alerts_generated
        }

    def get_prediction(self, db: Session, case_id: str):
        # Get most recent prediction
        prediction = db.query(Prediction).filter(Prediction.case_number == case_id)\
                       .order_by(Prediction.prediction_timestamp.desc()).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="No prediction found for this case")
            
        locs = []
        # Sort locations by risk score descending
        sorted_locs = sorted(prediction.locations, key=lambda x: x.risk_score, reverse=True)
        for p_loc in sorted_locs:
            locs.append({
                "location_id": p_loc.location_code,
                "location_name": p_loc.location.location_name,
                "city": p_loc.location.city,
                "district": p_loc.location.district,
                "state": p_loc.location.state,
                "latitude": p_loc.location.latitude,
                "longitude": p_loc.location.longitude,
                "risk_score": p_loc.risk_score,
                "confidence_score": p_loc.confidence_score,
                "risk_level": p_loc.risk_level
            })
            
        rfs = []
        for rf in prediction.risk_factors:
            rfs.append({
                "factor_name": rf.factor_name,
                "importance_score": rf.importance_score,
                "impact_direction": rf.impact_direction
            })
            
        return {
            "case_id": prediction.case_number,
            "model_version": prediction.model_version,
            "prediction_timestamp": prediction.prediction_timestamp,
            "overall_risk_level": prediction.overall_risk_level,
            "locations": locs,
            "risk_factors": rfs
        }

# Singleton instance
prediction_service = PredictionService()
