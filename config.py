from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = Field(..., env="DB_URL")
    
settings = Settings()