from web3 import Web3

BESU_URL = "http://localhost:8545"
w3 = Web3(Web3.HTTPProvider(BESU_URL))


def main():
    code = w3.eth.get_code(
        w3.to_checksum_address("0x0B0b8EFf5b2B8C8f3284e14381d7DcD6dF6C0C59")
    )
    print("Contract bytecode:", code)
    print("Contract bytecode:", code.hex())


if __name__ == "__main__":
    main()
