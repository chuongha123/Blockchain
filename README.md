# Chạy app
.venv\Scripts\activate
uvicorn app.main:app --host localhost --port 8000 --reload

# Tạo public url, sau khi tạo xong bỏ vào file .env set biến PUBLIC_URL
cloudflared tunnel --url http://localhost:8000
