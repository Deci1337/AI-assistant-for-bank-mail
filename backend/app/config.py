"""Configuration helpers for the BizMail backend."""

from functools import lru_cache
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Holds application-wide configuration."""

    yandex_api_key: str
    yandex_folder_id: str
    yandex_model: str
    
    # Cache settings (in-memory, disabled by default)
    cache_enabled: bool = False

    def __init__(self) -> None:
        api_key = os.getenv("YANDEX_API_KEY") or os.getenv("api_key")
        folder_id = os.getenv("YANDEX_FOLDER_ID") or os.getenv("folder_id")
        
        if not api_key:
            raise RuntimeError("YANDEX_API_KEY (or api_key) is not set")
        if not folder_id:
            raise RuntimeError("YANDEX_FOLDER_ID (or folder_id) is not set")

        self.yandex_api_key = api_key
        self.yandex_folder_id = folder_id
        self.yandex_model = os.getenv("YANDEX_MODEL", "qwen3-235b-a22b-fp8/latest")
        
        # Cache configuration (disabled by default for in-memory storage)
        self.cache_enabled = os.getenv("CACHE_ENABLED", "false").lower() == "true"


def get_settings() -> Settings:
    """Return settings instance."""
    return Settings()

