# Technical Specification: Stock Analyzer Dashboard (Python)

**Version:** 1.0
**Last Updated:** 2026-01-14
**Author:** Claude (AI Assistant)
**Status:** Production

---

## 1. Overview

### 1.1 Purpose

The Stock Analyzer Dashboard is a web-based application that provides interactive stock market analysis, visualization, and news integration. It enables users to research equity securities through charts, financial metrics, and news correlation for significant price movements.

### 1.2 Scope

This specification covers:
- System architecture and component interactions
- Data sources and API integrations
- Deployment and runtime requirements
- Configuration and environment setup
- Troubleshooting procedures

### 1.3 Glossary

| Term | Definition |
|------|------------|
| OHLCV | Open, High, Low, Close, Volume - standard price data format |
| MA | Moving Average - trend indicator calculated over N periods |
| Ticker | Unique stock symbol (e.g., AAPL for Apple Inc.) |
| Significant Move | Daily price change of ±5% or greater |
| yfinance | Python library providing Yahoo Finance data |
| Finnhub | Third-party financial news API service |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Browser                                │
│                        (localhost:8501)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Streamlit Web Server                             │
│                        (app.py)                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐ │
│  │ Sidebar UI     │  │ Chart Display  │  │ News Panel             │ │
│  │ - Search box   │  │ - Plotly figs  │  │ - Thumbnails           │ │
│  │ - Period       │  │ - Candlestick  │  │ - Headlines            │ │
│  │ - Chart type   │  │ - Line         │  │ - Source links         │ │
│  │ - MA toggles   │  │ - Markers      │  │                        │ │
│  └────────────────┘  └────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Stock Analyzer Module                             │
│                   (stock_analyzer.py)                                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Core Functions:                                                 │ │
│  │ - get_stock_info()       - create_plotly_candlestick()         │ │
│  │ - get_historical_data()  - create_plotly_line()                │ │
│  │ - calculate_returns()    - search_tickers()                    │ │
│  │ - calculate_volatility() - get_news_for_dates()                │ │
│  │ - calculate_moving_averages()                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌────────────────────────────┐    ┌────────────────────────────────────┐
│     Yahoo Finance API       │    │         Finnhub API                │
│       (via yfinance)        │    │      (via finnhub-python)          │
│                             │    │                                    │
│  - Stock quotes             │    │  - Company news                    │
│  - Historical OHLCV         │    │  - News images                     │
│  - Company info             │    │  - Article URLs                    │
│  - Ticker search            │    │                                    │
└────────────────────────────┘    └────────────────────────────────────┘
```

### 2.2 Component Description

| Component | File | Responsibility |
|-----------|------|----------------|
| Web Interface | `app.py` | User interaction, layout, state management |
| Analysis Engine | `stock_analyzer.py` | Data fetching, calculations, chart generation |
| Configuration | `.env` | API keys, environment variables |

### 2.3 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Runtime | Python | 3.10.11 |
| Web Framework | Streamlit | 1.53.0 |
| Charting | Plotly | 6.5.2 |
| Data Processing | pandas | 2.3.3 |
| Market Data | yfinance | 1.0 |
| News Data | finnhub-python | 2.4.26 |
| UI Components | streamlit-searchbox | 0.1.24 |

---

## 3. Data Flow

### 3.1 Ticker Search Flow

```
User Input → st_searchbox → ticker_search() → yf.Search() → Yahoo API
                                    ↓
                             Format results
                                    ↓
                             Return (display, symbol) tuples
```

### 3.2 Chart Generation Flow

```
User selects ticker + period + options
            ↓
get_historical_data(ticker, period)
            ↓
yf.Ticker.history() → Yahoo Finance API
            ↓
pandas DataFrame (OHLCV)
            ↓
create_plotly_candlestick() or create_plotly_line()
            ├── Calculate daily returns
            ├── Identify significant moves (±5%)
            ├── get_news_for_dates() → Finnhub + yfinance news
            └── Build Plotly figure with traces + markers
            ↓
st.plotly_chart() → Render in browser
```

### 3.3 News Aggregation Flow

```
get_news_for_dates(ticker, dates, full_data=True)
            ↓
    ┌───────┴───────┐
    ▼               ▼
Finnhub API    yfinance news
    │               │
    └───────┬───────┘
            ▼
    Merge all news items
            ↓
    _score_news_relevance() for each item
            ↓
    Sort by date, then by relevance score
            ↓
    Return most relevant news per date
