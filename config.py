from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    #Database
    DB_URL: Optional[str] = None
    DB_NAME: Optional[str] = None

    #JWT Security
    SECRET_KEY: str

    #Cloudinary
    CLOUDINARY_SECRET_KEY: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_CLOUD_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "ignore"
    )

settings = BaseConfig()