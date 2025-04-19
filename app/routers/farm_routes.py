from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy.orm import Session

from app.model.farm_data import Farm, Product
from app.model.user import User
from app.services.database import get_db
from app.services.security import get_current_active_user
from app.services.generate_qr import GenerateQRService

router = APIRouter(prefix="/farm", tags=["farm"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))
generate_qr_service = GenerateQRService()

@router.get("/harvest/{farm_id}")
async def harvest_farm(
    farm_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a farm as harvested"""
    # Check if the user has access to this farm
    if current_user.role != "admin" and current_user.link_product != farm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to harvest this farm"
        )
    
    # Get the farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Farm with ID {farm_id} not found"
        )
    
    # Get the product and mark as harvested
    product = db.query(Product).filter(Product.id == farm_id).first()
    if product:
        product.is_harvested = True
        db.commit()
    
    # Generate QR code URL
    farm_data_url = f"{request.base_url}farm/{farm_id}"
    
    # Redirect back to profile page
    return RedirectResponse(url="/users/me", status_code=303)

@router.post("/harvest-ajax/{farm_id}")
async def harvest_farm_ajax(
    farm_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a farm as harvested via AJAX and return QR code"""
    # Check if the user has access to this farm
    if current_user.role != "admin" and current_user.link_product != farm_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "You don't have permission to harvest this farm"}
        )
    
    # Get the farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": f"Farm with ID {farm_id} not found"}
        )
    
    # Get the product and mark as harvested
    product = db.query(Product).filter(Product.id == farm_id).first()
    if product:
        product.is_harvested = True
        db.commit()
    
    # Generate QR code with farm data URL
    farm_data_url = f"/farm/{farm_id}"
    qr_code_base64 = generate_qr_service.generate_qr_base64(farm_data_url)
    
    return JSONResponse(content={
        "success": True,
        "message": "Farm marked as harvested successfully",
        "qr_code": qr_code_base64,
        "farm_url": farm_data_url
    }) 