"""
data/fetcher.py
---------------
Lay du lieu OHLCV tu vnstock API.

Cach dung:
    from data.fetcher import fetch_stock_data, fetch_multiple_stocks

    df = fetch_stock_data('VCB', '2020-01-01', '2024-12-31')
    all_data = fetch_multiple_stocks(['VCB', 'FPT', 'VNM'])
"""

import os
import logging
from pathlib import Path
import pandas as pd

# Try to import vnstock, catch error if not installed
try:
    from vnstock.api.quote import Quote
except ImportError:
    Quote = None

from config import DEFAULT_SYMBOLS, DEFAULT_START, DEFAULT_END, RAW_DATA_DIR

os.environ['VNSTOCK_TELEMETRY'] = 'off'   # tat quang cao / telemetry

logger = logging.getLogger(__name__)


def fetch_stock_data(symbol: str, start: str = DEFAULT_START, end: str = DEFAULT_END) -> pd.DataFrame:
    """
    Lay du lieu gia lich su (OHLCV) cua 1 ma co phieu.

    Args:
        symbol : Ma co phieu, vi du 'VCB', 'FPT'
        start  : Ngay bat dau, dinh dang 'YYYY-MM-DD'
        end    : Ngay ket thuc, dinh dang 'YYYY-MM-DD'

    Returns:
        DataFrame voi cot: time, open, high, low, close, volume
    """
    if Quote is None:
        raise ImportError("Please install vnstock to fetch data via API.")
        
    logger.info(f"[FETCH] {symbol} | {start} -> {end}")
    q = Quote(symbol=symbol, source='VCI')
    df = q.history(start=start, end=end, interval='1D')
    df['symbol'] = symbol
    logger.info(f"   [OK] {symbol}: {len(df)} ngay giao dich")
    return df


def fetch_multiple_stocks(
    symbols: list = DEFAULT_SYMBOLS,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    save_csv: bool = True
) -> dict:
    """
    Lay data cho nhieu ma, tuy chon luu ra CSV.

    Returns:
        dict { 'VCB': DataFrame, 'FPT': DataFrame, ... }
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    result = {}

    for symbol in symbols:
        try:
            df = fetch_stock_data(symbol, start, end)
            result[symbol] = df

            if save_csv:
                path = RAW_DATA_DIR / f'{symbol}.csv'
                df.to_csv(path, index=False)
                logger.info(f"   [SAVED] {path}")

        except Exception as e:
            logger.error(f"   [ERROR] {symbol}: {e}")

    logger.info(f"\n[DONE] Tai duoc {len(result)}/{len(symbols)} ma.")
    return result


def load_stock_from_csv(symbol: str) -> pd.DataFrame:
    """
    Load data da luu tu CSV thay vi goi API lai.
    Dung sau khi da fetch_multiple_stocks() mot lan roi.
    """
    path = RAW_DATA_DIR / f'{symbol}.csv'
    if not path.exists():
        raise FileNotFoundError(f"Chua co data cho {symbol}. Chay fetch_stock_data() truoc.")
    df = pd.read_csv(path, parse_dates=['time'])
    return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = fetch_multiple_stocks()
    if 'VCB' in data:
        logger.info("\n[PREVIEW] VCB (3 dong cuoi):")
        logger.info("\n" + data['VCB'].tail(3).to_string())
