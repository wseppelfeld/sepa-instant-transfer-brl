import re
from typing import Optional

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF (individual taxpayer registry)"""
    if not cpf:
        return False
    
    # Remove non-numeric characters
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Check if CPF has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Validate first check digit
    sum_digits = 0
    for i in range(9):
        sum_digits += int(cpf[i]) * (10 - i)
    
    remainder = sum_digits % 11
    first_check_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf[9]) != first_check_digit:
        return False
    
    # Validate second check digit
    sum_digits = 0
    for i in range(10):
        sum_digits += int(cpf[i]) * (11 - i)
    
    remainder = sum_digits % 11
    second_check_digit = 0 if remainder < 2 else 11 - remainder
    
    return int(cpf[10]) == second_check_digit

def validate_cnpj(cnpj: str) -> bool:
    """Validate Brazilian CNPJ (corporate taxpayer registry)"""
    if not cnpj:
        return False
    
    # Remove non-numeric characters
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Check if CNPJ has 14 digits
    if len(cnpj) != 14:
        return False
    
    # Check if all digits are the same
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validate first check digit
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights1[i] for i in range(12))
    remainder = sum_digits % 11
    first_check_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cnpj[12]) != first_check_digit:
        return False
    
    # Validate second check digit
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights2[i] for i in range(13))
    remainder = sum_digits % 11
    second_check_digit = 0 if remainder < 2 else 11 - remainder
    
    return int(cnpj[13]) == second_check_digit

def validate_bank_code(bank_code: str) -> bool:
    """Validate Brazilian bank code (3 digits)"""
    # List of valid Brazilian bank codes (partial list)
    valid_codes = {
        '001',  # Banco do Brasil
        '033',  # Santander
        '104',  # Caixa Econômica Federal
        '237',  # Bradesco
        '341',  # Itaú
        '260',  # Nu Pagamentos (Nubank)
        '077',  # Banco Inter
        '212',  # Banco Original
        '290',  # PagSeguro
        '336',  # C6 Bank
    }
    
    return bank_code in valid_codes or (len(bank_code) == 3 and bank_code.isdigit())

def validate_pix_key(pix_key: str, key_type: str) -> bool:
    """Validate PIX key based on its type"""
    if not pix_key or not key_type:
        return False
    
    if key_type == 'cpf':
        return validate_cpf(pix_key)
    elif key_type == 'cnpj':
        return validate_cnpj(pix_key)
    elif key_type == 'email':
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, pix_key) is not None
    elif key_type == 'phone':
        # Brazilian phone format: +55XXXXXXXXXXX
        phone_pattern = r'^\+55\d{10,11}$'
        return re.match(phone_pattern, pix_key) is not None
    elif key_type == 'random':
        # UUID format for random keys
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return re.match(uuid_pattern, pix_key.lower()) is not None
    
    return False

def format_cpf(cpf: str) -> str:
    """Format CPF with dots and dash"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def format_cnpj(cnpj: str) -> str:
    """Format CNPJ with dots, slash and dash"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj