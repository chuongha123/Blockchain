from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from requests import Session
import uuid

from app.model.farm_data import Product
from app.model.user import User
from app.services.database import get_db
from app.services.security import check_admin_role

router = APIRouter(tags=["product-management"])
# Initialize templates
templates = Jinja2Templates(directory="app/templates")

PRODUCT_MANAGEMENT_TEMPLATE = "pages/admin/product/product_management.html"
PRODUCT_CREATE_TEMPLATE = "pages/admin/product/product_create.html"
PRODUCT_EDIT_TEMPLATE = "pages/admin/product/product_edit.html"


@router.get("/product-management", response_class=HTMLResponse)
async def product_management(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    products = db.query(Product).all()
    return templates.TemplateResponse(
        PRODUCT_MANAGEMENT_TEMPLATE,
        {"request": request, "current_user": current_user, "products": products},
    )


@router.get("/product-management/create", response_class=HTMLResponse)
async def product_create_form(
    request: Request,
    current_user: User = Depends(check_admin_role),
):
    return templates.TemplateResponse(
        PRODUCT_CREATE_TEMPLATE,
        {"request": request, "current_user": current_user},
    )


@router.post("/product-management/create", response_class=HTMLResponse)
async def product_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    product = Product(
        id=str(uuid.uuid4()), name=name, description=description, is_harvested=False
    )

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/admin/product-management", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/product-management/{product_id}/edit", response_class=HTMLResponse)
async def product_edit_form(
    request: Request,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse(
        PRODUCT_EDIT_TEMPLATE,
        {"request": request, "current_user": current_user, "product": product},
    )


@router.post("/product-management/{product_id}/edit", response_class=HTMLResponse)
async def product_edit(
    request: Request,
    product_id: str,
    name: str = Form(...),
    description: str = Form(None),
    is_harvested: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = name
    product.description = description
    product.is_harvested = is_harvested

    db.commit()

    return RedirectResponse(
        url="/admin/product-management", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/product-management/{product_id}/delete")
async def product_delete(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return RedirectResponse(
        url="/admin/product-management", status_code=status.HTTP_303_SEE_OTHER
    )
