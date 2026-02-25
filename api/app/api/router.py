"""
API Router - Aggregates all feature routers.
Routes are auto-registered by the generate_feature script.
"""

from fastapi import APIRouter
from app.features.kosts.router import router as kosts_router
from app.features.dashboard.router import router as dashboard_router
from app.features.tenants.router import router as tenants_router
from app.features.users.router import router as users_router
from app.features.transactions.router import router as transactions_router
from app.features.export.router import router as export_router
from app.features.regions.router import router as regions_router
from app.features.failsafe.router import router as failsafe_router

api_router = APIRouter()

# Feature routers will be auto-registered here by generate_feature.py
api_router.include_router(kosts_router, prefix="/kosts", tags=["Kosts"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(regions_router, prefix="/regions", tags=["Regions"])
api_router.include_router(failsafe_router, prefix="/failsafe", tags=["Failsafe"])
