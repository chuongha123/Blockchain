import json
import os

from web3 import Web3

BESU_URL = "http://localhost:8545"
ETH_SIGNER_URL = "http://localhost:8555"

w3 = Web3(Web3.HTTPProvider(ETH_SIGNER_URL))
base_dir = os.path.abspath(os.path.dirname(__file__))

assert w3.is_connected(), "Cannot connect to Ethereum Node!"

# Load ABI from IoTStorage.json
contract_path = os.path.join(base_dir, "../contract/IoTStorage.json")
with open(contract_path, "r") as f:
    contract_json = json.load(f)
    CONTRACT_ABI = contract_json["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]

# Load contract_address from contract_address.json
contract_path = os.path.join(base_dir, "../contract/contract_address.json")
with open(contract_path, "r") as f:
    contract_address_json = json.load(f)
    CONTRACT_ADDRESS = contract_address_json["contract_address"]

# Load contract_address from contract_address.json
account_address_path = os.path.join(base_dir, "../scripts/account_info.json")
with open(account_address_path, "r") as f:
    account_address_json = json.load(f)
    ACCOUNT_ADDRESS = account_address_json["address"]
    PRIVATE_KEY = account_address_json["private_key"]
    PASSWORD = account_address_json["password"]
