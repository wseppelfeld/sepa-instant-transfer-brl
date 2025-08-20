import pytest
from tests.conftest import client, auth_headers

def test_register_user(client):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "cpf": "98765432109",
        "password": "newpassword"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert response.json()["username"] == user_data["username"]

def test_register_duplicate_email(client):
    user_data = {
        "email": "test@example.com",
        "username": "testuser2",
        "full_name": "Test User 2",
        "cpf": "11111111111",
        "password": "testpassword"
    }
    
    # First registration should succeed
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Second registration with same email should fail
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400

def test_login_success(client):
    # First register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "full_name": "Login User",
        "cpf": "22222222222",
        "password": "loginpassword"
    }
    
    client.post("/api/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "email": "login@example.com",
        "password": "loginpassword"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_current_user_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401