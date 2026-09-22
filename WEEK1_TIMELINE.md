# 📅 Tuần 1 — StockSense Project Kickoff

> **Mục tiêu cuối tuần:** Cả 2 người hiểu rõ bài toán, có data thật, có danh sách features đã thống nhất.

---

## 👨‍💻 IT (bạn) — Chi tiết từng ngày

### Ngày 1 — Setup môi trường (2-3 tiếng)

**Cài đặt:**
```bash
# 1. Tạo folder project
mkdir stocksense
cd stocksense

# 2. Tạo virtual environment
python -m venv venv
venv\Scripts\activate       # Windows

# 3. Cài thư viện tuần 1
pip install vnstock pandas numpy matplotlib jupyter
pip install ta              # Technical Analysis library
```

**Tạo cấu trúc thư mục:**
```
stocksense/
├── data/
│   ├── raw/            ← data gốc từ API
│   └── processed/      ← data đã clean
├── notebooks/
│   └── 01_EDA.ipynb    ← khám phá data
├── docs/               ← tài liệu cho bạn Kinh tế
└── requirements.txt
```

**Deliverable:** Folder project tạo xong, môi trường chạy được.

---

### Ngày 2 — Lấy data thật (2-3 tiếng)

**Viết script lấy data từ vnstock:**

```python
# data/fetcher.py
from vnstock3 import Vnstock

def fetch_stock_data(symbol: str, start: str, end: str):
    """
    Lấy dữ liệu OHLCV của 1 mã cổ phiếu
    symbol: 'VCB', 'FPT', 'VNM'...
    start/end: 'YYYY-MM-DD'
    """
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    df = stock.quote.history(start=start, end=end, interval='1D')
    return df

# Test với 5 mã
symbols = ['VCB', 'FPT', 'VNM', 'HPG', 'VIC']
for s in symbols:
    df = fetch_stock_data(s, '2020-01-01', '2024-12-31')
    df.to_csv(f'data/raw/{s}.csv', index=False)
    print(f'{s}: {len(df)} rows')
```

**Deliverable:** 5 file CSV trong `data/raw/`, mỗi file ~1200 rows (5 năm data).

---

### Ngày 3 — Khám phá data (EDA) (2-3 tiếng)

**Mở notebook và trả lời các câu hỏi:**

```python
# notebooks/01_EDA.ipynb

# Câu hỏi 1: Data có bị thiếu không?
df.isnull().sum()

# Câu hỏi 2: Phân phối % thay đổi giá hàng ngày thế nào?
df['daily_return'] = df['close'].pct_change()
df['daily_return'].describe()

# Câu hỏi 3: Volume có bất thường không?
df['volume'].plot()

# Câu hỏi 4: Các mã có tương quan nhau không?
# → Khi VCB tăng, VNM có tăng theo không?
```

**Ghi lại findings vào Google Doc để chia sẻ với bạn Kinh tế.**

**Deliverable:** Notebook chạy được, 5-10 chart cơ bản, findings document.

---

### Ngày 4 — Tính Technical Indicators (2-3 tiếng)

```python
# data/features.py
import ta

def add_technical_indicators(df):
    # RSI — momentum indicator
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

    # MACD — trend indicator
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()

    # Bollinger Bands — volatility
    bb = ta.volatility.BollingerBands(df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_pct'] = bb.bollinger_pband()   # 0=lower, 1=upper

    # Moving Averages
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()

    # Volume
    df['volume_ma20'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma20']

    return df.dropna()
```

**Deliverable:** DataFrame có ~12 features mới, visualize được trên chart.

---

### Ngày 5 — Buổi họp với bạn Kinh tế (1-2 tiếng)

**Bạn IT chuẩn bị mang vào buổi họp:**
- [ ] Chart giá + RSI + MACD của VCB (print ra hoặc share màn hình)
- [ ] Danh sách 12 features đã tính được
- [ ] 2-3 câu hỏi cần bạn Kinh tế trả lời (xem phần dưới)

