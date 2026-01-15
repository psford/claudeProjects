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
| Pre-commit hooks | Block commits with security issues | Planned |
| Dynamic Analysis (DAST) | Runtime security testing | Planned |

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
| 01/14/2026 | Completed: Interactive charts (Plotly) and Web dashboard (Streamlit) |
| 01/14/2026 | Initial roadmap created; added Plotly interactive charts to high priority |

