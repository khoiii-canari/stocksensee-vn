# StockSense 📈

> AI-powered Vietnamese Stock Analysis & Prediction Dashboard

---

## Overview

**StockSense** is an end-to-end Machine Learning system that analyzes and predicts stock price trends on the Vietnamese stock market (HOSE/HNX).

Users enter a stock ticker (e.g. `VCB`, `FPT`, `VNM`) and the system:
1. Displays historical price charts with technical indicators
2. Predicts the 5-day price trend (upward or downward)
3. **Explains why** the model made that prediction (Explainable AI via SHAP)

---

## Project Structure

```
stocksense/
├── config.py            ← Central configurations (features, tickers, hyperparams)
├── data/
│   ├── fetcher.py       ← Pull OHLCV data from vnstock API / load cached CSV
│   ├── features.py      ← Compute 20+ technical indicators & clean features
│   ├── raw/             ← Raw CSV files (one per ticker: VCB, FPT, VNM, HPG, VIC)
│   └── processed/       ← Cleaned data + features, ready for modeling
├── models/
│   ├── train.py         ← Train XGBoost model with TimeSeriesSplit & save artifacts
│   ├── evaluate.py      ← Metrics (Accuracy, Precision, Recall, F1) & confusion matrix
│   ├── explain.py       ← SHAP Explainability (Waterfall, beeswarm, feature impact)
│   ├── predict.py       ← Production inference pipeline for current stock signals
│   └── saved/           ← Serialized model (.pkl), feature list, and evaluation metrics (.json)
├── app/
│   └── main.py          ← Multi-page interactive Streamlit dashboard
├── notebooks/           ← EDA scripts and interactive Plotly HTML reports
├── docs/                ← Project documentation & Data Dictionary
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# 1. Clone and navigate
git clone <repo-url>
cd stocksense

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Fetch stock data (first time only or use cached in data/raw)
python data/fetcher.py

# 5. Run Exploratory Data Analysis (EDA)
python notebooks/01_EDA.py

# 6. Train XGBoost Model with TimeSeries Validation
python models/train.py

# 7. Evaluate model & check metrics
python models/evaluate.py

# 8. Run inference on latest market data
python models/predict.py

# 9. Launch Streamlit Web Dashboard
streamlit run app/main.py
```

---

## Data

| Property | Details |
|----------|---------|
| Source | vnstock API (free, real data from HOSE/HNX) |
| Tickers | VCB, FPT, VNM, HPG, VIC (expandable) |
| Period | 2020 – 2024 (~1,307 trading days per ticker) |
| Raw features | 7 columns: time, open, high, low, close, volume, symbol |
| Engineered features | 26 columns after technical indicator computation |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data | `vnstock`, `pandas`, `numpy` |
| Features | `ta` (Technical Analysis library) |
| Model | `scikit-learn`, `XGBoost`, `SHAP` |
| Visualization | `plotly`, `matplotlib` |
| Dashboard | `Streamlit` |
| Deployment | Streamlit Cloud |

---

## Team

| Role | Background | Responsibilities |
|------|-----------|-----------------|
| IT Engineer | Computer Science | Data pipeline, ML modeling, dashboard, deployment |
| Finance Analyst | Economics | Feature design, model validation, business logic, UX feedback |

---

## Roadmap
 
| Week | Goal | Status |
|------|------|--------|
| 1–2 | Data collection, feature engineering, EDA | ✅ Hoàn thành |
| 3–4 | XGBoost model training, TimeSeries CV, SHAP explainability | ✅ Hoàn thành |
| 5–6 | Streamlit dashboard (Technical charts, AI prediction, SHAP breakdown) | ✅ Hoàn thành |
| 7–8 | Deployment & Cloud Hosting | 🚀 Sẵn sàng deploy |
