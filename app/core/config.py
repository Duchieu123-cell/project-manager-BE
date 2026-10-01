from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str
    ENVIRONMENT: Literal["development", "production"]
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    SQL_LOG: bool = False

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # asyncpg yêu cầu scheme phải là postgresql+asyncpg://
        uri = self.DATABASE_URL
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql+asyncpg://", 1)
        elif uri.startswith("postgresql://") and not uri.startswith("postgresql+asyncpg://"):
            uri = uri.replace("postgresql://", "postgresql+asyncpg://", 1)
        return uri
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
@lru_cache
def get_settings() -> Settings:
    """
    Sử dụng lru_cache để đảm bảo chỉ đọc và parse file .env đúng 1 lần duy nhất 
    suốt vòng đời ứng dụng, tránh nghẽn I/O khi gọi ở nhiều nơi.
    """
    return Settings()

# Biến dùng trực tiếp trong code
settings = get_settings()