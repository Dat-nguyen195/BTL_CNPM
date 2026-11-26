from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    POSTGREST_URL: str | None = None
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()