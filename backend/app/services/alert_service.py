import os
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.case import Case

class AlertService:
    def __init__(self):
        # Default threshold is 0.80 if not set in environment
        self.alert_threshold = float(os.getenv("ALERT_RISK_THRESHOLD", "0.80"))

    def evaluate_prediction_for_alerts(self, db: Session, case: Case, prediction_id: int, locations: list):
        """
        Evaluates a list of predicted locations. 
        If a location meets the risk threshold, generates an alert unless an active one already exists.
        Returns the number of alerts generated.
        """
        alerts_generated = 0
        
        for loc in locations:
            risk_score = loc['risk_score']
            if risk_score >= self.alert_threshold:
                # Check for existing ACTIVE alert for this case and location
                existing_alert = db.query(Alert).filter(
                    Alert.case_number == case.case_number,
                    Alert.location_code == loc['location_id'], # In our schema we returned location_code as location_id
                    Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"]) # Prevent duplicate while someone is working on it
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    alert_type = "CRITICAL_RISK_LOCATION" if risk_score >= 0.90 else "HIGH_RISK_LOCATION"
                    
                    message = (
                        f"Potential high-risk withdrawal location identified for case {case.case_number}. "
                        f"Location: {loc['location_name']}. "
                        f"Risk Score: {risk_score:.4f}. "
                        "Review recommended by authorized personnel."
                    )
                    
                    new_alert = Alert(
                        case_number=case.case_number,
                        prediction_id=prediction_id,
                        location_code=loc['location_id'],
                        alert_type=alert_type,
                        risk_level=loc['risk_level'],
                        risk_score=risk_score,
                        title=f"High Risk Location - {case.case_number}",
                        message=message,
                        status="ACTIVE"
                    )
                    
                    db.add(new_alert)
                    alerts_generated += 1
        
        if alerts_generated > 0:
            db.commit()
            
        return alerts_generated

    def get_alerts(self, db: Session, status: str = None, risk_level: str = None, case_number: str = None):
        query = db.query(Alert)
        
        if status and status != 'ALL':
            query = query.filter(Alert.status == status)
        if risk_level and risk_level != 'ALL':
            query = query.filter(Alert.risk_level == risk_level)
        if case_number:
            query = query.filter(Alert.case_number == case_number)
            
        return query.order_by(Alert.created_at.desc()).all()

    def get_alert(self, db: Session, alert_id: int):
        return db.query(Alert).filter(Alert.id == alert_id).first()

    def update_alert_status(self, db: Session, alert_id: int, new_status: str, user_id: int = None):
        from datetime import datetime
        alert = self.get_alert(db, alert_id)
        if not alert:
            return None
            
        alert.status = new_status
        if new_status == "ACKNOWLEDGED":
            alert.acknowledged_at = datetime.utcnow()
            if user_id:
                alert.acknowledged_by = user_id
        elif new_status in ["RESOLVED", "DISMISSED"]:
            alert.resolved_at = datetime.utcnow()
            if user_id:
                alert.resolved_by = user_id
                
        db.commit()
        db.refresh(alert)
        return alert

alert_service = AlertService()
