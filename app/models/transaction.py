from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db.database import Base

class TransactionStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionType(PyEnum):
    INSTANT_TRANSFER = "instant_transfer"
    PIX_TRANSFER = "pix_transfer"
    SEPA_TRANSFER = "sepa_transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction identification
    transaction_id = Column(String, unique=True, index=True, nullable=False)  # UUID
    reference_number = Column(String, unique=True, index=True)  # External reference
    
    # Transaction details
    amount = Column(Numeric(15, 2), nullable=False)  # Brazilian Real amount
    currency = Column(String(3), default="BRL", nullable=False)
    description = Column(Text)
    
    # Transaction type and status
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Sender and receiver information
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    sender_account_id = Column(Integer, ForeignKey("accounts.id"))
    receiver_account_id = Column(Integer, ForeignKey("accounts.id"))
    
    # External recipient details (for transfers to other banks)
    external_recipient_name = Column(String)
    external_recipient_bank = Column(String)
    external_recipient_account = Column(String)
    external_recipient_document = Column(String)  # CPF/CNPJ
    
    # PIX details
    pix_key = Column(String)
    pix_end_to_end_id = Column(String, unique=True, index=True)  # PIX end-to-end ID
    
    # SEPA/ISO 20022 details
    sepa_instruction_id = Column(String)
    sepa_end_to_end_id = Column(String)
    sepa_payment_info_id = Column(String)
    
    # Processing details
    processing_fee = Column(Numeric(10, 2), default=0.00)
    exchange_rate = Column(Numeric(10, 6))  # For future multi-currency support
    
    # Fraud detection and compliance
    risk_score = Column(Numeric(5, 2))  # Risk assessment score
    compliance_check = Column(Boolean, default=False)
    anti_fraud_check = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Error handling
    error_code = Column(String)
    error_message = Column(Text)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_transactions")
    sender_account = relationship("Account", foreign_keys=[sender_account_id], back_populates="sent_transactions")
    receiver_account = relationship("Account", foreign_keys=[receiver_account_id], back_populates="received_transactions")