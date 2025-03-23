import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import db

# Tải biến môi trường
load_dotenv()


class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance

    def _initialize_firebase(self):
        """Khởi tạo kết nối Firebase"""
        cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
        db_url = os.getenv("FIREBASE_DATABASE_URL")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {"databaseURL": db_url})
        print("Firebase đã được khởi tạo thành công")

    def get_device_data(self, device_id):
        """Lấy dữ liệu thiết bị từ Firebase"""
        try:
            ref = db.reference(f"devices/{device_id}")
            data = ref.get()

            if data is None:
                return None

            return data
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu từ Firebase: {str(e)}")
            return None
