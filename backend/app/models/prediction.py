from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), ForeignKey('cases.case_number'), index=True)
    model_version = Column(String(20))
    overall_risk_level = Column(String(20))
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    
    locations = relationship('PredictionLocation', back_populates='prediction', cascade="all, delete-orphan")
    risk_factors = relationship('RiskFactor', back_populates='prediction', cascade="all, delete-orphan")
    case = relationship('Case', back_populates='predictions')
    alerts = relationship('Alert', back_populates='prediction')

class PredictionLocation(Base):
    __tablename__ = 'prediction_locations'

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'), index=True)
    location_code = Column(String(100), ForeignKey('withdrawal_locations.location_code'))
    risk_score = Column(Float)
    confidence_score = Column(Float)
    risk_level = Column(String(20))
    
    prediction = relationship('Prediction', back_populates='locations')
    location = relationship('WithdrawalLocation')
