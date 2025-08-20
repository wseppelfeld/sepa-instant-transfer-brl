from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime, date

from app.db.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionResponse, TransactionSummary
from app.core.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[TransactionStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get user's transaction history"""
    query = db.query(Transaction).filter(
        or_(
            Transaction.sender_id == current_user.id,
            Transaction.receiver_id == current_user.id
        )
    )
    
    # Apply filters
    if status:
        query = query.filter(Transaction.status == status)
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Transaction.created_at))
    
    # Apply pagination
    transactions = query.offset(offset).limit(limit).all()
    
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific transaction by ID"""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        or_(
            Transaction.sender_id == current_user.id,
            Transaction.receiver_id == current_user.id
        )
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction

@router.get("/account/{account_id}", response_model=List[TransactionResponse])
def get_account_transactions(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get transactions for a specific account"""
    # Verify account ownership
    from app.models.account import Account
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    transactions = db.query(Transaction).filter(
        or_(
            Transaction.sender_account_id == account_id,
            Transaction.receiver_account_id == account_id
        )
    ).order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
    
    return transactions

@router.get("/summary/monthly", response_model=TransactionSummary)
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month, ge=1, le=12)
):
    """Get monthly transaction summary"""
    from sqlalchemy import func, extract
    from decimal import Decimal
    
    # Filter transactions for the specified month
    query = db.query(Transaction).filter(
        Transaction.sender_id == current_user.id,
        extract('year', Transaction.created_at) == year,
        extract('month', Transaction.created_at) == month
    )
    
    # Calculate summary statistics
    total_transactions = query.count()
    
    # Sum amounts and fees
    amounts_and_fees = query.with_entities(
        func.sum(Transaction.amount).label('total_amount'),
        func.sum(Transaction.processing_fee).label('total_fees')
    ).first()
    
    total_amount = amounts_and_fees.total_amount or Decimal('0')
    total_fees = amounts_and_fees.total_fees or Decimal('0')
    
    # Count successful and failed transactions
    successful_transactions = query.filter(
        Transaction.status == TransactionStatus.COMPLETED
    ).count()
    
    failed_transactions = query.filter(
        Transaction.status == TransactionStatus.FAILED
    ).count()
    
    return TransactionSummary(
        total_transactions=total_transactions,
        total_amount=total_amount,
        total_fees=total_fees,
        successful_transactions=successful_transactions,
        failed_transactions=failed_transactions
    )

@router.get("/export/csv")
def export_transactions_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Export transaction history as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    query = db.query(Transaction).filter(
        or_(
            Transaction.sender_id == current_user.id,
            Transaction.receiver_id == current_user.id
        )
    )
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    transactions = query.order_by(desc(Transaction.created_at)).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Transaction ID', 'Date', 'Type', 'Amount', 'Currency', 
        'Status', 'Description', 'Recipient', 'Fee'
    ])
    
    # Write data
    for transaction in transactions:
        recipient = (
            transaction.external_recipient_name or 
            (transaction.receiver.full_name if transaction.receiver else 'N/A')
        )
        
        writer.writerow([
            transaction.transaction_id,
            transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.transaction_type.value,
            float(transaction.amount),
            transaction.currency,
            transaction.status.value,
            transaction.description or '',
            recipient,
            float(transaction.processing_fee)
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="transactions.csv"'}
    )