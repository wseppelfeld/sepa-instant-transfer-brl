from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://sepa_user:sepa_password@localhost:5432/sepa_brl_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "SEPA Instant Transfer BRL"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Brazilian Banking
    PIX_ENDPOINT_URL: Optional[str] = None
    CENTRAL_BANK_URL: str = "https://api.bcb.gov.br"
    
    class Config:
        env_file = ".env"

settings = Settings()