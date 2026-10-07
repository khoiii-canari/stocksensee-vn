import logging
import pandas as pd
import ta

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    'rsi', 'rsi_oversold', 'rsi_overbought',
    'macd', 'macd_signal', 'macd_diff',
    'ma20', 'ma50', 'price_above_ma20', 'price_above_ma50', 'golden_cross',
    'bb_upper', 'bb_lower', 'bb_pct', 'bb_width',
    'volume_ma20', 'volume_ratio', 'high_volume',
    'daily_return', 'return_volatility_5d', 'return_volatility_20d',
    'price_change_5d', 'price_change_20d',
]

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Adding technical indicators.")
    df = df.copy()
    close  = df['close']
    high   = df['high']
    low    = df['low']
    volume = df['volume']

    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(close, window=14).rsi()
    df['rsi_oversold']  = (df['rsi'] < 30).astype(int)
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)

    # MACD
    macd = ta.trend.MACD(close)
    df['macd']        = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff']   = macd.macd_diff()

    # Moving Averages
    df['ma20'] = close.rolling(window=20).mean()
    df['ma50'] = close.rolling(window=50).mean()
    df['price_above_ma20'] = (close > df['ma20']).astype(int)
    df['price_above_ma50'] = (close > df['ma50']).astype(int)
    df['golden_cross']     = ((df['ma20'] > df['ma50']) &
                              (df['ma20'].shift(1) <= df['ma50'].shift(1))).astype(int)

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_pct']   = bb.bollinger_pband()
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['ma20']

    # Volume
    df['volume_ma20']  = volume.rolling(window=20).mean()
    df['volume_ratio'] = volume / df['volume_ma20']
    df['high_volume']  = (df['volume_ratio'] > 2).astype(int)

    # Additional Features
    df['daily_return'] = close.pct_change()
    df['return_volatility_5d'] = df['daily_return'].rolling(window=5).std()
    df['return_volatility_20d'] = df['daily_return'].rolling(window=20).std()
    df['price_change_5d'] = close.pct_change(periods=5)
    df['price_change_20d'] = close.pct_change(periods=20)

    # Only drop rows that have NaN because of the rolling windows at the beginning.
    df = df.dropna()
    return df

def add_target(df: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    logger.info(f"Adding target with horizon={horizon}.")
    df = df.copy()
    
    # Target: 1 if close price increases after `horizon` days, else 0
    future_close = df['close'].shift(-horizon)
    mask = future_close.notna()
    
    df = df[mask].copy()
    df['target'] = (future_close[mask] > df['close'][mask]).astype(int)
    
    return df
