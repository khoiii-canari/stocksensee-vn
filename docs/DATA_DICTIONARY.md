# Giải thích các cột trong file CSV Raw Data

> File này giúp bạn Kinh tế đọc hiểu dữ liệu thô trong thư mục `data/raw/`.
> Mỗi file CSV (VCB.csv, FPT.csv...) có cùng cấu trúc cột như bên dưới.

---

## Ví dụ 3 dòng đầu của VCB.csv

| time | open | high | low | close | volume | symbol |
|------|------|------|-----|-------|--------|--------|
| 2019-10-14 | 36.29 | 36.50 | 36.08 | 36.08 | 620,800 | VCB |
| 2019-10-15 | 36.08 | 36.25 | 35.95 | 36.16 | 648,400 | VCB |
| 2019-10-16 | 36.59 | 36.63 | 36.37 | 36.54 | 668,740 | VCB |

> **Đơn vị giá:** nghìn đồng (VND). Ví dụ `36.29` = 36,290 VND/cổ phiếu.

---

## Giải thích từng cột

### 🗓️ `time` — Ngày giao dịch
- Định dạng: `YYYY-MM-DD` (năm-tháng-ngày)
- Là ngày **phiên giao dịch thực tế** trên sàn HOSE/HNX
- Không có ngày thứ 7, Chủ nhật, ngày lễ (sàn đóng cửa)
- Ví dụ: `2024-12-31` = ngày giao dịch cuối năm 2024

---

### 📂 `open` — Giá mở cửa
- Giá khớp lệnh **đầu tiên** trong ngày (lúc 9:00 sáng)
- Thường khác giá đóng cửa hôm trước vì có tin tức qua đêm
- **Ý nghĩa phân tích:** So sánh `open` với `close` để biết phiên hôm đó net dương hay âm
  - `close > open` → nến xanh (tăng trong ngày)
  - `close < open` → nến đỏ (giảm trong ngày)

---

### 📈 `high` — Giá cao nhất trong ngày
- Mức giá **cao nhất** được khớp lệnh trong toàn bộ phiên giao dịch
- Bị giới hạn bởi **trần +7%** so với giá tham chiếu (đặc thù VN)
- **Ý nghĩa phân tích:** Khoảng cách `high - close` lớn → bên bán đang mạnh (giá bị kéo xuống từ đỉnh)

---

### 📉 `low` — Giá thấp nhất trong ngày
- Mức giá **thấp nhất** được khớp lệnh trong toàn bộ phiên giao dịch
- Bị giới hạn bởi **sàn -7%** so với giá tham chiếu (đặc thù VN)
- **Ý nghĩa phân tích:** `close - low` nhỏ → giá hồi phục tốt từ đáy trong ngày

---

### 💰 `close` — Giá đóng cửa *(quan trọng nhất)*
- Giá khớp lệnh **cuối cùng** trong ngày (lúc 14:30-14:45)
- Đây là giá được dùng làm **giá tham chiếu** cho ngày hôm sau
- **Đây là cột mà model ML sẽ học và dự đoán**
- Mọi chỉ số kỹ thuật (RSI, MACD...) đều tính từ cột này

---

### 📊 `volume` — Khối lượng giao dịch
- Tổng số **cổ phiếu** được mua + bán trong ngày (đơn vị: cổ phiếu)
- Ví dụ: `620800` = có 620,800 cổ phiếu VCB được giao dịch trong ngày đó
- **KHÔNG phải** giá trị tiền (muốn ra tiền thì nhân với `close`)
- **Ý nghĩa phân tích:**
  - Volume cao + giá tăng = xu hướng tăng có xác nhận (tiền đang đổ vào)
  - Volume cao + giá giảm = bán tháo (cảnh báo nguy hiểm)
  - Volume thấp = thị trường đang do dự, ít người quan tâm

---

### 🏷️ `symbol` — Mã cổ phiếu
- Tên mã chứng khoán trên sàn
- Ví dụ: `VCB` = Vietcombank, `FPT` = FPT Corp, `VNM` = Vinamilk
- Cột này được thêm vào để khi ghép nhiều file lại vẫn biết dòng nào thuộc mã nào

---

## Cách đọc 1 dòng hoàn chỉnh

```
time: 2024-12-31
open: 60.72  → Sáng mở cửa: 60,720 VND
high: 60.85  → Cao nhất ngày: 60,850 VND
low:  60.06  → Thấp nhất ngày: 60,060 VND  ← giảm mạnh từ đỉnh
close: 60.06 → Đóng cửa: 60,060 VND        ← đóng ở mức thấp = nến đỏ
volume: 2,375,289  → Hơn 2.3 triệu cổ phiếu được giao dịch (volume cao)
```

**Đọc:** Ngày cuối năm 2024, VCB mở cửa ở 60,720 đồng, có lúc lên đến 60,850 nhưng sau đó bị kéo xuống mạnh, đóng cửa ở 60,060 — volume cao bất thường (2.3 triệu cp) cho thấy có lực bán lớn vào cuối năm.

---

## Câu hỏi gợi ý cho bạn Kinh tế

Khi nhìn vào data, hãy thử trả lời:

1. **Volume:** Ngày nào VCB có volume cao nhất? Hôm đó có tin tức gì không?
2. **Giá:** Giá VCB thấp nhất trong giai đoạn 2020-2024 là bao nhiêu? Thời điểm nào?
3. **Pattern:** Có thấy pattern volume tăng vào cuối tháng/quý không?
   *(Gợi ý: mùa BCTC → nhà đầu tư mua/bán trước kết quả)*

> Ghi câu trả lời vào Google Doc để chia sẻ với bạn IT trong buổi họp Ngày 5.
