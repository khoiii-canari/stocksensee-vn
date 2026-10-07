"""
notebooks/01_EDA.py
-------------------
Exploratory Data Analysis — Understand the data before training any model.

Run:    python notebooks/01_EDA.py
Output: Interactive HTML charts saved to notebooks/charts/
        Open in any browser. Share HTML files — no Python required to view.
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')
os.environ['VNSTOCK_TELEMETRY'] = 'off'

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data.fetcher import load_stock_from_csv
from data.features import add_technical_indicators

# --- Config ---
CHARTS_DIR   = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)
FOCUS_SYMBOL = 'VCB'
ALL_SYMBOLS  = ['VCB', 'FPT', 'VNM', 'HPG', 'VIC']

print("=" * 60)
print("  STOCKSENSE — Exploratory Data Analysis (EDA)")
print("=" * 60)


# ============================================================
# SECTION 1: Load and validate data
# ============================================================
print("\n[1/5] Loading data...")

all_data = {}
for sym in ALL_SYMBOLS:
    df_raw  = load_stock_from_csv(sym)
    df_feat = add_technical_indicators(df_raw)
    all_data[sym] = df_feat
    print(f"   {sym}: {len(df_feat)} rows, {df_feat.shape[1]} cols")

df = all_data[FOCUS_SYMBOL]
print(f"\n   Date range    : {df['time'].min().date()} -> {df['time'].max().date()}")
print(f"   Missing values: {df.isnull().sum().sum()} (expected: 0)")


# ============================================================
# SECTION 2: Chart 1 — Price + RSI + MACD + Volume
# ============================================================
print("\n[2/5] Generating price + indicators chart...")

fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    row_heights=[0.5, 0.2, 0.15, 0.15],
    vertical_spacing=0.03,
    subplot_titles=[
        f'{FOCUS_SYMBOL} — Closing Price + Bollinger Bands + Moving Averages',
        'RSI (14) — Oversold < 30  |  Overbought > 70',
        'MACD Histogram',
        'Volume vs. 20-Day Average'
    ]
)

# Row 1: Price + Bollinger Bands + MAs
fig.add_trace(go.Scatter(x=df['time'], y=df['close'],
    name='Close', line=dict(color='#2196F3', width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=df['time'], y=df['bb_upper'],
    name='BB Upper', line=dict(color='#E0E0E0', width=1, dash='dash'), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=df['time'], y=df['bb_lower'],
    name='BB Lower', line=dict(color='#E0E0E0', width=1, dash='dash'),
    fill='tonexty', fillcolor='rgba(200,200,200,0.1)', showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=df['time'], y=df['ma20'],
    name='MA20', line=dict(color='#FF9800', width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=df['time'], y=df['ma50'],
    name='MA50', line=dict(color='#9C27B0', width=1)), row=1, col=1)

gc = df[df['golden_cross'] == 1]
if len(gc) > 0:
    fig.add_trace(go.Scatter(x=gc['time'], y=gc['close'],
        mode='markers', name='Golden Cross',
        marker=dict(symbol='triangle-up', size=12, color='gold')), row=1, col=1)

# Row 2: RSI
fig.add_trace(go.Scatter(x=df['time'], y=df['rsi'],
    name='RSI', line=dict(color='#4CAF50', width=1.5)), row=2, col=1)
fig.add_hline(y=70, line_dash='dash', line_color='red',   annotation_text='70', row=2, col=1)
fig.add_hline(y=30, line_dash='dash', line_color='green', annotation_text='30', row=2, col=1)
fig.add_hline(y=50, line_dash='dot',  line_color='gray',  row=2, col=1)

# Row 3: MACD histogram
colors_macd = ['#4CAF50' if v >= 0 else '#F44336' for v in df['macd_diff']]
fig.add_trace(go.Bar(x=df['time'], y=df['macd_diff'],
    name='MACD Diff', marker_color=colors_macd), row=3, col=1)

# Row 4: Volume
colors_vol = ['#4CAF50' if c >= o else '#F44336' for c, o in zip(df['close'], df['open'])]
fig.add_trace(go.Bar(x=df['time'], y=df['volume'],
    name='Volume', marker_color=colors_vol), row=4, col=1)
fig.add_trace(go.Scatter(x=df['time'], y=df['volume_ma20'],
    name='Vol MA20', line=dict(color='orange', width=1.5)), row=4, col=1)

fig.update_layout(
    height=900, title_text=f'Technical Analysis: {FOCUS_SYMBOL} (2020-2024)',
    template='plotly_dark', hovermode='x unified',
    legend=dict(orientation='h', y=1.02)
)

path1 = os.path.join(CHARTS_DIR, '01_price_indicators.html')
fig.write_html(path1)
print(f"   Saved: {path1}")


# ============================================================
# SECTION 3: Chart 2 — Daily Return Distribution
# ============================================================
print("\n[3/5] Analyzing daily return distributions...")

fig2 = make_subplots(rows=2, cols=3, subplot_titles=ALL_SYMBOLS)

for i, sym in enumerate(ALL_SYMBOLS):
    row = i // 3 + 1
    col = i %  3 + 1
    ret = all_data[sym]['close'].pct_change().dropna() * 100
    mean_r, std_r = ret.mean(), ret.std()

    fig2.add_trace(go.Histogram(x=ret, name=sym, nbinsx=60,
        marker_color='#2196F3' if sym == FOCUS_SYMBOL else '#78909C',
        opacity=0.8), row=row, col=col)
    fig2.add_vline(x=mean_r, line_dash='dash', line_color='yellow', row=row, col=col)

    print(f"   {sym}: mean={mean_r:.3f}%/day,  std={std_r:.3f}%,  "
          f"max gain={ret.max():.1f}%,  max loss={ret.min():.1f}%")

fig2.update_layout(
    height=500, title='Daily Return Distribution — All Tickers (2020-2024)',
    template='plotly_dark', showlegend=False
)

path2 = os.path.join(CHARTS_DIR, '02_daily_returns.html')
fig2.write_html(path2)
print(f"   Saved: {path2}")


# ============================================================
# SECTION 4: Chart 3 — Cross-Ticker Correlation
# ============================================================
print("\n[4/5] Computing correlation matrix...")

close_df = pd.DataFrame({sym: all_data[sym].set_index('time')['close'] for sym in ALL_SYMBOLS})
corr = close_df.pct_change().corr()

print("\n   Correlation Matrix (Daily Returns):")
print(corr.round(2).to_string())

fig3 = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r',
    title='Return Correlation Matrix — 2020-2024', aspect='auto')
fig3.update_layout(height=450, template='plotly_dark')

path3 = os.path.join(CHARTS_DIR, '03_correlation.html')
fig3.write_html(path3)
print(f"   Saved: {path3}")


# ============================================================
# SECTION 5: Chart 4 — RSI Signal Backtest
# ============================================================
print("\n[5/5] Backtesting RSI signal validity...")

df['future_5d_return'] = df['close'].shift(-5) / df['close'] - 1

bins   = [0, 30, 45, 55, 70, 100]
labels = ['< 30 (Oversold)', '30-45', '45-55', '55-70', '> 70 (Overbought)']
df['rsi_zone'] = pd.cut(df['rsi'], bins=bins, labels=labels)

zone_stats = df.groupby('rsi_zone', observed=True)['future_5d_return'].agg(
    win_rate=lambda x: (x > 0).mean(),
    avg_return='mean',
    count='count'
).reset_index()

print("\n   RSI Zone -> Win Rate (5-day forward):")
print(zone_stats.to_string(index=False))

colors_bar = ['#4CAF50' if w > 0.5 else '#F44336' for w in zone_stats['win_rate']]
fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=zone_stats['rsi_zone'].astype(str), y=zone_stats['win_rate'],
    marker_color=colors_bar,
    text=[f"{w:.1%}" for w in zone_stats['win_rate']],
    textposition='outside', name='Win Rate'
))
fig4.add_hline(y=0.5, line_dash='dash', line_color='white',
               annotation_text='50% baseline (random)')
fig4.update_layout(
    title=f'RSI Zone vs. 5-Day Win Rate — {FOCUS_SYMBOL}',
    xaxis_title='RSI Zone',
    yaxis_title='Win Rate (price up after 5 days)',
    yaxis_tickformat='.0%', template='plotly_dark', height=450
)

path4 = os.path.join(CHARTS_DIR, '04_rsi_signal_test.html')
fig4.write_html(path4)
print(f"   Saved: {path4}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("  DONE — Open these files in your browser:")
print("=" * 60)
for i, p in enumerate([path1, path2, path3, path4], 1):
    print(f"  {i}. {p}")
print("\n  Tip: Zoom, click legends, and hover for exact values.")
print("=" * 60)
