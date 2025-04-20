from fastapi import APIRouter

from app.routers.admin.farm_management_routes import router as farm_management_router
from app.routers.admin.product_management_routes import router as product_management_router
from app.routers.admin.user_management_routes import router as user_management_router

# Initialize router for admin
router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(farm_management_router)
router.include_router(user_management_router)
router.include_router(product_management_router)
