## 🚀 **Hướng dẫn cài đặt Cloudflare Tunnel trên Windows**  

Cloudflare Tunnel giúp bạn **tạo một đường hầm bảo mật** để truy cập ứng dụng từ bên ngoài mà **không cần mở port trên router**.  

---

### 🛠 **Bước 1: Tải và cài đặt Cloudflared**  
📌 **Cloudflared** là client giúp kết nối máy bạn với Cloudflare.  

🔹 **Cách 1: Cài đặt qua PowerShell**  
Mở **PowerShell (Administrator)** và chạy lệnh sau:  
```powershell
Invoke-WebRequest -Uri https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile cloudflared.exe
Move-Item cloudflared.exe C:\Windows\System32\cloudflared.exe
```
📌 **Cách này giúp bạn chạy `cloudflared` ở mọi nơi trên Windows**.  

🔹 **Cách 2: Tải về thủ công**  
1. Truy cập 👉 [https://github.com/cloudflare/cloudflared/releases](https://github.com/cloudflare/cloudflared/releases)  
2. Tải **cloudflared-windows-amd64.exe**  
3. Đổi tên thành `cloudflared.exe` và **di chuyển vào thư mục `C:\Windows\System32\`**.  

👉 **Sau khi cài đặt xong**, kiểm tra bằng lệnh:  
```sh
cloudflared --version
```
Nếu hiển thị phiên bản, bạn đã cài thành công! ✅  

---

### 🛠 **Bước 2: Đăng nhập Cloudflare**  
1. Chạy lệnh:  
   ```sh
   cloudflared tunnel login
   ```
2. Trình duyệt sẽ mở ra yêu cầu bạn đăng nhập Cloudflare.  
3. Chọn một **domain bạn đã thêm vào Cloudflare**.  

📌 **Lưu ý**: Nếu bạn không có domain riêng, bạn vẫn có thể dùng Cloudflare Tunnel với tên miền `.cloudflare.dev`.  

---

### 🛠 **Bước 3: Tạo tunnel mới**  
1. Tạo tunnel với tên tùy chỉnh (ví dụ: `my-tunnel`):  
   ```sh
   cloudflared tunnel create my-tunnel
   ```
2. Cloudflare sẽ tạo một tunnel và trả về ID (lưu lại để dùng sau).  

---

### 🛠 **Bước 4: Cấu hình Tunnel**  
1. Chạy lệnh sau để tạo file cấu hình:  
   ```sh
   notepad C:\Users\%USERNAME%\.cloudflared\config.yml
   ```
2. Dán nội dung sau vào file (sửa `localhost:8080` thành ứng dụng của bạn):  
   ```yaml
   tunnel: my-tunnel
   credentials-file: C:\Users\%USERNAME%\.cloudflared\my-tunnel.json

   ingress:
     - hostname: myapp.example.com
       service: http://localhost:8080
     - service: http_status:404
   ```
3. Lưu lại file.  

📌 **Nếu không có domain, bỏ dòng `hostname` đi. Cloudflare sẽ cấp cho bạn một URL `.cloudflare.dev`.**  

---

### 🛠 **Bước 5: Chạy Tunnel**  
Chạy lệnh sau để khởi động tunnel:  
```sh
cloudflared tunnel run my-tunnel
```
👉 Sau khi chạy xong, bạn có thể truy cập ứng dụng qua **Cloudflare Tunnel** mà **không cần mở port**! 🎉  

---

### 🚀 **Bước 6: Tự động chạy Cloudflare Tunnel khi bật máy (Tùy chọn)**  
Nếu bạn muốn tunnel **chạy tự động khi khởi động Windows**, hãy thêm nó vào **Task Scheduler** hoặc dùng lệnh:  
```sh
cloudflared service install
```
📌 **Lệnh này sẽ giúp Tunnel chạy nền mà không cần mở terminal mỗi lần khởi động.**  

---

## 🔥 **Tóm lại**  
✅ **Không cần mở port trên router**  
✅ **Bảo mật hơn, có chống DDoS miễn phí**  
✅ **Tích hợp domain tùy chỉnh hoặc dùng `.cloudflare.dev`**  