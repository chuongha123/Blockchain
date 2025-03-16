from eth_account import Account

from api.config import w3, CONTRACT_ABI, CONTRACT_ADDRESS

# Kết nối với hợp đồng
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
private_key = "0ffe7d9804adc81eaf0ed4069199e60d6da463d60aae94adcc9e677efba3b805"  # Khóa riêng của bạn
account = Account.from_key(private_key)

def store_sensor_data(device_id, temperature):
    nonce = w3.eth.get_transaction_count(account.address)
    # Xây dựng giao dịch deploy
    stored_func = contract.functions.storeData(device_id, temperature)
    transaction = stored_func.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.to_wei("1", "gwei"),
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
    device_id, timestamp, temperature = contract.functions.getData(index).call()
    return {"timestamp": timestamp, "device_id": device_id, "temperature": temperature}


def get_all_data():
    nonce = w3.eth.get_transaction_count(account.address)
    data = contract.functions.getAllData().call({
        "from": account.address,
        "nonce": nonce
    })
    return data
