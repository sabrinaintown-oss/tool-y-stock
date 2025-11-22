import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 页面配置 ---
st.set_page_config(page_title="工具Y - ETF强力版", page_icon="🛡️", layout="centered")

# --- CSS样式 ---
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; border-radius: 10px; padding: 15px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心功能：爬取 StockAnalysis (替代Finviz) ---
def get_stockanalysis_data(ticker):
    """
    尝试从 StockAnalysis.com 获取数据，它的反爬虫机制比 Finviz 宽松
    """
    # StockAnalysis 的 URL 结构：ETF 和 股票 是分开的，我们先试 ETF
    # 比如: https://stockanalysis.com/etf/spy/
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # 定义可能的 URL 格式
    urls = [
        f"https://stockanalysis.com/etf/{ticker.lower()}/",     # 格式1: ETF
        f"https://stockanalysis.com/stocks/{ticker.lower()}/"   # 格式2: 个股
    ]

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=4)
            if response.status_code == 200:
                # 成功连接，开始解析表格
                dfs = pd.read_html(response.text)
                
                result_data = {}
                
                # StockAnalysis 的页面通常有多个表格，我们需要遍历查找包含 'Short' 的数据
                for df in dfs:
                    # 转换为字符串以便搜索
                    df_str = df.to_string()
                    
                    # 查找包含 'Short' 或 'Shares' 的行
                    # 表格通常是两列: [属性, 数值]
                    if df.shape[1] >= 2:
                        for index, row in df.iterrows():
                            key = str(row[0])
                            val = str(row[1])
                            
                            if "Short %" in key or "Short Interest" in key:
                                result_data['Short % of Float'] = val
                            if "Short Ratio" in key:
                                result_data['Short Ratio'] = val
                            if "Shares Short" in key:
                                result_data['Shares Short'] = val
                
                # 如果找到了数据，就返回
                if result_data:
                    return result_data
        except Exception:
            continue # 尝试下一个 URL
            
    return None

# --- 主界面 ---
st.title("🛡️ 工具Y：ETF 做空数据强力版")
st.markdown("集成 **Yahoo** (基础) + **StockAnalysis** (ETF增强) 双数据源。")

col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入代码 (如 SPY, TQQQ, NVDA)", value="SPY")
with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 查询", use_container_width=True)

if search_btn or ticker_input:
    ticker = ticker_input.strip().upper()
    
    if ticker:
        st.divider()
        st.subheader(f"📊 {ticker} 分析报告")
        
        # 使用 st.status 显示进度，让用户知道没死机
        with st.status("正在多渠道搜寻数据...", expanded=True) as status:
            
            # 1. 获取 Yahoo 基础信息
            status.write("正在连接 Yahoo Finance...")
            y_stock = yf.Ticker(ticker)
            y_info = y_stock.info
            price = y_info.get('currentPrice') or y_info.get('navPrice') or y_info.get('previousClose')
            y_short_float = y_info.get('shortPercentOfFloat')
            y_short_ratio = y_info.get('shortRatio')
            
            # 2. 如果 Yahoo 数据不全，启动 StockAnalysis 爬虫
            sa_data = None
            if not y_short_float or not y_short_ratio:
                status.write("Yahoo 数据不全，正在启动 StockAnalysis 爬虫 (这可能需要几秒钟)...")
                sa_data = get_stockanalysis_data(ticker)
                
            status.update(label="数据检索完成！", state="complete", expanded=False)

        # --- 展示数据 ---
        st.metric("当前价格", f"${price}" if price else "N/A")

        c1, c2 = st.columns(2)
        
        # --- 数据处理逻辑 ---
        # 优先使用 StockAnalysis 的数据 (因为它通常对ETF更准)，如果没有则用 Yahoo
        
        # 1. Short % of Float
        with c1:
            st.markdown("### 📉 Short % (做空占比)")
            final_short_float = None
            source_label = ""
            
            if sa_data and 'Short % of Float' in sa_data:
                final_short_float = sa_data['Short % of Float']
                source_label = "StockAnalysis"
            elif y_short_float:
                final_short_float = f"{y_short_float*100:.2f}%"
                source_label = "Yahoo Finance"
            
            if final_short_float:
                st.metric(f"来源: {source_label}", final_short_float, delta="做空热度", delta_color="off")
            else:
                st.warning("暂无数据")

        # 2. Short Ratio
        with c2:
            st.markdown("### ⏱️ Short Ratio (回补天数)")
            final_short_ratio = None
            source_label = ""
            
            if sa_data and 'Short Ratio' in sa_data:
                final_short_ratio = sa_data['Short Ratio']
                source_label = "StockAnalysis"
            elif y_short_ratio:
                final_short_ratio = f"{y_short_ratio}"
                source_label = "Yahoo Finance"
                
            if final_short_ratio:
                st.metric(f"来源: {source_label}", final_short_ratio)
            else:
                st.warning("暂无数据")

        # --- 补充信息 ---
        if sa_data and 'Shares Short' in sa_data:
             st.info(f"💡 总做空股数 (Shares Short): {sa_data['Shares Short']}")

        # --- 外部链接 (保底方案) ---
        st.write("---")
        st.caption("如果上方仍显示无数据，请直接点击下方链接查看原始网页：")
        
        l1, l2 = st.columns(2)
        with l1:
            st.link_button(f"👉 查看 StockAnalysis ({ticker})", f"https://stockanalysis.com/etf/{ticker.lower()}/")
        with l2:
            st.link_button(f"👉 查看 Finviz ({ticker})", f"https://finviz.com/quote.ashx?t={ticker}")

        # --- 图表 ---
        try:
            hist = y_stock.history(period="6m")
            if not hist.empty:
                st.line_chart(hist['Close'])
        except:
            pass

