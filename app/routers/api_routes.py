from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.admin.farm_api_routes import router as farm_api_router
from app.model.farm_data import FarmData
from app.model.user import User
from app.security import get_current_active_user

# Initialize API router
router = APIRouter(prefix="/api", tags=["api"])
router.include_router(farm_api_router)

# Import necessary services
from app.blockchain import BlockchainService
from app.generate_qr import GenerateQRService

# Initialize services
blockchain_service = BlockchainService()
generate_qr_service = GenerateQRService()


class ContactForm(BaseModel):
    name: str
    email: str
    message: str


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
async def store_farm_data(data: FarmData):
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
