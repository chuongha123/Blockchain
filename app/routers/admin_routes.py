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

# Template constants
USER_FORM_TEMPLATE = "admin/user_form.html"
ADMIN_ERROR_TEMPLATE = "admin/error.html"


# API routes for user management
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db), current_user: User = Depends(check_admin_role)
):
    """Get all users - Only admin can access"""
    users = db.query(User).all()
    return users


# Create user routes - These need to come BEFORE the parameterized routes
@router.get("/users/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request, current_user: User = Depends(check_admin_role)
):
    """Form create user - Only admin can access"""
    return templates.TemplateResponse(
        USER_FORM_TEMPLATE,
        {"request": request, "current_user": current_user, "user": None},
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
    current_user: User = Depends(check_admin_role),
):
    """Process create user - Only admin can access"""
    # Check username and email
    db_user_by_username = db.query(User).filter(User.username == username).first()
    if db_user_by_username:
        return templates.TemplateResponse(
            USER_FORM_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "user": None,
                "error": "Username is exist",
            },
            status_code=400,
        )

    db_user_by_email = db.query(User).filter(User.email == email).first()
    if db_user_by_email:
        return templates.TemplateResponse(
            USER_FORM_TEMPLATE,
            {
                "request": request,
                "current_user": current_user,
                "user": None,
                "error": "Email is exist",
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
        link_product=link_product,
    )

    # Save to database
    db.add(db_user)
    db.commit()

    # Redirect to users management page
    return RedirectResponse(
        url="/admin/users-management", status_code=status.HTTP_303_SEE_OTHER
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
        raise HTTPException(status_code=404, detail="User not found")
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
    current_user: User = Depends(check_admin_role),
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
        "admin/users.html",
        {"request": request, "current_user": current_user, "users": users},
    )


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
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
                "error": "User not found",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        USER_FORM_TEMPLATE,
        {"request": request, "current_user": current_user, "user": user},
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
    current_user: User = Depends(check_admin_role),
):
    """Process edit user - Only admin can access"""
    # Find user to update
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

    # Check username is exist in database
    if username != db_user.username:
        db_user_by_username = db.query(User).filter(User.username == username).first()
        if db_user_by_username:
            return templates.TemplateResponse(
                USER_FORM_TEMPLATE,
                {
                    "request": request,
                    "current_user": current_user,
                    "user": db_user,
                    "error": "Username is exist",
                },
                status_code=400,
            )

    # Check email is exist in database
    if email != db_user.email:
        db_user_by_email = db.query(User).filter(User.email == email).first()
        if db_user_by_email:
            return templates.TemplateResponse(
                USER_FORM_TEMPLATE,
                {
                    "request": request,
                    "current_user": current_user,
                    "user": db_user,
                    "error": "Email is exist",
                },
                status_code=400,
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
        url="/admin/users-management", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/users/{user_id}/delete", response_class=HTMLResponse)
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
                "error": "Không tìm thấy người dùng",
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
                "error": "Cannot delete your own account",
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        "admin/user_delete.html",
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
        url="/admin/users-management", status_code=status.HTTP_303_SEE_OTHER
    )


# Farm Management Routes
@router.get("/farm-management", response_class=HTMLResponse)
async def farm_management(
    request: Request,
    farmId: Optional[str] = None,
    productId: Optional[str] = None,
    current_user: User = Depends(check_admin_role),
):
    """Farm management page - Only admin can access"""
    try:
        # Import here to avoid circular import
        from app.blockchain import BlockchainService
        import time
        from datetime import datetime

        blockchain_service = BlockchainService()

        # Get all unique farm IDs from blockchain
        all_farms = []
        farmIds = set()

        # If search filters are provided, apply them
        if farmId or productId:
            # For now, if both filters are provided, we'll just use farmId
            # A more sophisticated approach would scan all farms and filter by productId too
            if farmId:
                farm_data = blockchain_service.get_sensor_data_by_farm_id(farmId)
                if farm_data:
                    farmIds.add(farmId)
        else:
            # This is simple for now - in a real system, we'd need a getUniqueFarmIds function
            # For now, we'll just get data from a few predefined farm IDs to check
            predefined_farms = ["FARM123", "FARM456", "FARM789"]
            for farm_id in predefined_farms:
                data = blockchain_service.get_sensor_data_by_farm_id(farm_id)
                if data and len(data) > 0:
                    farmIds.add(farm_id)

        # For each farm ID, get the last entry and count
        for farm_id in farmIds:
            farm_data = blockchain_service.get_sensor_data_by_farm_id(farm_id)

            if farm_data and len(farm_data) > 0:
                # Sort by timestamp (desc) to get the latest
                farm_data.sort(key=lambda x: x["timestamp"], reverse=True)
                latest_data = farm_data[0]

                # Format the timestamp
                timestamp = int(latest_data["timestamp"])
                formatted_time = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                farm_info = {
                    "farmId": farm_id,
                    "dataCount": len(farm_data),
                    "lastUpdate": formatted_time,
                    "lastTemperature": latest_data["temperature"],
                    "lastHumidity": latest_data["humidity"],
                }

                all_farms.append(farm_info)

        return templates.TemplateResponse(
            "admin/farm_management.html",
            {"request": request, "current_user": current_user, "farm_list": all_farms},
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
        "admin/farm_data_generator.html",
        {"request": request, "current_user": current_user, "farm_id": farm_id},
    )


