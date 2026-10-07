# StockSense — Project Overview

> **Audience:** Anyone who wants to understand this project — teammates, recruiters, advisors, or your future self.

---

## 1. What is this project?

**StockSense** is a Machine Learning system for analyzing and predicting stock price trends on the Vietnamese stock market (HOSE/HNX).

Given a stock ticker (e.g. `VCB`, `FPT`, `VNM`), the system:
1. Renders an interactive historical price chart with technical indicators
2. Predicts whether the price will trend **up or down** over the next 5 trading days
3. **Explains each prediction** — which factors contributed most and by how much (Explainable AI)

---

## 2. Why does this project exist?

### The Problem

Vietnam has approximately **8 million individual brokerage accounts**. Most retail investors:
- Make decisions based on rumors, social media tips, and emotion
- Lack access to professional-grade analysis tools used by institutional funds
- Cannot read or interpret technical indicators (RSI, MACD, etc.)

### The Solution

StockSense brings **data-driven analysis + Machine Learning** to retail investors — free, no coding required, accessible via a web link.

### What Makes It Different

| Typical Tools | StockSense |
|---------------|------------|
| Display charts only | Charts + trend prediction |
| Black-box predictions | **Explains every prediction** (Explainable AI) |
| Foreign market data | Vietnamese market data |
| Paid subscriptions | Free and open source |

---

## 3. How does it work?

### Data Pipeline

```
Step 1 — Data Collection
   vnstock API  ──►  Daily OHLCV prices for each ticker
   (Source: HOSE/HNX)   from 2020 to present

Step 2 — Feature Engineering
   Raw OHLCV  ──►  RSI, MACD, Bollinger Bands, MA20, MA50,
                   Volume Ratio, Golden Cross...
                   (signals that professional traders use)

Step 3 — ML Model Training
   Features  ──►  XGBoost learns patterns from 5 years of history
                  Question: "When RSI < 30 AND volume doubles,
                              does price rise over the next 5 days?"

Step 4 — Explainability (SHAP)
   Prediction  ──►  "Price predicted UP because:
                     RSI oversold (+40%), Volume spike (+30%)..."

Step 5 — Dashboard
   Everything  ──►  Streamlit web app, interactive, shareable link
```

### Concrete Example

> User enters **VCB**. The system returns:
> - 1-year price chart with RSI and MACD overlays
> - Prediction: "5-day trend: **Upward** (67% confidence)"
> - Explanation: RSI at 28 (oversold), today's volume is 2.1× the 20-day average, price just touched the lower Bollinger Band

---

## 4. Known Limitations

> **The model does not predict the future with 100% accuracy — and no model ever will.**

Stock prices are influenced by news events, government policy, and crowd psychology — none of which appear in historical price data.

The model's realistic purpose:
- Identify **recurring statistical patterns** in historical data
- Output a **probability**, not a precise price target
- Serve as **one input** in an investment decision, not a crystal ball

*Being able to articulate this in an interview demonstrates mature, production-level ML thinking.*

---

## 5. Dataset

| Property | Details |
|----------|---------|
| Source | vnstock API (free, real-time HOSE/HNX data) |
| Tickers | VCB, FPT, VNM, HPG, VIC |
| Date range | 2020–01–01 to 2024–12–31 |
| Raw size | ~1,307 trading days × 5 tickers = 6,535 rows |
| After engineering | 1,258 rows × 26 columns (per ticker) |
| Refresh | Re-fetchable daily with a single command |

---

## 6. Technical Indicators

| Indicator | Financial Meaning |
|-----------|------------------|
| **RSI (14)** | Momentum oscillator: < 30 = oversold (buy signal), > 70 = overbought (sell signal) |
| **MACD** | Trend strength: positive histogram = bullish momentum, negative = bearish |
| **Bollinger Bands** | Volatility envelope: price near lower band often mean-reverts upward |
| **MA20 / MA50** | 20-day and 50-day moving averages: short and medium-term trend direction |
| **Golden Cross** | MA20 crosses above MA50: strong bullish signal |
| **Volume Ratio** | Today's volume ÷ 20-day average: > 2× indicates unusual activity |

---

## 7. Tech Stack

### Libraries

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data** | `vnstock`, `pandas`, `numpy` | Data collection and manipulation |
| **Features** | `ta` | Technical indicator computation |
| **Modeling** | `scikit-learn`, `XGBoost` | Training and evaluating ML models |
| **Explainability** | `SHAP` | Per-prediction feature attribution |
| **Visualization** | `plotly`, `matplotlib` | Interactive and static charts |
| **Dashboard** | `Streamlit` | Web app without HTML/CSS/JS |
| **Deployment** | Streamlit Cloud | Public URL, free tier |

### Design Decisions

- **XGBoost over LSTM:** Faster iteration, better SHAP compatibility, strong baseline for tabular data
- **Streamlit over Flask/React:** Python-only, no frontend knowledge required
- **vnstock over paid APIs:** Free, Vietnamese market coverage, active community

---

## 8. Project Structure

```
stocksense/
├── data/
│   ├── fetcher.py        Pull and cache OHLCV data from vnstock API
│   ├── features.py       Compute 15+ technical indicators + target variable
│   ├── raw/              Raw CSV files per ticker (VCB.csv, FPT.csv, ...)
│   └── processed/        Cleaned + featured data ready for modeling
│
├── models/               (Week 3–4)
│   ├── train.py          Train XGBoost model with TimeSeriesSplit
│   ├── evaluate.py       Metrics: accuracy, precision, recall, directional acc.
│   └── explain.py        SHAP waterfall and beeswarm plots
│
├── app/                  (Week 5–6)
│   └── main.py           Streamlit dashboard — 3 pages
│
├── notebooks/            EDA scripts and exploratory analysis
├── docs/                 Project documentation for all team members
├── requirements.txt      Python dependencies
└── README.md             Setup guide and project summary
```

---

## 9. Team

| Role | Background | Key Contributions |
|------|-----------|------------------|
| **IT Engineer** | Computer Science | Data pipeline, ML model, Streamlit dashboard, deployment |
| **Finance Analyst** | Economics | Problem framing, feature design, model validation, business rules |

This is a deliberate **cross-domain collaboration** — mirroring how real fintech teams operate.

---

## 10. Development Roadmap

| Week | Milestone | Owner |
|------|-----------|-------|
| 1–2 | Data collection, feature engineering, EDA | IT (code) + Finance (feature design) |
| 3–4 | XGBoost model, SHAP explainability | IT (code) + Finance (validate outputs) |
| 5–6 | Streamlit dashboard | IT (code) + Finance (UX feedback) |
| 7–8 | Deployment, README polish, demo prep | Both |

---

*Last updated: Week 1 — Data pipeline and EDA complete.*
