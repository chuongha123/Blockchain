# Hướng Dẫn Quản Lý Database Migration

Dự án này sử dụng Alembic để quản lý các thay đổi cấu trúc cơ sở dữ liệu theo thời gian.

## Cài đặt

Đảm bảo đã cài đặt Alembic:

```bash
pip install alembic
```

## Tạo Migration Mới

Để tạo một script migration mới:

```bash
# Tự động sinh script dựa trên thay đổi của model
python migrate.py create "Mô tả thay đổi" --auto

# Hoặc tạo script trống để tự viết
python migrate.py create "Mô tả thay đổi"
```

## Cập Nhật Cơ Sở Dữ Liệu

Để áp dụng các migration:

```bash
# Áp dụng tất cả migration chưa được chạy
python migrate.py upgrade

# Áp dụng migration cụ thể
python migrate.py upgrade <revision>

# Quay lại phiên bản trước đó
python migrate.py downgrade <revision>

# Lùi lại 1 bước
python migrate.py downgrade -1
```

## Xem Lịch Sử Migration

Để kiểm tra lịch sử migration:

```bash
# Hiển thị phiên bản hiện tại
python migrate.py current

# Hiển thị lịch sử migration
python migrate.py history --verbose
```

## Quy Tắc Viết Migration

Khi viết script migration, cần đảm bảo:
- Kiểm tra bảng/cột đã tồn tại trước khi tạo
- Xử lý di chuyển dữ liệu nếu cần
- Cung cấp cách quay lại phiên bản trước (downgrade)

## Kiểm Thử Migration

Luôn thử nghiệm migration trên bản sao của database production trước khi áp dụng lên môi trường thật. 