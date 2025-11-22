import streamlit as st
import yfinance as yf
import pandas as pd

# --- 页面配置 ---
st.set_page_config(
    page_title="工具Y - 个股做空数据查询",
    page_icon="📉",
    layout="centered"
)

# --- 标题与简介 ---
st.title("📉 工具Y：个股做空透视镜")
st.markdown("""
输入美股代码（如 TSLA, AAPL, GME），快速获取**做空比率 (Short Ratio)** 及 **做空占比 (Short % of Float)**。
*数据来源: Yahoo Finance (基于最近一次交易所报告)*
""")

st.divider()

# --- 侧边栏或顶部输入 ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入股票代码", value="TSLA", help="输入美股代码，不区分大小写")
with col2:
    st.write("") # 占位，为了让按钮对齐
    st.write("")
    search_btn = st.button("🔍 查询数据", use_container_width=True)

# --- 核心逻辑 ---
if search_btn or ticker_input:
    ticker_symbol = ticker_input.strip().upper()
    
    if ticker_symbol:
        try:
            with st.spinner(f'正在从交易所获取 {ticker_symbol} 的数据...'):
                stock = yf.Ticker(ticker_symbol)
                info = stock.info
                
                # 获取核心数据
                current_price = info.get('currentPrice', 0)
                short_ratio = info.get('shortRatio')
                short_float = info.get('shortPercentOfFloat')
                shares_short = info.get('sharesShort')
                
                # --- 结果展示区 ---
                st.subheader(f"📊 {ticker_symbol} 做空数据报告")
                
                # 第一行：核心指标
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric(label="当前股价", value=f"${current_price}")
                
                with metric_col2:
                    val = f"{short_ratio} 天" if short_ratio else "无数据"
                    st.metric(label="Short Ratio (回补天数)", value=val, 
                              help="以当前日均交易量，空头买回所有股票需要的天数。数值越大，轧空风险越高。")
                
                with metric_col3:
                    val = f"{short_float * 100:.2f}%" if short_float else "无数据"
                    delta_color = "inverse" if short_float and short_float > 0.2 else "normal" # 如果做空超过20%显示红色警示
                    st.metric(label="Short % of Float", value=val, delta="做空占比", delta_color="off")

                # --- 额外数据表格 ---
                with st.expander("查看更多详细数据"):
                    detail_data = {
                        "指标": ["被做空股数 (Shares Short)", "流通股总数 (Float Shares)", "做空比率 (Short Ratio)", "前收盘价"],
                        "数值": [
                            f"{shares_short:,}" if shares_short else "N/A",
                            f"{info.get('floatShares', 0):,}" if info.get('floatShares') else "N/A",
                            short_ratio,
                            info.get('previousClose')
                        ]
                    }
                    st.table(pd.DataFrame(detail_data))

                # --- 价格走势图 (辅助判断) ---
                st.write("📈 **最近 3 个月价格走势** (辅助判断轧空趋势)")
                hist = stock.history(period="3m")
                st.line_chart(hist['Close'])

        except Exception as e:
            st.error(f"无法找到代码 {ticker_symbol}，请检查拼写是否正确。错误信息: {e}")
    else:

        st.warning("请输入有效的股票代码。")
