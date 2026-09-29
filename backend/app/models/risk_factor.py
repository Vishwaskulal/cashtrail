from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), index=True, nullable=False)
    factor_name = Column(String(100), nullable=False)
    importance_score = Column(Float, nullable=False)
    impact_direction = Column(String(20), nullable=False) # e.g., POSITIVE, NEGATIVE

    # Relationships
    prediction = relationship("Prediction", back_populates="risk_factors")
