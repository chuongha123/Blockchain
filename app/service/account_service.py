import os
import json
import secrets
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List

import hvac
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
import boto3
from botocore.exceptions import ClientError

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccountService:
    """Service quản lý account blockchain an toàn"""
    
    def __init__(self, storage_type: str = "file"):
        """
        Khởi tạo AccountService
        
        Args:
            storage_type (str): Loại lưu trữ khóa ('file', 'vault', 'aws_kms')
        """
        self.storage_type = storage_type
        self.config = self._load_config()
        
        # Khởi tạo storage provider tương ứng
        if storage_type == "vault":
            self._init_vault_client()
        elif storage_type == "aws_kms":
            self._init_aws_kms_client()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load cấu hình từ biến môi trường"""
        return {
            "account_dir": os.getenv("ACCOUNT_DIR", "accounts"),
            "vault_url": os.getenv("VAULT_URL", "http://localhost:8200"),
            "vault_token": os.getenv("VAULT_TOKEN", ""),
            "vault_path": os.getenv("VAULT_PATH", "secret/blockchain/accounts"),
            "aws_region": os.getenv("AWS_REGION", "ap-southeast-1"),
            "aws_access_key": os.getenv("AWS_ACCESS_KEY", ""),
            "aws_secret_key": os.getenv("AWS_SECRET_KEY", ""),
            "kms_key_id": os.getenv("KMS_KEY_ID", ""),
        }
    
    def _init_vault_client(self) -> None:
        """Khởi tạo kết nối tới Hashicorp Vault"""
        try:
            self.vault_client = hvac.Client(
                url=self.config["vault_url"],
                token=self.config["vault_token"]
            )
            if not self.vault_client.is_authenticated():
                raise Exception("Không thể xác thực với Vault")
            logger.info("Đã kết nối thành công với Vault")
        except Exception as e:
            logger.error(f"Lỗi khi kết nối Vault: {str(e)}")
            raise
    
    def _init_aws_kms_client(self) -> None:
        """Khởi tạo kết nối tới AWS KMS"""
        try:
            self.kms_client = boto3.client('kms',
                region_name=self.config["aws_region"],
                aws_access_key_id=self.config["aws_access_key"],
                aws_secret_access_key=self.config["aws_secret_key"]
            )
            logger.info("Đã kết nối thành công với AWS KMS")
        except Exception as e:
            logger.error(f"Lỗi khi kết nối AWS KMS: {str(e)}")
            raise
    
    def create_account(self, account_id: str = None) -> Dict[str, str]:
        """
        Tạo account blockchain mới
        
        Args:
            account_id (str, optional): ID cho account. Nếu None, sẽ tạo ngẫu nhiên
            
        Returns:
            Dict[str, str]: Thông tin account (address, id)
        """
        try:
            # Tạo entropy ngẫu nhiên
            entropy = secrets.token_bytes(32)
            
            # Tạo account mới từ entropy
            account: LocalAccount = Account.create(entropy)
            
            # Tạo account_id nếu chưa có
            if not account_id:
                account_id = f"account_{secrets.token_hex(4)}"
            
            # Chuẩn bị dữ liệu account
            account_data = {
                "account_id": account_id,
                "address": account.address,
                "private_key": account.key.hex()
            }
            
            # Lưu trữ account theo phương thức đã chọn
            self._store_account(account_id, account_data)
            
            # Trả về thông tin account (không bao gồm private key)
            return {
                "account_id": account_id,
                "address": account.address
            }
        except Exception as e:
            logger.error(f"Lỗi khi tạo account: {str(e)}")
            raise
    
    def get_account(self, account_id: str) -> Dict[str, str]:
        """
        Lấy thông tin account theo ID (không bao gồm private key)
        
        Args:
            account_id (str): ID của account
            
        Returns:
            Dict[str, str]: Thông tin account
        """
        try:
            account_data = self._retrieve_account(account_id)
            return {
                "account_id": account_id,
                "address": account_data["address"]
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin account {account_id}: {str(e)}")
            raise
    
    def get_private_key(self, account_id: str) -> str:
        """
        Lấy private key của account (chỉ sử dụng trong các quy trình bảo mật)
        
        Args:
            account_id (str): ID của account
            
        Returns:
            str: Private key của account
        """
        try:
            account_data = self._retrieve_account(account_id)
            return account_data["private_key"]
        except Exception as e:
            logger.error(f"Lỗi khi lấy private key của account {account_id}: {str(e)}")
            raise
    
    def list_accounts(self) -> List[Dict[str, str]]:
        """
        Liệt kê tất cả các account
        
        Returns:
            List[Dict[str, str]]: Danh sách thông tin account
        """
        if self.storage_type == "file":
            try:
                accounts = []
                account_dir = Path(self.config["account_dir"])
                if not account_dir.exists():
                    return []
                
                for account_file in account_dir.glob("*.json"):
                    account_id = account_file.stem
                    with open(account_file, "r") as f:
                        account_data = json.load(f)
                    
                    accounts.append({
                        "account_id": account_id,
                        "address": account_data["address"]
                    })
                return accounts
            except Exception as e:
                logger.error(f"Lỗi khi liệt kê accounts: {str(e)}")
                raise
        elif self.storage_type == "vault":
            try:
                accounts = []
                vault_path = self.config["vault_path"]
                response = self.vault_client.secrets.kv.v2.list_secrets(
                    path=vault_path
                )
                
                if not response or "data" not in response or "keys" not in response["data"]:
                    return []
                
                for account_id in response["data"]["keys"]:
                    secret = self.vault_client.secrets.kv.v2.read_secret_version(
                        path=f"{vault_path}/{account_id}"
                    )
                    account_data = secret["data"]["data"]
                    accounts.append({
                        "account_id": account_id,
                        "address": account_data["address"]
                    })
                return accounts
            except Exception as e:
                logger.error(f"Lỗi khi liệt kê accounts từ Vault: {str(e)}")
                raise
        else:
            raise NotImplementedError(f"Chưa hỗ trợ liệt kê accounts cho {self.storage_type}")
    
    def _store_account(self, account_id: str, account_data: Dict[str, str]) -> None:
        """
        Lưu trữ account theo phương thức đã chọn
        
        Args:
            account_id (str): ID của account
            account_data (Dict[str, str]): Dữ liệu account
        """
        if self.storage_type == "file":
            self._store_account_to_file(account_id, account_data)
        elif self.storage_type == "vault":
            self._store_account_to_vault(account_id, account_data)
        elif self.storage_type == "aws_kms":
            self._store_account_to_aws_kms(account_id, account_data)
        else:
            raise ValueError(f"Phương thức lưu trữ không hỗ trợ: {self.storage_type}")
    
    def _store_account_to_file(self, account_id: str, account_data: Dict[str, str]) -> None:
        """
        Lưu account vào file local (CHỈ SỬ DỤNG CHO MÔI TRƯỜNG DEV)
        
        Args:
            account_id (str): ID của account
            account_data (Dict[str, str]): Dữ liệu account
        """
        try:
            # Tạo thư mục nếu chưa tồn tại
            account_dir = Path(self.config["account_dir"])
            account_dir.mkdir(parents=True, exist_ok=True)
            
            # Lưu thông tin account vào file
            account_file = account_dir / f"{account_id}.json"
            with open(account_file, "w") as f:
                json.dump(account_data, f, indent=2)
            
            logger.info(f"Đã lưu account {account_id} vào file {account_file}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu account vào file: {str(e)}")
            raise
    
    def _store_account_to_vault(self, account_id: str, account_data: Dict[str, str]) -> None:
        """
        Lưu account vào Hashicorp Vault
        
        Args:
            account_id (str): ID của account
            account_data (Dict[str, str]): Dữ liệu account
        """
        try:
            # Lưu thông tin account vào Vault
            vault_path = f"{self.config['vault_path']}/{account_id}"
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=vault_path,
                secret=account_data
            )
            
            logger.info(f"Đã lưu account {account_id} vào Vault tại {vault_path}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu account vào Vault: {str(e)}")
            raise
    
    def _store_account_to_aws_kms(self, account_id: str, account_data: Dict[str, str]) -> None:
        """
        Lưu account sử dụng AWS KMS để mã hóa private key
        
        Args:
            account_id (str): ID của account
            account_data (Dict[str, str]): Dữ liệu account
        """
        try:
            # Mã hóa private key bằng KMS
            private_key = account_data["private_key"]
            response = self.kms_client.encrypt(
                KeyId=self.config["kms_key_id"],
                Plaintext=private_key.encode('utf-8')
            )
            
            # Lưu ciphertext và thông tin khác
            encrypted_key = response['CiphertextBlob']
            secure_account_data = {
                "account_id": account_id,
                "address": account_data["address"],
                "encrypted_key": encrypted_key.hex()
            }
            
            # Tạo thư mục nếu chưa tồn tại
            account_dir = Path(self.config["account_dir"])
            account_dir.mkdir(parents=True, exist_ok=True)
            
            # Lưu thông tin đã mã hóa
            account_file = account_dir / f"{account_id}.json"
            with open(account_file, "w") as f:
                json.dump(secure_account_data, f, indent=2)
            
            logger.info(f"Đã lưu account {account_id} với khóa được mã hóa bởi AWS KMS")
        except Exception as e:
            logger.error(f"Lỗi khi lưu account với AWS KMS: {str(e)}")
            raise
    
    def _retrieve_account(self, account_id: str) -> Dict[str, str]:
        """
        Lấy dữ liệu account từ storage
        
        Args:
            account_id (str): ID của account
            
        Returns:
            Dict[str, str]: Dữ liệu account
        """
        if self.storage_type == "file":
            return self._retrieve_account_from_file(account_id)
        elif self.storage_type == "vault":
            return self._retrieve_account_from_vault(account_id)
        elif self.storage_type == "aws_kms":
            return self._retrieve_account_from_aws_kms(account_id)
        else:
            raise ValueError(f"Phương thức lưu trữ không hỗ trợ: {self.storage_type}")
    
    def _retrieve_account_from_file(self, account_id: str) -> Dict[str, str]:
        """
        Lấy dữ liệu account từ file local
        
        Args:
            account_id (str): ID của account
            
        Returns:
            Dict[str, str]: Dữ liệu account
        """
        try:
            account_file = Path(self.config["account_dir"]) / f"{account_id}.json"
            if not account_file.exists():
                raise FileNotFoundError(f"Không tìm thấy file account {account_id}")
            
            with open(account_file, "r") as f:
                account_data = json.load(f)
            
            return account_data
        except Exception as e:
            logger.error(f"Lỗi khi đọc account từ file: {str(e)}")
            raise
    
    def _retrieve_account_from_vault(self, account_id: str) -> Dict[str, str]:
        """
        Lấy dữ liệu account từ Hashicorp Vault
        
        Args:
            account_id (str): ID của account
            
        Returns:
            Dict[str, str]: Dữ liệu account
        """
        try:
            vault_path = f"{self.config['vault_path']}/{account_id}"
            response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=vault_path
            )
            
            if not response or "data" not in response or "data" not in response["data"]:
                raise ValueError(f"Không tìm thấy dữ liệu account {account_id} trong Vault")
            
            account_data = response["data"]["data"]
            return account_data
        except Exception as e:
            logger.error(f"Lỗi khi đọc account từ Vault: {str(e)}")
            raise
    
    def _retrieve_account_from_aws_kms(self, account_id: str) -> Dict[str, str]:
        """
        Lấy dữ liệu account từ storage đã mã hóa bằng AWS KMS
        
        Args:
            account_id (str): ID của account
            
        Returns:
            Dict[str, str]: Dữ liệu account
        """
        try:
            # Đọc dữ liệu đã mã hóa
            account_file = Path(self.config["account_dir"]) / f"{account_id}.json"
            if not account_file.exists():
                raise FileNotFoundError(f"Không tìm thấy file account {account_id}")
            
            with open(account_file, "r") as f:
                encrypted_data = json.load(f)
            
            # Giải mã private key
            encrypted_key = bytes.fromhex(encrypted_data["encrypted_key"])
            response = self.kms_client.decrypt(
                KeyId=self.config["kms_key_id"],
                CiphertextBlob=encrypted_key
            )
            
            # Tạo lại dữ liệu account
            decrypted_key = response["Plaintext"].decode("utf-8")
            account_data = {
                "account_id": account_id,
                "address": encrypted_data["address"],
                "private_key": decrypted_key
            }
            
            return account_data
        except Exception as e:
            logger.error(f"Lỗi khi đọc account từ storage với AWS KMS: {str(e)}")
            raise
    
    def import_account(self, private_key: str, account_id: str = None) -> Dict[str, str]:
        """
        Import account từ private key
        
        Args:
            private_key (str): Private key của account
            account_id (str, optional): ID cho account. Nếu None, sẽ tạo ngẫu nhiên
            
        Returns:
            Dict[str, str]: Thông tin account (address, id)
        """
        try:
            # Tạo account từ private key
            account: LocalAccount = Account.from_key(private_key)
            
            # Tạo account_id nếu chưa có
            if not account_id:
                account_id = f"account_{secrets.token_hex(4)}"
            
            # Chuẩn bị dữ liệu account
            account_data = {
                "account_id": account_id,
                "address": account.address,
                "private_key": private_key
            }
            
            # Lưu trữ account theo phương thức đã chọn
            self._store_account(account_id, account_data)
            
            # Trả về thông tin account (không bao gồm private key)
            return {
                "account_id": account_id,
                "address": account.address
            }
        except Exception as e:
            logger.error(f"Lỗi khi import account: {str(e)}")
            raise