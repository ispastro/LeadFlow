import sys
from typing import List, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # -----------------------------------------------------------------------
    # Database — optional, only needed if using external Postgres
    # -----------------------------------------------------------------------
    database_url: Optional[str] = None

    # -----------------------------------------------------------------------
    # AI services
    # -----------------------------------------------------------------------
    groq_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    use_qdrant: bool = True

    # -----------------------------------------------------------------------
    # LangSmith observability
    # -----------------------------------------------------------------------
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = False
    langsmith_project: str = "leadflow"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    # -----------------------------------------------------------------------
    # Server
    # -----------------------------------------------------------------------
    port: int = 8000
    host: str = "0.0.0.0"
    environment: str = "development"

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # -----------------------------------------------------------------------
    # Auth
    # -----------------------------------------------------------------------
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    admin_email: str
    admin_password: str

    # -----------------------------------------------------------------------
    # Rate limiting
    # -----------------------------------------------------------------------
    chat_rate_limit_per_minute: int = 30

    # -----------------------------------------------------------------------
    # RevOps graph settings (Phase 5 — HITL)
    # -----------------------------------------------------------------------
    # Score threshold (0-100) above which human approval is required
    hitl_score_threshold: int = 90
    # How long (seconds) the graph waits for a human approval before auto-routing
    # to manual_review. 0 = wait indefinitely.
    hitl_timeout_seconds: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got '{v}'")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("jwt_secret must be at least 32 characters long")
        return v

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("admin_password must be at least 8 characters long")
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"port must be between 1-65535, got {v}")
        return v

    @model_validator(mode="after")
    def production_guard(self) -> "Settings":
        if self.environment == "production":
            for name, value, bad in [
                ("jwt_secret", self.jwt_secret, "your-secret-key"),
                ("admin_password", self.admin_password, "admin123"),
            ]:
                if value == bad:
                    print(
                        f"FATAL: '{name}' is set to an insecure default in production.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
        return self

    # -----------------------------------------------------------------------
    # Computed properties
    # -----------------------------------------------------------------------

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def langsmith_enabled(self) -> bool:
        return bool(self.langsmith_api_key and self.langsmith_tracing)


settings = Settings()
