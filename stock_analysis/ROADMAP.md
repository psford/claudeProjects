# Future Enhancements Roadmap

Planned features and improvements for the claudeProjects codebase.

---

## Stock Analysis Tool

### High Priority

| Feature | Description | Status |
|---------|-------------|--------|
| Interactive charts (Plotly) | Add Plotly-based interactive charts with zoom, pan, hover data | **Complete** |
| Web dashboard (Streamlit) | Browser-based UI for stock analysis | **Complete** |
| Technical indicators | RSI, MACD, Bollinger Bands, Stochastic Oscillator | Planned |

### Medium Priority

| Feature | Description | Status |
|---------|-------------|--------|
| Multi-stock comparison chart | Visual comparison of multiple stocks on single chart | Planned |
| Portfolio tracker | Track holdings, calculate weighted returns | Planned |
| Earnings calendar integration | Show earnings dates on charts | Planned |
| Export to Excel | Export analysis data to .xlsx format | Planned |

### Low Priority / Nice to Have

| Feature | Description | Status |
|---------|-------------|--------|
| Real-time price streaming | WebSocket-based live price updates | Planned |
| News sentiment analysis | Integrate news API with sentiment scoring | Planned |
| Options chain analysis | Options data retrieval and Greeks calculation | Planned |
| Backtesting framework | Simple strategy backtesting capability | Planned |

---

## Infrastructure

### Security

| Feature | Description | Status |
|---------|-------------|--------|
| Static Analysis (SAST) | Bandit security scanner for Python code | **Complete** |
| Dynamic Analysis (DAST) | OWASP ZAP via Docker | **Complete** |
| Pre-commit hooks | Block commits with security issues | Planned |

### Security Headers (from ZAP scan 01/15/2026)

Production deployment should address these warnings. Low priority for local development.

| Header | Issue | Fix |
|--------|-------|-----|
| X-Frame-Options | Missing anti-clickjacking | Add `DENY` or `SAMEORIGIN` |
| X-Content-Type-Options | Missing nosniff | Add `nosniff` header |
| Content-Security-Policy | CSP not set | Define allowed sources |
| Permissions-Policy | Not set | Restrict browser features |
| Server | Version leak (Tornado) | Strip or customize header |
| Cross-Origin-Opener-Policy | Spectre isolation | Add COOP/COEP headers |

**Note:** These require a reverse proxy (nginx) or Streamlit middleware. Not applicable for localhost development.

### DevOps

| Feature | Description | Status |
|---------|-------------|--------|
| GitHub integration | Connect to remote repository | Blocked (auth issues) |
| Unit tests | pytest test suite for stock_analyzer | Planned |
| CI/CD pipeline | GitHub Actions for automated testing | Planned (needs GitHub) |
| Log archiving | Auto-archive logs >14 days when >1GB | Planned |

---

## Version History

| Date | Change |
|------|--------|
| 01/15/2026 | Completed: DAST (ZAP); added security headers section from scan results |
| 01/14/2026 | Completed: Interactive charts (Plotly) and Web dashboard (Streamlit) |
| 01/14/2026 | Initial roadmap created; added Plotly interactive charts to high priority |

