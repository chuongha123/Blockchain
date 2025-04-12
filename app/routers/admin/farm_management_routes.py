from datetime import time
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.constants.template_constant import ADMIN_ERROR_TEMPLATE
from app.model.user import User
from app.security import check_admin_role
from app.blockchain import BlockchainService
from datetime import datetime

router = APIRouter(tags=["farm"])
templates = Jinja2Templates(directory="app/templates")
FARM_GENERATE_TEMPLATE = "admin/farm_data_generator.html"


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

        return templates.TemplateResponse(
            "admin/farm/farm_management.html",
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
            FARM_GENERATE_TEMPLATE,
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
            FARM_GENERATE_TEMPLATE,
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
                FARM_GENERATE_TEMPLATE,
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
                FARM_GENERATE_TEMPLATE,
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
            FARM_GENERATE_TEMPLATE,
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
            FARM_GENERATE_TEMPLATE,
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
                FARM_GENERATE_TEMPLATE,
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
            FARM_GENERATE_TEMPLATE,
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
            FARM_GENERATE_TEMPLATE,
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
        "admin/farm/farm_management.html",
        {
            "request": request,
            "current_user": current_user,
            "error": error_message,
            "success": success_message,
            "farm_list": [],  # We'll reload the farm list
        },
    )
