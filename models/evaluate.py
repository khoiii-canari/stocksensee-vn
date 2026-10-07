import sys
from pathlib import Path
import logging
import joblib
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, FEATURE_COLUMNS, TARGET_COLUMN, HORIZON
from data.fetcher import load_stock_from_csv
from data.features import add_technical_indicators, add_target

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_model() -> Tuple[XGBClassifier, list]:
    """Load the trained XGBoost model and feature names."""
    model_path = Path(MODEL_DIR) / 'xgb_model.pkl'
    features_path = Path(MODEL_DIR) / 'feature_names.json'
    
    if not model_path.exists() or not features_path.exists():
        raise FileNotFoundError(f"Model or features file not found in {MODEL_DIR}")
        
    model = joblib.load(model_path)
    with open(features_path, 'r') as f:
        feature_names = json.load(f)
        
    return model, feature_names

def evaluate_model(model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """Evaluate model and return metrics dict."""
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    return {
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1': float(f1),
        'confusion_matrix': cm,
        'classification_report': report
    }

def plot_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray) -> go.Figure:
    """Return Plotly confusion matrix figure."""
    cm = confusion_matrix(y_true, y_pred)
    
    fig = go.Figure(data=go.Heatmap(
        z=cm, x=['Predicted Down', 'Predicted Up'], y=['Actual Down', 'Actual Up'],
        text=cm, texttemplate="%{text}",
        colorscale='Blues'
    ))
    fig.update_layout(title="Confusion Matrix", xaxis_title="Predicted Label", yaxis_title="True Label")
    return fig

def plot_feature_importance(model: XGBClassifier, feature_names: list) -> go.Figure:
    """Return Plotly feature importance bar chart (top 15)."""
    importance = model.feature_importances_
    df_imp = pd.DataFrame({'feature': feature_names, 'importance': importance})
    df_imp = df_imp.sort_values('importance', ascending=True).tail(15)
    
    fig = px.bar(df_imp, x='importance', y='feature', orientation='h',
                 title='Top 15 Feature Importances')
    return fig

def generate_evaluation_report(symbol: str) -> Dict[str, Any]:
    """Generate full evaluation report for a specific symbol."""
    try:
        model, feature_names = load_model()
        
        # Load and process data
        df_raw = load_stock_from_csv(symbol)
        df = add_technical_indicators(df_raw)
        df = add_target(df, horizon=HORIZON)
        
        X = df[feature_names]
        y = df[TARGET_COLUMN]
        
        metrics = evaluate_model(model, X, y)
        y_pred = model.predict(X)
        
        fig_cm = plot_confusion_matrix(y, y_pred)
        fig_imp = plot_feature_importance(model, feature_names)
        
        return {
            'symbol': symbol,
            'metrics': metrics,
            'fig_confusion_matrix': fig_cm,
            'fig_feature_importance': fig_imp
        }
    except Exception as e:
        logger.error(f"Error evaluating {symbol}: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        report = generate_evaluation_report('VCB')
        print("Evaluation Report for VCB:")
        print(f"Accuracy: {report['metrics']['accuracy']:.4f}")
        print(f"F1 Score: {report['metrics']['f1']:.4f}")
        print("Detailed Classification Report:")
        print(json.dumps(report['metrics']['classification_report'], indent=2))
    except Exception as e:
        logger.error(f"Execution failed: {e}")
