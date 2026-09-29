from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class WithdrawalLocation(Base):
    __tablename__ = "withdrawal_locations"

    id = Column(Integer, primary_key=True, index=True)
    location_code = Column(String(100), unique=True, index=True, nullable=False)
    location_name = Column(String(200), nullable=False)
    location_type = Column(String(50), nullable=False) # ATM, BANK_BRANCH, CASH_POINT, OTHER
    city = Column(String(100), nullable=False)
    district = Column(String(100), index=True, nullable=False)
    state = Column(String(100), index=True, nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    location_activity_score = Column(DECIMAL(5, 4), nullable=True)
    night_activity_score = Column(DECIMAL(5, 4), nullable=True)
    historical_withdrawal_frequency = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction_locations = relationship("PredictionLocation", back_populates="location")
