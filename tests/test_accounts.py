import pytest
from tests.conftest import client, auth_headers

def test_create_account(client, auth_headers):
    account_data = {
        "account_type": "checking",
        "bank_code": "001",
        "branch_code": "1234",
        "pix_key": "test@example.com",
        "pix_key_type": "email"
    }
    
    response = client.post("/api/accounts/", json=account_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["account_type"] == "checking"
    assert response.json()["bank_code"] == "001"
    assert response.json()["branch_code"] == "1234"
    assert response.json()["pix_key"] == "test@example.com"

def test_create_account_invalid_bank_code(client, auth_headers):
    account_data = {
        "account_type": "checking",
        "bank_code": "12",  # Invalid: should be 3 digits
        "branch_code": "1234",
    }
    
    response = client.post("/api/accounts/", json=account_data, headers=auth_headers)
    assert response.status_code == 422

def test_get_user_accounts(client, auth_headers):
    # First create an account
    account_data = {
        "account_type": "savings",
        "bank_code": "237",
        "branch_code": "5678",
    }
    
    client.post("/api/accounts/", json=account_data, headers=auth_headers)
    
    # Then get all accounts
    response = client.get("/api/accounts/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_account_balance(client, auth_headers):
    # Create an account
    account_data = {
        "account_type": "checking",
        "bank_code": "341",
        "branch_code": "9999",
    }
    
    create_response = client.post("/api/accounts/", json=account_data, headers=auth_headers)
    account_id = create_response.json()["id"]
    
    # Get balance
    response = client.get(f"/api/accounts/{account_id}/balance", headers=auth_headers)
    assert response.status_code == 200
    assert "balance" in response.json()
    assert "formatted_balance" in response.json()
    assert response.json()["currency"] == "BRL"

def test_get_account_unauthorized(client):
    response = client.get("/api/accounts/")
    assert response.status_code == 401