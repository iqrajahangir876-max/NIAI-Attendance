from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "NIAI Attendance"
    database_url: str = "sqlite:///./data/niai.db"
    jwt_secret: str = "change-me"
    access_token_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 15

    # Email / SMTP
    smtp_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    # Optional: set this to your sir's email. If blank, the logged-in teacher's email is used.
    notification_email: str = ""

    # Pakistan local time is used for class schedules.
    timezone: str = "Asia/Karachi"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
