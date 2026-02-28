from pydantic_settings import BaseSettings
from pathlib import Path

ROOT = Path(__file__).parent.parent  # → mistral-hackathon/


class EnvVariables(BaseSettings):
    OPENROUTER_API_KEY: str
    VAULT_PATH: str = "./vault"

    model_config = {"env_file": ROOT / ".env", "env_file_encoding": "utf-8"}


env = EnvVariables()
