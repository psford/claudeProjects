"""
Stock Analyzer Dashboard
A Streamlit web interface for stock analysis.

Run with: streamlit run stock_analysis/app.py
"""

import streamlit as st
from streamlit_searchbox import st_searchbox
from dotenv import load_dotenv
import os
import html

# Load environment variables from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
from stock_analyzer import (
    get_stock_info,
    get_historical_data,
    calculate_returns,
    calculate_volatility,
    create_plotly_candlestick,
    create_plotly_line,
    search_tickers,
    get_significant_moves_with_news,
)


def create_wiki_preview_css():
    """Generate CSS for Wikipedia-style hover previews."""
    return """
    <style>
    /* Wikipedia-style preview container */
    .wiki-preview-container {
        position: relative;
        display: inline-block;
    }

    /* The trigger link */
    .wiki-preview-trigger {
        color: #1a73e8;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
        border-bottom: 1px dotted #1a73e8;
    }

    .wiki-preview-trigger:hover {
        color: #1558b0;
    }

    /* The preview card - hidden by default */
    .wiki-preview-card {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        z-index: 1000;
        bottom: 100%;
        left: 0;
        margin-bottom: 10px;
        width: 320px;
        background: white;
        border: 1px solid #a2a9b1;
        border-radius: 2px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        padding: 0;
        transition: opacity 0.15s ease-in-out, visibility 0.15s ease-in-out;
        transition-delay: 0.3s;
    }

    /* Show card on hover with delay (like Wikipedia's 650ms) */
    .wiki-preview-container:hover .wiki-preview-card {
        visibility: visible;
        opacity: 1;
        transition-delay: 0.4s;
    }

    /* Preview image */
    .wiki-preview-image {
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-bottom: 1px solid #eaecf0;
    }

    /* No image placeholder */
    .wiki-preview-no-image {
        width: 100%;
        height: 80px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
    }

    /* Preview content area */
    .wiki-preview-content {
        padding: 12px 16px;
    }

    /* Preview title */
    .wiki-preview-title {
        font-size: 15px;
        font-weight: 700;
        color: #202122;
        margin: 0 0 8px 0;
        line-height: 1.3;
    }

    /* Preview summary */
    .wiki-preview-summary {
        font-size: 13px;
        color: #54595d;
        line-height: 1.5;
        margin: 0 0 8px 0;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Preview source */
    .wiki-preview-source {
        font-size: 11px;
        color: #72777d;
        margin: 0;
    }

    /* Arrow pointer */
    .wiki-preview-card::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 20px;
        border: 8px solid transparent;
        border-top-color: white;
    }

    .wiki-preview-card::before {
        content: '';
        position: absolute;
        top: 100%;
        left: 19px;
        border: 9px solid transparent;
        border-top-color: #a2a9b1;
    }

    /* Adjust position for cards near right edge */
    .wiki-preview-container.align-right .wiki-preview-card {
        left: auto;
        right: 0;
    }

    .wiki-preview-container.align-right .wiki-preview-card::after {
        left: auto;
        right: 20px;
    }

    .wiki-preview-container.align-right .wiki-preview-card::before {
        left: auto;
        right: 19px;
    }
    </style>
    """


def create_wiki_preview_html(headline, url, image_url, summary, source, index):
    """
    Generate HTML for a Wikipedia-style hover preview.

    Args:
        headline: News headline text
        url: Link to full article
        image_url: Thumbnail image URL
        summary: Article summary text
        source: News source name
        index: Unique index for this preview

    Returns:
        HTML string with hover preview
    """
    # Escape HTML entities to prevent XSS
    safe_headline = html.escape(headline or "No headline")
    safe_summary = html.escape(summary or "")
    safe_source = html.escape(source or "Unknown source")
    safe_url = html.escape(url or "#")

    # Truncate summary if too long
    if len(safe_summary) > 200:
        safe_summary = safe_summary[:197] + "..."

    # Build image section
    if image_url:
        safe_image = html.escape(image_url)
        image_html = f'<img class="wiki-preview-image" src="{safe_image}" alt="" onerror="this.style.display=\'none\'">'
    else:
        image_html = '<div class="wiki-preview-no-image">📰</div>'

    # Build summary section (only if summary exists)
    summary_html = f'<p class="wiki-preview-summary">{safe_summary}</p>' if safe_summary else ''

    return f'''
    <div class="wiki-preview-container" id="preview-{index}">
        <a href="{safe_url}" target="_blank" class="wiki-preview-trigger">{safe_headline}</a>
        <div class="wiki-preview-card">
            {image_html}
            <div class="wiki-preview-content">
                <p class="wiki-preview-title">{safe_headline}</p>
                {summary_html}
                <p class="wiki-preview-source">Source: {safe_source}</p>
            </div>
        </div>
    </div>
    '''


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
        clear_on_submit=False,
        rerun_on_update=True,
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
    analyze = st.button("🔍 Analyze", type="primary", width="stretch")

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
                    st.plotly_chart(fig, width="stretch")

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

                # Significant Moves with News
                st.markdown("---")
                st.markdown("### Significant Moves (±5%)")
                st.caption("Days with 5% or greater price change. Hover over headlines for preview.")

                with st.spinner("Loading news for significant moves..."):
                    moves = get_significant_moves_with_news(ticker, period=period)

                if moves:
                    # Inject CSS for Wikipedia-style previews
                    st.markdown(create_wiki_preview_css(), unsafe_allow_html=True)

                    for i, move in enumerate(moves):
                        date_str = move['date'].strftime('%Y-%m-%d')
                        ret = move['return_pct']
                        direction = move['direction']
                        news = move['news']

                        # Color based on direction
                        color = "green" if direction == 'up' else "red"
                        arrow = "↑" if direction == 'up' else "↓"
                        sign = "+" if ret > 0 else ""

                        with st.container():
                            col_date, col_content = st.columns([1, 4])

                            with col_date:
                                st.markdown(f"**{date_str}**")
                                st.markdown(f":{color}[{arrow} {sign}{ret:.1f}%]")

                            with col_content:
                                if news:
                                    # Create Wikipedia-style hover preview
                                    headline = news.get('headline', 'No headline')
                                    url = news.get('url', '')
                                    image = news.get('image', '')
                                    summary = news.get('summary', '')
                                    source = news.get('source', '')

                                    preview_html = create_wiki_preview_html(
                                        headline=headline,
                                        url=url,
                                        image_url=image,
                                        summary=summary,
                                        source=source,
                                        index=i
                                    )
                                    st.markdown(preview_html, unsafe_allow_html=True)

                                    # Show source below
                                    if source:
                                        st.caption(f"Source: {source}")
                                else:
                                    st.markdown("*No news found for this date*")

                            st.markdown("---")
                else:
                    st.info("No significant moves (±5%) found in this period.")

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

# Footer
st.markdown("---")
st.caption("Data provided by Yahoo Finance via yfinance. Use for informational purposes only.")