@router.get("/farm-management/generate-for/{farm_id}", response_class=HTMLResponse)
async def generate_farm_data_for_specific(
    request: Request, farm_id: str, current_user: User = Depends(check_admin_role)
):
    """Form to generate mock farm data for a specific farm - Only admin can access"""
    return templates.TemplateResponse(
        "admin/farm_data_generator.html",
        {"request": request, "current_user": current_user, "farm_id": farm_id},
    )


@router.post("/farm-management/generate-random", response_class=HTMLResponse)
async def generate_random_farm_data(
    request: Request,
    farm_id: str = Form(...),
    count: int = Form(10),
    product_id: Optional[str] = Form(None),
    min_temp: float = Form(20.0),
    max_temp: float = Form(35.0),
    min_humidity: float = Form(30.0),
    max_humidity: float = Form(90.0),
    min_water: float = Form(20.0),
    max_water: float = Form(100.0),
    min_light: float = Form(200.0),
    max_light: float = Form(800.0),
    current_user: User = Depends(check_admin_role),
):
    """Process mock data generation - Only admin can access"""
    try:
        from app.routers.mock_data_api import generate_random_product_id
        from app.blockchain import BlockchainService
        import random

        blockchain_service = BlockchainService()

        if count > 100:
            count = 100  # Limit to 100 for safety

        # Generate and store mock data
        results = []
        errors = []

        for i in range(count):
            # Generate mock data
            mock_data = {
                "farm_id": farm_id,
                "temperature": round(random.uniform(min_temp, max_temp), 2),
                "humidity": round(random.uniform(min_humidity, max_humidity), 1),
                "water_level": round(random.uniform(min_water, max_water), 1),
                "light_level": round(random.uniform(min_light, max_light), 1),
                "product_id": product_id or generate_random_product_id(),
                "timestamp": int(time.time()),
            }

            try:
                # Store data in blockchain
                tx_hash = blockchain_service.store_sensor_data(farm_id, mock_data)

                if tx_hash:
                    results.append({"success": True, "transaction_hash": tx_hash})
                else:
                    errors.append(f"Failed to store data batch {i+1}")
            except Exception as e:
                errors.append(f"Error in batch {i+1}: {str(e)}")

        # Return to generator page with result
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "success": f"Generated {len(results)} random data points for farm {farm_id}.",
                "error": "\n".join(errors) if errors else None,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "error": f"Error generating mock data: {str(e)}",
            },
        )


@router.post("/farm-management/generate-date-range", response_class=HTMLResponse)
async def generate_date_range_farm_data(
    request: Request,
    farm_id: str = Form(...),
    start_date: str = Form(...),
    end_date: Optional[str] = Form(None),
    interval_hours: int = Form(6),
    min_temp: float = Form(20.0),
    max_temp: float = Form(35.0),
    min_humidity: float = Form(30.0),
    max_humidity: float = Form(90.0),
    min_water: float = Form(20.0),
    max_water: float = Form(100.0),
    min_light: float = Form(200.0),
    max_light: float = Form(800.0),
    product_id: Optional[str] = Form(None),
    current_user: User = Depends(check_admin_role),
):
    """Generate farm data for a date range - Only admin can access"""
    try:
        from app.routers.mock_data_api import generate_random_product_id
        from app.blockchain import BlockchainService
        import random
        from datetime import datetime, timedelta

        blockchain_service = BlockchainService()

        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()

        # Ensure start_date is before end_date
        if start > end:
            return templates.TemplateResponse(
                "admin/farm_data_generator.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "farm_id": farm_id,
                    "error": "Start date must be before end date",
                },
            )

        # Calculate number of data points based on date range and interval
        interval = timedelta(hours=interval_hours)
        current_date = start
        data_points = []

        # Generate timestamps for each data point
        while current_date <= end:
            data_points.append(current_date)
            current_date += interval

        # Check if we're generating too many points
        if len(data_points) > 300:
            return templates.TemplateResponse(
                "admin/farm_data_generator.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "farm_id": farm_id,
                    "error": f"Date range and interval would generate {len(data_points)} records. Maximum is 300. Please use a larger interval or smaller date range.",
                },
            )

        results = []
        errors = []

        # Generate and store data for each timestamp
        for timestamp in data_points:
            # Generate mock data
            mock_data = {
                "farm_id": farm_id,
                "temperature": round(random.uniform(min_temp, max_temp), 2),
                "humidity": round(random.uniform(min_humidity, max_humidity), 1),
                "water_level": round(random.uniform(min_water, max_water), 1),
                "light_level": round(random.uniform(min_light, max_light), 1),
                "product_id": product_id or generate_random_product_id(),
                "timestamp": int(timestamp.timestamp()),
            }

            try:
                # Store data in blockchain
                tx_hash = blockchain_service.store_sensor_data(farm_id, mock_data)

                if tx_hash:
                    results.append(
                        {
                            "success": True,
                            "timestamp": timestamp.isoformat(),
                            "transaction_hash": tx_hash,
                        }
                    )
                else:
                    errors.append(
                        f"Failed to store data point at {timestamp.isoformat()}"
                    )
            except Exception as e:
                errors.append(
                    f"Error in data point at {timestamp.isoformat()}: {str(e)}"
                )

        # Return to generator page with result
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "success": f"Generated {len(results)} data points for farm {farm_id} from {start_date} to {end_date or 'today'}.",
                "error": "\n".join(errors) if errors else None,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "error": f"Error generating date range data: {str(e)}",
            },
        )


