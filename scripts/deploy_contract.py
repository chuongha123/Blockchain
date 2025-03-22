import json
from os import path

import requests
from web3 import Web3

from api.error import ContractOperationError


# Cấu hình kết nối và đường dẫn
BESU_URL = "http://localhost:8545"
ETHSIGNER_URL = "http://localhost:8555"
CONTRACT_JSON_PATH = path.join(
    path.abspath(path.dirname(__file__)), "../contract/IoTStorage.json"
)
CONTRACT_ADDRESS_OUTPUT = path.join(
    path.abspath(path.dirname(__file__)), "../contract/contract_address.json"
)
DEPLOYER_ADDRESS = "0x6b7084febbadc59cb1c9aa9346a4c84b1430be8a"
GAS_LIMIT = 8000000
GAS_PRICE = 0  # 0 Gwei cho môi trường dev


def load_contract_data(json_path: str) -> tuple:
    """Đọc file JSON và trả về ABI và bytecode của hợp đồng."""
    try:
        with open(json_path, "r") as f:
            contract_json = json.load(f)
        contract_abi = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]
        contract_bytecode = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"][
            "evm"
        ]["bytecode"]["object"]
        return contract_abi, contract_bytecode
    except Exception as e:
        raise ContractOperationError(f"Lỗi khi đọc file contract: {e}")


def connect_web3(provider_url: str) -> Web3:
    """Kết nối tới Besu thông qua HTTPProvider."""
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        raise ConnectionError("❌ Không thể kết nối với Ethereum Node!")
    return w3


def build_deploy_transaction(
    w3: Web3, contract_abi: dict, contract_bytecode: str, deployer: str, nonce: int
) -> dict:
    """Xây dựng giao dịch deploy hợp đồng."""
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    tx = contract.constructor().build_transaction(
        {
            "from": deployer,
            "nonce": nonce,
            "gas": GAS_LIMIT,
            "gasPrice": w3.to_wei(GAS_PRICE, "gwei"),
            "chainId": w3.eth.chain_id,
        }
    )
    return tx


def sign_transaction_via_ethsigner(tx: dict) -> str:
    """Gửi giao dịch tới EthSigner để ký và trả về giao dịch đã ký."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_signTransaction",
        "params": [tx],
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}
    print("⏳ Gửi giao dịch đến EthSigner để ký ...")
    response = requests.post(
        ETHSIGNER_URL,
        headers=headers,
        data=json.dumps(
            payload, default=lambda o: o.hex() if isinstance(o, bytes) else o
        ),
    )

    if response.status_code != 200:
        raise ContractOperationError(f"Lỗi khi gọi EthSigner: {response.text}")

    signed_tx = response.json().get("result")
    if not signed_tx:
        raise ContractOperationError("Không nhận được giao dịch đã ký từ EthSigner")

    return signed_tx


def deploy_contract(w3: Web3, signed_tx: str) -> str:
    """Gửi giao dịch đã ký và chờ nhận receipt, trả về địa chỉ contract."""
    tx_hash = w3.eth.send_raw_transaction(signed_tx)
    print("⏳ Đang chờ giao dịch được xác nhận...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    if tx_receipt["status"] == 0:
        print(
            "⚠️ Transaction bị revert. Kiểm tra nguyên nhân bằng debug_traceTransaction."
        )
        debug_trace = w3.provider.make_request("debug_traceTransaction", [tx_hash])
        print(json.dumps(debug_trace, indent=4))
        raise ContractOperationError("Giao dịch triển khai bị revert!")
    return tx_receipt.contractAddress


def save_contract_address(file_path: str, contract_address: str) -> None:
    """Ghi địa chỉ contract ra file JSON."""
    with open(file_path, "w") as f:
        json.dump({"contract_address": contract_address}, f, indent=4)
    print(f"✅ Địa chỉ Smart Contract đã được lưu tại: {file_path}")


def main():
    try:
        # Kết nối tới Besu
        w3 = connect_web3(ETHSIGNER_URL)
        print("Chain ID:", w3.eth.chain_id)
        print("Block number:", w3.eth.block_number)

        # Thiết lập tài khoản deploy
        deployer = Web3.to_checksum_address(DEPLOYER_ADDRESS)
        w3.eth.default_account = deployer
        nonce = w3.eth.get_transaction_count(deployer)
        print("Nonce:", nonce)

        # Đọc thông tin contract
        contract_abi, contract_bytecode = load_contract_data(CONTRACT_JSON_PATH)

        # Xây dựng giao dịch deploy
        tx = build_deploy_transaction(
            w3, contract_abi, contract_bytecode, deployer, nonce
        )

        # Ký giao dịch qua EthSigner
        signed_tx = sign_transaction_via_ethsigner(tx)
        print("Giao dịch đã được ký thành công, gửi đến Besu ...")

        # Gửi giao dịch và lấy địa chỉ contract
        contract_address = deploy_contract(w3, signed_tx)
        print(f"✅ Smart Contract đã được deploy tại: {contract_address}")

        # Lưu địa chỉ contract ra file
        save_contract_address(CONTRACT_ADDRESS_OUTPUT, contract_address)
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")


if __name__ == "__main__":
    main()
