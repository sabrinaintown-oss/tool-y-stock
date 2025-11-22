import streamlit as st
import yfinance as yf
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="工具Y - 终极指挥舱", page_icon="🚀", layout="centered")

# --- CSS 样式美化 ---
st.markdown("""
    <style>
    /* 调整按钮样式 */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 标题 ---
st.title("🚀 工具Y：做空数据指挥舱")
st.markdown("集成 Yahoo 实时行情，并提供 **ETF/个股** 深度做空数据的**一键直达通道**。")

# --- 输入区 ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入代码", value="SPY", placeholder="例如 SPY, TSLA, NVDA")
with col2:
    st.write("")
    st.write("")
    # 这里只是为了触发刷新，实际逻辑在下面
    st.button("🔍 查询", type="primary")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # --- 第一部分：Yahoo 基础数据 (最稳定) ---
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 价格获取逻辑
        price = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose')
        
        # Yahoo 的做空数据 (个股通常有，ETF通常无)
        y_short_float = info.get('shortPercentOfFloat')
        y_short_ratio = info.get('shortRatio')
        y_shares_short = info.get('sharesShort')
        
        st.divider()
        st.subheader(f"📊 {ticker} 基础概况 (Yahoo)")
        
        # 指标展示
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("当前价格", f"${price}" if price else "N/A")
        with m2:
            if y_short_float:
                st.metric("Short % (做空占比)", f"{y_short_float*100:.2f}%", delta="Yahoo数据")
            else:
                st.metric("Short % (做空占比)", "--", help="Yahoo 未提供此标的的比例数据")
        with m3:
            if y_short_ratio:
                st.metric("Short Ratio (天数)", f"{y_short_ratio}", delta="Yahoo数据")
            else:
                st.metric("Short Ratio (天数)", "--", help="Yahoo 未提供此标的的回补天数")

        # --- 第二部分：如果 Yahoo 没数据，或者想看更多 ---
        st.write("")
        st.info(f"💡 **提示：** 如果上方做空数据显示为 `--` (常见于 ETF)，请使用下方的 **指挥舱按钮** 查看深度数据。")
        
        st.subheader("🕵️ 深度数据传送门")
        
        # 生成外部链接
        url_finviz = f"https://finviz.com/quote.ashx?t={ticker}"
        # StockAnalysis 的 URL 需要小写
        url_sa_stock = f"https://stockanalysis.com/stocks/{ticker.lower()}/" 
        url_sa_etf = f"https://stockanalysis.com/etf/{ticker.lower()}/"
        url_shortsqueeze = f"https://shortsqueeze.com/?symbol={ticker}"
        
        # 布局按钮 - 第一排
        b1, b2 = st.columns(2)
        with b1:
            st.link_button(f"👉 Finviz (图表最全)", url_finviz, type="primary", use_container_width=True)
        with b2:
            # 这里的逻辑是引导用户去 Shortsqueeze.com，这是专门看做空的网站
            st.link_button(f"👉 ShortSqueeze.com (做空专用)", url_shortsqueeze, use_container_width=True)

        # 布局按钮 - 第二排
        b3, b4 = st.columns(2)
        with b3:
            # 判断是 ETF 还是 股票 (简单的链接跳转，让用户自己点)
            st.link_button(f"👉 StockAnalysis (ETF数据强)", url_sa_etf, help="如果是ETF点这里", use_container_width=True)
        with b4:
            st.link_button(f"👉 StockAnalysis (个股数据强)", url_sa_stock, help="如果是普通股票点这里", use_container_width=True)

        # --- 第三部分：图表 (辅助判断) ---
        st.write("---")
        st.caption("📉 价格走势 (辅助判断轧空趋势)")
        hist = stock.history(period="6m")
        if not hist.empty:
            st.line_chart(hist['Close'])
            
    except Exception as e:
        st.error(f"无法找到代码 {ticker}，请检查拼写。")

