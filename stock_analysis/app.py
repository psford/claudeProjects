"""
Stock Analyzer Dashboard
A Streamlit web interface for stock analysis.

Run with: streamlit run stock_analysis/app.py
"""

import streamlit as st
from streamlit_searchbox import st_searchbox
from dotenv import load_dotenv
import streamlit.components.v1 as components
import os
import html
import json

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


def create_chart_hover_preview_js(news_data):
    """
    Generate JavaScript for Wikipedia-style hover previews on Plotly chart markers.

    Args:
        news_data: Dict mapping date strings to news info dicts

    Returns:
        HTML/JS string to inject after chart
    """
    # Escape the JSON data for safe embedding
    news_json = json.dumps(news_data)

    return f'''
    <div id="wiki-hover-card" style="
        display: none;
        position: fixed;
        z-index: 10000;
        width: 320px;
        background: white;
        border: 1px solid #a2a9b1;
        border-radius: 4px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        pointer-events: none;
    ">
        <img id="wiki-hover-image" style="
            width: 100%;
            height: 140px;
            object-fit: cover;
            border-bottom: 1px solid #eaecf0;
            display: none;
        ">
        <div id="wiki-hover-placeholder" style="
            width: 100%;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        ">📰</div>
        <div style="padding: 12px 16px;">
            <div id="wiki-hover-date" style="
                font-size: 12px;
                color: #72777d;
                margin-bottom: 4px;
            "></div>
            <div id="wiki-hover-return" style="
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 8px;
            "></div>
            <div id="wiki-hover-headline" style="
                font-size: 14px;
                font-weight: 600;
                color: #202122;
                line-height: 1.4;
                margin-bottom: 8px;
            "></div>
            <div id="wiki-hover-summary" style="
                font-size: 12px;
                color: #54595d;
                line-height: 1.5;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            "></div>
            <div id="wiki-hover-source" style="
                font-size: 11px;
                color: #72777d;
                margin-top: 8px;
            "></div>
        </div>
    </div>

    <script>
    (function() {{
        const newsData = {news_json};
        const card = document.getElementById('wiki-hover-card');
        const cardImage = document.getElementById('wiki-hover-image');
        const cardPlaceholder = document.getElementById('wiki-hover-placeholder');
        const cardDate = document.getElementById('wiki-hover-date');
        const cardReturn = document.getElementById('wiki-hover-return');
        const cardHeadline = document.getElementById('wiki-hover-headline');
        const cardSummary = document.getElementById('wiki-hover-summary');
        const cardSource = document.getElementById('wiki-hover-source');

        let hoverTimeout = null;

        function showCard(x, y, dateStr) {{
            const news = newsData[dateStr];
            if (!news) return;

            // Set content
            cardDate.textContent = dateStr;

            const returnPct = news.return_pct;
            const sign = returnPct >= 0 ? '+' : '';
            const color = returnPct >= 0 ? '#16a34a' : '#dc2626';
            cardReturn.textContent = sign + returnPct.toFixed(1) + '% move';
            cardReturn.style.color = color;

            if (news.headline) {{
                cardHeadline.textContent = news.headline;
                cardHeadline.style.display = 'block';
            }} else {{
                cardHeadline.style.display = 'none';
            }}

            if (news.summary) {{
                cardSummary.textContent = news.summary;
                cardSummary.style.display = 'block';
            }} else {{
                cardSummary.style.display = 'none';
            }}

            if (news.source) {{
                cardSource.textContent = 'Source: ' + news.source;
                cardSource.style.display = 'block';
            }} else {{
                cardSource.style.display = 'none';
            }}

            if (news.image) {{
                cardImage.src = news.image;
                cardImage.style.display = 'block';
                cardPlaceholder.style.display = 'none';
                cardImage.onerror = function() {{
                    cardImage.style.display = 'none';
                    cardPlaceholder.style.display = 'flex';
                }};
            }} else {{
                cardImage.style.display = 'none';
                cardPlaceholder.style.display = 'flex';
            }}

            // Position card (above the cursor, centered)
            const cardWidth = 320;
            const cardHeight = card.offsetHeight || 300;
            let left = x - cardWidth / 2;
            let top = y - cardHeight - 20;

            // Keep within viewport
            const vw = window.innerWidth;
            const vh = window.innerHeight;
            if (left < 10) left = 10;
            if (left + cardWidth > vw - 10) left = vw - cardWidth - 10;
            if (top < 10) top = y + 20; // Show below if no room above

            card.style.left = left + 'px';
            card.style.top = top + 'px';
            card.style.display = 'block';
        }}

        function hideCard() {{
            card.style.display = 'none';
        }}

        // Find all Plotly charts and attach hover listeners
        function attachHoverListeners() {{
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(plot) {{
                if (plot._hoverAttached) return;
                plot._hoverAttached = true;

                plot.on('plotly_hover', function(data) {{
                    if (hoverTimeout) clearTimeout(hoverTimeout);

                    const point = data.points[0];
                    // Check if this is a marker trace (+5% or -5% move)
                    if (point.data.name && (point.data.name.includes('5% Move'))) {{
                        const x = data.event.clientX || data.event.pageX;
                        const y = data.event.clientY || data.event.pageY;

                        // Extract date from the point
                        const dateStr = point.x.substring(0, 10); // Get YYYY-MM-DD

                        // Add delay like Wikipedia (400ms)
                        hoverTimeout = setTimeout(function() {{
                            showCard(x, y, dateStr);
                        }}, 400);
                    }}
                }});

                plot.on('plotly_unhover', function(data) {{
                    if (hoverTimeout) clearTimeout(hoverTimeout);
                    hideCard();
                }});
            }});
        }}

        // Attach listeners now and on future chart updates
        attachHoverListeners();

        // Also watch for DOM changes (when Streamlit rerenders)
        const observer = new MutationObserver(function(mutations) {{
            setTimeout(attachHoverListeners, 100);
        }});
        observer.observe(document.body, {{ childList: true, subtree: true }});
    }})();
    </script>
    '''


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

                # Fetch significant moves with news for chart hover previews
                moves_for_chart = get_significant_moves_with_news(ticker, period=period)

                # Build news data dict for JavaScript
                news_data_for_js = {}
                for move in moves_for_chart:
                    date_str = move['date'].strftime('%Y-%m-%d')
                    news = move.get('news') or {}
                    news_data_for_js[date_str] = {
                        'return_pct': move['return_pct'],
                        'direction': move['direction'],
                        'headline': news.get('headline', ''),
                        'summary': news.get('summary', ''),
                        'image': news.get('image', ''),
                        'url': news.get('url', ''),
                        'source': news.get('source', ''),
                    }

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
                    st.plotly_chart(fig, key="main_chart")

                    # Inject JavaScript for hover preview on chart markers
                    # Using st.markdown to inject directly into page (not iframe)
                    if news_data_for_js:
                        st.markdown(
                            create_chart_hover_preview_js(news_data_for_js),
                            unsafe_allow_html=True
                        )

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

                # Significant Moves with News (reuse data from chart)
                st.markdown("---")
                st.markdown("### Significant Moves (±5%)")
                st.caption("Days with 5% or greater price change. Hover over chart markers for preview.")

                moves = moves_for_chart  # Reuse already-fetched data

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
