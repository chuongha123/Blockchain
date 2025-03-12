from eth_account import Account

# Tạo tài khoản mới
acct = Account.create()
print(f"Địa chỉ: {acct.address}")
print(f"Private Key: {acct.key.hex()}")
