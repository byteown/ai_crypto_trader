from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field('AI Crypto Agent')
    debug: bool = Field(False)

    model_config = SettingsConfigDict(env_file=".env", env_prefix='')


settings = Settings()