from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PredictionAnalyzeRequest(BaseModel):
    case_id: str = Field(..., description="The ID of the case to analyze")
    transaction_amount: float = Field(..., ge=0, description="Total amount involved")
    transaction_count: int = Field(..., ge=1, description="Number of transactions")
    transaction_velocity: float = Field(..., description="Transactions per hour")
    fraud_hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)")
    fraud_day: int = Field(..., ge=0, le=6, description="Day of the week (0-6)")
    crime_category: str = Field(..., description="Category of cybercrime")
    victim_latitude: float = Field(..., ge=-90.0, le=90.0, description="Victim latitude")
    victim_longitude: float = Field(..., ge=-180.0, le=180.0, description="Victim longitude")
    historical_similarity: float = Field(..., description="Historical similarity score")
    top_k: int = Field(5, ge=1, le=20, description="Number of top locations to return")

class PredictionLocationResponse(BaseModel):
    location_id: str
    location_name: str
    city: str
    district: str
    state: str
    latitude: float
    longitude: float
    risk_score: float
    confidence_score: float
    risk_level: str

class RiskFactorResponse(BaseModel):
    factor_name: str
    importance_score: float
    impact_direction: str

class PredictionResponse(BaseModel):
    case_id: str
    model_version: str
    prediction_timestamp: datetime
    overall_risk_level: str
    locations: List[PredictionLocationResponse]
    risk_factors: Optional[List[RiskFactorResponse]] = []
    alerts_generated: Optional[int] = 0

class ModelStatusResponse(BaseModel):
    model_loaded: bool
    model_name: str
    model_version: str
    feature_count: int
    status: str

class LocationResponse(BaseModel):
    location_id: str
    location_name: str
    location_type: str
    city: str
    district: str
    state: str
    latitude: float
    longitude: float
    location_activity_score: float
    night_activity_score: float
    historical_withdrawal_frequency: int
