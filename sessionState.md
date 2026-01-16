# Session State - Last Updated 01/16/2026

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
- **Core packages:** yfinance, pandas, numpy, mplfinance, streamlit, plotly, finnhub-python, python-dotenv, streamlit-searchbox, bandit, slack-sdk, slack-bolt

### .NET
- **Version:** .NET 8
- **Project:** stock_analyzer_dotnet (ASP.NET Core minimal API + Tailwind CSS frontend)

### Slack Integration
- **Status:** OPERATIONAL
- **Workspace:** psforddigitaldesign.slack.com
- **Channel:** #claude-notifications
- **Send:** `python stock_analysis/helpers/slack_notify.py "message"`
- **Receive:** `python stock_analysis/helpers/slack_listener.py` (background process)
- **Check inbox:** `python stock_analysis/helpers/slack_listener.py --check`

---

## Project Structure

```
claudeProjects/                      # Workspace root (shared across projects)
├── .git/                            # Local git repository
├── .gitignore                       # Excludes tokens, .env, credentials, logs
├── CLAUDE.md                        # Guidelines and known issues (38 guidelines)
├── claudeLog.md                     # Terminal action log
├── sessionState.md                  # This file
├── whileYouWereAway.md              # Task queue for rate-limited periods
├── claude_01*.md                    # Versioned CLAUDE.md backups
│
├── stock_analysis/                  # Python Stock Analysis Project
│   ├── .env                         # API keys (FINNHUB, SLACK tokens) - gitignored
│   ├── stock_analyzer.py            # Core analysis + charting + news functions
│   ├── app.py                       # Streamlit web dashboard
│   ├── dependencies.md              # Package and tool dependencies
│   ├── ROADMAP.md                   # Future enhancements roadmap
│   ├── docs/
│   │   ├── TECHNICAL_SPEC.md        # System architecture, APIs, troubleshooting
│   │   └── FUNCTIONAL_SPEC.md       # Business requirements, data mappings
│   ├── helpers/
│   │   ├── security_scan.py         # SAST scanner wrapper (Bandit)
│   │   ├── zap_scan.py              # DAST scanner wrapper (OWASP ZAP)
│   │   ├── slack_notify.py          # Send Slack notifications
│   │   ├── slack_listener.py        # Receive Slack messages (Socket Mode)
│   │   └── checkpoint.py            # Session state checkpointing
│   └── security_reports/            # ZAP scan HTML/JSON reports
│
└── stock_analyzer_dotnet/           # .NET Stock Analysis Project
    ├── src/
    │   ├── StockAnalyzer.Api/       # ASP.NET Core minimal API
    │   │   ├── wwwroot/             # Static files (HTML, CSS, JS)
    │   │   │   ├── index.html       # Main dashboard page
    │   │   │   └── js/
    │   │   │       ├── app.js       # Main application logic
    │   │   │       ├── api.js       # API client
    │   │   │       └── charts.js    # Plotly chart rendering
    │   │   └── appsettings.Development.json  # API keys (gitignored)
    │   └── StockAnalyzer.Core/      # Core business logic
    │       ├── Models/              # Data models
    │       └── Services/            # Stock data, news, analysis services
    └── docs/
        ├── TECHNICAL_SPEC.md        # .NET-specific architecture
        └── FUNCTIONAL_SPEC.md       # .NET-specific requirements
```

---

## Active Guidelines (from CLAUDE.md)

Key guidelines (38 total, see CLAUDE.md for all):
- **#15** Test before completion - Verify UI in browser, not just code analysis
- **#22** Context window efficiency - Hot/cold storage, BUT rules files are sacrosanct
- **#34** Building ≠ Running - Verify service is running before claiming it's available
- **#37** Proactive guideline updates - Add user feedback to CLAUDE.md when beneficial
- **#38** Test external services - Verify APIs/services work BEFORE integrating

---

## .NET Dashboard Features (COMPLETE)

- ✅ REST API with stock data endpoints
- ✅ Interactive Plotly charts (candlestick, line)
- ✅ Moving average overlays (20, 50, 200-day)
- ✅ Ticker search with autocomplete
- ✅ Significant move markers (triangles on chart)
- ✅ Wikipedia-style hover popups with news details
- ✅ Configurable threshold slider (3-10%)
- ✅ Cat images in popups (cataas.com)
- ✅ Security headers (CSP, etc.)
- ✅ SAST (SecurityCodeScan) - 0 warnings
- ✅ DAST (ZAP) - 114 passed, 0 failures

---

## Pending Tasks (from ROADMAP.md)

| Task | Description | Status |
|------|-------------|--------|
| Cats vs Dogs toggle | Radio button to choose cats or dogs for thumbnails | Planned |
| Hosting research | Identify free/cheap options to host online | Planned |
| SRI for CDN scripts | Subresource Integrity hashes | Planned |
| Unit tests | xUnit test suite | Planned |

---

## Git History (Recent - 01/16/2026)

| Hash | Description |
|------|-------------|
| b74e670 | Add guideline #38: Test external services before integrating |
| 2f5bba1 | Fix kitten images - switch to cataas.com |
| 3061e37 | Replace news thumbnails with kittens, add guidelines |
| 449d5b5 | Fix hover detection and popup race condition |
| 1969ca6 | Complete Wikipedia-style hover popups for significant moves |
| a161054 | Fix ticker search to support company name autocomplete |

---

## Quick Start for New Session

**Say "hello!"** to restore context automatically.

Then:
1. Read CLAUDE.md (sacrosanct rules)
2. Check `whileYouWereAway.md` for tasks
3. Check Slack inbox: `python stock_analysis/helpers/slack_listener.py --check`

To run .NET app:
```
cd stock_analyzer_dotnet
dotnet run --project src/StockAnalyzer.Api
# Visit http://localhost:5000
```

**Say "night!"** at end of session to save state.
