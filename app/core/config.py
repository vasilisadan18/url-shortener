from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "url_shortener"
    DATABASE_URL: Optional[str] = None

    REDIS_HOST: str = "redis"
    REDIS_PORT: int= 6379
    REDIS_DB: int= 0
    REDIS_URL: Optional[str] = None

    SECRET_KEY: str = "50b4ed23ba2dc93ea3a91a2e8fe935b24aacb6541939061a5cb80af4179c45ed"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int= 30
    
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int=6
    DEFAULT_EXPIRY_DAYS: int=30
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL= f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

settings= Settings()