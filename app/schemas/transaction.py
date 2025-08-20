from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionStatus, TransactionType

class TransactionBase(BaseModel):
    amount: Decimal
    currency: str = "BRL"
    description: Optional[str] = None
    transaction_type: TransactionType
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v.as_tuple().exponent < -2:
            raise ValueError('Amount cannot have more than 2 decimal places')
        return v

class TransferCreate(TransactionBase):
    receiver_account_id: Optional[int] = None
    external_recipient_name: Optional[str] = None
    external_recipient_bank: Optional[str] = None
    external_recipient_account: Optional[str] = None
    external_recipient_document: Optional[str] = None
    pix_key: Optional[str] = None

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    transaction_id: str
    reference_number: Optional[str] = None
    status: TransactionStatus
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    sender_account_id: Optional[int] = None
    receiver_account_id: Optional[int] = None
    external_recipient_name: Optional[str] = None
    external_recipient_bank: Optional[str] = None
    external_recipient_account: Optional[str] = None
    pix_key: Optional[str] = None
    pix_end_to_end_id: Optional[str] = None
    processing_fee: Decimal
    risk_score: Optional[Decimal] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    total_transactions: int
    total_amount: Decimal
    total_fees: Decimal
    successful_transactions: int
    failed_transactions: int