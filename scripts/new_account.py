import json
import os
from os import path

from eth_account import Account

base_dir = os.path.abspath(os.path.dirname(__file__))
# Create new account
acct = Account.create()

# Encrypt private key with password "123456" in keystore format (V3)
PASSWORD = "123456"
encrypted = Account.encrypt(acct.key, PASSWORD)

# write password to file
with open(path.join(base_dir, "../scripts/password.txt"), "w") as f:
    f.write(PASSWORD)

# Write file keystore (JSON)
with open(path.join(base_dir, "../scripts/keystore.json"), "w") as f:
    json.dump(encrypted, f, indent=4)

# Write file containing private key in hex format (plain text)
with open(path.join(base_dir, "../scripts/besu_key.txt"), "w") as f2:
    f2.write(acct.key.hex())


with open(path.join(base_dir, "../scripts/account_info.json"), "w") as f:
    account = {
        "address": acct.address,
        "private_key": acct.key.hex(),
        "password": PASSWORD,
    }
    json.dump(account, f, indent=4)

print("Account info has been created successfully.")
print(f"Account Address: {acct.address}")
print(f"Private Key: {acct.key.hex()}")
