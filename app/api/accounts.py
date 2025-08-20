from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.core.auth import get_current_active_user
from app.utils.currency import generate_account_number, generate_iban_compatible

router = APIRouter()

@router.post("/", response_model=AccountResponse)
def create_account(
    account: AccountCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Create a new account for the current user"""
    # Generate account number
    account_number = generate_account_number()
    
    # Ensure unique account number
    while db.query(Account).filter(Account.account_number == account_number).first():
        account_number = generate_account_number()
    
    # Generate IBAN-compatible format
    iban = generate_iban_compatible(account.bank_code, account.branch_code, account_number)
    
    # Create new account
    db_account = Account(
        account_number=account_number,
        account_type=account.account_type,
        bank_code=account.bank_code,
        branch_code=account.branch_code,
        pix_key=account.pix_key,
        pix_key_type=account.pix_key_type,
        iban=iban,
        owner_id=current_user.id
    )
    
    # Validate PIX key if provided
    if account.pix_key and account.pix_key_type:
        from app.utils.validators import validate_pix_key
        if not validate_pix_key(account.pix_key, account.pix_key_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PIX key for the specified type"
            )
        
        # Check PIX key uniqueness
        existing_pix = db.query(Account).filter(Account.pix_key == account.pix_key).first()
        if existing_pix:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIX key already registered"
            )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account

@router.get("/", response_model=List[AccountResponse])
def get_user_accounts(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Get all accounts for the current user"""
    accounts = db.query(Account).filter(Account.owner_id == current_user.id).all()
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Get specific account by ID"""
    account = db.query(Account).filter(
        Account.id == account_id, 
        Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update account information"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update fields if provided
    if account_update.pix_key is not None:
        if account_update.pix_key_type:
            from app.utils.validators import validate_pix_key
            if not validate_pix_key(account_update.pix_key, account_update.pix_key_type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid PIX key for the specified type"
                )
        
        # Check PIX key uniqueness
        existing_pix = db.query(Account).filter(
            Account.pix_key == account_update.pix_key,
            Account.id != account_id
        ).first()
        if existing_pix:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIX key already registered"
            )
        
        account.pix_key = account_update.pix_key
    
    if account_update.pix_key_type is not None:
        account.pix_key_type = account_update.pix_key_type
    
    if account_update.daily_limit is not None:
        account.daily_limit = account_update.daily_limit
    
    if account_update.monthly_limit is not None:
        account.monthly_limit = account_update.monthly_limit
    
    if account_update.is_active is not None:
        account.is_active = account_update.is_active
    
    db.commit()
    db.refresh(account)
    
    return account

@router.get("/{account_id}/balance")
def get_account_balance(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get account balance"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    from app.utils.currency import format_currency_brl
    
    return {
        "account_id": account.id,
        "balance": account.balance,
        "formatted_balance": format_currency_brl(account.balance),
        "currency": "BRL"
    }