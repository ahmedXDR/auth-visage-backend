from fastapi import APIRouter

from app.api.routes import oauth, users, utils

api_router = APIRouter()
api_router.include_router(utils.router)
api_router.include_router(oauth.router)
api_router.include_router(users.router)