---

## 👨‍💼 Kinh tế — Chi tiết từng ngày

### Ngày 1-2 — Nghiên cứu bài toán (3-4 tiếng tổng)

**Đọc và trả lời 3 câu hỏi này vào Google Doc:**

```
❓ Câu 1: Nhà đầu tư F0 (mới) thường mắc sai lầm gì?
   → Gợi ý: FOMO, không có stop-loss, nghe tin đồn...
   → Ta có thể dùng data để cảnh báo những sai lầm này không?

❓ Câu 2: Khi bạn phân tích 1 cổ phiếu, bạn xem gì đầu tiên?
   → Liệt kê theo thứ tự ưu tiên
   → Tại sao mỗi chỉ số lại quan trọng?

❓ Câu 3: Khi nào thì bạn KHÔNG mua dù chỉ số kỹ thuật tốt?
   → Tin tức xấu? Mùa báo cáo tài chính? Thị trường chung đang giảm?
   → Đây là "red flags" mà model cần biết
```

**Deliverable:** Google Doc có câu trả lời cho 3 câu hỏi trên.

---

### Ngày 3-4 — Feature Design (3-4 tiếng tổng)

**Điền vào bảng Google Sheets này:**

| Feature | Ý nghĩa tài chính | Ngưỡng quan trọng | Tín hiệu mua | Tín hiệu bán |
|---------|-------------------|-------------------|--------------|--------------|
| RSI | Đo momentum quá mua/quá bán | < 30 oversold, > 70 overbought | RSI < 30 và đang tăng | RSI > 70 và đang giảm |
| MACD | ... | ... | ... | ... |
| Volume | ... | ... | ... | ... |
| *(thêm hàng)* | | | | |

**Câu hỏi gợi ý để research:**
- RSI ngưỡng 30/70 có phù hợp với thị trường VN không? Hay cần điều chỉnh?
- Ngoài chỉ số kỹ thuật, có chỉ số cơ bản nào (P/E, EPS) nên đưa vào không?
- Cổ phiếu bluechip (VCB, VNM) và cổ phiếu nhỏ có cần phân tích khác nhau không?

**Deliverable:** Bảng Google Sheets hoàn chỉnh, ít nhất 8-10 features có giải thích.

---

### Ngày 5 — Buổi họp chung (1-2 tiếng)

**Bạn Kinh tế chuẩn bị:**
- [ ] Bảng features đã điền
- [ ] 3 câu trả lời từ Ngày 1-2
- [ ] Câu hỏi muốn hỏi về kỹ thuật (nếu có)

---

## 🤝 Buổi họp Ngày 5 — Agenda

```
[15 phút] IT demo: data đã lấy được + chart trực quan
[20 phút] Kinh tế trình bày: feature list + ý nghĩa từng cái
[15 phút] Thảo luận: feature nào giữ, feature nào bỏ
[10 phút] Thống nhất: target variable là gì?
           → Predict giá? Hay predict xu hướng (tăng/giảm)?
```

---

## ✅ Checklist cuối Tuần 1

### IT
- [ ] Môi trường Python cài xong, chạy được
- [ ] Data 5 mã cổ phiếu đã tải về (CSV)
- [ ] Notebook EDA có ít nhất 5 chart
- [ ] Script tính 8-10 technical indicators chạy được

### Kinh tế  
- [ ] Google Doc trả lời 3 câu hỏi bài toán
- [ ] Google Sheets feature list ít nhất 8 features
- [ ] Có ý kiến về target variable (predict cái gì)

### Cả 2
- [ ] Đã họp 1 lần, thống nhất feature list
- [ ] Biết tuần 2 sẽ làm gì

---

> **Tuần 2 preview:** IT bắt đầu build model đầu tiên (baseline). Kinh tế bắt đầu viết phần giải thích chỉ số cho user documentation.
