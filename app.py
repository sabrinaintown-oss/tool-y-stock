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
st.markdown("Quickly analyze Short Ratio and Short % of Float.")

# --- Input Area ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("Enter Ticker", value="SPY")
with col2:
    st.write("")
    st.write("")
    st.button("🚀 Analyze", type="primary")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # --- 1. Fetch Basic Data ---
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose')
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
                st.metric("Short % of Float", "--", help="Missing in Yahoo")
                
        with m3:
            if y_short_ratio:
                st.metric("Days to Cover", f"{y_short_ratio}", delta="Source: Yahoo")
            else:
                st.metric("Days to Cover", "--", help="Missing in Yahoo")

        if y_shares_short:
            st.caption(f"**Total Shares Short:** {y_shares_short:,}")

    except Exception:
        st.error("Error loading data.")

    # --- 2. Deep Dive Links ---
    st.write("")
    
    # Missing Data Warning
    if not y_short_float:
        st.info("Data missing above? Use the buttons below (Best for ETFs).")
    
    st.subheader("🔗 External Data Sources")

    # Generate URLs
    url_fintel = f"https://fintel.io/ss/us/{ticker.lower()}"
    
    # Logic for MarketWatch URL
    is_etf = ticker in ['SPY', 'QQQ', 'IWM', 'TQQQ', 'SQQQ', 'ARKK', 'SMH']
    if is_etf:
        url_mw = f"https://www.marketwatch.com/investing/fund/{ticker.lower()}"
    else:
        url_mw = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
    
    url_sq = f"https://shortsqueeze.com/?symbol={ticker}"
    url_yf = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"

    # --- BUTTONS (Formatted safely to prevent errors) ---
    r1_col1, r1_col2 = st.columns(2)
    
    with r1_col1:
        st.link_button(
            label="👉 Open Fintel.io (Best)", 
            url=url_fintel, 
            type="primary", 
            use_container_width=True
        )
        
    with r1_col2:
        st.link_button(
            label="👉 Open MarketWatch", 
            url=url_mw, 
            use_container_width=True
        )

    r2_col1, r2_col2 = st.columns(2)
    
    with r2_col1:
        st.link_button(
            label="👉 Open ShortSqueeze", 
            url=url_sq, 
            use_container_width=True
        )
        
    with r2_col2:
        st.link_button(
            label="👉 Yahoo Statistics", 
            url=url_yf, 
            use_container_width=True
        )

    # --- 3. Simple Chart ---
    st.divider()
    try:
        hist = stock.history(period="3m")
        if not hist.empty:
            st.line_chart(hist['Close'])
    except:
        pass
