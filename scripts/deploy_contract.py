import json
import time
from os import path
from web3 import Web3

# Kết nối tới Ethereum Private Node (Besu)
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
assert w3.is_connected(), "❌ Không thể kết nối với Ethereum Node!"

# Đọc Smart Contract từ JSON
base_dir = path.abspath(path.dirname(__file__))
with open(path.join(base_dir, "../contract/IoTStorage.json"), "r") as f:
    contract_json = json.load(f)
    contract_abi = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]
    contract_bytecode = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["evm"]["bytecode"]["object"]

# Chọn tài khoản để deploy
account = w3.eth.accounts[0]
w3.eth.default_account = account

# Deploy Smart Contract
IoTStorage = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
tx_hash = IoTStorage.constructor().transact({"from": account})
print("⏳ Đang chờ giao dịch được xác nhận...")

# Chờ nhận transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress

print(f"✅ Smart Contract đã được deploy tại: {contract_address}")

# Ghi địa chỉ contract ra file
with open(path.join(base_dir, "../contract/contract_address.json"), "w") as f:
    json.dump({"contract_address": contract_address}, f, indent=4)