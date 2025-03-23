import os

import qrcode
from dotenv import load_dotenv

load_dotenv()

def generate_qr_code(farm_id, base_url=os.getenv("PUBLIC_URL")):
    """Tạo mã QR cho thiết bị với URL"""
    # Tạo đường dẫn đầy đủ
    url = f"{base_url}/farm/{farm_id}"

    # Phương pháp 1: Sử dụng trực tiếp
    qr = qrcode.make(url)

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs("static/qr_codes", exist_ok=True)

    # Lưu hình ảnh
    file_path = f"static/qr_codes/qr_{farm_id}.png"
    qr.save(file_path)

    return f"qr_codes/qr_{farm_id}.png"
