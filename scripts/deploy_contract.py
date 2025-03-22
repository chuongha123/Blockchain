import json
from os import path

import requests
from web3 import Web3

from api.error import ContractOperationError


# Connection and path configuration
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
GAS_PRICE = 0  # 0 Gwei for dev environment


def load_contract_data(json_path: str) -> tuple:
    """Read JSON file and return contract ABI and bytecode."""
    try:
        with open(json_path, "r") as f:
            contract_json = json.load(f)
        contract_abi = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]
        contract_bytecode = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"][
            "evm"
        ]["bytecode"]["object"]
        return contract_abi, contract_bytecode
    except Exception as e:
        raise ContractOperationError(f"Error reading contract file: {e}")


def connect_web3(provider_url: str) -> Web3:
    """Connect to Besu through HTTPProvider."""
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        raise ConnectionError("❌ Cannot connect to Ethereum Node!")
    return w3


def build_deploy_transaction(
    w3: Web3, contract_abi: dict, contract_bytecode: str, deployer: str, nonce: int
) -> dict:
    """Build contract deployment transaction."""
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
    """Send transaction to EthSigner for signing and return the signed transaction."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_signTransaction",
        "params": [tx],
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}
    print("⏳ Sending transaction to EthSigner for signing...")
    response = requests.post(
        ETHSIGNER_URL,
        headers=headers,
        data=json.dumps(
            payload, default=lambda o: o.hex() if isinstance(o, bytes) else o
        ),
    )

    if response.status_code != 200:
        raise ContractOperationError(f"Error calling EthSigner: {response.text}")

    signed_tx = response.json().get("result")
    if not signed_tx:
        raise ContractOperationError("No signed transaction received from EthSigner")

    return signed_tx


def deploy_contract(w3: Web3, signed_tx: str) -> str:
    """Send signed transaction and wait for receipt, return contract address."""
    tx_hash = w3.eth.send_raw_transaction(signed_tx)
    print("⏳ Waiting for transaction confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    if tx_receipt["status"] == 0:
        print("⚠️ Transaction reverted. Checking reason with debug_traceTransaction.")
        debug_trace = w3.provider.make_request("debug_traceTransaction", [tx_hash])
        print(json.dumps(debug_trace, indent=4))
        raise ContractOperationError("Deployment transaction reverted!")
    return tx_receipt.contractAddress


def save_contract_address(file_path: str, contract_address: str) -> None:
    """Write contract address to JSON file."""
    with open(file_path, "w") as f:
        json.dump({"contract_address": contract_address}, f, indent=4)
    print(f"✅ Smart Contract address saved at: {file_path}")


def main():
    try:
        # Connect to Besu
        w3 = connect_web3(ETHSIGNER_URL)
        print("Chain ID:", w3.eth.chain_id)
        print("Block number:", w3.eth.block_number)

        # Setup deployer account
        deployer = Web3.to_checksum_address(DEPLOYER_ADDRESS)
        w3.eth.default_account = deployer
        nonce = w3.eth.get_transaction_count(deployer)
        print("Nonce:", nonce)

        # Read contract information
        contract_abi, contract_bytecode = load_contract_data(CONTRACT_JSON_PATH)

        # Build deployment transaction
        tx = build_deploy_transaction(
            w3, contract_abi, contract_bytecode, deployer, nonce
        )

        # Sign transaction via EthSigner
        signed_tx = sign_transaction_via_ethsigner(tx)
        print("Transaction successfully signed, sending to Besu...")

        # Send transaction and get contract address
        contract_address = deploy_contract(w3, signed_tx)
        print(f"✅ Smart Contract deployed at: {contract_address}")

        # Save contract address to file
        save_contract_address(CONTRACT_ADDRESS_OUTPUT, contract_address)
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
