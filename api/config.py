import json
import os

from web3 import Web3


PRIVATE_KEY = "dfb3ea0267d5c3a807672417d2c1eeb41522751da5effa1c052e46f2391566d3" # private key of the account you created using scripts/new_account.py
PASSWORD = "123456"
BESU_URL = "http://localhost:8545"
ETH_SIGNER_URL = "http://localhost:8555"
ACCOUNT_ADDRESS = "0xc269666872710c82Ba84163a9727A72C77Bc79bB"

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
