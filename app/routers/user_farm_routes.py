import os

from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.model.farm_data import Farm, Product
from app.model.user import User
from app.services.database import get_db
from app.services.security import get_current_active_user

router = APIRouter(prefix="/user-farms", tags=["user-farms"])
templates = Jinja2Templates(directory=os.path.join("app", "templates"))


@router.get("/link-farm", response_class=HTMLResponse)
async def link_farm_form(
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
):
    """Render form to link user with farms"""
    # Get all available farms
    available_farms = db.query(Farm).all()

    # Get user's current farms
    user_farms = db.query(Farm).filter(Farm.user_id == current_user.id).all()

    return templates.TemplateResponse(
        "link_farm.html",
        {
            "request": request,
            "current_user": current_user,
            "available_farms": available_farms,
            "user_farms": user_farms,
        },
    )


@router.post("/link-farm")
async def link_farm(
        farm_id: str = Form(...),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
):
    """Link a farm to the current user"""
    # Check if farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )

    # Link farm to user
    farm.user_id = current_user.id
    db.commit()

    return RedirectResponse(url="/users/me", status_code=303)


@router.post("/unlink-farm/{farm_id}")
async def unlink_farm(
        farm_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
):
    """Unlink a farm from the current user"""
    # Check if farm exists and belongs to user
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id, Farm.user_id == current_user.id)
        .first()
    )
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found or doesn't belong to you",
        )

    # Unlink farm from user
    farm.user_id = None
    db.commit()

    return RedirectResponse(url="/users/me", status_code=303)


@router.get("/my-farms", response_class=HTMLResponse)
async def my_farms(
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
):
    """View all farms linked to the current user"""
    # Get user's farms
    user_farms = db.query(Farm).filter(Farm.user_id == current_user.id).all()

    # For each farm, get product info to determine if harvested
    for farm in user_farms:
        product = db.query(Product).filter(Product.id == farm.id).first()
        if product:
            setattr(farm, "is_harvested", product.is_harvested)
        else:
            setattr(farm, "is_harvested", False)

    return templates.TemplateResponse(
        "my_farms.html",
        {"request": request, "current_user": current_user, "farms": user_farms},
    )
