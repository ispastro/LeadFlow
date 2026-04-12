from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_db_url: str
    database_url: str = None  # Optional alias
    
    # Groq
    groq_api_key: str
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
