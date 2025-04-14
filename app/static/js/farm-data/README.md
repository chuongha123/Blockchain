# Farm Data Modules

Đây là tập hợp các module JavaScript cho phần hiển thị dữ liệu nông trại. Cấu trúc được thiết kế theo mô hình module để cải thiện tính bảo trì và khả năng mở rộng.

## Cấu trúc thư mục

```
farm-data/
├── index.js           # Điểm khởi đầu chính, kết nối các module
├── utils.js           # Các hàm tiện ích dùng chung
├── table-manager.js   # Quản lý hiển thị và tương tác với bảng dữ liệu
├── filter-manager.js  # Quản lý bộ lọc dữ liệu
├── chart-manager.js   # Quản lý hiển thị biểu đồ
├── view-manager.js    # Quản lý chuyển đổi giữa các chế độ xem
└── README.md          # Tài liệu này
```

## Các module

### utils.js
Chứa các hàm tiện ích dùng chung cho toàn bộ ứng dụng, như định dạng thời gian, xử lý dữ liệu và kiểm tra DOM.

### table-manager.js
Quản lý toàn bộ phần hiển thị bảng dữ liệu, bao gồm:
- Sắp xếp dữ liệu
- Phân trang
- Hiển thị dữ liệu trong bảng

### filter-manager.js
Quản lý việc lọc dữ liệu theo các tiêu chí, hiện tại hỗ trợ:
- Lọc theo khoảng thời gian (từ ngày -> đến ngày)
- Xóa bộ lọc và khôi phục dữ liệu gốc

### chart-manager.js
Quản lý việc hiển thị dữ liệu dưới dạng biểu đồ:
- Hiển thị biểu đồ cho từng loại dữ liệu (nhiệt độ, độ ẩm...)
- Hiển thị biểu đồ tổng hợp tất cả các loại dữ liệu
- Xử lý lỗi và hiển thị thông báo phù hợp

### view-manager.js
Quản lý việc chuyển đổi giữa các chế độ xem:
- Bảng dữ liệu
- Biểu đồ
- Xử lý sự kiện khi chuyển đổi chế độ xem

### index.js
Điểm khởi đầu chính của ứng dụng, kết nối các module lại với nhau. Chức năng bao gồm:
- Khởi tạo tất cả các module
- Kết nối các sự kiện giữa các module
- Xử lý luồng dữ liệu giữa các thành phần

## Luồng dữ liệu

1. Dữ liệu ban đầu được tải từ server và lưu trong biến `originalData`
2. `FilterManager` có thể lọc dữ liệu này theo các tiêu chí
3. `TableManager` hiển thị dữ liệu đã lọc trong bảng và xử lý phân trang
4. `ChartManager` hiển thị dữ liệu đã lọc dưới dạng biểu đồ
5. `ViewManager` quản lý việc chuyển đổi giữa bảng và biểu đồ

## Cách mở rộng

Khi cần thêm tính năng mới:
1. **Thêm bộ lọc mới**: Mở rộng `FilterManager` để hỗ trợ các loại bộ lọc khác
2. **Thêm loại biểu đồ mới**: Mở rộng `ChartManager` để hỗ trợ các loại biểu đồ khác
3. **Thêm chế độ xem mới**: Mở rộng `ViewManager` và thêm phần UI tương ứng 