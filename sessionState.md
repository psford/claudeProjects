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

### Python
- **Version:** 3.10.11
- **Core packages:** yfinance, pandas, numpy, mplfinance, streamlit, plotly, finnhub-python, python-dotenv, streamlit-searchbox, bandit, slack-sdk, slack-bolt

### .NET
- **Version:** .NET 8
- **Project:** stock_analyzer_dotnet (ASP.NET Core minimal API + Tailwind CSS frontend)

### Slack Integration
- **Status:** OPERATIONAL (reaction-only acknowledgment)
- **Workspace:** psforddigitaldesign.slack.com
- **Channel:** #claude-notifications
- **Bot scopes:** chat:write, channels:history, reactions:write, app_mentions:read
- **Send:** `python stock_analysis/helpers/slack_notify.py "message"`
- **Listener:** `python stock_analysis/helpers/slack_listener.py --daemon`
- **Check inbox:** `python stock_analysis/helpers/slack_listener.py --check`
- **Sync history:** `python stock_analysis/helpers/slack_listener.py --sync`

---

## Project Structure

```
claudeProjects/
├── CLAUDE.md                        # Guidelines (40) + Deployment rules (D1-D5)
├── claudeLog.md                     # Terminal action log
├── sessionState.md                  # This file
├── whileYouWereAway.md              # Task queue
├── claude_01*.md                    # Versioned CLAUDE.md backups
│
├── stock_analysis/                  # Python Stock Analysis Project
│   ├── .env                         # API keys (gitignored)
│   ├── stock_analyzer.py
│   ├── app.py                       # Streamlit dashboard
│   ├── ROADMAP.md
│   ├── helpers/
│   │   ├── slack_notify.py          # Send Slack messages
│   │   ├── slack_listener.py        # Receive messages (reaction-only ack)
│   │   ├── security_scan.py         # SAST (Bandit)
│   │   ├── zap_scan.py              # DAST (ZAP)
│   │   └── checkpoint.py
│   └── security_reports/
│
└── stock_analyzer_dotnet/           # .NET Stock Analysis Project
    ├── src/StockAnalyzer.Api/
    │   ├── wwwroot/js/app.js        # Hover popups with cat images
    │   └── appsettings.Development.json  # API keys (gitignored)
    └── src/StockAnalyzer.Core/
```

---

## Guidelines Summary

**Total:** 41 general guidelines + 5 deployment rules

**Key guidelines:**
- **#15** Test before completion
- **#22** Context efficiency (rules files are sacrosanct)
- **#37** Proactive guideline updates from feedback
- **#38** Test external services before integrating
- **#41** Keep specs updated (FUNCTIONAL_SPEC.md, TECHNICAL_SPEC.md)

**Deployment rules (new section):**
- **D1** Kill before deploy - terminate old processes first
- **D2** Redeploy after committing
- **D3** Building ≠ Running
- **D4** Test end-to-end after deployment
- **D5** Deployment checklist

---

## .NET Dashboard Features (COMPLETE)

- ✅ REST API with stock data endpoints
- ✅ Interactive Plotly charts (candlestick, line)
- ✅ Moving average overlays (20, 50, 200-day)
- ✅ Ticker search with autocomplete
- ✅ Significant move markers (triangles)
- ✅ Wikipedia-style hover popups with cat images (cataas.com)
- ✅ Configurable threshold slider (3-10%)
- ✅ Security scans passed (SAST: 0, DAST: 114 passed)

---

## Pending Tasks (ROADMAP.md)

| Task | Description | Status |
|------|-------------|--------|
| Cats vs Dogs toggle | Radio button to choose cats or dogs for thumbnails | Planned |
| Image recognition | Ensure cat/dog faces are visible in thumbnails | Planned |
| Hosting research | Identify free/cheap hosting options | Planned |
| SRI for CDN scripts | Subresource Integrity hashes | Planned |
| Unit tests | xUnit test suite | Planned |

---

## Today's Session (01/16/2026)

**Slack improvements:**
- Added history sync (`--sync` flag) to catch missed messages
- Changed from reply acknowledgment to ✅ reaction only
- Fixed multiple listener issue (old code was handling messages)

**New guidelines:**
- #39: Slack reaction confirmation
- #40: Review security tools on new frameworks

**New deployment section:**
- D1-D5 deployment rules added
- Moved #28 and #34 into deployment section

**Commits today:**
- b5bda78 - Add deployment section to CLAUDE.md
- d03f7f0 - Replace Slack reply with reaction acknowledgment
- a113d28 - Add guidelines #39-40 from Slack history
- 54fa5ad - Add history sync to Slack listener

---

## Quick Start for New Session

**Say "hello!"** to restore context.

Then:
1. Check Slack: `python stock_analysis/helpers/slack_listener.py --sync`
2. Check tasks: `whileYouWereAway.md`

To run .NET app:
```
cd stock_analyzer_dotnet
dotnet run --project src/StockAnalyzer.Api
# Visit http://localhost:5000
```

**Say "night!"** at end of session to save state.
