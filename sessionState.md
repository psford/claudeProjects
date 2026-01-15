# Session State - Last Updated 01/14/2026

Use this file to restore context when starting a new session. Say **"hello!"** to restore state.

---

## User Profile

- **Name:** Patrick (psford)
- **Background:** Financial services business analyst, experience with Matlab, Python, Ruby
- **Preferred languages:** Python, TypeScript, HTML, CSS
- **Email:** patrick@psford.com

---

## Environment Status

### Git
- **Status:** Configured and working locally
- **User:** psford <patrick@psford.com>
- **Repository:** C:\Users\patri\Documents\claudeProjects (initialized)

### GitHub
- **Status:** NOT CONNECTED
- **Issue:** Windows credential manager had memory errors; token auth also failed
- **Next steps:** When needed, try `gh auth login` again or use SSH keys

### Python
- **Version:** 3.10.11
- **Core packages:** yfinance, pandas, numpy, mplfinance, streamlit, plotly, finnhub-python, python-dotenv, streamlit-searchbox

### Streamlit Server
- **Status:** Running in background (task b809410)
- **URL:** http://localhost:8501
- **Note:** May need to restart if computer was rebooted

---

## Project Structure

```
claudeProjects/
├── .git/                    # Local git repository
├── .gitignore               # Excludes tokens, .env, credentials
├── .env                     # API keys (FINNHUB_API_KEY) - gitignored
├── CLAUDE.md                # Guidelines and known issues (21 guidelines)
├── claudeLog.md             # Terminal action log
├── sessionState.md          # This file
├── dependencies.md          # Package and tool dependencies
├── ROADMAP.md               # Future enhancements roadmap
├── whileYouWereAway.md      # Task queue for rate-limited periods
├── rules.md                 # Additional rules (pre-existing)
├── claude_01132026-*.md     # Versioned backups (7 from 01/13)
├── claude_01142026-*.md     # Versioned backups (4 from 01/14)
├── docs/
│   ├── TECHNICAL_SPEC.md    # System architecture, APIs, troubleshooting
│   └── FUNCTIONAL_SPEC.md   # Business requirements, data mappings
└── stock_analysis/
    ├── stock_analyzer.py    # Core analysis + charting + news functions
    └── app.py               # Streamlit web dashboard
```

---

## Active Guidelines (from CLAUDE.md)

1-14. (Previous guidelines - see CLAUDE.md)
15. **Test before completion** - For web UI, must verify in browser, not just code analysis
16. **Commit freely** - No permission needed, maintain rollback capability
17. **No feature regression** - Never sacrifice functionality
18. **Task file on startup** - Check whileYouWereAway.md on "hello!"
19. **Enhancement tracking** - Document in ROADMAP.md
20. **Step-by-step evaluation** - Stop after each task for user review
21. **Guideline adherence** - Regularly refer back, update as needed

---

## Known Issues

### yfinance dividend yield (RESOLVED)
- **Fix:** Validation in `get_stock_info()` - values >10% divided by 100

### Streamlit deprecation warning
- **Issue:** `use_container_width` deprecated, use `width='stretch'`
- **Status:** Fixed in app.py for button, still shows for plotly_chart

---

## Stock Analysis Dashboard

### Features Implemented
- Ticker search with autocomplete (yfinance Search API)
- Interactive Plotly charts (Candlestick, Line)
- Moving average overlays (20, 50, 200-day)
- Significant move markers (±5% daily change)
- News integration (Finnhub + yfinance) with relevance scoring
- Company info, price data, key metrics display
- Performance summary (return, volatility, high/low)
- Significant Moves panel with thumbnails and clickable headlines

### PENDING - NOT WORKING
- **Wikipedia-style hover previews on chart markers**
  - JavaScript injection approach attempted but not functional
  - Code is in place but hover card does not appear
  - DO NOT REFACTOR - needs investigation in next session
  - Reference: Wikipedia Page Previews for design inspiration

### Key Files
- `stock_analysis/app.py` - Streamlit web interface
- `stock_analysis/stock_analyzer.py` - Core analysis module

### Key Functions in stock_analyzer.py
- `search_tickers(query)` - Autocomplete search
- `get_stock_info(ticker)` - Company info with validated dividend yield
- `get_historical_data(ticker, period)` - OHLCV data
- `create_plotly_candlestick(ticker, period, ...)` - Interactive chart
- `create_plotly_line(ticker, period, ...)` - Line chart
- `get_news_for_dates(ticker, dates)` - Batch news fetch
- `get_significant_moves_with_news(ticker, period)` - Moves + news
- `_score_news_relevance(headline, ticker)` - Prioritize stock-specific news

---

## API Keys

- **Finnhub:** Stored in `.env` as `FINNHUB_API_KEY`
- **Rate limit:** 60 requests/minute (free tier)

---

## Git History (Recent - 01/14/2026)

| Hash | Description |
|------|-------------|
| 5f8491b | Add documentation specs and Wikipedia-style hover previews |
| ed7fda6 | Combine multiple news sources with relevance scoring |
| 3fe11f5 | Add commit freely guideline (#16) |
| 907ea6c | Add news panel with thumbnails and clickable links |
| bb981de | Add news headlines to significant move markers |
| 862ceed | Add markers for significant daily price moves (5%+) |

---

## Pending Tasks

### Immediate (from whileYouWereAway.md)
- [x] Create technical specification - DONE
- [x] Create functional specification - DONE
- [x] Add no-regression guideline (#17) - DONE
- [ ] **Wikipedia-style hover previews - NOT WORKING, NEEDS FIX**

### Future (from ROADMAP.md)
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Multi-stock comparison chart
- [ ] Portfolio tracker
- [ ] Export to Excel
- [ ] Unit tests

---

## Quick Start for New Session

**Say "hello!"** to restore context automatically.

Then:
1. Check if Streamlit server is running: `curl http://localhost:8501`
2. If not, start it: `streamlit run stock_analysis/app.py`
3. Check `whileYouWereAway.md` for new tasks
4. Resume work on Wikipedia-style hover previews (NOT WORKING)

**Say "night!"** at end of session to save state.
