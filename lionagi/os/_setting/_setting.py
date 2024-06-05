import json
import csv
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional


class Settings:
    def __init__(self):
        self._lock = threading.Lock()
        self._config = {}
        self._models = {
            "default_chat_model": None,
            "embed_model": None,
            "finetune_model": None,
            "vision_model": None,
            "audio_model": None,
            "video_model": None,
        }
        self._loggers = {
            "api_data_logger": None,
            "global_message_logger": None,
        }
        self._retry_config = {}
        self._default_service = None

    def load_from_json(self, file_path):
        with self._lock:
            with open(file_path, "r") as file:
                self._config = json.load(file)

    def save_to_json(self, file_path):
        with self._lock:
            with open(file_path, "w") as file:
                json.dump(self._config, file, indent=4)

    def load_default_service(self, file_path):
        with self._lock:
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                self._default_service = next(reader)

    def save_default_service(self, file_path):
        with self._lock:
            fieldnames = ["provider", "api_key", "rate_limit"]
            with open(file_path, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(self._default_service)

    @contextmanager
    def service_context(self, provider=None, api_key=None, rate_limit=None):
        with self._lock:
            service_config = {
                "provider": provider or self._default_service["provider"],
                "api_key": api_key or self._default_service["api_key"],
                "rate_limit": rate_limit or self._default_service["rate_limit"],
            }
            yield service_config

    def get_config(self, key: str) -> Any:
        with self._lock:
            return self._config.get(key)

    def set_config(self, key: str, value: Any):
        with self._lock:
            self._config[key] = value

    def get_model(self, model_name: str) -> Any:
        with self._lock:
            return self._models.get(model_name)

    def set_model(self, model_name: str, model: Any):
        with self._lock:
            self._models[model_name] = model

    def get_logger(self, logger_name: str) -> Optional[Callable[[str], None]]:
        with self._lock:
            return self._loggers.get(logger_name)

    def set_logger(self, logger_name: str, logger: Callable[[str], None]):
        with self._lock:
            self._loggers[logger_name] = logger

    def get_retry_config(self) -> Dict[str, Any]:
        with self._lock:
            return self._retry_config

    def set_retry_config(self, retry_config: Dict[str, Any]):
        with self._lock:
            self._retry_config = retry_config

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "config": self._config,
                "models": self._models,
                "loggers": self._loggers,
                "retry_config": self._retry_config,
            }

    def from_dict(self, data: dict):
        with self._lock:
            self._config = data.get("config", {})
            self._models = data.get("models", self._models)
            self._loggers = data.get("loggers", self._loggers)
            self._retry_config = data.get("retry_config", self._retry_config)


# Singleton instance for global settings
settings = Settings()


# Example usage
def main():
    # Set some configurations
    settings.set_config("example_key", "example_value")
    settings.set_model("default_chat_model", "ChatModelV1")
    settings.set_logger("api_data_logger", lambda msg: print(f"API log: {msg}"))
    settings.set_retry_config({"retries": 3, "delay": 5})

    # Access configurations
    print(settings.get_config("example_key"))
    print(settings.get_model("default_chat_model"))
    api_logger = settings.get_logger("api_data_logger")
    if api_logger:
        api_logger("This is a test log message.")

    # Save settings to JSON
    settings.save_to_json("settings.json")

    # Load settings from JSON
    settings.load_from_json("settings.json")


if __name__ == "__main__":
    main()
