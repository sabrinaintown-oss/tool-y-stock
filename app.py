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
        
        # Attempt to get price
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
                st.metric("Days to Cover", f"{y_short_ratio}", delta="Source: Yahoo")
            else:
                st.metric("Days to Cover", "--", help="Yahoo Finance data missing.")

        # Show Shares Short if available
        if y_shares_short:
            st.caption(f"**Total Shares Short:** {y_shares_short:,}")

    except Exception as e:
        st.error(f"Could not load data for {ticker}. Please check the symbol.")

    # --- 2. Deep Dive Links ---
    st.write("")
    st.write("")
    
    # Logic: If data is missing (common for ETFs), show a helpful tip
    if not y_short_float:
        st.markdown("""
        <div class="info-box">
            <b>Data missing above?</b><br>
            Short interest data for ETFs (like SPY, QQQ) is often hidden or not calculated by standard free APIs.
            Use the <b>Fintel</b> link below for the most reliable data.
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🔗 Deep Dive: External Data Sources")
    st.caption("Click buttons below to open official data pages directly.")

    # Generate Smart Links
    url_fintel = f"https://fintel.io/ss/us/{ticker.lower()}"
    
    # MarketWatch URL logic
    is_common_etf = ticker in ['SPY', 'QQQ', 'IWM', 'TQQQ', 'SQQQ', 'ARKK', 'SMH']
    url_marketwatch = f"https://www.marketwatch.com/investing/fund/{ticker.lower()}" if is_common_etf else f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
    
    url_shortsqueeze = f"https://shortsqueeze.com/?symbol={ticker}"
    url_yahoo_stats = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"

    # Row 1 Buttons
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        st.link_button(f"👉 Open Fintel.io (Best for Data)", url_fintel, type="primary", use_container_width=
