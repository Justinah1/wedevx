import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    # App settings
    APP_NAME: str = "Lead Management System"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    
    # JWT settings
    SECRET_KEY: str = os.environ.get("SESSION_SECRET", "a_super_secure_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings
    SMTP_SERVER: str = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.environ.get("SMTP_USERNAME", "your-email@gmail.com")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "your-app-password")
    ATTORNEY_EMAIL: str = os.environ.get("ATTORNEY_EMAIL", "attorney@company.com")
    COMPANY_NAME: str = os.environ.get("COMPANY_NAME", "Your Company")
    
    # File upload settings
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

settings = Settings()
