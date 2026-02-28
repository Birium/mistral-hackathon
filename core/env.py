from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVariables(BaseSettings):
    OPENROUTER_API_KEY: str
    VAULT_PATH: str = "/vault"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


env = EnvVariables()