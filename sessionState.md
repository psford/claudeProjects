# Session State - Last Updated 01/13/2026

Use this file to restore context when starting a new session. Say "let's get started again" and Claude should read this file.

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
- **Packages installed:** yfinance, pandas, numpy, beautifulsoup4

---

## Project Structure

```
claudeProjects/
├── .git/                    # Local git repository
├── .gitignore               # Excludes tokens, .env, credentials
├── CLAUDE.md                # Guidelines and known issues (READ THIS FIRST)
├── claudeLog.md             # Terminal action log (summaries only)
├── sessionState.md          # This file
├── rules.md                 # Additional rules (pre-existing)
├── claude_01132026-*.md     # Versioned backups of CLAUDE.md
└── stock_analysis/
    └── stock_analyzer.py    # yfinance stock analysis tool
```

---

## Active Guidelines (from CLAUDE.md)

1. Documentation in GitHub-flavored Markdown
2. Version history is important - create sections as needed
3. Request tooling with detailed options
4. Math must be correct to 5 decimal places
5. **Challenge user on bad practices/security issues**
6. Provide alternatives when suggesting approaches
7. Never sign up for paid services
8. Provide detailed instructions for account access (no passwords)
9. Never act illegally
10. Cite sources where possible
11. **Backup CLAUDE.md as `claude_MMDDYYYY-N.md` before each commit**
12. **Log terminal summaries to claudeLog.md**
13. **Naming: camelCase for JS/TS, snake_case for Python**
14. **Session commands: "night!" = save state, "hello!" = restore state**

---

## Known Issues

### yfinance dividend yield (RESOLVED)
- **Problem:** dividendYield returned 40% instead of 0.4%
- **Fix:** Validation in `get_stock_info()` - values >10% divided by 100
- **Status:** Implemented in stock_analyzer.py

---

## Stock Analysis Tool

**Location:** `stock_analysis/stock_analyzer.py`

**Available functions:**
- `get_stock_info(ticker)` - Basic info with validated dividend yield
- `get_historical_data(ticker, period, interval)` - OHLCV data
- `calculate_returns(df)` - Daily & cumulative returns
- `calculate_moving_averages(df, windows)` - MA-20, MA-50, MA-200
- `calculate_volatility(df)` - Annualized volatility
- `get_financials(ticker)` - Income statement, balance sheet, cash flow
- `compare_stocks(tickers, period)` - Normalized comparison
- `print_stock_summary(ticker)` - Formatted console output

**Usage:**
```python
from stock_analyzer import *
print_stock_summary("AAPL")
```

---

## Git History (01/13/2026)

| Hash | Description |
|------|-------------|
| 8b97aee | Add terminal logging system |
| 7feb79d | Fix dividend yield validation |
| a6f414b | Add known issues section |
| 01c3e5c | Add stock analysis tool |
| a3dab31 | Clarify versioning guideline |
| e8a4e37 | Initial commit |

---

## Pending / Future Tasks

- [ ] Set up GitHub authentication when ready for remote repos
- [ ] Add visualization features to stock_analyzer (matplotlib/plotly)
- [ ] Consider additional stock analysis functions (RSI, MACD, Bollinger Bands)

---

## Quick Start for New Session

**Say "hello!"** to restore context automatically.

Or manually:
1. Read `CLAUDE.md` for current guidelines
2. Read `sessionState.md` (this file) for context
3. Check `claudeLog.md` for recent actions
4. Read `dependencies.md` for installed packages
5. Run `git log --oneline` to see commit history

**Say "night!"** at end of session to save state.
