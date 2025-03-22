from web3 import Web3

BESU_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(BESU_URL))


def main():
    code = w3.eth.get_code(w3.to_checksum_address("0x95B10206f2D0Bf7d627A72bfdf1c1B9A55841e35"))
    print("Contract bytecode:", code)
    print("Contract bytecode:", code.hex())


if __name__ == "__main__":
    main()