@router.post("/farm-management/generate-specific-date", response_class=HTMLResponse)
async def generate_specific_date_farm_data(
    request: Request,
    farm_id: str = Form(...),
    date: str = Form(...),
    count_per_day: int = Form(4),
    min_temp: float = Form(20.0),
    max_temp: float = Form(35.0),
    min_humidity: float = Form(30.0),
    max_humidity: float = Form(90.0),
    min_water: float = Form(20.0),
    max_water: float = Form(100.0),
    min_light: float = Form(200.0),
    max_light: float = Form(800.0),
    product_id: Optional[str] = Form(None),
    current_user: User = Depends(check_admin_role),
):
    """Generate farm data for a specific date - Only admin can access"""
    try:
        from app.routers.mock_data_api import generate_random_product_id
        from app.blockchain import BlockchainService
        import random
        from datetime import datetime, timedelta

        blockchain_service = BlockchainService()

        if count_per_day > 24:
            count_per_day = 24  # Limit to 24 for safety (one per hour)

        try:
            # Parse the date string
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return templates.TemplateResponse(
                "admin/farm_data_generator.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "farm_id": farm_id,
                    "error": "Invalid date format. Use YYYY-MM-DD format.",
                },
            )

        # Calculate hour interval based on count_per_day
        hour_interval = 24 // count_per_day

        results = []
        errors = []

        for i in range(count_per_day):
            # Generate timestamp for specific hours of the day
            hour = i * hour_interval
            target_datetime = target_date.replace(hour=hour)
            timestamp = int(target_datetime.timestamp())

            # Generate mock data
            mock_data = {
                "farm_id": farm_id,
                "temperature": round(random.uniform(min_temp, max_temp), 2),
                "humidity": round(random.uniform(min_humidity, max_humidity), 1),
                "water_level": round(random.uniform(min_water, max_water), 1),
                "light_level": round(random.uniform(min_light, max_light), 1),
                "product_id": product_id or generate_random_product_id(),
                "timestamp": timestamp,
            }

            try:
                # Store data in blockchain
                tx_hash = blockchain_service.store_sensor_data(farm_id, mock_data)

                if tx_hash:
                    formatted_time = datetime.fromtimestamp(timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    results.append(
                        {
                            "success": True,
                            "time": formatted_time,
                            "transaction_hash": tx_hash,
                        }
                    )
                else:
                    errors.append(f"Failed to store data point at hour {hour}")
            except Exception as e:
                errors.append(f"Error in data point at hour {hour}: {str(e)}")

        # Return to generator page with result
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "success": f"Generated {len(results)} data points for farm {farm_id} on {date}.",
                "error": "\n".join(errors) if errors else None,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "admin/farm_data_generator.html",
            {
                "request": request,
                "current_user": current_user,
                "farm_id": farm_id,
                "error": f"Error generating specific date data: {str(e)}",
            },
        )


@router.post("/farm-management/delete", response_class=HTMLResponse)
async def delete_farm_data(
    request: Request,
    farmId: str = Form(...),
    current_user: User = Depends(check_admin_role),
):
    """Delete farm data for a specific farm - Only admin can access"""
    error_message = None
    success_message = None

    try:
        # Since blockchain data is immutable, we can't actually delete it
        # In a real app, we might mark it as "deleted" in a database
        # For this demo, we'll just return a message saying this isn't supported

        error_message = "Xóa dữ liệu blockchain không được hỗ trợ vì tính chất bất biến của blockchain. Thay vào đó, bạn có thể thêm một cơ chế đánh dấu dữ liệu là 'đã xóa' trong ứng dụng của mình."
    except Exception as e:
        error_message = f"Lỗi khi xử lý yêu cầu xóa: {str(e)}"

    # Redirect back to farm management page
    return templates.TemplateResponse(
        "admin/farm_management.html",
        {
            "request": request,
            "current_user": current_user,
            "error": error_message,
            "success": success_message,
            "farm_list": [],  # We'll reload the farm list
        },
    )
