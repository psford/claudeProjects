"""
Stock Analyzer Dashboard
A Streamlit web interface for stock analysis.

Run with: streamlit run stock_analysis/app.py
"""

import streamlit as st
from streamlit_searchbox import st_searchbox
from stock_analyzer import (
    get_stock_info,
    get_historical_data,
    calculate_returns,
    calculate_volatility,
    create_plotly_candlestick,
    create_plotly_line,
    search_tickers,
)


def ticker_search(query: str) -> list:
    """Search function for the searchbox component."""
    if not query or len(query) < 2:
        return []

    results = search_tickers(query, max_results=8)
    # Format results for searchbox: list of (display_text, value) tuples
    options = []
    for r in results:
        display = f"{r['symbol']} - {r['name']}"
        if r['exchange']:
            display += f" ({r['exchange']})"
        options.append((display, r['symbol']))

    return options

# Page configuration
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Stock Analyzer Dashboard")
st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("Settings")

    # Ticker search with autocomplete
    st.markdown("**Search Stock**")
    selected = st_searchbox(
        ticker_search,
        key="ticker_searchbox",
        placeholder="Type company name or ticker...",
        default="AAPL",
    )

    # Extract ticker from selection (None if cleared)
    ticker = None
    if selected:
        if isinstance(selected, tuple):
            ticker = selected[1]  # Get the symbol from (display, symbol) tuple
        else:
            ticker = selected
        ticker = ticker.upper().strip() if ticker else None

    # Period selector
    period = st.selectbox(
        "Time Period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,  # Default to 1y
        help="Select the historical data range"
    )

    # Chart type
    chart_type = st.selectbox(
        "Chart Type",
        options=["Candlestick", "Line"],
        index=0
    )

    # Moving averages
    st.subheader("Moving Averages")
    show_ma20 = st.checkbox("MA-20", value=True)
    show_ma50 = st.checkbox("MA-50", value=True)
    show_ma200 = st.checkbox("MA-200", value=False)

    # Volume toggle (for candlestick only)
    if chart_type == "Candlestick":
        show_volume = st.checkbox("Show Volume", value=True)
    else:
        show_volume = False

    # Analyze button
    analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)

# Build moving averages list
moving_averages = []
if show_ma20:
    moving_averages.append(20)
if show_ma50:
    moving_averages.append(50)
if show_ma200:
    moving_averages.append(200)

# Main content
if not ticker:
    st.info("Enter a company name or ticker symbol in the sidebar to get started.")
elif ticker:
    # Fetch data
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            info = get_stock_info(ticker)
            hist = get_historical_data(ticker, period=period)

            if hist.empty:
                st.error(f"No data found for ticker: {ticker}")
            else:
                # Chart section
                st.subheader(f"{info.get('name', ticker)} ({ticker})")

                if chart_type == "Candlestick":
                    fig = create_plotly_candlestick(
                        ticker,
                        period=period,
                        show_volume=show_volume,
                        moving_averages=moving_averages if moving_averages else None
                    )
                else:
                    fig = create_plotly_line(
                        ticker,
                        period=period,
                        moving_averages=moving_averages if moving_averages else None
                    )

                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                # Info columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("### Company Info")
                    st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                    if isinstance(info.get('market_cap'), (int, float)):
                        market_cap = info['market_cap']
                        if market_cap >= 1e12:
                            cap_str = f"${market_cap/1e12:.2f}T"
                        elif market_cap >= 1e9:
                            cap_str = f"${market_cap/1e9:.2f}B"
                        else:
                            cap_str = f"${market_cap/1e6:.2f}M"
                        st.markdown(f"**Market Cap:** {cap_str}")
                    else:
                        st.markdown(f"**Market Cap:** N/A")

                with col2:
                    st.markdown("### Price Data")
                    if isinstance(info.get('current_price'), (int, float)):
                        st.markdown(f"**Current Price:** ${info['current_price']:.2f}")
                    if isinstance(info.get('52_week_high'), (int, float)):
                        st.markdown(f"**52-Week High:** ${info['52_week_high']:.2f}")
                    if isinstance(info.get('52_week_low'), (int, float)):
                        st.markdown(f"**52-Week Low:** ${info['52_week_low']:.2f}")

                with col3:
                    st.markdown("### Key Metrics")
                    if isinstance(info.get('pe_ratio'), (int, float)):
                        st.markdown(f"**P/E Ratio:** {info['pe_ratio']:.2f}")
                    else:
                        st.markdown("**P/E Ratio:** N/A")

                    if isinstance(info.get('dividend_yield'), (int, float)):
                        st.markdown(f"**Dividend Yield:** {info['dividend_yield']*100:.2f}%")
                    else:
                        st.markdown("**Dividend Yield:** N/A")

                    if isinstance(info.get('beta'), (int, float)):
                        st.markdown(f"**Beta:** {info['beta']:.2f}")
                    else:
                        st.markdown("**Beta:** N/A")

                # Performance metrics
                st.markdown("---")
                st.markdown("### Performance")

                hist_with_returns = calculate_returns(hist)
                total_return = hist_with_returns["Cumulative_Return"].iloc[-1] * 100
                volatility = calculate_volatility(hist) * 100

                perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

                with perf_col1:
                    st.metric(
                        "Total Return",
                        f"{total_return:.2f}%",
                        delta=f"{total_return:.2f}%"
                    )

                with perf_col2:
                    st.metric("Volatility (Ann.)", f"{volatility:.2f}%")

                with perf_col3:
                    st.metric(
                        "Period High",
                        f"${hist['High'].max():.2f}"
                    )

                with perf_col4:
                    st.metric(
                        "Period Low",
                        f"${hist['Low'].min():.2f}"
                    )

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

# Footer
st.markdown("---")
st.caption("Data provided by Yahoo Finance via yfinance. Use for informational purposes only.")
