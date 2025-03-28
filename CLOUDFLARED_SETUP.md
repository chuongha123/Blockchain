# Hướng Dẫn Cấu Hình Cloudflare Tunnel Trên Máy Tính

## 1️⃣ Giới Thiệu
Cloudflare Tunnel giúp bạn expose ứng dụng chạy trên máy tính cá nhân lên internet một cách an toàn mà không cần mở cổng (port forwarding) hoặc dùng VPS. Hướng dẫn này sẽ giúp bạn thiết lập Cloudflare Tunnel để kết nối với domain bạn đã đăng ký trên Cloudflare.

---

## 2️⃣ Yêu Cầu
- **Máy tính chạy Windows, macOS hoặc Linux**
- **Đã có tài khoản Cloudflare**
- **Đã có domain được quản lý trên Cloudflare**
- **Ứng dụng web đang chạy trên máy tính (ví dụ: http://localhost:8000)**

---

## 3️⃣ Cài Đặt Cloudflared
### **Windows**
1. Tải xuống Cloudflared tại [https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation)
2. Cài đặt bằng lệnh PowerShell:
   ```powershell
   iwr -Uri https://bin.equinox.io/c/VdrWdbjqyF/cloudflared-stable-windows-amd64.zip -OutFile cloudflared.zip
   Expand-Archive cloudflared.zip -DestinationPath C:\cloudflared
   cd C:\cloudflared
   ````
3. Kiểm tra cài đặt:
   ```powershell
   cloudflared --version
   ```

### **Linux/macOS**
1. Cài đặt qua Terminal:
   ```sh
   sudo apt install cloudflared   # Ubuntu/Debian
   brew install cloudflared       # macOS
   ```
2. Kiểm tra cài đặt:
   ```sh
   cloudflared --version
   ```

---

## 4️⃣ Xác Thực Cloudflare
1. **Đăng nhập Cloudflare:**
   ```sh
   cloudflared tunnel login
   ```
2. Trình duyệt mở ra, đăng nhập vào Cloudflare và chọn domain bạn muốn sử dụng.
3. Sau khi xác thực, một file `cert.pem` sẽ được lưu tại:
   - **Windows:** `C:\Users\<tên người dùng>\.cloudflared\cert.pem`
   - **Linux/macOS:** `~/.cloudflared/cert.pem`

---

## 5️⃣ Tạo và Cấu Hình Tunnel
1. **Tạo Tunnel:**
   ```sh
   cloudflared tunnel create my-tunnel
   ```
   - Lệnh này tạo một Tunnel mới và sinh ra một file JSON chứa thông tin xác thực tại `~/.cloudflared/`.

2. **Liệt kê các Tunnel đã tạo:**
   ```sh
   cloudflared tunnel list
   ```
   Ghi lại ID Tunnel vừa tạo.

3. **Thêm Route DNS:**
   ```sh
   cloudflared tunnel route dns my-tunnel example.com
   ```
   Thay `example.com` bằng domain thực tế của bạn.

---

## 6️⃣ Cấu Hình File `config.yml`
Tạo file `config.yml` trong thư mục `~/.cloudflared/` (hoặc `C:\Users\<tên người dùng>\.cloudflared\` trên Windows) với nội dung:

```yaml
tunnel: my-tunnel
credentials-file: C:/Users/<tên người dùng>/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: example.com
    service: http://localhost:8000
  - service: http_status:404
```
> ⚠️ **Lưu ý:**
> - Thay `<tunnel-id>` bằng ID Tunnel của bạn.
> - Đường dẫn trên Windows có thể cần đổi `\` thành `/` hoặc dùng `"C:\Users\..."`

---

## 7️⃣ Chạy Cloudflare Tunnel
Khởi động Tunnel:
```sh
cloudflared tunnel run my-tunnel
```
Nếu thành công, bạn có thể truy cập ứng dụng qua `https://example.com`.

---

## 8️⃣ Tự Động Chạy Tunnel Khi Khởi Động Máy (Tuỳ Chọn)
### **Windows**
```powershell
sc.exe create Cloudflared binPath= "C:\cloudflared\cloudflared.exe tunnel run my-tunnel" start= auto
sc.exe start Cloudflared
```

### **Linux/macOS**
```sh
sudo cloudflared service install
sudo systemctl start cloudflared
```

---

## 9️⃣ Kiểm Tra Và Debug
- **Xem log của Tunnel:**
  ```sh
  cloudflared tunnel logs
  ```
- **Kiểm tra DNS đã trỏ đúng chưa:**
  ```sh
  nslookup example.com
  ```
- **Kiểm tra Tunnel đang chạy:**
  ```sh
  cloudflared tunnel info my-tunnel
  ```

---

## 🔥 Kết Luận
Bạn đã thiết lập thành công Cloudflare Tunnel để public ứng dụng trên máy tính cá nhân lên Internet một cách bảo mật mà không cần mở cổng hoặc dùng VPS. Nếu gặp lỗi, hãy kiểm tra log và chắc chắn domain đã trỏ về Tunnel.

🚀 **Chúc bạn thành công!**