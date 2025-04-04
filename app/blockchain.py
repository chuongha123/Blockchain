from dotenv import load_dotenv
from web3 import Web3

from app.config import CONTRACT_ABI, BESU_URL, CONTRACT_ADDRESS, PRIVATE_KEY

# Load environment variables
load_dotenv()


class BlockchainService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlockchainService, cls).__new__(cls)
            cls._instance._initialize_blockchain()
        return cls._instance

    def _initialize_blockchain(self):
        """Initialize blockchain connection"""
        try:
            provider_url = BESU_URL
            contract_address = CONTRACT_ADDRESS
            private_key = PRIVATE_KEY

            # Connect Web3
            self.web3 = Web3(Web3.HTTPProvider(provider_url))

            if not self.web3.is_connected():
                print("Cannot connect to blockchain")
                return

            # Create account from private key
            self.account = self.web3.eth.account.from_key(private_key)

            # Initialize contract
            self.contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(contract_address),
                abi=CONTRACT_ABI,
            )

            print(f"Connected to blockchain, account address: {self.account.address}")
            self.initialized = True

        except Exception as e:
            print(f"Error initializing blockchain: {str(e)}")
            self.initialized = False

    def store_sensor_data(self, farm_id, data):
        """Store sensor data into blockchain"""
        if not getattr(self, "initialized", False):
            print("Blockchain not initialized")
            return None

        try:
            temperature = int(
                float(data.get("temperature", 0)) * 100
            )
            humidity = int(data.get("humidity"))
            water_level = int(data.get("water_level"))
            light_level = int(data.get("light_level"))
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            # Build deployment transaction
            stored_func = self.contract.functions.storeData(farm_id, temperature, humidity, water_level,
                                                            data.get("product_id"), light_level)
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
            print(f"Error storing data into blockchain: {str(e)}")
            return None

    def get_sensor_data_by_farm_id(self, farm_id):
        """Get sensor data from blockchain by farm_id"""
        if not getattr(self, "initialized", False):
            print("Blockchain not initialized")
            return None

        try:
            raw_data = self.contract.functions.getDataByFarmId(farm_id).call()
            if not raw_data:
                print(f"No data found for farm {farm_id}")
                return None

            formatted_data = []
            for item in raw_data:
                formatted_item = {
                    'timestamp': item[0],
                    'farmId': item[1],
                    'temperature': item[2] / 100,
                    'humidity': item[3],
                    'waterLevel': item[4],
                    'productId': item[5],
                    'lightLevel': item[6]
                }
                formatted_data.append(formatted_item)

            return formatted_data  # Return formatted data

        except Exception as e:
            print(f"Error getting data from blockchain: {str(e)}")
            return None
