"""
API Router - Aggregates all feature routers.
Routes are auto-registered by the generate_feature script.
"""

from fastapi import APIRouter
from app.features.kosts.router import router as kosts_router
from app.features.dashboard.router import router as dashboard_router
from app.features.tenants.router import router as tenants_router
from app.features.users.router import router as users_router

api_router = APIRouter()

# Feature routers will be auto-registered here by generate_feature.py
api_router.include_router(kosts_router, prefix="/kosts", tags=["Kosts"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

