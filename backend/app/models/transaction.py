from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), index=True, nullable=False)
    transaction_reference = Column(String(100), index=True, nullable=False)
    transaction_type = Column(String(50), nullable=False) # UPI, CARD, NET_BANKING, WALLET, OTHER
    amount = Column(DECIMAL(15, 2), nullable=False)
    transaction_timestamp = Column(DateTime, index=True, nullable=False)
    source_identifier = Column(String(100), nullable=False)
    destination_identifier = Column(String(100), nullable=False)
    transfer_velocity = Column(Float, nullable=True) # E.g., transfers per hour
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="transactions")
