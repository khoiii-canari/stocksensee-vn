from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODEL_DIR = PROJECT_ROOT / 'models' / 'saved'
CHARTS_DIR = PROJECT_ROOT / 'notebooks' / 'charts'

# Stock config
DEFAULT_SYMBOLS = ['VCB', 'FPT', 'VNM', 'HPG', 'VIC']
DEFAULT_START = '2020-01-01'
DEFAULT_END = '2024-12-31'

# Model config
HORIZON = 5  # predict 5 days ahead
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_SPLITS = 5  # TimeSeriesSplit folds

# Feature columns (all technical indicators)
FEATURE_COLUMNS = [
    'rsi', 'rsi_oversold', 'rsi_overbought',
    'macd', 'macd_signal', 'macd_diff',
    'ma20', 'ma50', 'price_above_ma20', 'price_above_ma50', 'golden_cross',
    'bb_upper', 'bb_lower', 'bb_pct', 'bb_width',
    'volume_ma20', 'volume_ratio', 'high_volume',
    'daily_return', 'return_volatility_5d', 'return_volatility_20d',
    'price_change_5d', 'price_change_20d',
]
TARGET_COLUMN = 'target'
