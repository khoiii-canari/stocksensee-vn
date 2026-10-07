import sys
from pathlib import Path
import logging
import json
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import load_stock_from_csv
from data.features import add_technical_indicators, add_target
from config import (
    FEATURE_COLUMNS, TARGET_COLUMN, DEFAULT_SYMBOLS,
    MODEL_DIR, PROCESSED_DATA_DIR, N_SPLITS, RANDOM_STATE, HORIZON
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_prepare_data(symbols: List[str]) -> pd.DataFrame:
    """Load and prepare data for multiple symbols, combined into one dataset."""
    logger.info(f"Loading data for symbols: {symbols}")
    dfs = []
    for symbol in symbols:
        try:
            df_raw = load_stock_from_csv(symbol)
            if df_raw.empty:
                logger.warning(f"No data for {symbol}")
                continue
                
            df = add_technical_indicators(df_raw)
            df = add_target(df, horizon=HORIZON)
            df['symbol'] = symbol  # Keep track of symbol
            dfs.append(df)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            
    if not dfs:
        raise ValueError("No data loaded for any symbol.")
        
    combined_df = pd.concat(dfs, ignore_index=True)
    # Sort by time to preserve temporal order
    if 'time' in combined_df.columns:
        combined_df = combined_df.sort_values('time').reset_index(drop=True)
        
    logger.info(f"Combined data shape: {combined_df.shape}")
    return combined_df

def train_model() -> None:
    """Train the XGBoost model using TimeSeriesSplit and save artifacts."""
    try:
        # Create output directories
        Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
        Path(PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
        
        # Load data
        df = load_and_prepare_data(DEFAULT_SYMBOLS)
        
        # Save processed data
        processed_data_path = Path(PROCESSED_DATA_DIR) / 'train_data.csv'
        df.to_csv(processed_data_path, index=False)
        logger.info(f"Saved processed data to {processed_data_path}")
        
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]
        
        # Calculate scale_pos_weight for class imbalance
        neg_count = (y == 0).sum()
        pos_count = (y == 1).sum()
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        # Initialize model
        model = XGBClassifier(
            max_depth=6,
            learning_rate=0.1,
            n_estimators=200,
            scale_pos_weight=scale_pos_weight,
            eval_metric='logloss',
            random_state=RANDOM_STATE
        )
        
        # TimeSeries cross-validation
        tscv = TimeSeriesSplit(n_splits=N_SPLITS)
        
        fold_metrics = []
        logger.info(f"Starting {N_SPLITS}-fold TimeSeries CV")
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            
            acc = float(accuracy_score(y_val, y_pred))
            prec = float(precision_score(y_val, y_pred, zero_division=0))
            rec = float(recall_score(y_val, y_pred, zero_division=0))
            f1 = float(f1_score(y_val, y_pred, zero_division=0))
            
            metrics = {'fold': fold + 1, 'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}
            fold_metrics.append(metrics)
            logger.info(f"Fold {fold + 1} Metrics: {metrics}")
            
        # Compute mean metrics
        mean_metrics = {
            'accuracy': float(np.mean([m['accuracy'] for m in fold_metrics])),
            'precision': float(np.mean([m['precision'] for m in fold_metrics])),
            'recall': float(np.mean([m['recall'] for m in fold_metrics])),
            'f1': float(np.mean([m['f1'] for m in fold_metrics])),
            'folds': fold_metrics
        }
        logger.info(f"Mean CV Metrics: {mean_metrics}")
        
        # Train final model on ALL data
        logger.info("Training final model on all data")
        model.fit(X, y)
        
        # Save model and artifacts
        model_path = Path(MODEL_DIR) / 'xgb_model.pkl'
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")
        
        features_path = Path(MODEL_DIR) / 'feature_names.json'
        with open(features_path, 'w') as f:
            json.dump(FEATURE_COLUMNS, f)
            
        metrics_path = Path(MODEL_DIR) / 'metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(mean_metrics, f, indent=4)
            
        logger.info("Training pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    train_model()
