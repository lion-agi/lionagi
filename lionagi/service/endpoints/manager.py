# lionagi/service/endpoints/manager.py

import logging
from typing import Any, Dict
from pydantic import ValidationError

from lionagi.service.endpoints.config import EndpointConfig
from lionagi.service.endpoints.endpoint import EndPoint  # Import EndPoint


class EndpointManager:
    def __init__(self):
        self.endpoints: Dict[str, EndPoint] = {}  # Store EndPoint instances

    def register_endpoint(self, config: EndpointConfig):
        """Registers a single endpoint configuration."""
        if config.name in self.endpoints:
            logging.warning(f"Overwriting existing endpoint: {config.name}")
        # Create the EndPoint instance when registering
        self.endpoints[config.name] = EndPoint(config=config)
        logging.info(f"Registered endpoint: {config.name}")

    def load_endpoints_from_file(self, config_path: str):
        """Loads endpoint definitions from a configuration file (e.g., YAML, JSON)."""
        try:
            with open(config_path, "r") as f:
                import yaml  # Or json, toml

                config_data = yaml.safe_load(f)  # Or json.load, toml.load
        except FileNotFoundError:
            logging.error(f"Endpoint configuration file not found: {config_path}")
            return
        except Exception as e:
            logging.exception(f"Failed to load endpoint configurations: {e}")
            return

        if not isinstance(config_data, list):
            raise ValueError(
                "Endpoint config file must contain a list of endpoint definitions."
            )

        for endpoint_data in config_data:
            try:
                endpoint_config = EndpointConfig(**endpoint_data)
                self.register_endpoint(endpoint_config)
            except ValidationError as e:
                logging.error(
                    f"Invalid endpoint definition: {endpoint_data}. Error: {e}"
                )
            except Exception as e:
                logging.exception(f"Failed to register endpoint: {e}")

    def get_endpoint(self, name: str) -> EndPoint:
        """Retrieves an endpoint configuration by name."""
        if name not in self.endpoints:
            raise ValueError(f"Endpoint '{name}' not found.")
        return self.endpoints[name]

    def list_endpoints(self) -> list[EndPoint]:
        """Lists all currently registered endpoints."""
        return list(self.endpoints.values())

    async def invoke_endpoint(
        self, endpoint_name: str, input_data: dict
    ) -> dict:  # Changed to dict
        """Invokes a specific endpoint by name."""
        endpoint = self.get_endpoint(endpoint_name)

        # TODO: You'd likely have more sophisticated logic here for:
        #   -  Preprocessing input_data based on endpoint.config.request_schema
        #   -  Selecting the correct HTTP method (GET, POST, etc.)
        #   -  Handling headers
        #   -  Choosing between _invoke and _stream

        # For this example, we assume a simple POST request with JSON data
        try:
            # Invoke the endpoint using the aiohttp client session
            response = await endpoint._invoke(payload=input_data, headers={})
            return response
        except Exception as e:
            # TODO: More robust error handling (custom exceptions, logging, etc.)
            raise ValueError(f"Error invoking endpoint {endpoint_name}: {e}")