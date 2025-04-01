# Install App

#### 1. Mở terminal và chạy lệnh để install packages

```bash
# Tạo thư mục virtual environment
python -m venv .venv

# Active env
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

# Run app

```bash
.venv\Scripts\activate
uvicorn app.main:app --host localhost --port 8000 --reload
```

# Tạo public url, sau khi tạo xong bỏ vào file .env set biến PUBLIC_URL

```bash
cloudflared tunnel run iot-tunnel
```

# Cloudflared config, config link này trong thư mục C:\Users\chuon\cloudflared\config.yml

C:\Users\chuon\.cloudflared\2c34b23c-c0a5-4c23-b340-78da70423478.json




    
    