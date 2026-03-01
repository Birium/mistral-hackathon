from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

KNOWER_CONFIG = Path.home() / ".config" / "knower" / "config"


class EnvVariables(BaseSettings):
    OPENROUTER_API_KEY: str
    VAULT_PATH: str = str(Path.home() / "knower-vault")
    ELEVENLABS_API_KEY: Optional[str] = None
    DEV: bool = False

    model_config = SettingsConfigDict(
        # Falls back to env vars when the file is absent (e.g. CI)
        env_file=str(KNOWER_CONFIG) if KNOWER_CONFIG.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",  # ignore KNOWER_HOME, CORE_PORT, etc.
    )


env = EnvVariables()
