import sys
from pathlib import Path
import logging
import pandas as pd
from typing import Dict, Any, Tuple
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEFAULT_SYMBOLS
from data.fetcher import load_stock_from_csv
from data.features import add_technical_indicators
from models.evaluate import load_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_model_and_features() -> Tuple[XGBClassifier, list]:
    """Alias for load_model from evaluate.py for clear intent."""
    return load_model()

def predict_stock(symbol: str, model: XGBClassifier = None, feature_names: list = None) -> Dict[str, Any]:
    """Full inference pipeline for a single stock returning latest prediction."""
    try:
        if model is None or feature_names is None:
            model, feature_names = load_model_and_features()
            
        df_raw = load_stock_from_csv(symbol)
        if df_raw.empty:
            raise ValueError(f"No data available for {symbol}")
            
        df = add_technical_indicators(df_raw)
        if df.empty:
            raise ValueError(f"No data left after adding indicators for {symbol}")
            
        latest_row = df.iloc[[-1]].copy()
        
        X_latest = latest_row[feature_names]
        
        prob = float(model.predict_proba(X_latest)[0][1])
        pred = 'UP' if prob >= 0.5 else 'DOWN'
        
        date = str(latest_row['time'].values[0]) if 'time' in latest_row else 'Unknown'
        latest_price = float(latest_row['close'].values[0]) if 'close' in latest_row else 0.0
        
        features_used = {feat: float(X_latest.iloc[0][feat]) for feat in feature_names}
        
        return {
            'symbol': symbol,
            'date': date,
            'prediction': pred,
            'probability': prob,
            'latest_price': latest_price,
            'features_used': features_used
        }
    except Exception as e:
        logger.error(f"Error predicting {symbol}: {e}", exc_info=True)
        raise

def predict_all_stocks() -> Dict[str, Dict[str, Any]]:
    """Run predict_stock for all default symbols."""
    model, feature_names = load_model_and_features()
    results = {}
    
    for symbol in DEFAULT_SYMBOLS:
        try:
            results[symbol] = predict_stock(symbol, model, feature_names)
        except Exception as e:
            logger.error(f"Failed to predict for {symbol}: {e}")
            
    return results

if __name__ == '__main__':
    try:
        logger.info("Running inference for all default symbols...")
        results = predict_all_stocks()
        
        print("\n--- Latest Stock Predictions ---")
        for sym, res in results.items():
            print(f"{sym} ({res['date']}) - Price: {res['latest_price']:.2f} - "
                  f"Prediction: {res['prediction']} (Prob: {res['probability']:.2%})")
        print("--------------------------------")
    except Exception as e:
        logger.error(f"Prediction script failed: {e}")
