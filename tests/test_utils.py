import pytest
from decimal import Decimal
from app.utils.validators import validate_cpf, validate_cnpj, validate_bank_code, validate_pix_key
from app.utils.currency import format_currency_brl, parse_currency_brl, validate_currency_amount

def test_validate_cpf_valid():
    # Valid CPF
    assert validate_cpf("11144477735") == True
    
def test_validate_cpf_invalid():
    # Invalid CPF
    assert validate_cpf("12345678901") == False
    assert validate_cpf("111.111.111-11") == False  # All same digits
    assert validate_cpf("123456789") == False  # Too short
    assert validate_cpf("") == False  # Empty

def test_validate_cnpj_valid():
    # Valid CNPJ
    assert validate_cnpj("11222333000181") == True
    
def test_validate_cnpj_invalid():
    # Invalid CNPJ
    assert validate_cnpj("12345678000100") == False  # Invalid check digits
    assert validate_cnpj("11111111111111") == False  # All same digits
    assert validate_cnpj("123456789") == False  # Too short
    assert validate_cnpj("") == False  # Empty

def test_validate_bank_code():
    assert validate_bank_code("001") == True
    assert validate_bank_code("237") == True
    assert validate_bank_code("12") == False  # Too short
    assert validate_bank_code("1234") == False  # Too long
    assert validate_bank_code("abc") == False  # Non-numeric

def test_validate_pix_key():
    assert validate_pix_key("test@example.com", "email") == True
    assert validate_pix_key("11144477735", "cpf") == True
    assert validate_pix_key("+5511999999999", "phone") == True
    assert validate_pix_key("invalid-email", "email") == False

def test_format_currency_brl():
    assert format_currency_brl(Decimal("1234.56")) == "R$ 1.234,56"
    assert format_currency_brl(Decimal("0.99")) == "R$ 0,99"
    assert format_currency_brl(Decimal("1000000.00")) == "R$ 1.000.000,00"

def test_parse_currency_brl():
    assert parse_currency_brl("R$ 1.234,56") == Decimal("1234.56")
    assert parse_currency_brl("R$ 0,99") == Decimal("0.99")
    assert parse_currency_brl("1234,56") == Decimal("1234.56")
    assert parse_currency_brl("") == Decimal("0.00")

def test_validate_currency_amount():
    assert validate_currency_amount(Decimal("100.50")) == True
    assert validate_currency_amount("R$ 100,50") == True
    assert validate_currency_amount(Decimal("0")) == False  # Not positive
    assert validate_currency_amount(Decimal("100.555")) == False  # Too many decimals