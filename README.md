# 📡 Hệ thống Thu thập, Lưu trữ và Tiền xử lý Dữ liệu IoT

Dự án mô phỏng việc thu thập dữ liệu từ cảm biến qua vi điều khiển ESP32, truyền tải qua giao thức MQTT, lưu trữ vào cơ sở dữ liệu chuỗi thời gian (InfluxDB) và thực hiện tiền xử lý dữ liệu bằng Python.

**Thông tin sinh viên:**
- **Họ và tên: Đào Khánh Duy
- **Mã sinh viên: B23DCCN235
- **Lớp/Nhóm: Lớp IoT 04 – Tổ TH 01

---

## 🏗 Kiến trúc Hệ thống

Hệ thống hoạt động theo mô hình Pipeline 1 chiều:
1. **Edge Node:** ESP32 (Wokwi) đọc dữ liệu từ cảm biến (Nhiệt độ, Độ ẩm, Khoảng cách) và Publish gói tin JSON lên MQTT Broker.
2. **Message Broker:** Sử dụng EMQX (`broker.emqx.io`) để làm trạm trung chuyển gói tin.
3. **Data Ingestion:** Script Python (`mqtt_to_influx.py`) đóng vai trò Subscriber, bắt dữ liệu thời gian thực và ghi trực tiếp vào **InfluxDB**.
4. **Data Processing:** Script Python (`data_preprocessing.py`) định kỳ lấy dữ liệu thô từ InfluxDB, điền khuyết (ffill), lọc nhiễu (IQR), chuẩn hóa (Z-score) và ghi lại bảng dữ liệu sạch.
5. **Visualization:** Dashboards trực quan hóa dữ liệu Real-time trên giao diện của InfluxDB.

---

## 📂 Cấu trúc thư mục

```text
├── mqtt_to_influx.py         # Kịch bản subscribe MQTT và ghi dữ liệu thô vào InfluxDB
├── data_preprocessing.py     # Kịch bản làm sạch, lọc nhiễu và chuẩn hóa dữ liệu
├── sketch.ino                # (Tùy chọn) Mã nguồn C++ chạy trên ESP32 (Wokwi)
├── diagram.png               # (Tùy chọn) Hình ảnh sơ đồ kiến trúc
└── README.md                 # Tài liệu hướng dẫn
```

---

## ⚙️ Yêu cầu môi trường (Prerequisites)

Để chạy được dự án này trên máy cá nhân, bạn cần cài đặt:
- **Python 3.8+**
- **InfluxDB 2.x** (Cài đặt trực tiếp hoặc qua Docker)
- Các thư viện Python cần thiết:
  ```bash
  pip install paho-mqtt influxdb-client pandas scikit-learn numpy
  ```

---

## 🚀 Hướng dẫn cấu hình và Khởi chạy

### Bước 1: Cấu hình Cơ sở dữ liệu (InfluxDB)
1. Khởi động InfluxDB tại `http://localhost:8086`.
2. Tạo Organization là `B23DCCN235` và Bucket là `Bucket`.
3. Tạo API Token có quyền Đọc/Ghi.
4. Mở file `mqtt_to_influx.py` và `data_preprocessing.py`, thay thế biến `INFLUX_TOKEN` bằng Token thực tế của bạn.

### Bước 2: Bật thiết bị biên (Wokwi)
- Chạy mạch mô phỏng ESP32 trên Wokwi (Đảm bảo code đã cài đặt đúng địa chỉ MQTT broker là `broker.emqx.io` và Topic là `ptit/iot/B23DCCN235/telemetry`).
- Đợi đến khi Serial Monitor báo `publish=OK`.

### Bước 3: Thu thập dữ liệu (Real-time)
Mở Terminal, chạy lệnh:
```bash
python mqtt_to_influx.py
```
> Script sẽ chạy ngầm liên tục để đón dữ liệu từ MQTT và ghi vào measurement `sensor_environment` trên InfluxDB.

### Bước 4: Tiền xử lý dữ liệu
Mở một cửa sổ Terminal khác, chạy lệnh:
```bash
python data_preprocessing.py
```
> Script sẽ lấy dữ liệu trong 24 giờ qua, xử lý lọc nhiễu, chuẩn hóa và ghi kết quả vào measurement `sensor_processed`. Sau đó bạn có thể xem so sánh trên Dashboard của InfluxDB.

---

## 📝 Kết quả đạt được
- Xây dựng thành công luồng truyền tải dữ liệu IoT End-to-End.
- Độ trễ hệ thống (Latency) thấp (< 200ms).
- Khắc phục thành công các lỗi mất mát dữ liệu và xử lý mượt mà các giá trị ngoại lai (outliers) bằng thư viện Pandas.
