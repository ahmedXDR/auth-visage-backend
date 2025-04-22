from fastapi import APIRouter

from app.api.routes import projects, trusted_origins, utils

api_router = APIRouter()
api_router.include_router(projects.router)
api_router.include_router(utils.router)
api_router.include_router(trusted_origins.router)
