from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.alert import AlertResponse, AlertListResponse, AlertStatusUpdate
from app.services.alert_service import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("", response_model=AlertListResponse)
def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    case_number: Optional[str] = Query(None, description="Filter by case number"),
    db: Session = Depends(get_db)
):
    alerts = alert_service.get_alerts(db, status=status, risk_level=risk_level, case_number=case_number)
    return {"alerts": alerts, "total": len(alerts)}

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, update_data: AlertStatusUpdate = None, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status not in ["ACTIVE"]:
        raise HTTPException(status_code=400, detail="Only ACTIVE alerts can be acknowledged")
        
    user_id = update_data.user_id if update_data else None
    updated_alert = alert_service.update_alert_status(db, alert_id, "ACKNOWLEDGED", user_id=user_id)
    return updated_alert

@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, update_data: AlertStatusUpdate = None, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if alert.status not in ["ACTIVE", "ACKNOWLEDGED"]:
        raise HTTPException(status_code=400, detail="Only ACTIVE or ACKNOWLEDGED alerts can be resolved")
        
    user_id = update_data.user_id if update_data else None
    updated_alert = alert_service.update_alert_status(db, alert_id, "RESOLVED", user_id=user_id)
    return updated_alert

@router.patch("/{alert_id}/dismiss", response_model=AlertResponse)
def dismiss_alert(alert_id: int, update_data: AlertStatusUpdate = None, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if alert.status not in ["ACTIVE"]:
        raise HTTPException(status_code=400, detail="Only ACTIVE alerts can be dismissed")
        
    user_id = update_data.user_id if update_data else None
    updated_alert = alert_service.update_alert_status(db, alert_id, "DISMISSED", user_id=user_id)
    return updated_alert
