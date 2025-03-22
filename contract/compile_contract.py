import json
from os import path

import solcx
from solcx import compile_standard

# Cấu hình phiên bản Solidity
SOLIDITY_VERSION = "0.8.17"
if SOLIDITY_VERSION not in solcx.get_installed_solc_versions():
    solcx.install_solc(SOLIDITY_VERSION)
solcx.set_solc_version(SOLIDITY_VERSION)

# Định nghĩa đường dẫn
BASE_DIR = path.dirname(__file__)
CONTRACT_PATH = path.join(BASE_DIR, "../contract/IoTStorage.sol")
OUTPUT_PATH = path.join(BASE_DIR, "../contract/IoTStorage.json")

# Đọc file Solidity
with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
    contract_source_code = f.read()

# Compile Smart Contract với tối ưu hóa
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IoTStorage.sol": {"content": contract_source_code}},
        "settings": {
            "optimizer": {"enabled": True, "runs": 200},  # Bật tối ưu hóa
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.deployedBytecode"]
                }
            },
        },
    },
)

# Ghi ra file JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(compiled_sol, f, indent=4)

print(f"✅ Smart Contract compiled successfully! JSON saved at {OUTPUT_PATH}")
