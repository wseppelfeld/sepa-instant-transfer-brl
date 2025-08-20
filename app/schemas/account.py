from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AccountBase(BaseModel):
    account_type: str
    bank_code: str
    branch_code: str
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None
    
    @validator('bank_code')
    def validate_bank_code(cls, v):
        if len(v) != 3 or not v.isdigit():
            raise ValueError('Bank code must be 3 digits')
        return v
    
    @validator('branch_code')
    def validate_branch_code(cls, v):
        if len(v) != 4 or not v.isdigit():
            raise ValueError('Branch code must be 4 digits')
        return v
    
    @validator('pix_key_type')
    def validate_pix_key_type(cls, v):
        if v and v not in ['cpf', 'email', 'phone', 'random']:
            raise ValueError('Invalid PIX key type')
        return v

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None

class AccountResponse(AccountBase):
    id: int
    account_number: str
    balance: Decimal
    daily_limit: Decimal
    monthly_limit: Decimal
    is_active: bool
    is_blocked: bool
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True