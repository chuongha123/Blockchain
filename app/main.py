import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.model.FarmPayload import FarmData
from app.blockchain import BlockchainService

app = FastAPI(title="Farm Monitor API")

# Thiết lập templates và static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Khởi tạo blockchain service
blockchain_service = BlockchainService()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ"""
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
    from qr_generator import generate_qr_code

    qr_path = generate_qr_code(farm_id)
    return {"message": "QR code đã được tạo", "qr_url": f"/static/{qr_path}"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
