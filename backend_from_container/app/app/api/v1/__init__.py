"""API v1 module with route registration."""
from fastapi import APIRouter
from app.api.v1 import auth, agents, commands, system, settings, installer, websocket, files, services, software, events, processes, network, power

api_router = APIRouter()

# Register all API routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(commands.router, prefix="/commands", tags=["Commands"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(installer.router, prefix="/installer", tags=["Installer"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(files.router, prefix="/files", tags=["File Manager"])
api_router.include_router(services.router, tags=["Services"])
# api_router.include_router(registry.router, tags=["Registry"])  # Temporarily disabled
api_router.include_router(software.router, tags=["Software Management"])
api_router.include_router(events.router, tags=["Event Viewer"])
api_router.include_router(processes.router, tags=["Process Manager"])
api_router.include_router(network.router, tags=["Network Configuration"])
api_router.include_router(power.router, tags=["Power Management"])