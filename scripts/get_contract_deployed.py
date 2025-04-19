import json
from os import path

from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://localhost:8000"))
CONTRACT_JSON_PATH = path.join(path.abspath(path.dirname(__file__)), "../contract/IoTStorage.json")

contract_address = "0xB5a8159bC208Afa56b7f05D02caA699738197035"
abi = json.load(open(CONTRACT_JSON_PATH))["contracts"]["IoTStorage.sol"]["IoTStorage"]["abi"]

contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=abi)
print("Contract Address:", contract.address)