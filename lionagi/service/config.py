# lionagi/service/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    api_keys: dict = {}
    endpoints_config_path: str = "endpoints.yaml"  # Default path
    plugin_dir: str = "plugins"  # Default plugin directory

    class Config:
        env_file = ".env"  # Load environment variables from .env
        env_file_encoding = "utf-8"

# Example usage (later, in ServiceSystem):
# settings = Settings()