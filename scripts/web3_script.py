import json
import os

from solcx import compile_standard

base_dir = os.path.abspath(os.path.dirname(__file__))
contract_path = os.path.join(base_dir, "../contract")

# Đọc nội dung file Solidity
with open(os.path.join(contract_path, 'IoTStorage.sol'), "r") as file:
    contract_source = file.read()

# Compile Smart Contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IoTStorage.sol": {"content": contract_source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "bin"]}}},
    }
)

# Lưu ra file IoTStorage.json
with open("../contract/IoTStorage.json", "w") as f:
    json.dump(compiled_sol, f)
