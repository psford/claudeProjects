# Session State - Last Updated 01/16/2026 (11:45 PM)

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
- **Status:** Configured and working locally
- **User:** psford <patrick@psford.com>
- **Repository:** C:\Users\patri\Documents\claudeProjects (master branch)

### GitHub
- **Status:** NOT CONNECTED
- **Issue:** Windows credential manager had memory errors; token auth also failed
- **Pending:** CI/CD Jenkins workflow (depends on GitHub fix)

### Python
- **Version:** 3.10.11
- **Core packages:** yfinance, pandas, numpy, slack-sdk, slack-bolt, playwright, openai-whisper, python-dotenv, bandit

### .NET
- **Version:** .NET 8
- **Project:** stock_analyzer_dotnet (ASP.NET Core minimal API + Tailwind CSS frontend)

### Slack Integration
- **Status:** OPERATIONAL
- **Workspace:** psforddigitaldesign.slack.com
- **Channel:** #claude-notifications (C0A8LB49E1M)
- **Poll for messages:** `python helpers/slack_listener.py --poll`
- **Check inbox:** `python helpers/slack_listener.py --check`
- **Send message:** `python helpers/slack_notify.py "message"`
- **Add reaction:** `python helpers/slack_notify.py --react -c CHANNEL -ts TIMESTAMP`

---

## Project Structure

```
claudeProjects/
├── CLAUDE.md                    # Guidelines (9 themed sections)
├── sessionState.md              # This file
├── claudeLog.md                 # Action log
├── whileYouWereAway.md          # Task queue
├── .env                         # API keys (gitignored)
├── slack_inbox.json             # Slack messages (gitignored)
│
├── helpers/                     # Reusable Python scripts
│   ├── slack_listener.py        # Receive messages (--poll mode)
│   ├── slack_notify.py          # Send messages & reactions
│   ├── ui_test.py               # Playwright UI testing
│   ├── speech_to_text.py        # Whisper transcription
│   ├── Invoke-SpeechToText.ps1  # PowerShell wrapper
│   ├── security_scan.py         # SAST (Bandit)
│   └── checkpoint.py            # Session state saves
│
├── stock_analyzer_dotnet/       # Active .NET project
│   ├── docs/
│   │   ├── FUNCTIONAL_SPEC.md   # v1.8
│   │   └── TECHNICAL_SPEC.md    # v1.12
│   ├── ROADMAP.md
│   └── src/
│       ├── StockAnalyzer.Api/   # Web API + frontend
│       └── StockAnalyzer.Core/  # Business logic
│
└── archive/                     # Archived projects
    ├── stock_analysis_python/   # Original Python version
    └── CLAUDE_v1_original.md    # Pre-reorganization guidelines
```

---

## CLAUDE.md Structure (Reorganized)

9 themed sections replacing 46 numbered rules:
1. **Principles** - Core values (challenge me, admit limitations, cite sources, etc.)
2. **Session Protocol** - hello!/night!, checkpoints, between-tasks behavior
3. **Development Workflow** - Planning, coding standards, testing (Playwright), pre-commit
4. **Communication** - Research before asking, Slack integration
5. **File Management** - Version control, backups, archiving
6. **Security** - SAST/DAST scanning, pre-commit hooks
7. **Project Files Reference** - Quick reference table
8. **Stock Analyzer Specific** - Doc sync, build targets
9. **Deprecated** - Archived items

**Key additions this session:**
- "Admit limitations" principle - If I can't do something, say so immediately
- "Use Chocolatey" principle - Preferred Windows package manager
- Playwright for UI testing (smoke, verify, screenshot)
- React to ALL Slack messages when acknowledged (not just completed)
- Between-tasks: Check Slack when idle

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

---

## New Tools This Session

| Tool | Purpose | Usage |
|------|---------|-------|
| `ui_test.py` | Playwright UI testing | `python helpers/ui_test.py smoke http://localhost:5000` |
| `speech_to_text.py` | Whisper transcription | `python helpers/speech_to_text.py --duration 10` |
| Slack polling | Real-time message monitoring | `python helpers/slack_listener.py --poll` |
| Slack reactions | Acknowledge messages | `--react -c CHANNEL -ts TIMESTAMP` |

---

## Pending Tasks (whileYouWereAway.md)

- #8: Review roadmap and propose user stories
- #10: .NET rewrite (DONE - all features implemented)
- #12: CI/CD Jenkins workflow (blocked on GitHub)

---

## Today's Session Summary (01/16/2026)

**Bollinger Bands:** Added to charts (model, service, UI, rendering)

**Documentation page:** Already complete from previous session

**CLAUDE.md reorganization:** 46 flat rules → 9 themed sections

**New guidelines added:**
- "Admit limitations" - Don't pretend to have capabilities I lack
- "Use Chocolatey" - Preferred Windows package manager
- "Between tasks" - Check Slack when idle
- Updated Slack reaction rule - React to ALL messages when acknowledged

**New tooling:**
- Playwright for UI testing (screenshot, smoke, verify, check)
- OpenAI Whisper for speech-to-text (local, free)
- Slack polling mode (--poll, 10s interval)
- Slack reaction support (--react)

**Commits:**
- c0d979f - Add Bollinger Bands technical indicator
- 71ce069 - Reorganize CLAUDE.md: 46 rules → 9 themed sections
- 8438744 - Add speech-to-text using OpenAI Whisper
- edac024 - Add Playwright UI testing and Slack reaction support
- 60a44b2 - Add capability honesty principle
- 63c41e2 - Add Chocolatey preference
- 887000f - Update Slack reaction guideline
- 8b4b078 - Add polling mode to Slack listener

---

## Quick Start for New Session

**Say "hello!"** to restore context.

Then:
1. Check Slack: `python helpers/slack_listener.py --check`
2. Start poll listener (optional): `python helpers/slack_listener.py --poll`
3. Review tasks: Read `whileYouWereAway.md`

To run .NET app:
```powershell
cd stock_analyzer_dotnet
dotnet run --project src/StockAnalyzer.Api
# Visit http://localhost:5000
```

**Say "night!"** at end of session to save state.
