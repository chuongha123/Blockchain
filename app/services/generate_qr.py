import datetime
import os

import qrcode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GenerateQRService:
    def generate_qr_code(seft, farm_id, base_url=os.getenv("PUBLIC_URL")):
        """Generate QR code for device with URL"""
        # Create full path
        url = f"{base_url}/farm/{farm_id}"

        # Method 1: Direct usage
        qr = qrcode.make(url)

        print("QR:", url)

        # Create directory if it doesn't exist
        os.makedirs("app/static/qr_codes", exist_ok=True)

        # Save image
        unique_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"app/static/qr_codes/qr_{farm_id}_{unique_id}.png"
        qr.save(file_path)

        return f"qr_codes/qr_{farm_id}_{unique_id}.png"

    def generate_qr_home_page_code(seft):
        """Generate QR code for home page"""
        url = f"{os.getenv('PUBLIC_URL')}"
        qr = qrcode.make(url)
        file_path = "app/static/qr_codes/qr_home_page.png"
        qr.save(file_path)
        return "qr_codes/qr_home_page.png"
