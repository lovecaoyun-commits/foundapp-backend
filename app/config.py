import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "found-app-dev-secret-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OSS_ACCESS_KEY_ID: str = os.getenv("OSS_ACCESS_KEY_ID", "")
    OSS_ACCESS_KEY_SECRET: str = os.getenv("OSS_ACCESS_KEY_SECRET", "")
    OSS_BUCKET: str = os.getenv("OSS_BUCKET", "found-app")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
    TRTC_APP_ID: str = os.getenv("TRTC_APP_ID", "1600137968")
    TRTC_APP_KEY: str = os.getenv("TRTC_APP_KEY", "")
    SMS_ENABLED: bool = os.getenv("SMS_ENABLED", "false").lower() == "true"
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
