from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), ForeignKey("cases.case_number"), index=True, nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), index=True, nullable=False)
    location_code = Column(String(100), nullable=False)
    
    alert_type = Column(String(50), nullable=False) # e.g., HIGH_RISK_LOCATION, CRITICAL_RISK_LOCATION
    risk_level = Column(String(20), nullable=False) # e.g., HIGH, CRITICAL
    risk_score = Column(Float, nullable=False)
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), index=True, default="ACTIVE") # ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    case = relationship("Case", back_populates="alerts")
    prediction = relationship("Prediction", back_populates="alerts")
    acknowledging_user = relationship("User", foreign_keys=[acknowledged_by], back_populates="acknowledged_alerts")
    resolving_user = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_alerts")
