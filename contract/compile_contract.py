import json
import solcx
from solcx import compile_standard
from os import path

# Cài đặt phiên bản Solidity
solcx.install_solc("0.8.20")  # Chọn phiên bản phù hợp với contract

# Đọc file Solidity
with open(path.join(path.dirname(__file__), "../contract/IoTStorage.sol"), "r") as f:
    contract_source_code = f.read()

# Compile Smart Contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IoTStorage.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.deployedBytecode"]
                }
            }
        },
    },
)

# Ghi ra file JSON
output_path = path.join(path.dirname(__file__), "../contract/IoTStorage.json")
with open(output_path, "w") as f:
    json.dump(compiled_sol, f, indent=4)

print(f"✅ Smart Contract compiled successfully! JSON saved at {output_path}")