from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True, nullable=False)
    complaint_date = Column(DateTime, index=True, nullable=False)
    crime_category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    victim_state = Column(String(100), index=True, nullable=False)
    victim_district = Column(String(100), nullable=False)
    victim_latitude = Column(DECIMAL(10, 8), nullable=True)
    victim_longitude = Column(DECIMAL(11, 8), nullable=True)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(String(50), index=True, nullable=False) # NEW, UNDER_ANALYSIS, ALERTED, etc.
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="cases")
    transactions = relationship("Transaction", back_populates="case")
    predictions = relationship("Prediction", back_populates="case")
    alerts = relationship("Alert", back_populates="case")
    investigation_notes = relationship("InvestigationNote", back_populates="case")
