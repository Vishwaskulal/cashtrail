from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AlertBase(BaseModel):
    case_number: str
    prediction_id: int
    location_code: str
    alert_type: str
    risk_level: str
    risk_score: float
    title: str
    message: str
    status: str

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None

    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int

class AlertStatusUpdate(BaseModel):
    status: str # ACKNOWLEDGED, RESOLVED, DISMISSED
    user_id: Optional[int] = None # Simulating the authorized user
