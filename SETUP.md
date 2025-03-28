# 🚀 Hướng Dẫn Setup Source Trước Khi Chạy

## 1️⃣ Tạo Account Mới

Mở **Terminal** hoặc **CMD** và chạy lệnh sau để tạo account mới (nếu chưa có):

```bash
python scripts/new_account.py
```

### 📌 Kết quả sau khi chạy lệnh:
```bash
Keystore file has been created successfully.
Account info has been created successfully.
Account Address: 0x0a13C0D6FcE5F1D09aeeE287fAe1cF8eaa9E9f1c
Private Key: e80c44ba20300e43208ffb1301303b137810455182797fb1ada79e1816864c36
```
✅ **Sau khi chạy xong**, thông tin account sẽ được lưu vào các file:
- `scripts/keystore.json`
- `scripts/account_info.json`

---

## 2️⃣ Cấu Hình Account Address Trong `docker-compose.yml`

Copy giá trị của **Account Address** và set vào biến `miner-coinbase` trong file `docker-compose.yml` tại dòng sau:

```yaml
...
  besu:
    image: hyperledger/besu:latest
    container_name: besu-node
    ports:
      - "8545:8545"
      - "30303:30303"
    command: >
      --network=dev
      --rpc-http-enabled
      --rpc-http-api=ADMIN,CLIQUE,ETH,NET,TXPOOL,WEB3,DEBUG
      --rpc-http-host=0.0.0.0
      --rpc-http-port=8545
      --p2p-port=30303
      --node-private-key-file=/keys/besu_key.txt
      --data-path=/var/lib/besu
      --host-allowlist=*
      --rpc-http-cors-origins=*
      --miner-enabled
      --miner-coinbase=0x0a13C0D6FcE5F1D09aeeE287fAe1cF8eaa9E9f1c # 🔧 Sửa ở dòng này
...
```

---

## 3️⃣ Chạy `docker-compose`

Mở Terminal và chạy các lệnh sau:

```bash
cd docker/besu-node  # Trỏ vào thư mục docker/besu-node
docker-compose up -d  # Chạy docker-compose
```

---

## 4️⃣ Deploy Smart Contract Lên Blockchain

```bash
cd scripts  # Chuyển vào thư mục scripts
python deploy_contract.py  # Chạy lệnh deploy
```

---

## 5️⃣ Chạy Flask API

```bash
uvicorn app.main:app --host localhost --port 8000 --reload
```

---

✅ **Hoàn thành!** Bạn đã thiết lập xong hệ thống. 🎉