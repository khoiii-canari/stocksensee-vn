import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to sys path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import project modules
try:
    from data.fetcher import load_stock_from_csv, DEFAULT_SYMBOLS
    from data.features import add_technical_indicators, FEATURE_COLUMNS
    from models.predict import predict_stock, load_model_and_features
    from models.evaluate import load_model, evaluate_model, plot_confusion_matrix, plot_feature_importance
    from models.explain import get_shap_values, explain_prediction, plot_shap_bar
    from config import DEFAULT_SYMBOLS, FEATURE_COLUMNS, MODEL_DIR, HORIZON
    MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import necessary modules: {e}")
    MODULES_AVAILABLE = False


# Theme colors
COLOR_UP = '#4CAF50'
COLOR_DOWN = '#F44336'
COLOR_BLUE = '#2196F3'
COLOR_ORANGE = '#FF9800'
COLOR_BG = '#0e1117'

st.set_page_config(
    page_title='StockSense VN',
    page_icon='📈',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Caching Data Loading
@st.cache_data(ttl=3600)
def get_data(symbol):
    if not MODULES_AVAILABLE:
        return None
    df = load_stock_from_csv(symbol)
    if df is not None and not df.empty:
        df = add_technical_indicators(df)
    return df

@st.cache_resource
def get_model():
    if not MODULES_AVAILABLE:
        return None, None
    try:
        model, feature_names = load_model_and_features()
        return model, feature_names
    except Exception as e:
        return None, None

@st.cache_data
def get_metrics():
    metrics_path = Path(__file__).parent.parent / "models" / "saved" / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def create_candlestick_chart(df):
    fig = go.Figure()
    x_axis = df['time'] if 'time' in df.columns else df.index
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=x_axis,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color=COLOR_UP,
        decreasing_line_color=COLOR_DOWN
    ))
    
    # Bollinger Bands
    if 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['bb_upper'], line=dict(color='rgba(250, 250, 250, 0.2)', width=1), name='BB Upper'))
        fig.add_trace(go.Scatter(x=x_axis, y=df['bb_lower'], line=dict(color='rgba(250, 250, 250, 0.2)', width=1), fill='tonexty', fillcolor='rgba(250, 250, 250, 0.05)', name='BB Lower'))
    
    # Moving Averages
    if 'ma20' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['ma20'], line=dict(color=COLOR_ORANGE, width=1.5), name='MA20'))
    if 'ma50' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['ma50'], line=dict(color=COLOR_BLUE, width=1.5), name='MA50'))
        
    fig.update_layout(
        title='Price History & Bollinger Bands',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=0),
        height=500
    )
    return fig

