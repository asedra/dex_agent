from fastapi import APIRouter
from .v1 import agents, commands, system, installer, websocket, auth, settings, files, services, events, software, processes, network, power, registry
from . import metrics

api_router = APIRouter()

# Include all API routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(commands.router, prefix="/commands", tags=["commands"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(installer.router, prefix="/installer", tags=["installer"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(services.router, tags=["services"])
api_router.include_router(registry.router, tags=["registry"])
api_router.include_router(events.router, tags=["events"])
api_router.include_router(software.router, tags=["software"])
api_router.include_router(processes.router, tags=["processes"])
api_router.include_router(network.router, tags=["network"])
api_router.include_router(power.router, tags=["power"])
api_router.include_router(metrics.router, tags=["monitoring"]) 