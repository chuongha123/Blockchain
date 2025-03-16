import json
import requests
from os import path
from web3 import Web3

from api.config import ETH_SIGNER_URL

# Kết nối tới Besu (nếu Besu và EthSigner được kết nối với nhau qua downstream, Besu nhận giao dịch đã ký)
w3 = Web3(Web3.HTTPProvider(ETH_SIGNER_URL))
assert w3.is_connected(), "❌ Không thể kết nối với Ethereum Node!"

# Đọc Smart Contract từ JSON
base_dir = path.abspath(path.dirname(__file__))
with open(path.join(base_dir, "../contract/IoTStorage.json"), "r") as f:
    contract_json = json.load(f)
    contract_abi = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]
    contract_bytecode = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["evm"]["bytecode"]["object"]

# Địa chỉ tài khoản deploy (cần khớp với tài khoản đã cấu hình EthSigner)
# Chú ý: khi sử dụng EthSigner, bạn không cần ký giao dịch cục bộ.
deployer_address = Web3.to_checksum_address("0x65ffd1ddba81dea2bae9d3fc59a60a6b0f746d57")

w3.eth.default_account = deployer_address

# Thiết lập chain_id (ví dụ: 1337 nếu genesis của bạn đặt là 1337)
chain_id = w3.eth.chain_id
print("Chain ID:", chain_id)
print("Block number:", w3.eth.block_number)

# Lấy nonce của tài khoản deploy
nonce = w3.eth.get_transaction_count(deployer_address)
print("Nonce:", nonce)

# Xây dựng giao dịch deploy hợp đồng
IoTStorage = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
transaction = IoTStorage.constructor().build_transaction({
    "from": deployer_address,
    "nonce": nonce,
    "gas": 3000000,
    "gasPrice": w3.to_wei("0", "gwei"),  # Chế độ dev nên gasPrice = 0
    "chainId": chain_id
})

payload = {
    "jsonrpc": "2.0",
    "method": "eth_signTransaction",
    "params": [transaction],
    "id": 1
}

# Gửi giao dịch đến EthSigner để ký qua API
# EthSigner của bạn đang chạy trên cổng 8555 (HTTP endpoint) với subcommand file-based-signer
headers = {"Content-Type": "application/json"}

print("⏳ Gửi giao dịch đến EthSigner để ký ...")
response = requests.post(
    ETH_SIGNER_URL,
    headers=headers,
    data=json.dumps(payload, default=lambda o: o.hex() if isinstance(o, bytes) else o)
)
if response.status_code != 200:
    print("Lỗi khi gọi EthSigner:", response.text)
    exit(1)

signed_tx = response.json().get("result")
if not signed_tx:
    print("Không nhận được giao dịch đã ký từ EthSigner")
    exit(1)

print("Giao dịch đã được ký thành công, gửi đến Besu ...")
tx_hash = w3.eth.send_raw_transaction(signed_tx)
print(tx_hash)
print("⏳ Đang chờ giao dịch được xác nhận...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
contract_address = tx_receipt.contractAddress
print(f"✅ Smart Contract đã được deploy tại: {contract_address}")

# Ghi địa chỉ contract ra file
with open(path.join(base_dir, "../contract/contract_address.json"), "w") as f:
    json.dump({"contract_address": contract_address}, f, indent=4)