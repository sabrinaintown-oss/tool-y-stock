import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 页面配置 ---
st.set_page_config(page_title="工具Y - Finviz增强版", page_icon="🕵️", layout="centered")

# --- CSS样式 ---
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; border-radius: 10px; padding: 15px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心功能：爬取 Finviz 数据 ---
def get_finviz_data(ticker):
    """
    伪装成浏览器去 Finviz 抓取数据
    """
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    # 必须加上 User-Agent，否则 Finviz 会认为是机器人并拦截
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status() # 检查是否连接成功
        
        # 使用 Pandas 读取网页中的表格
        tables = pd.read_html(response.text)
        
        # Finviz 的数据通常在一个很大的表格里，我们需要找到包含 'Short Float' 的那个
        for df in tables:
            # 将表格转换为字符串方便搜索
            df_str = df.to_string()
            if 'Short Float' in df_str:
                # 这是一个键值对表格，我们需要重组它
                # 这种表格通常是 col0=key, col1=value, col2=key, col3=value...
                data = {}
                # 遍历所有列，尝试提取键值对
                for i in range(0, len(df.columns), 2):
                    keys = df.iloc[:, i]
                    values = df.iloc[:, i+1]
                    for k, v in zip(keys, values):
                        data[str(k)] = v
                return data
        return None
    except Exception as e:
        return None

# --- 主界面 ---
st.title("🕵️ 工具Y：做空侦探 (含Finviz数据)")
st.markdown("集成 **Yahoo Finance** (速度快) 与 **Finviz** (ETF数据全) 双引擎。")

col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入代码 (如 SPY, TSLA)", value="SPY")
with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 开始侦查", use_container_width=True)

if search_btn or ticker_input:
    ticker = ticker_input.strip().upper()
    
    if ticker:
        st.divider()
        st.subheader(f"📊 {ticker} 分析报告")
        
        # 1. 尝试获取 Yahoo 数据
        with st.status("正在从 Yahoo Finance 获取基础数据...", expanded=True) as status:
            y_stock = yf.Ticker(ticker)
            y_info = y_stock.info
            price = y_info.get('currentPrice') or y_info.get('navPrice') or y_info.get('previousClose')
            
            # 尝试从 Yahoo 获取做空数据
            y_short_float = y_info.get('shortPercentOfFloat')
            y_short_ratio = y_info.get('shortRatio')
            
            status.update(label="Yahoo 数据获取完毕，正在尝试连接 Finviz...", state="running")
            
            # 2. 尝试获取 Finviz 数据 (补充)
            f_data = get_finviz_data(ticker)
            f_short_float = f_data.get('Short Float') if f_data else None
            f_short_ratio = f_data.get('Short Ratio') if f_data else None
            
            status.update(label="所有数据源检索完成！", state="complete", expanded=False)

        # --- 数据整合展示 ---
        
        # 显示价格
        st.metric("当前价格", f"${price}" if price else "N/A")
        
        # 对比展示做空数据
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 📉 Short Float (做空占比)")
            # 优先显示 Finviz，因为 ETF 数据它更全
            if f_short_float and f_short_float != '-':
                st.metric("来源: Finviz", f_short_float, delta="首选数据")
            elif y_short_float:
                st.metric("来源: Yahoo", f"{y_short_float*100:.2f}%")
            else:
                st.warning("两大数据源均未提供 Short Float")

        with c2:
            st.markdown("### ⏱️ Short Ratio (回补天数)")
            if f_short_ratio and f_short_ratio != '-':
                st.metric("来源: Finviz", f_short_ratio, delta="首选数据")
            elif y_short_ratio:
                st.metric("来源: Yahoo", f"{y_short_ratio}")
            else:
                st.warning("两大数据源均未提供 Short Ratio")
        
        # --- 更多 Finviz 详情 ---
        if f_data:
            with st.expander(f"查看 Finviz 抓取到的完整数据 ({ticker})"):
                # 挑选一些重要指标展示
                keys_to_show = ['Short Float', 'Short Ratio', 'Shs Float', 'Inst Own', 'Insider Own']
                display_data = {k: f_data.get(k, '-') for k in keys_to_show}
                st.table(pd.DataFrame(display_data.items(), columns=['指标', '数值']))
        else:
            st.info("未能成功抓取 Finviz 数据，可能是网络阻断或该标的无数据。")

        # --- 走势图 ---
        st.write("---")
        st.caption("近6个月走势")
        try:
            hist = y_stock.history(period="6m")
            st.line_chart(hist['Close'])
        except:
            pass
