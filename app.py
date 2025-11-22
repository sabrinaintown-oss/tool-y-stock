import streamlit as st
import yfinance as yf
import pandas as pd

# --- 页面配置 ---
st.set_page_config(
    page_title="工具Y - Pro版",
    page_icon="📊",
    layout="centered"
)

# --- CSS样式优化 ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 标题 ---
st.title("📊 工具Y：做空数据透视 (含ETF支持)")
st.markdown("查询美股/ETF的 **做空比率** 及 **做空规模**。")

# --- 输入区 ---
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("请输入代码 (如 SPY, ARKK, NVDA)", value="SPY")
with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 查询", use_container_width=True)

# --- 核心逻辑 ---
if search_btn or ticker_input:
    ticker_symbol = ticker_input.strip().upper()
    
    if ticker_symbol:
        try:
            with st.spinner(f'正在挖掘 {ticker_symbol} 的数据...'):
                stock = yf.Ticker(ticker_symbol)
                info = stock.info
                
                # --- 数据提取 (增强容错性) ---
                price = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose')
                short_ratio = info.get('shortRatio') # 回补天数
                short_float = info.get('shortPercentOfFloat') # 做空占比
                shares_short = info.get('sharesShort') # 总做空股数
                
                # --- 结果展示 ---
                st.divider()
                st.subheader(f"📈 {ticker_symbol} 数据报告")

                # 第一行指标
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("当前价格", f"${price}" if price else "N/A")
                with c2:
                    # 如果是ETF，Yahoo经常没有Short Ratio，显示N/A
                    val = f"{short_ratio} 天" if short_ratio else "N/A"
                    st.metric("Short Ratio (回补天数)", val)
                with c3:
                    # 做空占比
                    if short_float:
                        val = f"{short_float * 100:.2f}%"
                        st.metric("Short % of Float", val, delta="做空热度", delta_color="off")
                    else:
                        st.metric("Short % of Float", "数据源缺失", help="Yahoo Finance 未提供此ETF的流通占比数据")

                # --- 第二行：针对 ETF 的补充数据 ---
                st.write("")
                st.caption("💡 提示：ETF 的流通股是动态变化的，因此由于计算困难，免费数据源常缺失比率数据。请参考下方的【总做空股数】。")
                
                c4, c5 = st.columns(2)
                with c4:
                    st.metric("被做空总股数 (Shares Short)", f"{shares_short:,}" if shares_short else "无数据")
                with c5:
                    # 这是一个备用方案按钮
                    finviz_url = f"https://finviz.com/quote.ashx?t={ticker_symbol}&p=d"
                    st.write("看不到数据？试试 Finviz：")
                    st.link_button(f"👉 去 Finviz 查看 {ticker_symbol} 详情", finviz_url)

                # --- 图表 ---
                st.write("---")
                st.write("**近 6 个月走势**")
                hist = stock.history(period="6m")
                if not hist.empty:
                    st.line_chart(hist['Close'])
                else:
                    st.warning("暂无图表数据")

        except Exception as e:
            st.error(f"发生错误：无法获取 {ticker_symbol}。可能是代码输入错误。")
            # st.exception(e) # 调试用
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

