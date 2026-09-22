"""
data/features.py
----------------
Tính toán Technical Indicators từ dữ liệu OHLCV.

Mỗi indicator có comment giải thích ý nghĩa tài chính.
Bạn Kinh tế có thể đề xuất thêm/bỏ indicator ở đây.

Cách dùng:
    from data.features import add_technical_indicators

    df_raw = load_stock_from_csv('VCB')
    df     = add_technical_indicators(df_raw)
"""

import pandas as pd
import ta


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm các technical indicators vào DataFrame.

    Input : DataFrame với cột close, high, low, volume
    Output: DataFrame gốc + ~15 cột mới
    """
    df = df.copy()
    close  = df['close']
    high   = df['high']
    low    = df['low']
    volume = df['volume']

    # ── MOMENTUM ──────────────────────────────────────────────────────────────
    # RSI (Relative Strength Index)
    # Ý nghĩa: Đo tốc độ và độ lớn của thay đổi giá.
    # RSI < 30 → "oversold" (bị bán quá mức, có thể bật lên)
    # RSI > 70 → "overbought" (bị mua quá mức, có thể điều chỉnh xuống)
    df['rsi'] = ta.momentum.RSIIndicator(close, window=14).rsi()
    df['rsi_oversold']  = (df['rsi'] < 30).astype(int)  # 1 nếu oversold
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int) # 1 nếu overbought

    # ── TREND ─────────────────────────────────────────────────────────────────
    # MACD (Moving Average Convergence Divergence)
    # Ý nghĩa: Đo momentum của xu hướng.
    # macd_diff > 0 → bullish (đà tăng)
    # macd_diff < 0 → bearish (đà giảm)
    # Giao cắt 0 → tín hiệu đảo chiều
    macd = ta.trend.MACD(close)
    df['macd']        = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff']   = macd.macd_diff()  # histogram

    # Moving Averages (Đường trung bình động)
    # Ý nghĩa: Làm mượt nhiễu ngắn hạn, xác định xu hướng dài hạn.
    # Giá > MA20 → ngắn hạn tích cực
    # Giá > MA50 → trung hạn tích cực
    # MA20 cắt MA50 từ dưới lên → "golden cross" (tín hiệu mua mạnh)
    df['ma20'] = close.rolling(window=20).mean()
    df['ma50'] = close.rolling(window=50).mean()
    df['price_above_ma20'] = (close > df['ma20']).astype(int)
    df['price_above_ma50'] = (close > df['ma50']).astype(int)
    df['golden_cross']     = ((df['ma20'] > df['ma50']) &
                              (df['ma20'].shift(1) <= df['ma50'].shift(1))).astype(int)

    # ── VOLATILITY ────────────────────────────────────────────────────────────
    # Bollinger Bands
    # Ý nghĩa: Đo độ biến động. Giá chạm lower band thường = cơ hội mua.
    # bb_pct = 0 → giá ở lower band (có thể oversold)
    # bb_pct = 1 → giá ở upper band (có thể overbought)
    bb = ta.volatility.BollingerBands(close, window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_pct']   = bb.bollinger_pband()  # vị trí trong dải (0→1)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['ma20']  # độ rộng dải

    # ── VOLUME ────────────────────────────────────────────────────────────────
    # Ý nghĩa: Volume tăng đột biến + giá tăng = tín hiệu mạnh (có tiền lớn vào)
    # Volume tăng đột biến + giá giảm = cảnh báo (bán tháo)
    df['volume_ma20']  = volume.rolling(window=20).mean()
    df['volume_ratio'] = volume / df['volume_ma20']  # > 2 là đột biến
    df['high_volume']  = (df['volume_ratio'] > 2).astype(int)

    # ── TARGET VARIABLE ───────────────────────────────────────────────────────
    # Đây là thứ model sẽ cố dự đoán:
    # 1 = giá 5 ngày sau CAO HƠN hôm nay (nên mua)
    # 0 = giá 5 ngày sau THẤP HƠN hôm nay (không nên mua)
    df['target'] = (close.shift(-5) > close).astype(int)

    # Bỏ các hàng bị NaN do rolling windows
    df = df.dropna()
    print(f"✅ Feature engineering xong: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


if __name__ == '__main__':
    # Test thử
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from data.fetcher import load_stock_from_csv

    df_raw = load_stock_from_csv('VCB')
    df     = add_technical_indicators(df_raw)
    print(df[['close', 'rsi', 'macd_diff', 'bb_pct', 'volume_ratio', 'target']].tail(5))
