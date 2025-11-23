import streamlit as st
import yfinance as yf

# --- Page Configuration ---
st.set_page_config(
    page_title="Short Interest Command Center",
    page_icon="📉",
    layout="centered"
)

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #e6fffa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00bfa5;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("📉 Short Interest Command Center")
st.markdown("""
    Quickly analyze **Short Ratio** and **Short % of Float**.  
    *Includes direct links to Fintel & MarketWatch for hard-to-find ETF data.*
""")

# --- Input Area ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("Enter Ticker Symbol", value="SPY", placeholder="e.g. SPY, TSLA, GME")
with col2:
    st.write("")
    st.write("")
    st.button("🚀 Analyze", type="primary")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # --- 1. Fetch Basic Data from Yahoo Finance ---
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Attempt to get price (different keys for stocks vs ETFs)
        price = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose')
        
        # Attempt to get Short Data
        y_short_float = info.get('shortPercentOfFloat')
        y_short_ratio = info.get('shortRatio')
        y_shares_short = info.get('sharesShort')
        
        st.divider()
        st.subheader(f"📌 Overview: {ticker}")
        
        # Display Key Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Current Price", f"${price}" if price else "--")
        
        with m2:
            if y_short_float:
                st.metric("Short % of Float", f"{y_short_float*100:.2f}%", delta="Source: Yahoo")
            else:
                st.metric("Short % of Float", "--", help="Yahoo Finance often does not provide this percentage for ETFs.")
                
        with m3:
            if y_short_ratio:
                st.
