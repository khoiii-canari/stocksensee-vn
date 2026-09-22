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
os.environ['VNSTOCK_TELEMETRY'] = 'off'   # tat quang cao / telemetry

import pandas as pd

# Danh sach ma co phieu mac dinh de phan tich
DEFAULT_SYMBOLS = ['VCB', 'FPT', 'VNM', 'HPG', 'VIC']
DEFAULT_START   = '2020-01-01'
DEFAULT_END     = '2024-12-31'
RAW_DATA_DIR    = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')


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
    from vnstock.api.quote import Quote
    print(f"[FETCH] {symbol} | {start} -> {end}")
    q = Quote(symbol=symbol, source='VCI')
    df = q.history(start=start, end=end, interval='1D')
    df['symbol'] = symbol
    print(f"   [OK] {symbol}: {len(df)} ngay giao dich")
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
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    result = {}

    for symbol in symbols:
        try:
            df = fetch_stock_data(symbol, start, end)
            result[symbol] = df

            if save_csv:
                path = os.path.join(RAW_DATA_DIR, f'{symbol}.csv')
                df.to_csv(path, index=False)
                print(f"   [SAVED] {path}")

        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")

    print(f"\n[DONE] Tai duoc {len(result)}/{len(symbols)} ma.")
    return result


def load_stock_from_csv(symbol: str) -> pd.DataFrame:
    """
    Load data da luu tu CSV thay vi goi API lai.
    Dung sau khi da fetch_multiple_stocks() mot lan roi.
    """
    path = os.path.join(RAW_DATA_DIR, f'{symbol}.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Chua co data cho {symbol}. Chay fetch_stock_data() truoc.")
    df = pd.read_csv(path, parse_dates=['time'])
    return df


if __name__ == '__main__':
    data = fetch_multiple_stocks()
    if 'VCB' in data:
        print("\n[PREVIEW] VCB (3 dong cuoi):")
        print(data['VCB'].tail(3).to_string())
