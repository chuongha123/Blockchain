from typing import List, Optional
from fastapi import APIRouter, Depends, Form, Request, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from requests import Session
from app.constants.messages_constant import (
    CANNOT_DELETE_YOUR_OWN_ACCOUNT_ERROR_MESSAGE,
    USER_EXIST_ERROR_MESSAGE,
    USER_NOT_FOUND_ERROR_MESSAGE,
)
from app.constants.template_constant import ADMIN_ERROR_TEMPLATE
from app.services.database import get_db
from app.model.user import User, UserCreate, UserResponse, UserUpdate
from app.model.farm_data import Farm
from app.services.security import check_admin_role, get_password_hash

router = APIRouter(tags=["user"])
# Initialize templates
templates = Jinja2Templates(directory="app/templates")

USER_FORM_TEMPLATE = "admin/user/user_form.html"
USER_DELETE_TEMPLATE = "admin/user/user_delete.html"
USER_USERS_TEMPLATE = "admin/user/users.html"
USER_MANAGEMENT_ROUTE = "/admin/users-management"


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db), current_user: User = Depends(check_admin_role)
):
    """Get all users - Only admin can access"""
    users = db.query(User).all()
    return users


# Create user routes - These need to come BEFORE the parameterized routes
@router.get("/users-management/add", response_class=HTMLResponse)
async def create_user_form(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Form create user - Only admin can access"""
    # Get all farms for the form dropdown
    farms = db.query(Farm).all()
    
    # Debug: In ra số lượng farm
    print(f"DEBUG: Số lượng farm tìm được: {len(farms)}")
    if farms:
        for farm in farms:
            print(f"DEBUG: Farm ID: {farm.id}, Farm Name: {farm.name}")
    else:
        print("DEBUG: Không tìm thấy farm nào trong cơ sở dữ liệu")
        
        # Tạo farm mẫu nếu không có farm nào
        try:
            sample_farms = [
                Farm(id="FARM-001", name="Nông trại 1", description="Nông trại mẫu 1"),
                Farm(id="FARM-002", name="Nông trại 2", description="Nông trại mẫu 2"),
                Farm(id="FARM-003", name="Nông trại 3", description="Nông trại mẫu 3")
            ]
            
            for farm in sample_farms:
                db.add(farm)
            
            db.commit()
            print("DEBUG: Đã tạo 3 farm mẫu")
            
            # Lấy lại danh sách farm sau khi tạo
            farms = db.query(Farm).all()
        except Exception as e:
            print(f"DEBUG: Lỗi khi tạo farm mẫu: {str(e)}")
    
    return templates.TemplateResponse(
        USER_FORM_TEMPLATE,
        {
            "request": request, 
            "current_user": current_user, 
            "user": None,
            "farms": farms
        },
    )


@router.post("/users/create", response_class=HTMLResponse)
async def create_user_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(True),
    farm_ids: List[str] = Form([]),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process create user - Only admin can access"""
    # Check username and email
    db_user_by_username = db.query(User).filter(User.username == username).first()
    if db_user_by_username:
        farms = db.query(Farm).all()
        return templates.TemplateResponse(
            USER_FORM_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "user": None,
                "farms": farms,
                "error": USER_EXIST_ERROR_MESSAGE,
            },
            status_code=400,
        )

    db_user_by_email = db.query(User).filter(User.email == email).first()
    if db_user_by_email:
        farms = db.query(Farm).all()
        return templates.TemplateResponse(
            USER_FORM_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "user": None,
                "farms": farms,
                "error": USER_EXIST_ERROR_MESSAGE,
            },
            status_code=400,
        )

    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
        role=role,
        link_product=farm_ids[0] if farm_ids else None,  # Backward compatibility with legacy field
    )

    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Link farms to user
    for farm_id in farm_ids:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            farm.user_id = db_user.id
    
    db.commit()

    # Redirect to users management page
    return RedirectResponse(
        url=USER_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )


