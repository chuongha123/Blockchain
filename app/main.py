import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pydantic import BaseModel

from app.blockchain import BlockchainService
from app.generate_qr import GenerateQRService
from app.model.FarmPayload import FarmData

app = FastAPI(title="Farm Monitor API")

load_dotenv()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

blockchain_service = BlockchainService()
generate_qr_service = GenerateQRService()

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

class ContactForm(BaseModel):
    name: str
    email: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/farm/{farm_id}", response_class=HTMLResponse)
async def farm_data(request: Request, farm_id: str):
    """Hiển thị thông tin nông trại theo device_id"""
    # Lấy dữ liệu từ blockchain
    data = blockchain_service.get_sensor_data_by_farm_id(farm_id)

    if not data:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Không tìm thấy dữ liệu cho thiết bị {farm_id}",
            },
        )

    # Trả về template với dữ liệu
    return templates.TemplateResponse(
        "farm_data.html", {"request": request, "farm_id": farm_id, "data": data}
    )


@app.get("/api/farm/{farm_id}")
async def get_farm_data(farm_id: str):
    """API trả về dữ liệu nông trại dạng JSON"""
    data = blockchain_service.get_sensor_data_by_farm_id(farm_id)

    if not data:
        raise HTTPException(
            status_code=404, detail=f"Không tìm thấy dữ liệu cho farm {farm_id}"
        )

    return data


@app.post("/api/farm")
async def store_farm_data(data: FarmData):
    """API lưu trữ dữ liệu cảm biến vào blockchain"""
    try:
        # Chuẩn bị dữ liệu để lưu vào blockchain
        farm_payload = {
            "temperature": data.temperature,
            "farm_id": data.farm_id,
            "humidity": data.humidity,
            "water_level": data.water_level,
            "product_id": data.product_id,
            "light_level": data.light_level,
        }

        # Gọi service lưu trữ dữ liệu
        tx_hash = blockchain_service.store_sensor_data(farm_payload.get("farm_id"), farm_payload)

        if not tx_hash:
            raise HTTPException(
                status_code=500,
                detail="Không thể lưu dữ liệu vào blockchain. Vui lòng kiểm tra lại kết nối và thử lại.",
            )

        # Trả về kết quả thành công với transaction hash
        return {
            "success": True,
            "message": "Dữ liệu đã được lưu trữ thành công",
            "transaction_hash": tx_hash,
            "farm_id": data.farm_id,
        }

    except Exception as e:
        # Xử lý các lỗi khác nếu có
        raise HTTPException(
            status_code=500, detail=f"Lỗi khi lưu trữ dữ liệu: {str(e)}"
        )


@app.get("/generate-qr/{farm_id}")
async def create_qr_code(farm_id: str):
    """Tạo mã QR cho thiết bị"""
    try:
        qr_path = generate_qr_service.generate_qr_code(farm_id)
        if not qr_path:
            raise ValueError("QR path is empty")
        return {"message": "QR code đã được tạo", "qr_url": f"/static/{qr_path}"}
    except Exception as e:
        return {
            "error": "Không thể tạo mã QR",
            "details": str(e)
        }


@app.get("/generate-qr")
async def create_qr_code():
    """Tạo mã QR cho thiết bị"""
    try:
        qr_path = generate_qr_service.generate_qr_home_page_code()
        if not qr_path:
            raise ValueError("QR path is empty")
        return {"message": "QR code đã được tạo", "qr_url": f"/static/{qr_path}"}
    except Exception as e:
        return {
            "error": "Không thể tạo mã QR",
            "details": str(e)
        }


@app.post("/send-contact")
async def send_contact_email(contact: ContactForm):
    """Xử lý gửi email từ form liên hệ"""
    try:
        # Kiểm tra thông tin cấu hình email
        if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER]):
            return {
                "success": False,
                "message": "Chưa cấu hình email server. Vui lòng liên hệ quản trị viên."
            }
        print(EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER)
        # Tạo nội dung email
        subject = f"Liên hệ mới từ {contact.name}"
        
        # Tạo message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        
        # Có thể thêm Reply-To để người nhận có thể phản hồi cho người gửi form
        msg['Reply-To'] = contact.email
        
        # Nội dung email
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
        
        msg.attach(MIMEText(body, 'html'))
        
        # Gửi email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": "Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong thời gian sớm nhất."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Không thể gửi email: {str(e)}"
        }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
