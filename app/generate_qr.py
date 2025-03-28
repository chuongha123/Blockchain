import os

import qrcode


class GenerateQRService:
    def generate_qr_code(seft, farm_id, base_url=os.getenv("PUBLIC_URL")):
        """Tạo mã QR cho thiết bị với URL"""
        url = f"{base_url}/farm/{farm_id}"

        qr = qrcode.make(url)

        print("QR:", url)

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs("app/static/qr_codes", exist_ok=True)

        # Save an image
        file_path = f"app/static/qr_codes/qr_{farm_id}.png"
        qr.save(file_path)

        return f"qr_codes/qr_{farm_id}.png"

    def generate_qr_home_page_code(seft):
        """Tạo mã QR cho trang chủ"""
        url = f"{os.getenv('PUBLIC_URL')}"
        qr = qrcode.make(url)
        file_path = f"app/static/qr_codes/qr_home_page.png"
        qr.save(file_path)
        return f"qr_codes/qr_home_page.png"
