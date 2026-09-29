from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.prediction import (
    PredictionAnalyzeRequest, 
    PredictionResponse, 
    ModelStatusResponse,
    LocationResponse
)
from app.services.prediction_service import prediction_service
from app.models.withdrawal_location import WithdrawalLocation

router = APIRouter(prefix="/api", tags=["Predictions"])

from app.models.prediction import Prediction

@router.get("/predictions", response_model=List[PredictionResponse])
def get_all_predictions(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve recent predictions."""
    preds = db.query(Prediction).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()
    # Serialize using prediction_service.get_prediction logic or simple map
    results = []
    for p in preds:
        locs = []
        for p_loc in sorted(p.locations, key=lambda x: x.risk_score, reverse=True):
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
        for rf in p.risk_factors:
            rfs.append({
                "factor_name": rf.factor_name,
                "importance_score": rf.importance_score,
                "impact_direction": rf.impact_direction
            })
        results.append({
            "case_id": p.case_number,
            "model_version": p.model_version,
            "prediction_timestamp": p.prediction_timestamp,
            "overall_risk_level": p.overall_risk_level,
            "locations": locs,
            "risk_factors": rfs,
            "alerts_generated": 0 # Not persisted currently in Prediction, but schema allows Optional
        })
    return results

@router.get("/predictions/model-status", response_model=ModelStatusResponse)
def get_model_status():
    """Check if the ML model is loaded and ready."""
    return prediction_service.get_model_status()

@router.post("/predictions/analyze", response_model=PredictionResponse)
def analyze_case(request: PredictionAnalyzeRequest, db: Session = Depends(get_db)):
    """Run prediction on a case and rank candidate withdrawal locations."""
    return prediction_service.analyze_case(db, request, top_k=request.top_k)

@router.get("/predictions/{case_id}", response_model=PredictionResponse)
def get_prediction(case_id: str, db: Session = Depends(get_db)):
    """Retrieve the most recent prediction results for a case."""
    return prediction_service.get_prediction(db, case_id)

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(
    state: Optional[str] = None,
    district: Optional[str] = None,
    city: Optional[str] = None,
    location_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return candidate withdrawal locations, with optional filtering."""
    query = db.query(WithdrawalLocation).filter(WithdrawalLocation.state == 'Karnataka')
    if state and state != 'Karnataka':
        return [] # Return empty if querying non-Karnataka
    if district:
        query = query.filter(WithdrawalLocation.district == district)
    if city:
        query = query.filter(WithdrawalLocation.city == city)
    if location_type:
        query = query.filter(WithdrawalLocation.location_type == location_type)
        
    locations = query.all()
    results = []
    for loc in locations:
        results.append({
            "location_id": loc.location_code,
            "location_name": loc.location_name,
            "location_type": loc.location_type,
            "city": loc.city,
            "district": loc.district,
            "state": loc.state,
            "latitude": float(loc.latitude),
            "longitude": float(loc.longitude),
            "location_activity_score": float(loc.location_activity_score) if loc.location_activity_score else 0.0,
            "night_activity_score": float(loc.night_activity_score) if loc.night_activity_score else 0.0,
            "historical_withdrawal_frequency": loc.historical_withdrawal_frequency or 0
        })
    return results