def create_rsi_chart(df):
    fig = go.Figure()
    x_axis = df['time'] if 'time' in df.columns else df.index
    if 'rsi' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['rsi'], line=dict(color='#E0E0E0', width=1.5), name='RSI'))
        fig.add_hline(y=70, line_dash="dash", line_color=COLOR_DOWN)
        fig.add_hline(y=30, line_dash="dash", line_color=COLOR_UP)
    fig.update_layout(title='RSI (14)', template='plotly_dark', height=250, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def create_macd_chart(df):
    fig = go.Figure()
    x_axis = df['time'] if 'time' in df.columns else df.index
    if 'macd' in df.columns and 'macd_signal' in df.columns and 'macd_diff' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['macd'], line=dict(color=COLOR_BLUE, width=1.5), name='MACD'))
        fig.add_trace(go.Scatter(x=x_axis, y=df['macd_signal'], line=dict(color=COLOR_ORANGE, width=1.5), name='Signal'))
        colors = [COLOR_UP if val >= 0 else COLOR_DOWN for val in df['macd_diff']]
        fig.add_trace(go.Bar(x=x_axis, y=df['macd_diff'], marker_color=colors, name='Histogram'))
    fig.update_layout(title='MACD', template='plotly_dark', height=250, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def create_volume_chart(df):
    fig = go.Figure()
    x_axis = df['time'] if 'time' in df.columns else df.index
    colors = [COLOR_UP if row['close'] >= row['open'] else COLOR_DOWN for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=x_axis, y=df['volume'], marker_color=colors, name='Volume'))
    if 'volume_ma20' in df.columns:
        fig.add_trace(go.Scatter(x=x_axis, y=df['volume_ma20'], line=dict(color=COLOR_ORANGE, width=1.5), name='Volume MA20'))
    fig.update_layout(title='Volume', template='plotly_dark', height=250, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def page_technical_analysis(symbol, df):
    st.header(f"📊 Technical Analysis: {symbol}")
    
    if df is None or df.empty:
        st.warning("No data available for this symbol.")
        return

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        price_change = latest['close'] - prev['close']
        pct_change = (price_change / prev['close']) * 100
        st.metric("Current Price", f"{latest['close']:,.0f}", f"{pct_change:+.2f}%")
    with c2:
        vol_change = (latest['volume'] - prev['volume']) / prev['volume'] * 100
        st.metric("Volume", f"{latest['volume']:,.0f}", f"{vol_change:+.2f}%")
    with c3:
        rsi_val = latest.get('rsi', 0)
        rsi_delta = rsi_val - prev.get('rsi', 0)
        st.metric("RSI (14)", f"{rsi_val:.1f}", f"{rsi_delta:+.1f}")
    with c4:
        vol_ratio = latest.get('volume_ratio', 0)
        st.metric("Volume Ratio", f"{vol_ratio:.2f}x", help="Current volume vs 20-day average")

    st.plotly_chart(create_candlestick_chart(df), use_container_width=True)
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.plotly_chart(create_rsi_chart(df), use_container_width=True)
    with sc2:
        st.plotly_chart(create_macd_chart(df), use_container_width=True)
    with sc3:
        st.plotly_chart(create_volume_chart(df), use_container_width=True)
        
    st.subheader("Recent Data (Last 10 Days)")
    st.dataframe(df.tail(10)[['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'volume_ratio']].sort_index(ascending=False), use_container_width=True)

def page_ai_prediction(symbol, df):
    st.header("🤖 AI Prediction")
    
    model, feature_names = get_model()
    if model is None or feature_names is None:
        st.warning("⚠️ Model is not trained yet. Please run the training pipeline first.")
        return
        
    try:
        pred_res = predict_stock(symbol)
        if pred_res is None:
            st.error("Could not generate prediction.")
            return
            
        prediction = pred_res['prediction']
        probability = pred_res['probability']
        latest_price = pred_res['latest_price']
        
        color = COLOR_UP if prediction == 'UP' else COLOR_DOWN
        emoji = "📈" if prediction == 'UP' else "📉"
        
        st.markdown(f"""
        <div style="background-color: {color}20; padding: 2rem; border-radius: 10px; text-align: center; border: 1px solid {color}50;">
            <h2 style="margin:0;">Predicted Next Move: <span style="color: {color};">{prediction} {emoji}</span></h2>
            <p style="font-size: 1.2rem; margin-top: 10px;">Confidence: <strong>{probability:.1%}</strong></p>
            <p>Based on latest price: {latest_price:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Key Current Metrics")
        
        features_used = pred_res['features_used']
        
        # Display top features
        cols = st.columns(4)
        show_features = ['rsi', 'macd_diff', 'volume_ratio', 'price_change_5d']
        
        for i, f in enumerate(show_features):
            with cols[i % 4]:
                if f in features_used:
                    val = features_used[f]
                    st.metric(f.upper().replace('_', ' '), f"{val:.3f}")
        
        st.info("ℹ️ **Disclaimer**: AI predictions are based on historical patterns and do not guarantee future performance. Use for informational purposes only.")
        
        with st.expander("View All Feature Values"):
            st.json(features_used)
            
    except Exception as e:
        st.error(f"Error making prediction: {e}")

def page_shap_explanation(symbol, df):
    st.header("🔍 SHAP Explanation")
    
    model, feature_names = get_model()
    if model is None or feature_names is None:
        st.warning("⚠️ Model is not trained yet. Please run the training pipeline first.")
        return
        
    try:
        latest_row = df.iloc[-1:]
        X_row = latest_row[feature_names]
        
        explanation = explain_prediction(model, X_row, feature_names)
        
        pred_int = explanation['prediction']
        pred_label = 'UP' if pred_int == 1 else 'DOWN'
        color = COLOR_UP if pred_int == 1 else COLOR_DOWN
        emoji = "📈" if pred_int == 1 else "📉"
        
        st.subheader(f"Why did the model predict {pred_label} {emoji}?")
        st.markdown(f"**Confidence:** {explanation['probability']:.1%}")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"### 🟢 Top Positive Factors (Pushing UP)")
            for factor in explanation['top_positive_factors'][:5]:
                st.markdown(f"- **{factor['feature']}**: {factor['feature_value']:.2f} *(Impact: +{factor['shap_value']:.3f})*")
                
        with c2:
            st.markdown(f"### 🔴 Top Negative Factors (Pushing DOWN)")
            for factor in explanation['top_negative_factors'][:5]:
                st.markdown(f"- **{factor['feature']}**: {factor['feature_value']:.2f} *(Impact: {factor['shap_value']:.3f})*")
                
        st.markdown("---")
        st.subheader("Feature Impact Details")
        st.info("The values below show the exact SHAP (SHapley Additive exPlanations) values for this specific prediction.")
        
        # Simple plain language explanation
        top_pos = explanation['top_positive_factors'][0] if explanation['top_positive_factors'] else None
        top_neg = explanation['top_negative_factors'][0] if explanation['top_negative_factors'] else None
        
        if top_pos and top_neg:
            strongest = top_pos if top_pos['shap_value'] > abs(top_neg['shap_value']) else top_neg
            direction = "upward" if strongest == top_pos else "downward"
            st.write(f"The strongest signal for this {direction} movement is **{strongest['feature']}** with a value of {strongest['feature_value']:.2f}.")

        # Global feature importance using SHAP bar chart
        try:
            shap_values = get_shap_values(model, X_row)
            fig = plot_shap_bar(shap_values, feature_names)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.write(f"Could not generate SHAP plot: {e}")
            
    except Exception as e:
        st.error(f"Error generating explanation: {e}")

def page_model_performance():
    st.header("📋 Model Performance")
    
    metrics = get_metrics()
    if metrics:
        st.subheader("Latest Backtest Results")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with c2:
            st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with c3:
            st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with c4:
            st.metric("F1 Score", f"{metrics.get('f1', 0):.2%}")
            
        st.info("ℹ️ Validated using TimeSeriesSplit to prevent lookahead bias.")
        
        with st.expander("Raw Metrics JSON"):
            st.json(metrics)
    else:
        st.warning("⚠️ No metrics found. Run the training pipeline to generate evaluation metrics.")
        
    model, feature_names = get_model()
    if model:
        st.subheader("Global Feature Importance (XGBoost Weight)")
        try:
            fig = plot_feature_importance(model, feature_names)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not plot feature importance: {e}")


def main():
    if not MODULES_AVAILABLE:
        st.stop()

    with st.sidebar:
        st.title("StockSense 📈")
        st.markdown("*AI-powered Vietnamese Stock Analysis*")
        st.markdown("---")
        
        symbol = st.selectbox("Select Stock Symbol", DEFAULT_SYMBOLS)
        
        page = st.radio("Navigation", 
            ['📊 Technical Analysis', '🤖 AI Prediction', '🔍 SHAP Explanation', '📋 Model Performance']
        )
        
        st.markdown("---")
        st.markdown("""
        <div style='font-size: 0.8rem; color: #888;'>
        <b>Disclaimer:</b><br>
        Predictions and analysis are for informational purposes only. Do not make investment decisions solely based on this dashboard.
        </div>
        """, unsafe_allow_html=True)
        
    df = get_data(symbol)
    
    if page == '📊 Technical Analysis':
        page_technical_analysis(symbol, df)
    elif page == '🤖 AI Prediction':
        page_ai_prediction(symbol, df)
    elif page == '🔍 SHAP Explanation':
        page_shap_explanation(symbol, df)
    elif page == '📋 Model Performance':
        page_model_performance()

if __name__ == "__main__":
    main()
