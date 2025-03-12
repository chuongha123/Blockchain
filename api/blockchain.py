from web3 import Web3
from api.config import w3, CONTRACT_ABI, CONTRACT_ADDRESS

# Kết nối với Smart Contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def store_sensor_data(device_id, temperature):
    account = w3.eth.accounts[0]  # Lấy tài khoản đầu tiên (private network)
    tx_hash = contract.functions.storeData(device_id, temperature).transact({"from": account})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def get_sensor_data(index):
    timestamp, device_id, temperature = contract.functions.getData(index).call()
    return {"timestamp": timestamp, "device_id": device_id, "temperature": temperature}