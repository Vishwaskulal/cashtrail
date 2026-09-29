from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_cases: int
    high_risk_cases: int
    total_predictions: int
    active_alerts: int

class InvestigationNoteCreate(BaseModel):
    note_content: str
    author_id: int

class InvestigationNoteResponse(BaseModel):
    id: int
    case_number: str
    author_id: int
    note_content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CaseSummary(BaseModel):
    case_number: str
    complaint_date: datetime
    crime_category: str
    total_amount: float
    status: str
    risk_level: Optional[str] = "UNKNOWN"
    
    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    cases: List[CaseSummary]
    total: int
