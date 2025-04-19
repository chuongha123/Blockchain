from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.security import get_optional_user
from app.model.user import User

# Initialize templates router
router = APIRouter(tags=["templates"])

# Initialize templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: User = Depends(get_optional_user)):
    """Home page - No authentication required"""
    return templates.TemplateResponse(
        "home.html", {"request": request, "current_user": current_user}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/farm/{farm_id}", response_class=HTMLResponse)
async def farm_data(
    request: Request, farm_id: str, current_user: User = Depends(get_optional_user)
):
    """Display farm information by device_id - Requires authentication"""
    # Import here to avoid circular import
    from app.services.blockchain import BlockchainService

    if not current_user or not current_user.is_active:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "You are not active user",
            },
        )

    blockchain_service = BlockchainService()

    # Get data from blockchain
    data = blockchain_service.get_sensor_data_by_farm_id(farm_id)

    if not data:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"No data found for device {farm_id}",
            },
        )

    # Return template with data
    return templates.TemplateResponse(
        "farm_data.html",
        {
            "request": request,
            "current_user": current_user,
            "farm_id": farm_id,
            "data": data,
        },
    )
