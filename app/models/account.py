from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, nullable=False)  # "checking", "savings"
    
    # Brazilian banking details
    bank_code = Column(String(3), nullable=False)  # Brazilian bank code (3 digits)
    branch_code = Column(String(4), nullable=False)  # Agency code (4 digits)
    
    # Balance and limits
    balance = Column(Numeric(15, 2), default=0.00)  # Brazilian Real with 2 decimal places
    daily_limit = Column(Numeric(15, 2), default=10000.00)  # Daily transfer limit
    monthly_limit = Column(Numeric(15, 2), default=100000.00)  # Monthly transfer limit
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    # PIX integration
    pix_key = Column(String, unique=True, index=True)  # PIX key (CPF, email, phone, or random)
    pix_key_type = Column(String)  # "cpf", "email", "phone", "random"
    
    # SEPA/IBAN compatibility (for international transfers)
    iban = Column(String(34), unique=True, index=True)
    swift_code = Column(String(11))
    
    # Owner reference
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="accounts")
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_account_id", back_populates="sender_account")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.receiver_account_id", back_populates="receiver_account")