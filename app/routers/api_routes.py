from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.farm_report_service import FarmReportService

from app.routers.admin.farm_api_routes import router as farm_api_router
from app.model.farm_data import FarmData, Farm
from app.model.user import User
from app.services.security import get_current_active_user
from app.utils import generate_random_report_id
from sqlalchemy.orm import Session
from app.services.database import get_db

# Initialize API router
router = APIRouter(prefix="/api", tags=["api"])
router.include_router(farm_api_router)

# Import necessary services
from app.services.blockchain import BlockchainService
from app.services.generate_qr import GenerateQRService

# Initialize services
blockchain_service = BlockchainService()
generate_qr_service = GenerateQRService()


class ContactForm(BaseModel):
    name: str
    email: str
    message: str


class FarmCreate(BaseModel):
    id: str
    name: str
    description: str = None


@router.get("/farm/{farm_id}")
async def get_farm_data(
    farm_id: str, current_user: User = Depends(get_current_active_user)
):
    """API returns farm data in JSON format - Requires authentication"""
    data = blockchain_service.get_sensor_data_by_farm_id(farm_id)

    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for farm {farm_id}")

    return data


@router.post("/farm")
async def store_farm_data(data: FarmData, db: Session = Depends(get_db)):
    """API stores sensor data into blockchain - Requires authentication"""
    try:
        # Prepare data to store into blockchain
        farm_payload = {
            "temperature": data.temperature,
            "farm_id": data.farm_id,
            "humidity": data.humidity,
            "water_level": data.water_level,
            "product_id": data.product_id,
            "light_level": data.light_level,
        }

        # Call service to store data
        tx_hash = blockchain_service.store_sensor_data(
            farm_payload.get("farm_id"), farm_payload
        )

        if not tx_hash:
            raise HTTPException(
                status_code=500,
                detail="Cannot store data into blockchain. Please check connection and try again.",
            )

        FarmReportService.create_report(
            db=db,
            report_id=generate_random_report_id(),
            farm_id=data.farm_id,
            product_id=data.product_id,
            temperature=data.temperature,
            humidity=data.humidity,
            water_level=data.water_level,
            light_level=data.light_level,
        )

        # Return success with transaction hash
        return {
            "success": True,
            "message": "Data stored successfully",
            "transaction_hash": tx_hash,
            "farm_id": data.farm_id,
        }

    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")


@router.post("/send-contact")
async def send_contact_email(contact: ContactForm):
    """API processes sending email from contact form"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os

    try:
        # Get email configuration from environment variables
        EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
        EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
        EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
        EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

        # Check email configuration
        if not all(
            [EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER]
        ):
            return {
                "success": False,
                "message": "Email server not configured. Please contact administrator.",
            }

        # Create email content
        subject = f"New contact from {contact.name}"

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject

        # Optionally add Reply-To to allow recipient to reply to sender
        msg["Reply-To"] = contact.email

        # Email content
        body = f"""
        <html>
        <body>
            <h2>Thông tin liên hệ mới</h2>
            <p><strong>Họ và tên:</strong> {contact.name}</p>
            <p><strong>Email:</strong> {contact.email}</p>
            <p><strong>Nội dung:</strong></p>
            <p>{contact.message}</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

        return {
            "success": True,
            "message": "Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong thời gian sớm nhất.",
        }

    except Exception as e:
        return {"success": False, "message": f"Không thể gửi email: {str(e)}"}


@router.get("/debug/farms")
async def debug_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API để debug danh sách farms"""
    # Kiểm tra quyền admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    
    farms = db.query(Farm).all()
    
    # Convert farms to dict for JSON response
    farms_data = []
    for farm in farms:
        farm_dict = {
            "id": farm.id,
            "name": farm.name,
            "description": farm.description,
            "user_id": farm.user_id,
            "created_at": str(farm.created_at),
            "updated_at": str(farm.updated_at)
        }
        farms_data.append(farm_dict)
    
    return {
        "success": True,
        "count": len(farms_data),
        "farms": farms_data
    }


@router.post("/farms/add")
async def add_farm(
    farm: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API để thêm farm mới"""
    # Kiểm tra quyền admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    
    # Kiểm tra farm_id đã tồn tại chưa
    existing_farm = db.query(Farm).filter(Farm.id == farm.id).first()
    if existing_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Farm với ID '{farm.id}' đã tồn tại"
        )
    
    # Tạo farm mới
    new_farm = Farm(
        id=farm.id,
        name=farm.name,
        description=farm.description
    )
    
    try:
        db.add(new_farm)
        db.commit()
        db.refresh(new_farm)
        
        return {
            "success": True,
            "message": f"Đã thêm thành công farm: {farm.name}",
            "farm": {
                "id": new_farm.id,
                "name": new_farm.name,
                "description": new_farm.description
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thêm farm: {str(e)}"
        )
