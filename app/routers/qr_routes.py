from fastapi import APIRouter

from app.generate_qr import GenerateQRService

# Initialize QR code router
router = APIRouter(tags=["qr"])

# Initialize service
generate_qr_service = GenerateQRService()


@router.get("/generate-qr/{farm_id}")
async def create_qr_code(farm_id: str):
    """Create QR code for device - Requires authentication"""
    try:
        qr_path = generate_qr_service.generate_qr_code(farm_id)
        if not qr_path:
            raise ValueError("QR path is empty")
        return {"message": "QR code created", "qr_url": f"/static/{qr_path}"}
    except Exception as e:
        return {
            "error": "Cannot create QR code",
            "details": str(e)
        }


@router.get("/generate-qr")
async def create_qr_code():
    """Create QR code for home page - No authentication required"""
    try:
        qr_path = generate_qr_service.generate_qr_home_page_code()
        if not qr_path:
            raise ValueError("QR path is empty")
        return {"message": "QR code created", "qr_url": f"/static/{qr_path}"}
    except Exception as e:
        return {
            "error": "Cannot create QR code",
            "details": str(e)
        }
