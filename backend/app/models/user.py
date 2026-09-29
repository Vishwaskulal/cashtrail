from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # e.g. LEA_OFFICER, BANK_OFFICER, I4C_OFFICER, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="creator")
    investigation_notes = relationship("InvestigationNote", back_populates="author")
    acknowledged_alerts = relationship("Alert", foreign_keys="[Alert.acknowledged_by]", back_populates="acknowledging_user")
    resolved_alerts = relationship("Alert", foreign_keys="[Alert.resolved_by]", back_populates="resolving_user")
