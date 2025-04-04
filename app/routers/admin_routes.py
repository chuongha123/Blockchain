from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.model.user import User, UserResponse, UserCreate, UserUpdate
from app.security import check_admin_role, get_password_hash

# Khởi tạo router cho admin
router = APIRouter(prefix="/admin", tags=["admin"])

# Khởi tạo templates
templates = Jinja2Templates(directory="app/templates")

# API routes cho quản lý user
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Lấy danh sách tất cả người dùng - Chỉ admin mới có quyền truy cập"""
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Lấy thông tin một người dùng theo ID - Chỉ admin mới có quyền truy cập"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Tạo người dùng mới - Chỉ admin mới có quyền truy cập"""
    # Kiểm tra username đã tồn tại chưa
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    
    # Kiểm tra email đã tồn tại chưa
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    
    # Mã hóa mật khẩu
    hashed_password = get_password_hash(user.password)
    
    # Tạo user mới
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user"  # Mặc định là user
    )
    
    # Lưu vào database
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
    """Cập nhật thông tin người dùng - Chỉ admin mới có quyền truy cập"""
    # Tìm user cần update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    # Cập nhật các trường nếu có trong request
    update_data = user_update.dict(exclude_unset=True)
    
    # Nếu có password, mã hóa trước khi lưu
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Cập nhật dữ liệu
    for key, value in update_data.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)
    
    # Lưu vào database
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_role)
):
    """Xóa người dùng - Chỉ admin mới có quyền truy cập"""
    # Không cho phép admin tự xóa chính mình
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản của chính mình")
    
    # Tìm user cần xóa
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    # Xóa khỏi database
    db.delete(db_user)
    db.commit()
    
    return None

# Template routes cho admin panel
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    current_user: User = Depends(check_admin_role)
):
    """Trang dashboard admin - Chỉ admin mới có quyền truy cập"""
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
    """Trang quản lý người dùng - Chỉ admin mới có quyền truy cập"""
    users = db.query(User).all()
    return templates.TemplateResponse(
        "admin/users.html", 
        {"request": request, "current_user": current_user, "users": users}
    )

@router.get("/users/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request, 
    current_user: User = Depends(check_admin_role)
):
    """Form tạo người dùng mới - Chỉ admin mới có quyền truy cập"""
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
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Xử lý form tạo người dùng mới - Chỉ admin mới có quyền truy cập"""
    # Kiểm tra username và email
    db_user_by_username = db.query(User).filter(User.username == username).first()
    if db_user_by_username:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request, 
                "current_user": current_user, 
                "user": None,
                "error": "Tên đăng nhập đã tồn tại"
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
                "error": "Email đã tồn tại"
            },
            status_code=400
        )
    
    # Tạo người dùng mới
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
        role=role
    )
    
    # Lưu vào database
    db.add(db_user)
    db.commit()
    
    # Chuyển về trang quản lý người dùng
    return RedirectResponse(
        url="/admin/users-management",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Form chỉnh sửa người dùng - Chỉ admin mới có quyền truy cập"""
    # Tìm user cần chỉnh sửa
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
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Xử lý form chỉnh sửa người dùng - Chỉ admin mới có quyền truy cập"""
    # Tìm user cần update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Không tìm thấy người dùng"
            },
            status_code=404
        )
    
    # Kiểm tra username đã tồn tại chưa (nếu thay đổi)
    if username != db_user.username:
        db_user_by_username = db.query(User).filter(User.username == username).first()
        if db_user_by_username:
            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request, 
                    "current_user": current_user, 
                    "user": db_user,
                    "error": "Tên đăng nhập đã tồn tại"
                },
                status_code=400
            )
    
    # Kiểm tra email đã tồn tại chưa (nếu thay đổi)
    if email != db_user.email:
        db_user_by_email = db.query(User).filter(User.email == email).first()
        if db_user_by_email:
            return templates.TemplateResponse(
                "admin/user_form.html",
                {
                    "request": request, 
                    "current_user": current_user, 
                    "user": db_user,
                    "error": "Email đã tồn tại"
                },
                status_code=400
            )
    
    # Cập nhật thông tin
    db_user.username = username
    db_user.email = email
    db_user.is_active = is_active
    db_user.role = role
    
    # Cập nhật mật khẩu nếu có
    if password:
        db_user.hashed_password = get_password_hash(password)
    
    # Lưu vào database
    db.commit()
    
    # Chuyển về trang quản lý người dùng
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
    """Xác nhận xóa người dùng - Chỉ admin mới có quyền truy cập"""
    # Tìm user cần xóa
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
    
    # Không cho phép admin tự xóa chính mình
    if current_user.id == user_id:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Không thể xóa tài khoản của chính mình"
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
    """Xử lý xóa người dùng - Chỉ admin mới có quyền truy cập"""
    # Không cho phép admin tự xóa chính mình
    if current_user.id == user_id:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Không thể xóa tài khoản của chính mình"
            },
            status_code=400
        )
    
    # Tìm user cần xóa
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return templates.TemplateResponse(
            "admin/error.html",
            {
                "request": request, 
                "current_user": current_user,
                "error": "Không tìm thấy người dùng"
            },
            status_code=404
        )
    
    # Xóa khỏi database
    db.delete(db_user)
    db.commit()
    
    # Chuyển về trang quản lý người dùng
    return RedirectResponse(
        url="/admin/users-management",
        status_code=status.HTTP_303_SEE_OTHER
    ) 