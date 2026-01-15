# Project Dependencies

Tracking all libraries, tools, and data dependencies used in this project.

---

## System Tools

| Tool | Version | Status | Notes |
|------|---------|--------|-------|
| Python | 3.10.11 | Installed | Primary language |
| pip | 23.0.1 | Installed | Package manager |
| Git | - | Configured | Local repo only |
| GitHub CLI (gh) | - | Installed | Not authenticated |
| Chocolatey | 2.0.0 | Installed | Windows package manager |

---

## Python Packages

### Direct Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| yfinance | 1.0 | Stock market data retrieval |
| pandas | 2.3.3 | Data manipulation and analysis |
| mplfinance | 0.12.10b0 | Financial charting (candlestick, OHLC) |

### Transitive Dependencies (via yfinance)

| Package | Purpose |
|---------|---------|
| beautifulsoup4 | HTML parsing |
| curl_cffi | HTTP requests |
| frozendict | Immutable dictionaries |
| multitasking | Parallel downloads |
| numpy | Numerical operations |
| peewee | Data caching (SQLite) |
| platformdirs | Platform-specific directories |
| protobuf | Protocol buffers |
| pytz | Timezone handling |
| requests | HTTP requests |
| websockets | Real-time data streams |

### Transitive Dependencies (via pandas)

| Package | Purpose |
|---------|---------|
| numpy | Numerical operations |
| python-dateutil | Date parsing |
| pytz | Timezone handling |
| tzdata | Timezone database |

### Transitive Dependencies (via mplfinance)

| Package | Purpose |
|---------|---------|
| matplotlib | Core plotting library |
| pillow | Image handling |
| cycler | Color cycling |
| kiwisolver | Constraint solver |
| fonttools | Font handling |
| contourpy | Contour plotting |
| pyparsing | Parser library |

---

## Project Files

### Configuration Files

| File | Purpose |
|------|---------|
| CLAUDE.md | Guidelines and known issues |
| sessionState.md | Session context for continuity |
| claudeLog.md | Terminal action log |
| dependencies.md | This file |
| ROADMAP.md | Future enhancements roadmap |
| .gitignore | Git exclusions |

### Source Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| stock_analysis/stock_analyzer.py | Stock analysis + charting | yfinance, pandas, mplfinance |

---

## External Data Sources

| Source | Used By | Notes |
|--------|---------|-------|
| Yahoo Finance | yfinance | Free, unofficial API; data can be inconsistent (see known issues in CLAUDE.md) |

---

## Version History

| Date | Change |
|------|--------|
| 01/14/2026 | Added mplfinance for charting; added ROADMAP.md |
| 01/13/2026 | Initial creation - documented yfinance, pandas, system tools |
