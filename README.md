# Chạy app
.venv\Scripts\activate
uvicorn app.main:app --host localhost --port 8000 --reload

# Tạo public url, sau khi tạo xong bỏ vào file .env set biến PUBLIC_URL
cloudflared tunnel run iot-tunnel
<!-- cloudflared tunnel --url http://localhost:8000 -->

# cloudflared config, config link này trong C:\Users\chuon\.cloudflared\config.yml
C:\Users\chuon\.cloudflared\2c34b23c-c0a5-4c23-b340-78da70423478.json