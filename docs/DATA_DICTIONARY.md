# Data Dictionary — Raw CSV Files

> **Audience:** Anyone reading the files in `data/raw/` (VCB.csv, FPT.csv, etc.)
> All files share the same column structure described below.

---

## Sample rows — VCB.csv

| time | open | high | low | close | volume | symbol |
|------|------|------|-----|-------|--------|--------|
| 2019-10-14 | 36.29 | 36.50 | 36.08 | 36.08 | 620,800 | VCB |
| 2019-10-15 | 36.08 | 36.25 | 35.95 | 36.16 | 648,400 | VCB |
| 2019-10-16 | 36.59 | 36.63 | 36.37 | 36.54 | 668,740 | VCB |

> **Price unit:** thousands of VND. e.g. `36.29` = 36,290 VND per share.

---

## Column Definitions

### `time` — Trading Date
- Format: `YYYY-MM-DD`
- Represents the actual **exchange trading session** date (HOSE/HNX)
- Excludes weekends and public holidays (exchange is closed)
- Example: `2024-12-31` = last trading session of 2024

---

### `open` — Opening Price
- The **first matched price** of the trading session (~9:00 AM)
- Often differs from the previous day's close due to overnight news or events
- **Analytical use:** Compare `open` vs `close` to characterize the session
  - `close > open` → green candle (net gain during the day)
  - `close < open` → red candle (net loss during the day)

---

### `high` — Intraday High
- The **highest matched price** during the entire trading session
- Capped by the **+7% daily limit** above the reference price (Vietnam-specific rule)
- **Analytical use:** A large `high - close` spread means sellers pushed price down from its peak

---

### `low` — Intraday Low
- The **lowest matched price** during the entire trading session
- Floored by the **−7% daily limit** below the reference price (Vietnam-specific rule)
- **Analytical use:** A small `close - low` spread means the price recovered well from its intraday bottom

---

### `close` — Closing Price *(most important column)*
- The **last matched price** of the session (~2:30–2:45 PM)
- Becomes the **reference price** for the next session's ±7% limit
- **This is the column the ML model learns to predict**
- All technical indicators (RSI, MACD, Bollinger Bands, etc.) are derived from this column

---

### `volume` — Trading Volume
- Total number of **shares** bought and sold during the session (unit: shares)
- Example: `620800` = 620,800 shares of VCB changed hands that day
- **Not** a monetary value (to get VND value: `volume × close × 1000`)
- **Analytical use:**
  - High volume + rising price → confirmed uptrend (money flowing in)
  - High volume + falling price → potential sell-off (warning signal)
  - Low volume → market indecision, low conviction

---

### `symbol` — Ticker Symbol
- The stock's exchange identifier
- Examples: `VCB` = Vietcombank, `FPT` = FPT Corp, `VNM` = Vinamilk
- Added programmatically so that rows remain identifiable when multiple files are merged

---

## Reading a Full Row

```
time:   2024-12-31
open:   60.72   → Session opened at 60,720 VND
high:   60.85   → Reached a high of 60,850 VND
low:    60.06   → Dropped as far as 60,060 VND   ← sharp intraday pullback
close:  60.06   → Closed at 60,060 VND           ← closed at the low → bearish
volume: 2,375,289 → Over 2.3M shares traded       ← abnormally high volume
```

**Interpretation:** On the last trading day of 2024, VCB opened at 60,720 VND, briefly touched 60,850, then was pushed sharply lower to close at the session low of 60,060. The abnormally high volume (2.3M shares, vs. a ~1M daily average) suggests significant selling pressure into year-end.

---

## Questions for the Finance Analyst

When reviewing the data in Excel or Google Sheets, consider:

1. **Volume spikes:** On which dates did VCB show the highest volume? Was there a corporate announcement or macro event that day?
2. **Price lows:** What was VCB's lowest closing price over 2020–2024? What was the market context at that time?
3. **Seasonal patterns:** Do you observe volume clustering at quarter-end or around earnings season?
   *(Hint: institutional rebalancing and earnings-driven trading often create repeatable patterns.)*

> Record your findings in the shared Google Doc before the Day 5 alignment meeting.
