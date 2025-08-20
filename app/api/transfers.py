from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.schemas.transaction import TransferCreate, TransactionResponse
from app.core.auth import get_current_active_user

router = APIRouter()

@router.post("/instant", response_model=TransactionResponse)
def create_instant_transfer(
    transfer: TransferCreate,
    sender_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create an instant transfer"""
    # Validate sender account
    sender_account = db.query(Account).filter(
        Account.id == sender_account_id,
        Account.owner_id == current_user.id
    ).first()
    
    if not sender_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender account not found"
        )
    
    if not sender_account.is_active or sender_account.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender account is not available for transfers"
        )
    
    # Check sufficient balance
    if sender_account.balance < transfer.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Check daily limit
    from sqlalchemy import func, and_
    today = datetime.now().date()
    daily_total = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.sender_account_id == sender_account_id,
            func.date(Transaction.created_at) == today,
            Transaction.status == TransactionStatus.COMPLETED
        )
    ).scalar() or Decimal('0')
    
    if daily_total + transfer.amount > sender_account.daily_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daily transfer limit exceeded"
        )
    
    receiver_account = None
    receiver_user = None
    
    # Handle internal transfer (to another account in the system)
    if transfer.receiver_account_id:
        receiver_account = db.query(Account).filter(
            Account.id == transfer.receiver_account_id
        ).first()
        
        if not receiver_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver account not found"
            )
        
        if not receiver_account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver account is not active"
            )
        
        receiver_user = db.query(User).filter(
            User.id == receiver_account.owner_id
        ).first()
    
    # Handle PIX transfer
    elif transfer.pix_key:
        # For demonstration, we'll treat PIX as external transfer
        # In production, you'd integrate with PIX infrastructure
        pass
    
    # Validate external transfer data
    elif not all([
        transfer.external_recipient_name,
        transfer.external_recipient_bank,
        transfer.external_recipient_account
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing recipient information for external transfer"
        )
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    
    db_transaction = Transaction(
        transaction_id=transaction_id,
        amount=transfer.amount,
        currency=transfer.currency,
        description=transfer.description,
        transaction_type=transfer.transaction_type,
        status=TransactionStatus.PROCESSING,
        sender_id=current_user.id,
        receiver_id=receiver_user.id if receiver_user else None,
        sender_account_id=sender_account_id,
        receiver_account_id=transfer.receiver_account_id,
        external_recipient_name=transfer.external_recipient_name,
        external_recipient_bank=transfer.external_recipient_bank,
        external_recipient_account=transfer.external_recipient_account,
        external_recipient_document=transfer.external_recipient_document,
        pix_key=transfer.pix_key,
        risk_score=Decimal('1.0'),  # Basic risk assessment
        compliance_check=True,
        anti_fraud_check=True
    )
    
    db.add(db_transaction)
    
    try:
        # Process the transfer
        # Debit sender account
        sender_account.balance -= transfer.amount
        
        # Credit receiver account (if internal)
        if receiver_account:
            receiver_account.balance += transfer.amount
            db_transaction.status = TransactionStatus.COMPLETED
            db_transaction.completed_at = datetime.utcnow()
        else:
            # For external transfers, mark as processing
            # In production, this would integrate with external payment systems
            db_transaction.status = TransactionStatus.PROCESSING
        
        db_transaction.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_transaction)
        
        return db_transaction
    
    except Exception as e:
        db.rollback()
        db_transaction.status = TransactionStatus.FAILED
        db_transaction.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer processing failed"
        )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transfer_status(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get transfer status by transaction ID"""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        (Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction

@router.post("/{transaction_id}/cancel")
def cancel_transfer(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a pending transfer"""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.sender_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status not in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or failed transaction"
        )
    
    # Reverse the transaction if it was processing
    if transaction.status == TransactionStatus.PROCESSING:
        sender_account = db.query(Account).filter(
            Account.id == transaction.sender_account_id
        ).first()
        
        if sender_account:
            sender_account.balance += transaction.amount
        
        if transaction.receiver_account_id:
            receiver_account = db.query(Account).filter(
                Account.id == transaction.receiver_account_id
            ).first()
            if receiver_account:
                receiver_account.balance -= transaction.amount
    
    transaction.status = TransactionStatus.CANCELLED
    db.commit()
    
    return {"message": "Transfer cancelled successfully"}