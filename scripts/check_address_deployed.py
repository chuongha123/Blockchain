from web3 import Web3

BESU_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(BESU_URL))

code = w3.eth.get_code(w3.to_checksum_address("0xE7C14B58Df6deFa0BFd0CD60b28BB8795b6f3e20"))
print("Contract bytecode:", code)
print("Contract bytecode:", code.hex())