```

---

## 4. API Integration

### 4.1 Yahoo Finance (yfinance)

**Base URL:** Unofficial Yahoo Finance API (managed by library)

**Rate Limits:** Not officially documented; library implements internal throttling

**Key Endpoints Used:**

| Function | yfinance Method | Data Returned |
|----------|-----------------|---------------|
| Stock info | `Ticker.info` | Company name, sector, P/E, dividend yield, etc. |
| Historical prices | `Ticker.history(period, interval)` | OHLCV DataFrame |
| Ticker search | `Search(query)` | Matching symbols and company names |
| News | `Ticker.news` | Recent news articles with metadata |

**Period Options:** `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

### 4.2 Finnhub API

**Base URL:** `https://finnhub.io/api/v1/`

**Authentication:** API key via `FINNHUB_API_KEY` environment variable

**Rate Limits:** 60 requests/minute (free tier)

**Endpoint Used:**

| Endpoint | Purpose | Parameters |
|----------|---------|------------|
| `/company-news` | Stock-specific news | `symbol`, `from`, `to` dates |

**Response Fields:**

```json
{
  "datetime": 1704067200,
  "headline": "Article title",
  "image": "https://...",
  "source": "Source name",
  "summary": "Article summary",
  "url": "https://..."
}
```

---

## 5. Data Models

### 5.1 Stock Info Dictionary

Returned by `get_stock_info(ticker)`:

```python
{
    "name": str,           # Company long name
    "sector": str,         # Business sector
    "industry": str,       # Specific industry
    "market_cap": int,     # Market capitalization in USD
    "current_price": float,# Current/latest price
    "52_week_high": float, # 52-week high price
    "52_week_low": float,  # 52-week low price
    "pe_ratio": float,     # Trailing P/E ratio
    "dividend_yield": float, # Annualized dividend yield (decimal)
    "beta": float          # Market beta coefficient
}
```

### 5.2 News Data Dictionary

Returned by `get_news_for_dates()` with `full_data=True`:

```python
{
    datetime: {
        "headline": str,   # Article headline
        "url": str,        # Link to full article
        "image": str,      # Thumbnail URL
        "summary": str,    # Article summary
        "source": str      # Publisher name
    }
}
```

### 5.3 Significant Move Dictionary

Returned by `get_significant_moves_with_news()`:

```python
{
    "date": datetime,      # Date of the move
    "return_pct": float,   # Percentage change (e.g., 5.5 for +5.5%)
    "direction": str,      # "up" or "down"
    "news": dict | None    # News data or None if not found
}
```

---

## 6. Configuration

### 6.1 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FINNHUB_API_KEY` | Yes | Finnhub API authentication key |

**Location:** `.env` file in project root

**Format:**
```
FINNHUB_API_KEY=your_api_key_here
```

### 6.2 Streamlit Configuration

**Page Settings (in app.py):**

```python
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)
```

### 6.3 Default Values

| Setting | Default | Configurable |
|---------|---------|--------------|
| Chart period | 1 year (`1y`) | Yes (UI dropdown) |
| Chart type | Candlestick | Yes (UI dropdown) |
| MA-20 | Enabled | Yes (checkbox) |
| MA-50 | Enabled | Yes (checkbox) |
| MA-200 | Disabled | Yes (checkbox) |
| Volume display | Enabled | Yes (checkbox) |
| Significant move threshold | 5% | No (hardcoded) |

---

## 7. Deployment

### 7.1 Prerequisites

