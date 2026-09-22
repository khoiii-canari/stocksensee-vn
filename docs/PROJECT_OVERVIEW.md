# StockSense — Tổng Quan Dự Án

> **Dành cho:** Bất kỳ ai muốn hiểu dự án này — bạn đồng đội, recruiter, giảng viên, hay chính bạn sau 3 tháng quên hết.

---

## 1. Dự án này là gì?

**StockSense** là một hệ thống phân tích và dự đoán xu hướng cổ phiếu trên thị trường chứng khoán Việt Nam (HOSE/HNX), được xây dựng bằng Machine Learning.

Người dùng nhập vào một mã cổ phiếu (ví dụ: `VCB`, `FPT`, `VNM`) và hệ thống sẽ:

1. Hiển thị biểu đồ giá lịch sử kèm các chỉ số kỹ thuật
2. Dự đoán xu hướng giá trong 5 ngày tới (tăng hay giảm)
3. **Giải thích tại sao** model đưa ra dự đoán đó (yếu tố nào ảnh hưởng nhiều nhất)

---

## 2. Tại sao cần dự án này?

### Vấn đề thực tế

Có khoảng **8 triệu tài khoản chứng khoán** tại Việt Nam, phần lớn là nhà đầu tư cá nhân (F0). Họ thường:

- Ra quyết định dựa trên tin đồn, hội nhóm Zalo, cảm tính
- Không có công cụ phân tích bài bản như các quỹ đầu tư lớn
- Không biết đọc biểu đồ kỹ thuật (RSI, MACD...)

### Giải pháp

StockSense đưa **công cụ phân tích dữ liệu + Machine Learning** vào tay nhà đầu tư cá nhân — miễn phí, không cần biết code, chỉ cần vào web là dùng được.

### Điểm khác biệt so với các tool thông thường

| Tool thông thường | StockSense |
|-------------------|------------|
| Chỉ hiển thị biểu đồ | Hiển thị + dự đoán xu hướng |
| Dự đoán như "hộp đen" | **Giải thích từng dự đoán** (Explainable AI) |
| Data nước ngoài | Data thị trường Việt Nam thật |
| Mất phí | Miễn phí, mã nguồn mở |

---

## 3. Hệ thống hoạt động như thế nào?

### Luồng dữ liệu (Data Pipeline)

```
Bước 1: Thu thập dữ liệu
   vnstock API  ──►  Giá đóng cửa, mở cửa, cao/thấp, khối lượng
   (nguồn: HOSE/HNX)    mỗi ngày từ 2020 đến nay

Bước 2: Tính chỉ số kỹ thuật (Feature Engineering)
   Dữ liệu thô  ──►  RSI, MACD, Bollinger Bands, MA20, MA50, Volume ratio...
                      (những "tín hiệu" mà nhà đầu tư chuyên nghiệp hay dùng)

Bước 3: Huấn luyện Model ML
   Dữ liệu + Chỉ số  ──►  XGBoost model học pattern từ 5 năm lịch sử
                            Câu hỏi: "Khi RSI < 30 + volume tăng 2x,
                                       5 ngày sau giá có tăng không?"

Bước 4: Giải thích dự đoán (Explainable AI)
   Kết quả dự đoán  ──►  SHAP values phân tích đóng góp từng yếu tố
                           "Giá tăng vì: RSI oversold (+40%), Volume tăng (+30%)..."

Bước 5: Hiển thị trên Dashboard
   Tất cả  ──►  Streamlit web app — người dùng tương tác, xem kết quả
```

### Ví dụ cụ thể

> Người dùng nhập **VCB**, hệ thống trả về:
> - Biểu đồ giá 1 năm với đường RSI phía dưới
> - Dự đoán: "Xu hướng 5 ngày tới: **Tăng** (xác suất 67%)"
> - Lý do: RSI đang ở 28 (oversold), volume hôm nay gấp 2.1 lần trung bình, giá vừa chạm lower Bollinger Band

---

## 4. Giới hạn cần biết

> **Model không dự đoán được tương lai chính xác 100%.**

Thị trường chứng khoán bị ảnh hưởng bởi tin tức, chính sách, tâm lý đám đông — những thứ không có trong data lịch sử.

Mục tiêu thực tế của model là:
- Tìm **pattern lặp lại** trong dữ liệu quá khứ
- Đưa ra **xác suất** xu hướng, không phải giá tuyệt đối
- Là **một công cụ tham khảo** trong quá trình phân tích, không phải oracle

---

## 5. Dữ liệu

