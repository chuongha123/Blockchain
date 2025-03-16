import json
from eth_account import Account

# Tạo một tài khoản mới
acct = Account.create()

# Mã hóa private key với mật khẩu "123456" theo định dạng keystore (V3)
encrypted = Account.encrypt(acct.key, "123456")

# Ghi file keystore (JSON)
with open("keystore.json", "w") as f:
    json.dump(encrypted, f, indent=4)
print("Keystore file đã được tạo thành công.")

# Ghi file chứa private key dạng hex (plain text)
with open("besu_key.txt", "w") as f2:
    f2.write(acct.key.hex())

print(f"Địa chỉ: {acct.address}")
print(f"Private Key: {acct.key.hex()}")