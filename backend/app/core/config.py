from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field('AI Crypto Agent')
    debug: bool = Field(False)
    database_url: str = Field("postgresql+asyncpg://agent:password@localhost:5432/db")
    redis_url: str = Field("redis://localhost:6379/0")

    model_config = SettingsConfigDict(env_file=".env", env_prefix='')


settings = Settings()