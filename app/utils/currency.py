from decimal import Decimal
import locale
from typing import Union

def format_currency_brl(amount: Union[Decimal, float, int]) -> str:
    """Format amount as Brazilian Real currency (R$ 1.234,56)"""
    try:
        # Ensure we have a Decimal for precise calculation
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Format with Brazilian locale-style
        # Convert to float for formatting (careful with precision)
        amount_float = float(amount)
        
        # Format with 2 decimal places and Brazilian number format
        formatted = f"{amount_float:,.2f}"
        
        # Replace commas and dots to match Brazilian format
        # Brazilian format: 1.234.567,89 (dots for thousands, comma for decimal)
        parts = formatted.split('.')
        if len(parts) == 2:
            integer_part = parts[0]
            decimal_part = parts[1]
            
            # Add dots as thousand separators
            if ',' in integer_part:
                integer_part = integer_part.replace(',', '.')
            
            # Use comma as decimal separator
            formatted = f"{integer_part},{decimal_part}"
        
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ 0,00"

def parse_currency_brl(currency_str: str) -> Decimal:
    """Parse Brazilian currency string to Decimal"""
    if not currency_str:
        return Decimal('0.00')
    
    # Remove currency symbol and spaces
    amount_str = currency_str.replace('R$', '').replace(' ', '')
    
    # Handle Brazilian number format (dots for thousands, comma for decimal)
    # First, handle the decimal separator (comma)
    if ',' in amount_str:
        parts = amount_str.rsplit(',', 1)  # Split on last comma
        if len(parts) == 2:
            integer_part = parts[0].replace('.', '')  # Remove thousand separators
            decimal_part = parts[1]
            amount_str = f"{integer_part}.{decimal_part}"
    else:
        # No decimal part, just remove dots (thousand separators)
        amount_str = amount_str.replace('.', '')
    
    try:
        return Decimal(amount_str)
    except (ValueError, TypeError):
        return Decimal('0.00')

def validate_currency_amount(amount: Union[str, Decimal, float]) -> bool:
    """Validate if amount is a valid currency value"""
    try:
        if isinstance(amount, str):
            amount = parse_currency_brl(amount)
        elif not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Check if amount is positive and has at most 2 decimal places
        return amount > 0 and amount.as_tuple().exponent >= -2
    except (ValueError, TypeError):
        return False

def format_account_number(bank_code: str, branch_code: str, account_number: str) -> str:
    """Format Brazilian account number"""
    return f"{bank_code}-{branch_code}-{account_number}"

def generate_account_number() -> str:
    """Generate a new account number"""
    import random
    import string
    
    # Generate 8-digit account number
    return ''.join(random.choices(string.digits, k=8))

def generate_iban_compatible(bank_code: str, branch_code: str, account_number: str) -> str:
    """Generate IBAN-compatible format for Brazilian accounts"""
    # Brazil doesn't use IBAN, but we can create a compatible format
    # for international transfers
    country_code = "BR"
    check_digits = "00"  # Would need proper calculation for real IBAN
    
    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number.zfill(12)}"