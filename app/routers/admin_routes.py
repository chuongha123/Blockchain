from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.model.user import User, UserResponse, UserCreate, UserUpdate
from app.security import check_admin_role, get_password_hash

# Initialize router for admin
router = APIRouter(prefix="/admin", tags=["admin"])

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# API routes for user management
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Get all users - Only admin can access"""
    users = db.query(User).all()
    return users

# Create user routes - These need to come BEFORE the parameterized routes
@router.get("/users/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request, 
    current_user: User = Depends(check_admin_role)
):
    """Form create user - Only admin can access"""
    return templates.TemplateResponse(
        "admin/user_form.html", 
        {"request": request, "current_user": current_user, "user": None}
    )

@router.post("/users/create", response_class=HTMLResponse)
async def create_user_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(True),
    link_product: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Process create user - Only admin can access"""
    # Check username and email
    db_user_by_username = db.query(User).filter(User.username == username).first()
    if db_user_by_username:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request, 
                "current_user": current_user, 
                "user": None,
                "error": "Username is exist"
            },
            status_code=400
        )
    
    db_user_by_email = db.query(User).filter(User.email == email).first()
    if db_user_by_email:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request, 
                "current_user": current_user, 
                "user": None,
                "error": "Email is exist"
            },
            status_code=400
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
        role=role,
        link_product=link_product
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    
    # Redirect to users management page
    return RedirectResponse(
        url="/admin/users-management",
        status_code=status.HTTP_303_SEE_OTHER
    )

# Now the parameterized routes
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Get user info by ID - Only admin can access"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Create new user - Only admin can access"""
    # Check username is exist
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username is exist")
    
    # Check email is exist
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email is exist")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user"  # Default is user
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
    current_user: User = Depends(check_admin_role)
):
    """Update user info - Only admin can access"""
    # Find user to update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
    current_user: User = Depends(check_admin_role)
):
    """Delete user - Only admin can access"""
    # Cannot delete yourself
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Find user to delete
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete from database
    db.delete(db_user)
    db.commit()
    
    return None

# Template routes cho admin panel
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    current_user: User = Depends(check_admin_role)
):
    """Admin dashboard page - Only admin can access"""
    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {"request": request, "current_user": current_user}
    )

@router.get("/users-management", response_class=HTMLResponse)
async def users_management(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Users management page - Only admin can access"""
    users = db.query(User).all()
    return templates.TemplateResponse(
        "admin/users.html", 
        {"request": request, "current_user": current_user, "users": users}
    )

@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Form edit user - Only admin can access"""
    # Find user to edit
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "User not found"
            },
            status_code=404
        )
    
    return templates.TemplateResponse(
        "admin/user_form.html", 
        {"request": request, "current_user": current_user, "user": user}
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
    link_product: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Process edit user - Only admin can access"""
    # Find user to update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "User not found"
            },
            status_code=404
        )
    
    # Check username is exist in database
    if username != db_user.username:
        db_user_by_username = db.query(User).filter(User.username == username).first()
        if db_user_by_username:
            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request, 
                    "current_user": current_user, 
                    "user": db_user,
                    "error": "Username is exist"
                },
                status_code=400
            )
    
    # Check email is exist in database
    if email != db_user.email:
        db_user_by_email = db.query(User).filter(User.email == email).first()
        if db_user_by_email:
            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request, 
                    "current_user": current_user, 
                    "user": db_user,
                    "error": "Email is exist"
                },
                status_code=400
            )
    
    # Update user info
    db_user.username = username
    db_user.email = email
    db_user.is_active = is_active
    db_user.role = role
    db_user.link_product = link_product
    
    # Update password if have
    if password:
        db_user.hashed_password = get_password_hash(password)
    
    # Save to database
    db.commit()
    
    # Redirect to users management page
    return RedirectResponse(
        url="/admin/users-management",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_confirm(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Confirm delete user - Only admin can access"""
    # Find user to delete
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Không tìm thấy người dùng"
            },
            status_code=404
        )
    
    # Cannot delete yourself
    if current_user.id == user_id:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Cannot delete your own account"
            },
            status_code=400
        )
    
    return templates.TemplateResponse(
        "admin/user_delete.html", 
        {"request": request, "current_user": current_user, "user": user}
    )

@router.post("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_submit(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Process delete user - Only admin can access"""
    # Cannot delete yourself
    if current_user.id == user_id:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Cannot delete your own account"
            },
            status_code=400
        )
    
    # Find user to delete
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "User not found"
            },
            status_code=404
        )
    
    # Delete from database
    db.delete(db_user)
    db.commit()
    
    # Redirect to users management page
    return RedirectResponse(
        url="/admin/users-management",
        status_code=status.HTTP_303_SEE_OTHER
    ) 