- Python 3.10+
- pip package manager
- Finnhub API key (free tier: https://finnhub.io/)

### 7.2 Installation Steps

```bash
# 1. Clone/navigate to project directory
cd claudeProjects

# 2. Install dependencies
pip install yfinance pandas mplfinance streamlit plotly streamlit-searchbox finnhub-python python-dotenv

# 3. Configure API key
echo "FINNHUB_API_KEY=your_key_here" > .env

# 4. Run the application
streamlit run stock_analysis/app.py
```

### 7.3 Running the Application

**Start Server:**
```bash
streamlit run stock_analysis/app.py
```

**Default Endpoints:**
- Local: `http://localhost:8501`
- Network: `http://<your-ip>:8501`

**Stop Server:** `Ctrl+C` in terminal

### 7.4 File Structure

```
claudeProjects/
├── .env                      # API keys (gitignored)
├── .gitignore               # Git exclusions
├── CLAUDE.md                # Project guidelines
├── ROADMAP.md               # Enhancement roadmap
├── dependencies.md          # Dependency documentation
├── sessionState.md          # Session context
├── claudeLog.md             # Terminal action log
├── docs/
│   ├── TECHNICAL_SPEC.md    # This document
│   └── FUNCTIONAL_SPEC.md   # Business requirements
└── stock_analysis/
    ├── __pycache__/         # Python cache
    ├── app.py               # Streamlit web interface
    └── stock_analyzer.py    # Core analysis module
```

---

## 8. Known Issues and Workarounds

### 8.1 Dividend Yield Inconsistency

**Issue:** yfinance returns dividend yield in inconsistent formats - sometimes as decimal (0.004 = 0.4%), sometimes as percentage (0.4 = 40%).

**Workaround:** Validation logic in `get_stock_info()`:

```python
raw_yield = info.get("dividendYield", "N/A")
if isinstance(raw_yield, (int, float)):
    if raw_yield > 0.10:
        dividend_yield = raw_yield / 100  # Correct inflated value
    else:
        dividend_yield = raw_yield
```

**Impact:** Without fix, stocks may show unrealistic dividend yields (e.g., 40% instead of 0.4%).

### 8.2 Streamlit Deprecation Warning

**Issue:** `use_container_width` parameter is deprecated after 2025-12-31.

**Message:**
```
Please replace `use_container_width` with `width`.
For `use_container_width=True`, use `width='stretch'`.
```

**Current Status:** Warning only; functionality unaffected.

**Fix:** Update button call in app.py:
```python
# Change from:
st.button("🔍 Analyze", use_container_width=True)
# To:
st.button("🔍 Analyze", width='stretch')
```

### 8.3 News Availability

**Issue:** News may not be available for all dates, especially older dates or less-covered stocks.

**Behavior:** System displays "*No news found for this date*" when no relevant news exists.

**Mitigation:** System checks multiple sources (Finnhub + yfinance) and looks back up to 2 days before significant moves.

---

## 9. Troubleshooting

### 9.1 Application Won't Start

**Symptom:** Error on `streamlit run stock_analysis/app.py`

**Possible Causes:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Missing dependency | `pip install streamlit` |
| `ModuleNotFoundError: No module named 'stock_analyzer'` | Wrong directory | Run from `claudeProjects/` root |
| `Address already in use` | Port 8501 occupied | Kill existing process or use `--server.port 8502` |

### 9.2 No Data Displayed

**Symptom:** "No data found for ticker" error

**Possible Causes:**

| Cause | Solution |
|-------|----------|
| Invalid ticker symbol | Verify ticker exists on Yahoo Finance |
| Network connectivity | Check internet connection |
| Yahoo Finance rate limit | Wait and retry |

### 9.3 News Not Loading

**Symptom:** News section shows "No news found" for all dates

**Possible Causes:**

| Cause | Solution |
|-------|----------|
| Missing API key | Check `.env` file contains valid `FINNHUB_API_KEY` |
| API rate limit exceeded | Wait 1 minute (free tier: 60 req/min) |
| Invalid API key | Verify key at https://finnhub.io/dashboard |

**Diagnostic Command:**
```python
import finnhub
client = finnhub.Client(api_key="your_key")
print(client.company_news("AAPL", _from="2026-01-01", to="2026-01-14"))
```

### 9.4 Chart Not Rendering

**Symptom:** Blank chart area or error message

**Possible Causes:**

| Cause | Solution |
|-------|----------|
| Insufficient data | Try shorter period or different ticker |
| Browser cache | Hard refresh (Ctrl+F5) |
| Plotly version conflict | `pip install --upgrade plotly` |

### 9.5 Search Not Working

**Symptom:** No results when typing in search box

**Possible Causes:**

| Cause | Solution |
|-------|----------|
| Query too short | Type at least 2 characters |
| yfinance Search API down | Check Yahoo Finance directly |
| streamlit-searchbox issue | Restart Streamlit server |

---

## 10. Security Considerations

### 10.1 API Key Storage

- API keys stored in `.env` file (not committed to git)
- `.gitignore` includes `.env` entry
- Keys loaded via `python-dotenv` at runtime

### 10.2 Data Privacy

- No user data is stored or transmitted
- All data requests are read-only
- No authentication/login system

### 10.3 Network Security

- Default: localhost only
- Network access possible but not encrypted (HTTP)
- Production deployment should use HTTPS reverse proxy

---

## 11. Performance Considerations

### 11.1 Data Caching

Currently no caching implemented. Each page refresh fetches fresh data.

**Future Enhancement:** Add `@st.cache_data` decorators for API responses.

### 11.2 API Rate Limits

| Service | Limit | Impact |
|---------|-------|--------|
| Finnhub | 60/min | News fetching may fail under heavy use |
| Yahoo Finance | Undocumented | Occasional request failures possible |

### 11.3 Memory Usage

- Historical data: ~100KB per 1-year ticker
- Charts: Rendered client-side (minimal server memory)
- News images: Loaded from external URLs (not cached)

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-14 | Initial technical specification |
| 1.1 | 2026-01-16 | Separated into Python-specific spec (.NET moved to separate doc) |

---

## 13. References (Python)

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [Finnhub API Documentation](https://finnhub.io/docs/api)
- [Stack Overflow: Practical Guide to Technical Specs](https://stackoverflow.blog/2020/04/06/a-practical-guide-to-writing-technical-specs/)
