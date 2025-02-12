# In your main file like: service/__init__.py

import asyncio
from aiohttp import web  # Import aiohttp's web module
from lionagi.service.system import ServiceSystem
from lionagi.service.config import Settings
from lionagi.service.endpoints.manager import EndpointManager

# --- Create the FastAPI app instance ---
# app = FastAPI() # remove

# --- Initialize service and settings ---
settings = Settings()
service = ServiceSystem()

# --- Define dynamic routes based on registered endpoints ---
# (This part is the same as in the previous response, but now it
#  takes the app and service as arguments)
def bind_routes(app: web.Application, service: ServiceSystem):
    for endpoint_def in service.endpoint_manager.list_endpoints():
        if endpoint_def.method == "GET":

            async def dynamic_get_route(
                request: web.Request, ep_name: str = endpoint_def.name
            ):
                # Get query params, body if any, etc.
                params = dict(request.query_params)
                return await service.endpoint_manager.invoke_endpoint(
                    ep_name, params
                )
            app.router.add_get(f"/{endpoint_def.name}", dynamic_get_route)

        elif endpoint_def.method == "POST":

            async def dynamic_post_route(
                request: web.Request, ep_name: str = endpoint_def.name
            ):
                body = await request.json()
                return await service.endpoint_manager.invoke_endpoint(ep_name, body)
            
            app.router.add_post(f"/{endpoint_def.name}", dynamic_post_route)
        else:
            logging.warning(f"{endpoint_def.method} is not supported")


# --- Example placeholder route (for testing) ---
async def root_handler(request: web.Request):
    return web.json_response({"message": "LionAGI Service is running"})


async def startup_event(app):
    await service.start(settings)


async def main():
    await service.start(settings)
# --- Bind routes on startup ---
# bind_routes(service.app, service)  # bind after routes are created. # remove

# service.app.router.add_get("/", root_handler) # move to service system
# service.app.on_startup.append(startup_event) # move to service system