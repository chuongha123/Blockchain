from eth_account import Account
from web3 import Web3

from api.config import CONTRACT_ABI, CONTRACT_ADDRESS, PRIVATE_KEY, BESU_URL

w3 = Web3(Web3.HTTPProvider(BESU_URL))
# Kết nối với hợp đồng
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)
account = Account.from_key(PRIVATE_KEY)
w3.eth.defaultAccount = account.address


def store_sensor_data(device_id, temperature):
    nonce = w3.eth.get_transaction_count(account.address)
    # Xây dựng giao dịch deploy
    stored_func = contract.functions.storeData(device_id, temperature)
    transaction = stored_func.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.to_wei("0", "gwei"),
        "chainId": w3.eth.chain_id
    })
    print("transaction: ", transaction)
    # Ký giao dịch cục bộ
    signed_tx = account.sign_transaction(transaction)
    # Gửi giao dịch đã ký
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("tx_receipt", tx_receipt)
    logs = contract.events.DataStored().process_receipt(tx_receipt)
    if logs:
        index = logs[0]["args"]["index"]
        print("Index của bản ghi:", index)
    else:
        print("Không có sự kiện nào được phát ra trong transaction receipt.")
    return tx_hash.hex()


def get_sensor_data(index):
    print("contract func: ", contract.functions)
    data = contract.functions.getData(index).call()
    return data


def get_all_data():
    data = contract.functions.getAllData().call()
    return data