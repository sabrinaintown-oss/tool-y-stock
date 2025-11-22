import streamlit as st
import yfinance as yf

# --- 页面配置 ---
st.set_page_config(page_title="工具Y - 免费数据导航", page_icon="🧭", layout="centered")

# --- 样式 ---
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00a8e8;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧭 工具Y：做空数据导航仪")
st.markdown("由于云服务器IP限制，自动抓取不稳定。本工具提供**最精准的免费数据源直达通道**。")

# --- 输入 ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入代码", value="SPY", placeholder="例如 SPY, TSLA")
with col2:
    st.write("")
    st.write("")
    st.button("🚀 分析", type="primary")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # 1. 尝试用 Yahoo 获取基础信息
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose')
        
        # Yahoo 的做空数据
        y_short_float = info.get('shortPercentOfFloat')
        y_short_ratio = info.get('shortRatio')
        
        st.divider()
        st.subheader(f"📌 {ticker} 数据概览")
        
        # 基础指标
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("参考价格", f"${price}" if price else "--")
        with c2:
            if y_short_float:
                st.metric("做空占比 (Yahoo)", f"{y_short_float*100:.2f}%")
            else:
                st.metric("做空占比", "N/A", help="Yahoo未提供此ETF数据")
        with c3:
            if y_short_ratio:
                st.metric("回补天数 (Yahoo)", f"{y_short_ratio}")
            else:
                st.metric("回补天数", "N/A", help="Yahoo未提供此ETF数据")

    except:
        st.error("代码输入有误或数据源暂时不可用")

    # --- 2. 核心功能：手动传送门 (解决抓取失败问题) ---
    st.write("")
    
    # 判断是否看起来像 ETF (粗略判断)
    is_etf_guess = True if ticker in ['SPY', 'QQQ', 'IWM', 'TQQQ', 'SQQQ', 'ARKK', 'SMH'] else False
    
    st.markdown('<div class="info-box">👇 <b>查不到数据？请点击下方按钮</b><br>ETF数据在 Yahoo 经常缺失，MarketWatch 是最佳免费替代。</div>', unsafe_allow_html=True)

    # 链接生成
    # MarketWatch 对 ETF 和 股票 的链接结构不同
    # 我们这里生成通用的搜索/行情链接，通常能自动重定向
    url_mw = f"https://www.marketwatch.com/investing/fund/{ticker.lower()}" # 针对ETF的结构
    url_mw_stock = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}" # 针对个股
    
    url_cnbc = f"https://www.cnbc.com/quotes/{ticker}?tab=profile" # CNBC Profile页常有数据
    url_finviz = f"https://finviz.com/quote.ashx?t={ticker}"

    st.subheader("🔗 免费数据源直达 (100% 可用)")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### ✅ 首选推荐")
        # MarketWatch 按钮
        st.link_button(f"MarketWatch (ETF专用)", url_mw, help="点击后查看页面中部的 'Short Interest' 栏目", type="primary", use_container_width=True)
        st.caption("适合 SPY, QQQ 等 ETF。进去后找 **'Short Interest'** 一栏。")
        
    with col_b:
        st.markdown("#### 🔄 备用来源")
        st.link_button(f"CNBC (数据概览)", url_cnbc, use_container_width=True)
        st.link_button(f"Finviz (图表分析)", url_finviz, use_container_width=True)
        st.caption("Finviz 适合看个股；CNBC 适合看汇总。")

    # --- 图表 ---
    st.write("---")
    try:
        hist = stock.history(period="3m")
        if not hist.empty:
            st.line_chart(hist['Close'])
    except:
        pass

