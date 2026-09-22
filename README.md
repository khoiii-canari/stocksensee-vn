# StockSense 📈

> AI-powered Vietnamese Stock Analysis & Prediction Dashboard

---

## Giới thiệu

StockSense giúp nhà đầu tư cá nhân phân tích cổ phiếu Việt Nam bằng Machine Learning.
Điểm đặc biệt: Model không chỉ dự đoán mà còn **giải thích tại sao** (Explainable AI với SHAP).

## Cấu trúc project

```
stocksense/
├── data/
│   ├── fetcher.py       ← Lấy data từ vnstock API
│   ├── features.py      ← Tính technical indicators
│   ├── raw/             ← CSV data gốc
│   └── processed/       ← Data đã clean + features
├── models/              ← Train & đánh giá model (Tuần 3-4)
├── app/                 ← Streamlit dashboard (Tuần 5-6)
├── notebooks/           ← EDA & experiments
├── docs/                ← Tài liệu cho bạn Kinh tế
├── requirements.txt
└── README.md
```

## Cài đặt

```bash
# 1. Tạo và kích hoạt virtual environment
python -m venv venv
venv\Scripts\activate      # Windows

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Lấy data lần đầu
python -m data.fetcher
```

## Team

| Vai trò | Background | Phụ trách |
|---------|-----------|-----------|
| IT Engineer | Công nghệ thông tin | Data pipeline, ML model, Dashboard |
| Finance Analyst | Kinh tế | Feature design, Model validation, Business logic |

## Tech Stack

- **Data**: `vnstock3`, `pandas`, `numpy`
- **Features**: `ta` (Technical Analysis)
- **Model**: `scikit-learn`, `xgboost`, `shap`
- **Dashboard**: `streamlit`, `plotly`
- **Deploy**: Streamlit Cloud