| Thông tin | Chi tiết |
|-----------|----------|
| Nguồn | vnstock API (miễn phí, dữ liệu thật từ HOSE/HNX) |
| Các mã | VCB, FPT, VNM, HPG, VIC (có thể mở rộng) |
| Khoảng thời gian | 2020 - 2024 (~1,307 ngày giao dịch/mã) |
| Tổng dữ liệu | ~6,500 rows, 7 cột raw → 26 cột sau feature engineering |
| Cập nhật | Có thể fetch lại mỗi ngày bằng 1 câu lệnh |

---

## 6. Các chỉ số kỹ thuật được sử dụng

| Chỉ số | Ý nghĩa ngắn gọn |
|--------|-----------------|
| **RSI (14)** | Đo momentum: < 30 = oversold (có thể mua), > 70 = overbought (có thể bán) |
| **MACD** | Đo xu hướng: histogram dương = đà tăng, âm = đà giảm |
| **Bollinger Bands** | Đo biến động: giá ở lower band = thường bật lại |
| **MA20 / MA50** | Đường trung bình 20 và 50 ngày: xác định xu hướng trung và ngắn hạn |
| **Golden Cross** | MA20 cắt MA50 từ dưới lên = tín hiệu mua mạnh |
| **Volume Ratio** | So sánh volume hôm nay vs trung bình 20 ngày: > 2 là đột biến |

---

## 7. Tech Stack

### Ngôn ngữ & Thư viện

| Tầng | Công nghệ | Mục đích |
|------|-----------|----------|
| **Data** | `vnstock`, `pandas`, `numpy` | Thu thập và xử lý dữ liệu |
| **Features** | `ta` (Technical Analysis) | Tính các chỉ số kỹ thuật |
| **Model** | `scikit-learn`, `XGBoost` | Train và đánh giá model ML |
| **Explainability** | `SHAP` | Giải thích từng dự đoán của model |
| **Visualization** | `plotly`, `matplotlib` | Vẽ biểu đồ tương tác |
| **Dashboard** | `Streamlit` | Web app không cần biết HTML/CSS |
| **Deploy** | Streamlit Cloud | Publish lên internet, có link public |

### Tại sao chọn những công cụ này?

- **XGBoost** thay vì LSTM/Deep Learning: Nhanh hơn, dễ debug hơn, phù hợp với tabular data (bảng số), và SHAP hỗ trợ tốt
- **Streamlit** thay vì Flask/React: Viết Python thuần là ra web app, không cần học frontend
- **vnstock** thay vì mua data: Miễn phí, dữ liệu VN thật, cộng đồng lớn

---

## 8. Cấu trúc thư mục

```
stocksense/
├── data/
│   ├── fetcher.py        Thu thập dữ liệu từ vnstock API
│   ├── features.py       Tính toán 15+ technical indicators
│   ├── raw/              CSV gốc (VCB.csv, FPT.csv...)
│   └── processed/        Data đã clean + features, sẵn sàng cho model
│
├── models/               (Tuần 3-4)
│   ├── train.py          Huấn luyện XGBoost model
│   ├── evaluate.py       Đánh giá và so sánh models
│   └── explain.py        Tạo SHAP explanations
│
├── app/                  (Tuần 5-6)
│   └── main.py           Streamlit dashboard (3 trang)
│
├── notebooks/            Jupyter notebooks cho EDA và thử nghiệm
├── docs/                 Tài liệu cho thành viên team
├── requirements.txt      Danh sách thư viện cần cài
└── README.md             Hướng dẫn cài đặt và chạy
```

---

## 9. Team

| Vai trò | Background | Đóng góp chính |
|---------|-----------|----------------|
| **IT Engineer** | Công nghệ thông tin | Data pipeline, ML model, Streamlit dashboard, Deploy |
| **Finance Analyst** | Kinh tế | Định nghĩa bài toán, Feature design, Validate model output, Business logic |

Đây là dự án **cross-domain** — kết hợp kiến thức tài chính và kỹ thuật phần mềm, phản ánh cách team thực tế tại các công ty fintech hoạt động.

---

## 10. Roadmap

| Tuần | Mục tiêu | Người thực hiện |
|------|----------|----------------|
| 1-2 | Thu thập data, tính indicators, EDA | IT (code) + Kinh tế (feature design) |
| 3-4 | Train XGBoost model, thêm SHAP | IT (code) + Kinh tế (validate output) |
| 5-6 | Xây Streamlit dashboard | IT (code) + Kinh tế (feedback UX) |
| 7-8 | Deploy, polish README, demo | Cả 2 |

---

*Tài liệu này được cập nhật theo tiến độ project.*
*Lần cập nhật gần nhất: Tuần 1 — Data pipeline hoàn thành.*
