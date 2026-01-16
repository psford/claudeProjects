# Session State - Last Updated 01/15/2026

Use this file to restore context when starting a new session. Say **"hello!"** to restore state.

---

<!-- CHECKPOINT_START -->
## Checkpoint (Auto-saved)

**Last checkpoint:** 2026-01-15 22:55:55

**Current state:** Implementing checkpoint system - guideline #30 added, helper script created

**Recovery:** If session ended unexpectedly, this checkpoint indicates where work was interrupted. Resume from here.

<!-- CHECKPOINT_END -->


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

### Streamlit Server
- **Status:** May be running in background
- **URL:** http://localhost:8501
- **Note:** Restart if needed with `streamlit run stock_analysis/app.py`

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
├── CLAUDE.md                        # Guidelines and known issues (24 guidelines)
├── claudeLog.md                     # Terminal action log
├── sessionState.md                  # This file
├── whileYouWereAway.md              # Task queue for rate-limited periods
├── claude_01*.md                    # Versioned CLAUDE.md backups
│
└── stock_analysis/                  # Stock Analysis Project
    ├── .env                         # API keys (FINNHUB, SLACK tokens) - gitignored
    ├── stock_analyzer.py            # Core analysis + charting + news functions
    ├── app.py                       # Streamlit web dashboard
    ├── dependencies.md              # Package and tool dependencies
    ├── ROADMAP.md                   # Future enhancements roadmap
    ├── docs/
    │   ├── TECHNICAL_SPEC.md        # System architecture, APIs, troubleshooting
    │   └── FUNCTIONAL_SPEC.md       # Business requirements, data mappings
    └── helpers/
        ├── security_scan.py         # SAST scanner wrapper (Bandit)
        ├── slack_notify.py          # Send Slack notifications
        └── slack_listener.py        # Receive Slack messages (Socket Mode)
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
22. **Context window efficiency** - Hot/cold storage; only load data when needed
23. **Check web before asking** - Search for syntax/best practices before asking user
24. **Local helper code** - Write reusable tools in helpers/, Unix philosophy

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
- Significant move markers (+/-5% daily change)
- News integration (Finnhub + yfinance) with relevance scoring
- Company info, price data, key metrics display
- Performance summary (return, volatility, high/low)
- Significant Moves panel with thumbnails and clickable headlines

### PENDING - NOT WORKING
- **Wikipedia-style hover previews on chart markers**
  - JavaScript injection approach attempted but not functional
  - Code is in place but hover card does not appear
  - DO NOT REFACTOR - needs investigation in next session

---

## Completed Tasks (01/15/2026)

| Task | Description | Result |
|------|-------------|--------|
| 1 | SAST static analyzer | Bandit installed, helpers/security_scan.py created |
| 2 | Context window guideline | Added as guideline #22 |
| 3 | Local helper code guideline | Added as guideline #24, helpers/ folder created |
| 5 | rules.md cleanup | Empty file deleted |
| 4 | Remote communication (Slack) | Full two-way integration via #claude-notifications |

---

## Pending Tasks (from whileYouWereAway.md)

| # | Task | Status |
|---|------|--------|
| 6 | DAST suggestions | Pending |
| 7 | "As a user" guideline | Pending |
| 8 | User stories from roadmap | Pending |
| 9 | Log archiving script | Pending |
| 10 | C#/.NET fork | Pending (moved to end) |

### Future (from ROADMAP.md)
- Technical indicators (RSI, MACD, Bollinger Bands)
- Multi-stock comparison chart
- Portfolio tracker
- Export to Excel
- Unit tests
- Wikipedia-style hover previews (BLOCKED - not working)

---

## Git History (Recent - 01/15/2026)

| Hash | Description |
|------|-------------|
| 7e40171 | Add Slack listener for two-way communication |
| 09bd277 | Add Slack integration for remote notifications |
| 425a053 | Add guidelines #22-24 (Tasks 2-3) |
| b20cbc2 | Add Bandit SAST security scanner |
| 92668db | Remove empty rules.md file |

---

## Quick Start for New Session

**Say "hello!"** to restore context automatically.

Then:
1. Check if Streamlit server is running: `curl http://localhost:8501`
2. If not, start it: `cd stock_analysis && streamlit run app.py`
3. Check `whileYouWereAway.md` for tasks
4. Continue with Task 6 (DAST suggestions)

**Say "night!"** at end of session to save state.
