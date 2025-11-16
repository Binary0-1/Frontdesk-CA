from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str = Field(..., env="DB_URL")
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
