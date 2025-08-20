import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db, Base
from app.core.config import settings

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    # Create a test user and get auth token
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "cpf": "12345678901",
        "password": "testpassword"
    }
    
    # Register user
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "SEPA Instant Transfer BRL API" in response.json()["message"]