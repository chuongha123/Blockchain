import random
import string
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.blockchain import BlockchainService
from app.model.farm_data import FarmData
from app.model.user import User
from app.services.security import get_optional_user

# Initialize API router
router = APIRouter(prefix="/api/mock", tags=["mock"])

# Initialize blockchain service
blockchain_service = BlockchainService()


def generate_random_product_id(prefix="PROD", length=8):
    """Generate random product ID"""
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choice(chars) for _ in range(length))
    return f"{prefix}-{random_part}"


class MockDataRequest(BaseModel):
    farm_id: str
    count: int = 1
    min_temp: float = 20.0
    max_temp: float = 35.0
    min_humidity: float = 30.0
    max_humidity: float = 90.0
    min_water: float = 20.0
    max_water: float = 100.0
    min_light: float = 200.0
    max_light: float = 800.0
    product_id: Optional[str] = None


def generate_random_product_id():
    """Generate a random product ID string"""
    letters = string.ascii_uppercase
    numbers = string.digits
    return (
        "".join(random.choice(letters) for _ in range(3))
        + "-"
        + "".join(random.choice(numbers) for _ in range(5))
    )


@router.post("/generate")
async def generate_mock_data(request: MockDataRequest):
    """Generate and store mock data in blockchain"""
    if request.count > 100:
        raise HTTPException(
            status_code=400, detail="Cannot generate more than 100 records at once"
        )

    results = []
    errors = []

    for i in range(request.count):
        # Generate random data within specified ranges
        mock_data = FarmData(
            farm_id=request.farm_id,
            temperature=round(random.uniform(request.min_temp, request.max_temp), 2),
            humidity=round(
                random.uniform(request.min_humidity, request.max_humidity), 1
            ),
            water_level=round(random.uniform(request.min_water, request.max_water), 1),
            light_level=round(random.uniform(request.min_light, request.max_light), 1),
            product_id=request.product_id or generate_random_product_id(),
        )

        # Prepare payload for blockchain
        farm_payload = {
            "temperature": mock_data.temperature,
            "farm_id": mock_data.farm_id,
            "humidity": mock_data.humidity,
            "water_level": mock_data.water_level,
            "product_id": mock_data.product_id,
            "light_level": mock_data.light_level,
        }

        try:
            # Call service to store data
            tx_hash = blockchain_service.store_sensor_data(
                mock_data.farm_id, farm_payload
            )

            if tx_hash:
                results.append(
                    {"success": True, "data": farm_payload, "transaction_hash": tx_hash}
                )
            else:
                errors.append(f"Failed to store data batch {i+1}")
        except Exception as e:
            errors.append(f"Error in batch {i+1}: {str(e)}")

    # Return result summary
    return {
        "success": len(errors) == 0,
        "total": request.count,
        "successful": len(results),
        "failed": len(errors),
        "errors": errors if errors else None,
        "results": results,
    }


@router.post("/bulk")
async def generate_bulk_mock_data(
    request: List[FarmData], current_user: User = Depends(get_optional_user)
):
    """Store bulk custom data in blockchain"""
    if len(request) > 100:
        raise HTTPException(
            status_code=400, detail="Cannot process more than 100 records at once"
        )

    results = []
    errors = []

    for i, data in enumerate(request):
        # Prepare payload for blockchain
        farm_payload = {
            "temperature": data.temperature,
            "farm_id": data.farm_id,
            "humidity": data.humidity,
            "water_level": data.water_level,
            "product_id": data.product_id,
            "light_level": data.light_level,
        }

        try:
            # Call service to store data
            tx_hash = blockchain_service.store_sensor_data(data.farm_id, farm_payload)

            if tx_hash:
                results.append(
                    {"success": True, "data": farm_payload, "transaction_hash": tx_hash}
                )
            else:
                errors.append(f"Failed to store data item {i+1}")
        except Exception as e:
            errors.append(f"Error in item {i+1}: {str(e)}")

    # Return result summary
    return {
        "success": len(errors) == 0,
        "total": len(request),
        "successful": len(results),
        "failed": len(errors),
        "errors": errors if errors else None,
        "results": results,
    }
