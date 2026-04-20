from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_db_url: str
    database_url: str = None  # Optional alias
    
    # Groq
    groq_api_key: str
    
    # Qdrant (Optional)
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    use_qdrant: bool = True
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Email Notifications (Optional)
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    notification_emails: Optional[str] = None
    dashboard_url: Optional[str] = "http://localhost:3001"
    
    # Auth
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    admin_email: str = "admin@leadflow.com"
    admin_password: str = "admin123"  # Change in production
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
