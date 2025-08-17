from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Example: postgresql://user:pass@localhost:5432/multitenant
    DATABASE_URL: str = "postgresql://postgres:my_password@localhost:5432/multitenant"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Super admin (manages tenants)
    SUPERADMIN_USERNAME: str = "superadmin"
    SUPERADMIN_PASSWORD: str = "supersecret"

    # Default public schema (stores Tenants registry)
    PUBLIC_SCHEMA: str = "public"

    class Config:
        env_file = ".env"

settings = Settings()
