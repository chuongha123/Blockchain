from fastapi import APIRouter, Body, Depends, HTTPException, Request, status, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.model.farm_data import Farm, Product
from app.model.user import User
from app.services.database import get_db
from app.services.security import get_current_active_user
from app.services.generate_qr import GenerateQRService

router = APIRouter(prefix="/farms", tags=["farm"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))
generate_qr_service = GenerateQRService()


class HarvestFarm(BaseModel):
    is_harvested: bool


@router.post("/{farm_id}/harvest")
async def harvest_farm(
    farm_id: str,
    is_harvested: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a farm as harvested via AJAX and return QR code"""

    # Get the farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    print(farm)
    if not farm:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Farm with ID {farm_id} not found"},
        )

    # Update the farm
    farm.is_harvested = is_harvested

    # Generate QR code with farm data URL
    farm_data_url = f"/farm/{farm_id}"
    qr_code_url = generate_qr_service.generate_qr_code(farm_id)
    farm.qr_code_url = f"/static/{qr_code_url}"

    db.commit()

    return JSONResponse(
        content={
            "success": True,
            "message": "Farm marked as harvested successfully",
            "qr_code": f"/static/{qr_code_url}",
            "farm_url": farm_data_url,
        }
    )
