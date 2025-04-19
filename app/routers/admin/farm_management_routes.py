from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.constants.template_constant import ADMIN_ERROR_TEMPLATE
from app.model.user import User
from app.model.farm_data import Farm
from app.services.security import check_admin_role
from app.services.blockchain import BlockchainService
from app.services.database import get_db
from datetime import datetime

router = APIRouter(tags=["farm"])
templates = Jinja2Templates(directory="app/templates")
FARM_GENERATE_TEMPLATE = "admin/farm_data_generator.html"
FARM_FORM_TEMPLATE = "admin/farm/farm_form.html"
FARM_DELETE_TEMPLATE = "admin/farm/farm_delete.html"
FARM_MANAGEMENT_ROUTE = "/admin/farm-management"


def _process_farm_data(farm_data):
    """Helper function to process farm data and return formatted info"""
    # Sort by timestamp (desc) to get the latest
    farm_data.sort(key=lambda x: x["timestamp"], reverse=True)
    latest_data = farm_data[0]

    # Format the timestamp
    timestamp = int(latest_data["timestamp"])
    formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    # Get product IDs for this farm
    product_ids = {
        data["product_id"]
        for data in farm_data
        if "product_id" in data and data["product_id"]
    }

    return {
        "farmId": latest_data["farm_id"],
        "dataCount": len(farm_data),
        "lastUpdate": formatted_time,
        "lastTemperature": latest_data.get("temperature", "N/A"),
        "lastHumidity": latest_data.get("humidity", "N/A"),
        "productIds": list(product_ids),
        "waterLevel": latest_data.get("water_level", "N/A"),
        "lightLevel": latest_data.get("light_level", "N/A"),
    }


@router.get("/farm-management", response_class=HTMLResponse)
async def farm_management(
    request: Request,
    current_user: User = Depends(check_admin_role),
    db: Session = Depends(get_db),
):
    """Farm management page - Only admin can access"""
    try:
        blockchain_service = BlockchainService()

        # Get all blockchain data
        all_blockchain_data = blockchain_service.get_all_sensor_data()
        # Group data by farm ID
        farm_data_map = {}
        for data in all_blockchain_data:
            if "farm_id" in data:
                farm_id = data["farm_id"]
                farm_data_map.setdefault(farm_id, []).append(data)

        # Process each farm's data
        all_farms = [
            _process_farm_data(farm_data)
            for farm_data in farm_data_map.values()
            if farm_data
        ]

        print(f"Found {len(all_farms)} farms with data")

        # Get all farms from database
        db_farms = db.query(Farm).all()

        return templates.TemplateResponse(
            "admin/farm/farm_management.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_list": all_farms,
                "db_farms": db_farms,
            },
        )
    except Exception as e:
        print(f"Error in farm management: {str(e)}")
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "error": f"Error loading farm data: {str(e)}",
            },
            status_code=500,
        )


@router.get("/farm-management/generate", response_class=HTMLResponse)
async def generate_farm_data_form(
    request: Request,
    farm_id: Optional[str] = None,
    current_user: User = Depends(check_admin_role),
):
    """Form to generate mock farm data - Only admin can access"""
    return templates.TemplateResponse(
        FARM_GENERATE_TEMPLATE,
        {"request": request, "current_user": current_user, "farm_id": farm_id},
    )


@router.get("/farm-management/generate-for/{farm_id}", response_class=HTMLResponse)
async def generate_farm_data_for_specific(
    request: Request, farm_id: str, current_user: User = Depends(check_admin_role)
):
    """Form to generate mock farm data for a specific farm - Only admin can access"""
    return templates.TemplateResponse(
        FARM_GENERATE_TEMPLATE,
        {"request": request, "current_user": current_user, "farm_id": farm_id},
    )


# Farm CRUD Routes
@router.get("/farm-management/add", response_class=HTMLResponse)
async def create_farm_form(
    request: Request, current_user: User = Depends(check_admin_role)
):
    """Form create farm - Only admin can access"""
    return templates.TemplateResponse(
        FARM_FORM_TEMPLATE,
        {"request": request, "current_user": current_user, "farm": None},
    )


@router.post("/farms/create", response_class=HTMLResponse)
async def create_farm_submit(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process create farm - Only admin can access"""
    # Check if farm with the same ID already exists
    db_farm = db.query(Farm).filter(Farm.id == id).first()
    if db_farm:
        return templates.TemplateResponse(
            FARM_FORM_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "farm": None,
                "error": f"Farm với ID '{id}' đã tồn tại",
            },
            status_code=400,
        )

    # Create new farm
    db_farm = Farm(
        id=id,
        name=name,
        description=description,
    )

    # Save to database
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)

    # Redirect to farm management page
    return RedirectResponse(
        url=FARM_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/farm-management/{farm_id}/edit", response_class=HTMLResponse)
async def edit_farm_form(
    request: Request,
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Form edit farm - Only admin can access"""
    # Find farm to edit
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": f"Farm với ID '{farm_id}' không tồn tại",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        FARM_FORM_TEMPLATE,
        {"request": request, "current_user": current_user, "farm": farm},
    )


@router.post("/farms/{farm_id}/edit", response_class=HTMLResponse)
async def edit_farm_submit(
    request: Request,
    farm_id: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process edit farm - Only admin can access"""
    # Find farm to edit
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": f"Farm với ID '{farm_id}' không tồn tại",
            },
            status_code=404,
        )

    # Update farm
    farm.name = name
    farm.description = description

    # Save to database
    db.commit()
    db.refresh(farm)

    # Redirect to farm management page
    return RedirectResponse(
        url=FARM_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/farm-management/{farm_id}/delete", response_class=HTMLResponse)
async def delete_farm_confirm(
    request: Request,
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Confirm delete farm - Only admin can access"""
    # Find farm to delete
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": f"Farm với ID '{farm_id}' không tồn tại",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        FARM_DELETE_TEMPLATE,
        {"request": request, "current_user": current_user, "farm": farm},
    )


@router.post("/farms/{farm_id}/delete", response_class=HTMLResponse)
async def delete_farm_submit(
    request: Request,
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process delete farm - Only admin can access"""
    # Find farm to delete
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": f"Farm với ID '{farm_id}' không tồn tại",
            },
            status_code=404,
        )

    # Delete from database
    db.delete(farm)
    db.commit()

    # Redirect to farm management page
    return RedirectResponse(
        url=FARM_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )
