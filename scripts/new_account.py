import json
import os
from os import path

from eth_account import Account

base_dir = os.path.abspath(os.path.dirname(__file__))
# Create new account
acct = Account.create()

# Encrypt private key with password "123456" in keystore format (V3)
encrypted = Account.encrypt(acct.key, "123456")

# Write file keystore (JSON)
with open(path.join(base_dir, "../scripts/keystore.json"), "w") as f:
    json.dump(encrypted, f, indent=4)
print("Keystore file đã được tạo thành công.")

# Write file containing private key in hex format (plain text)
with open(path.join(base_dir, "../scripts/besu_key.txt"), "w") as f2:
    f2.write(acct.key.hex())

print(f"Địa chỉ: {acct.address}")
print(f"Private Key: {acct.key.hex()}")
