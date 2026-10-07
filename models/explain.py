import sys
from pathlib import Path
import logging
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from xgboost import XGBClassifier
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import load_stock_from_csv
from data.features import add_technical_indicators
from models.evaluate import load_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_shap_values(model: XGBClassifier, X: pd.DataFrame) -> shap.Explanation:
    """Compute SHAP values using TreeExplainer."""
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X)
        return shap_values
    except Exception as e:
        logger.error(f"Error computing SHAP values: {e}")
        raise

def plot_shap_waterfall(shap_values: shap.Explanation, idx: int, feature_names: List[str]) -> plt.Figure:
    """Plot SHAP waterfall for a single prediction."""
    try:
        fig, ax = plt.subplots()
        shap.plots.waterfall(shap_values[idx], show=False)
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error generating waterfall plot: {e}")
        raise

def plot_shap_beeswarm(shap_values: shap.Explanation, X: pd.DataFrame, feature_names: List[str]) -> plt.Figure:
    """Plot SHAP beeswarm/summary plot for dataset."""
    try:
        fig, ax = plt.subplots()
        shap.plots.beeswarm(shap_values, show=False)
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error generating beeswarm plot: {e}")
        raise

def plot_shap_bar(shap_values: shap.Explanation, feature_names: List[str]) -> go.Figure:
    """Plot SHAP bar chart (mean absolute SHAP) in Plotly."""
    try:
        # For binary classification, shap_values.values might be 2D
        vals = shap_values.values
        if len(vals.shape) == 3:
            vals = vals[:, :, 1] # Take positive class
            
        mean_abs_shap = np.abs(vals).mean(axis=0)
        df_shap = pd.DataFrame({
            'feature': feature_names,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=True)
        
        fig = go.Figure(go.Bar(
            x=df_shap['mean_abs_shap'],
            y=df_shap['feature'],
            orientation='h'
        ))
        fig.update_layout(title="Mean Absolute SHAP Value (Feature Impact)")
        return fig
    except Exception as e:
        logger.error(f"Error generating SHAP bar plot: {e}")
        raise

def explain_prediction(model: XGBClassifier, X_row: pd.DataFrame, feature_names: List[str]) -> Dict[str, Any]:
    """Explain a single prediction returning top factors."""
    try:
        shap_values = get_shap_values(model, X_row)
        
        # Get base value and values
        base_value = shap_values[0].base_values
        if isinstance(base_value, np.ndarray):
            base_value = base_value[0]
            
        values = shap_values[0].values
        if len(values.shape) > 1:
            values = values[:, 1]
            
        # Sigmoid to get probability
        logit = base_value + np.sum(values)
        prob = 1 / (1 + np.exp(-logit))
        prediction = 1 if prob >= 0.5 else 0
        
        # Organize factors
        factors = []
        for i, feat in enumerate(feature_names):
            factors.append({
                'feature': feat,
                'shap_value': float(values[i]),
                'feature_value': float(X_row.iloc[0][feat])
            })
            
        factors.sort(key=lambda x: x['shap_value'], reverse=True)
        
        positive_factors = [f for f in factors if f['shap_value'] > 0]
        negative_factors = [f for f in factors if f['shap_value'] < 0]
        negative_factors.sort(key=lambda x: x['shap_value']) # Most negative first
        
        return {
            'prediction': prediction,
            'probability': float(prob),
            'top_positive_factors': positive_factors[:5],
            'top_negative_factors': negative_factors[:5]
        }
    except Exception as e:
        logger.error(f"Error explaining prediction: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        model, feature_names = load_model()
        df_raw = load_stock_from_csv('VCB')
        df = add_technical_indicators(df_raw)
        X = df[feature_names]
        
        # Explain latest row
        latest_row = X.iloc[[-1]]
        explanation = explain_prediction(model, latest_row, feature_names)
        print("Prediction Explanation for latest VCB data:")
        print(f"Prob: {explanation['probability']:.4f}")
        print("Top Positive:")
        for f in explanation['top_positive_factors']:
            print(f"  {f['feature']}: {f['shap_value']:.4f}")
    except Exception as e:
        logger.error(f"Execution failed: {e}")
