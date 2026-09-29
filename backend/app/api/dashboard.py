from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.case import Case
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.investigation import InvestigationNote
from app.schemas.dashboard import DashboardStats, InvestigationNoteCreate, InvestigationNoteResponse, CaseListResponse, CaseSummary

router = APIRouter(tags=["dashboard"])

@router.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_cases = db.query(func.count(Case.id)).scalar() or 0
    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "ACTIVE").scalar() or 0
    
    # We define HIGH_RISK cases as those having a prediction with overall_risk_level HIGH or CRITICAL
    high_risk_cases = db.query(func.count(func.distinct(Prediction.case_number))).filter(
        Prediction.overall_risk_level.in_(["HIGH", "CRITICAL"])
    ).scalar() or 0

    return {
        "total_cases": total_cases,
        "high_risk_cases": high_risk_cases,
        "total_predictions": total_predictions,
        "active_alerts": active_alerts
    }

@router.get("/api/cases", response_model=CaseListResponse)
def get_recent_cases(limit: int = 50, db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_at.desc()).limit(limit).all()
    
    summaries = []
    for c in cases:
        # Check latest prediction for risk level
        latest_pred = db.query(Prediction).filter(Prediction.case_number == c.case_number).order_by(Prediction.prediction_timestamp.desc()).first()
        risk_level = latest_pred.overall_risk_level if latest_pred else "UNKNOWN"
        
        summaries.append({
            "case_number": c.case_number,
            "complaint_date": c.complaint_date,
            "crime_category": c.crime_category,
            "total_amount": float(c.total_amount),
            "status": c.status,
            "risk_level": risk_level
        })
        
    return {"cases": summaries, "total": len(summaries)}

@router.get("/api/cases/{case_number}", response_model=CaseSummary)
def get_case(case_number: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.case_number == case_number).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
        
    latest_pred = db.query(Prediction).filter(Prediction.case_number == c.case_number).order_by(Prediction.prediction_timestamp.desc()).first()
    risk_level = latest_pred.overall_risk_level if latest_pred else "UNKNOWN"
    
    return {
        "case_number": c.case_number,
        "complaint_date": c.complaint_date,
        "crime_category": c.crime_category,
        "total_amount": float(c.total_amount),
        "status": c.status,
        "risk_level": risk_level
    }

@router.get("/api/investigations/cases/{case_number}/notes", response_model=list[InvestigationNoteResponse])
def get_investigation_notes(case_number: str, db: Session = Depends(get_db)):
    notes = db.query(InvestigationNote).filter(InvestigationNote.case_number == case_number).order_by(InvestigationNote.created_at.desc()).all()
    return notes

@router.post("/api/investigations/cases/{case_number}/notes", response_model=InvestigationNoteResponse)
def create_investigation_note(case_number: str, note_in: InvestigationNoteCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_number == case_number).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    note = InvestigationNote(
        case_number=case_number,
        author_id=note_in.author_id,
        note_content=note_in.note_content
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
