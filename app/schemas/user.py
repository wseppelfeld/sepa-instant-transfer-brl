from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('cpf')
    def validate_cpf(cls, v):
        if v:
            from app.utils.validators import validate_cpf
            if not validate_cpf(v):
                raise ValueError('Invalid CPF')
        return v
    
    @validator('cnpj')
    def validate_cnpj(cls, v):
        if v:
            from app.utils.validators import validate_cnpj
            if not validate_cnpj(v):
                raise ValueError('Invalid CNPJ')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None