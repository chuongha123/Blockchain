import os

from dotenv import load_dotenv
from flask import jsonify
from web3 import Web3

from api.config import CONTRACT_ABI
from app.model.FarmPayload import FarmData

# Tải biến môi trường
load_dotenv()


class BlockchainService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlockchainService, cls).__new__(cls)
            cls._instance._initialize_blockchain()
        return cls._instance

    def _initialize_blockchain(self):
        """Khởi tạo kết nối với blockchain"""
        try:
            provider_url = os.getenv("BLOCKCHAIN_PROVIDER_URL")
            contract_address = os.getenv("CONTRACT_ADDRESS")
            private_key = os.getenv("PRIVATE_KEY")

            # Kết nối Web3
            self.web3 = Web3(Web3.HTTPProvider(provider_url))

            if not self.web3.is_connected():
                print("Không thể kết nối tới blockchain")
                return

            # Tạo tài khoản từ private key
            self.account = self.web3.eth.account.from_key(private_key)

            # Khởi tạo contract
            self.contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(contract_address),
                abi=CONTRACT_ABI,
            )

            print(f"Đã kết nối tới blockchain, địa chỉ ví: {self.account.address}")
            self.initialized = True

        except Exception as e:
            print(f"Lỗi khi khởi tạo blockchain: {str(e)}")
            self.initialized = False

    def store_sensor_data(self, farm_id, data):
        """Lưu dữ liệu cảm biến vào blockchain"""
        if not getattr(self, "initialized", False):
            print("Blockchain chưa được khởi tạo")
            return None

        try:
            temperature = int(
                float(data.get("temperature", 0)) * 100
            )
            humidity = int(data.get("humidity"))
            water_level = int(data.get("water_level"))
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            # Build deployment transaction
            stored_func = self.contract.functions.storeData(farm_id, temperature, humidity, water_level, data.get("product_id"))
            transaction = stored_func.build_transaction(
                {
                    "from": self.account.address,
                    "nonce": nonce,
                    "gas": 3000000,
                    "gasPrice": self.web3.to_wei("0", "gwei"),
                    "chainId": self.web3.eth.chain_id,
                }
            )
            print("transaction: ", transaction)
            # Sign transaction locally
            signed_tx = self.account.sign_transaction(transaction)
            # Send signed transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt.transactionHash.hex()

        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu vào blockchain: {str(e)}")
            return None

    def get_sensor_data_by_farm_id(self, farm_id):
        """Lấy dữ liệu cảm biến từ blockchain theo farm_id"""
        if not getattr(self, "initialized", False):
            print("Blockchain chưa được khởi tạo")
            return None

        try:
            raw_data = self.contract.functions.getDataByFarmId(farm_id).call()
            if not raw_data:
                print(f"Không tìm thấy dữ liệu cho farm {farm_id}")
                return None

            # Chuyển đổi dữ liệu sang định dạng dễ đọc
            formatted_data = []
            for item in raw_data:
                formatted_item = {
                    'timestamp': item[0],
                    'farmId': item[1],
                    'temperature': item[2] / 100,  # Chuyển đổi lại temperature
                    'humidity': item[3],
                    'waterLevel': item[4],
                    'productId': item[5]
                }
                formatted_data.append(formatted_item)

            return formatted_data  # Trả về dữ liệu đã được định dạng

        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu từ blockchain: {str(e)}")
            return None
