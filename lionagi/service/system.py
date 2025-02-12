# lionagi/service/system.py (REVISED)

import logging
from aiohttp import web
from lionagi.service.endpoints.manager import EndpointManager
from lionagi.service.plugins.manager import PluginManager
# from lionagi.service.connectors.base import ResourceConnector  # Import Connector
from lionagi.service.imodel import iModel  # Import iModel

class ServiceSystem:
    def __init__(self):
        self.resource_registry = {}  # Maps connector names to iModel instances
        self.endpoint_manager = EndpointManager() # keep the endpoint manager.
        self.plugin_manager = PluginManager()
        self.app = web.Application()  # aiohttp Application, created ONCE
        self.control = ExecutionControl(concurrency=10, rps=60)

    async def start(self, config):

        self.plugin_manager.load_plugins()

        for plugin in self.plugin_manager.plugins_loaded:
            for connector in plugin.register_connectors():
                self.register_connector(connector)
            for endpoint_def in plugin.register_endpoints():
                self.endpoint_manager.register_endpoint(endpoint_def)

        self.endpoint_manager.load_endpoints_from_file(config.endpoints_config_path)

        # Create and register iModel instances based on configuration
        # This is where you'd define which endpoints go with which iModel
        # Example (assuming a config structure like in endpoints.yaml):
        openai_chat_endpoints = []
        for endpoint_config in self.endpoint_manager.list_endpoints():
            if endpoint_config.provider == "openai":
                openai_chat_endpoints.append(endpoint_config)


        if openai_chat_endpoints:
            openai_chat_imodel = iModel(provider="openai", endpoints={
                endpoint.name:endpoint for endpoint in openai_chat_endpoints
            }, requires_api_key=True)  # Pass EndpointConfigs
            
            for endpoint in openai_chat_endpoints:
                self.endpoint_manager.register_endpoint(endpoint)
            # self.register_connector(openai_chat_imodel)
            self.resource_registry[openai_chat_imodel.name] = openai_chat_imodel

        # TODO: Repeat for other providers/iModels (Anthropic, Exa, etc.)
        # ...

        self._bind_http_routes()

    def register_connector(self, connector):
        """Registers a resource connector instance, including iModels."""
        self.resource_registry[connector.name] = connector

    def _bind_http_routes(self):
        """Creates dynamic routes based on registered endpoints."""
        for endpoint_def in self.endpoint_manager.list_endpoints():
            endpoint = self.endpoint_manager.get_endpoint(endpoint_def.name)
            if endpoint_def.method == "GET":
                self.app.router.add_get(
                    f"/{endpoint_def.name}",
                    self.create_handler(endpoint),
                )
            elif endpoint_def.method == "POST":
                self.app.router.add_post(
                    f"/{endpoint_def.name}",
                    self.create_handler(endpoint),
                )
            else:
                logging.warning(
                    f"Method {endpoint_def.method} not implemented for HTTP."
                )

    def create_handler(self, endpoint: EndPoint):
        """Creates a request handler function for a given endpoint."""

        async def handle_request(request: web.Request):
            try:
                await self.control.acquire()  # rate limit
                if request.method == "GET":
                    params = dict(request.query)
                    result = await endpoint._invoke(
                        payload=params, headers={}
                    )  # Call _invoke on EndPoint

                elif request.method == "POST":
                    body = await request.json()
                    result = await endpoint._invoke(
                        payload=body, headers={}
                    )  # Call _invoke on EndPoint
                else:
                    return web.Response(status=405)

                return web.json_response(result)

            except Exception as e:
                logging.exception(f"Error handling request: {e}")
                return web.Response(status=500, text=str(e))
            finally:
                self.control.release()

        return handle_request