# Now the parameterized routes
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Get user info by ID - Only admin can access"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_ERROR_MESSAGE)
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Create new user - Only admin can access"""
    # Check username is exist
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail=USER_EXIST_ERROR_MESSAGE)

    # Check email is exist
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail=USER_EXIST_ERROR_MESSAGE)

    # Hash password
    hashed_password = get_password_hash(user.password)

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user",  # Default is user
    )

    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Update user info - Only admin can access"""
    # Find user to update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_ERROR_MESSAGE)

    # Update fields if have in request
    update_data = user_update.dict(exclude_unset=True)

    # If have password, hash before save
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    # Update data
    for key, value in update_data.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)

    # Save to database
    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Delete user - Only admin can access"""
    # Cannot delete yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail=CANNOT_DELETE_YOUR_OWN_ACCOUNT_ERROR_MESSAGE
        )

    # Find user to delete
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_ERROR_MESSAGE)

    # Delete from database
    db.delete(db_user)
    db.commit()

    return None


# Template routes cho admin panel
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, current_user: User = Depends(check_admin_role)
):
    """Admin dashboard page - Only admin can access"""
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "current_user": current_user}
    )


@router.get("/users-management", response_class=HTMLResponse)
async def users_management(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Users management page - Only admin can access"""
    users = db.query(User).all()
    return templates.TemplateResponse(
        USER_USERS_TEMPLATE,
        {"request": request, "current_user": current_user, "users": users},
    )


@router.get("/users-management/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Form edit user - Only admin can access"""
    # Find user to edit
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": USER_NOT_FOUND_ERROR_MESSAGE,
            },
            status_code=404,
        )
    
    # Get all farms
    farms = db.query(Farm).all()
    
    # Get user's farms
    user_farms = db.query(Farm).filter(Farm.user_id == user_id).all()
    user_farm_ids = [farm.id for farm in user_farms]
    
    return templates.TemplateResponse(
        USER_FORM_TEMPLATE,
        {
            "request": request, 
            "current_user": current_user, 
            "user": user,
            "farms": farms,
            "user_farm_ids": user_farm_ids
        },
    )


@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_submit(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    password: Optional[str] = Form(None),
    role: str = Form(...),
    is_active: bool = Form(True),
    farm_ids: List[str] = Form([]),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process edit user - Only admin can access"""
    # Find user to edit
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "status_code": 404,
                "detail": USER_NOT_FOUND_ERROR_MESSAGE,
            },
            status_code=404,
        )

    # Check username only if changed
    if user.username != username:
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            farms = db.query(Farm).all()
            user_farms = db.query(Farm).filter(Farm.user_id == user_id).all()
            user_farm_ids = [farm.id for farm in user_farms]
            return templates.TemplateResponse(
                USER_FORM_TEMPLATE,
                {
                    "request": request,
                    "current_user": current_user,
                    "user": user,
                    "farms": farms,
                    "user_farm_ids": user_farm_ids,
                    "error": USER_EXIST_ERROR_MESSAGE,
                },
                status_code=400,
            )

    # Check email only if changed
    if user.email != email:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            farms = db.query(Farm).all()
            user_farms = db.query(Farm).filter(Farm.user_id == user_id).all()
            user_farm_ids = [farm.id for farm in user_farms]
            return templates.TemplateResponse(
                USER_FORM_TEMPLATE,
                {
                    "request": request,
                    "current_user": current_user,
                    "user": user,
                    "farms": farms,
                    "user_farm_ids": user_farm_ids,
                    "error": USER_EXIST_ERROR_MESSAGE,
                },
                status_code=400,
            )

    # Update user
    user.username = username
    user.email = email
    user.role = role
    user.is_active = is_active
    user.link_product = farm_ids[0] if farm_ids else None  # Backward compatibility with legacy field

    # Only update password if provided
    if password:
        user.hashed_password = get_password_hash(password)

    # Update user's farms
    # First, remove all existing farm connections
    for farm in db.query(Farm).filter(Farm.user_id == user_id).all():
        farm.user_id = None
    
    # Then, add new connections
    for farm_id in farm_ids:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            farm.user_id = user_id
    
    # Save all changes
    db.commit()

    # Redirect to users management page
    return RedirectResponse(
        url=USER_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/users-management/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_confirm(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Confirm delete user - Only admin can access"""
    # Find user to delete
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "error": USER_NOT_FOUND_ERROR_MESSAGE,
            },
            status_code=404,
        )

    # Cannot delete yourself
    if current_user.id == user_id:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "error": CANNOT_DELETE_YOUR_OWN_ACCOUNT_ERROR_MESSAGE,
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        USER_DELETE_TEMPLATE,
        {"request": request, "current_user": current_user, "user": user},
    )


@router.post("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_submit(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role),
):
    """Process delete user - Only admin can access"""
    # Cannot delete yourself
    if current_user.id == user_id:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "error": "Cannot delete your own account",
            },
            status_code=400,
        )

    # Find user to delete
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return templates.TemplateResponse(
            ADMIN_ERROR_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "error": "User not found",
            },
            status_code=404,
        )

    # Delete from database
    db.delete(db_user)
    db.commit()

    # Redirect to users management page
    return RedirectResponse(
        url=USER_MANAGEMENT_ROUTE, status_code=status.HTTP_303_SEE_OTHER
    )
