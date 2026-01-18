# Session State - Last Updated 01/17/2026 (03:25 AM)

Use this file to restore context when starting a new session. Say **"hello!"** to restore state.

---

## User Profile

- **Name:** Patrick (psford)
- **Background:** Financial services business analyst, experience with Matlab, Python, Ruby
- **Preferred languages:** Python, TypeScript, HTML, CSS, C# (.NET)
- **Email:** patrick@psford.com

---

## Environment Status

### Git
- **Status:** Configured and working
- **User:** psford <patrick@psford.com>
- **Repository:** C:\Users\patri\Documents\claudeProjects (master branch)

### GitHub
- **Status:** CONNECTED (SSH auth)
- **Auth:** ED25519 SSH key (~/.ssh/github_ed25519)
- **Branch protection:** Enabled (PR reviews, status checks)
- **CI/CD:** GitHub Actions + Jenkins

### Python
- **Version:** 3.10.11
- **Core packages:** yfinance, pandas, numpy, slack-sdk, slack-bolt, playwright, openai-whisper, python-dotenv, bandit

### .NET
- **Version:** .NET 8
- **Project:** stock_analyzer_dotnet (ASP.NET Core minimal API + Tailwind CSS frontend)
- **Analyzers:** SecurityCodeScan, NetAnalyzers, Roslynator

### Slack Integration
- **Status:** OPERATIONAL (async bot)
- **Workspace:** psforddigitaldesign.slack.com
- **Channel:** #claude-notifications (C0A8LB49E1M)
- **Start bot:** `python helpers/slack_bot.py start`
- **Check status:** `python helpers/slack_bot.py status`
- **Stop bot:** `python helpers/slack_bot.py stop`

---

## Project Structure

```
claudeProjects/
├── CLAUDE.md                    # Guidelines
├── sessionState.md              # This file
├── claudeLog.md                 # Action log
├── whileYouWereAway.md          # Task queue
├── .env                         # API keys (gitignored)
├── slack_inbox.json             # Slack messages
│
├── .github/
│   ├── workflows/
│   │   ├── dotnet-ci.yml        # Build + test + security scan
│   │   └── codeql.yml           # Weekly SAST scans
│   ├── dependabot.yml           # Auto dependency updates
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── helpers/                     # Reusable Python scripts
│   ├── slack_bot.py             # Async bot manager (start/stop/status)
│   ├── slack_listener.py        # Receive messages
│   ├── slack_acknowledger.py    # Auto-acknowledge read messages
│   ├── slack_notify.py          # Send messages & reactions
│   ├── ui_test.py               # Playwright UI testing
│   ├── speech_to_text.py        # Whisper transcription
│   └── checkpoint.py            # Session state saves
│
├── stock_analyzer_dotnet/       # Active .NET project
│   ├── .editorconfig            # Analyzer rules (CA5xxx as errors)
│   ├── docs/
│   │   ├── FUNCTIONAL_SPEC.md   # v1.8
│   │   ├── TECHNICAL_SPEC.md    # v1.16
│   │   ├── CI_CD_SECURITY_PLAN.md
│   │   └── DOTNET_SECURITY_EVALUATION.md
│   ├── ROADMAP.md
│   └── src/
│       ├── StockAnalyzer.Api/   # Web API + frontend
│       │   └── wwwroot/
│       │       ├── index.html
│       │       ├── status.html  # Health dashboard
│       │       └── docs.html    # Documentation viewer
│       └── StockAnalyzer.Core/  # Business logic
│
└── archive/                     # Archived projects
```

---

## .NET Dashboard Features

- REST API with stock data endpoints
- Interactive Plotly charts (candlestick, line)
- Moving averages (SMA 20, 50, 200)
- Technical indicators: RSI, MACD, Bollinger Bands
- Stock comparison mode
- Significant move markers
- Cat/dog popup thumbnails
- Dark mode toggle
- Documentation page with search, TOC, architecture diagrams
- **NEW:** Health monitoring dashboard (/status.html)

---

## Security Tools

| Tool | Type | Integration |
|------|------|-------------|
| SecurityCodeScan | SAST | Build-time |
| NetAnalyzers | SAST | Build-time |
| Roslynator | Code quality | Build-time |
| CodeQL | SAST | GitHub Actions (weekly) |
| OWASP Dep Check | SCA | GitHub Actions |
| Dependabot | SCA | GitHub (auto-PRs) |
| Bandit | Python SAST | Pre-commit |
| detect-secrets | Secrets | Pre-commit |

---

## Today's Session Summary (01/17/2026)

**Health Monitoring Dashboard:**
- Created `/status.html` with real-time health status
- Shows API, Finnhub, Yahoo Finance status
- Endpoint response times, image cache levels
- Auto-refresh every 30 seconds, dark mode support

**Async Slack Bot:**
- Created `slack_acknowledger.py` - watches for read messages, sends checkmark
- Created `slack_bot.py` - manages listener + acknowledger as background services
- Listener and acknowledger run independently

**.NET Security Evaluation:**
- Added Microsoft.CodeAnalysis.NetAnalyzers to projects
- Added Roslynator.Analyzers to projects
- Created `.editorconfig` with CA5xxx security rules as errors
- Added OWASP Dependency Check to CI/CD workflow
- Created `dependabot.yml` for automated updates
- Created `DOTNET_SECURITY_EVALUATION.md` documentation

**New Guidelines Added:**
- "Update specs proactively" - Don't wait for reminders
- "Commit to GitHub" - Work isn't done until it's pushed

**Commits:**
- 1a46963 - Add health dashboard, async Slack bot, and .NET security tools
- 942aaed - Add 'update specs proactively' guideline

---

## Quick Start for New Session

**Say "hello!"** to restore context.

Then:
1. Start Slack bot: `python helpers/slack_bot.py start`
2. Check status: `python helpers/slack_bot.py status`
3. Review tasks: Read `whileYouWereAway.md`

To run .NET app:
```powershell
cd stock_analyzer_dotnet
dotnet run --project src/StockAnalyzer.Api
# Visit http://localhost:5000
# Status dashboard: http://localhost:5000/status.html
```

**Say "night!"** at end of session to save state.
