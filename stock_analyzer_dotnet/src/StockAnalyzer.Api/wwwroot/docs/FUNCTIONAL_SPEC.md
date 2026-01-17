# Functional Specification: Stock Analyzer Dashboard (.NET)

**Version:** 1.6
**Last Updated:** 2026-01-17
**Author:** Claude (AI Assistant)
**Status:** Production
**Audience:** Business Users, Product Owners, QA Testers

---

## 1. Executive Summary

### 1.1 Purpose

The Stock Analyzer Dashboard is a web-based tool that allows users to research publicly traded stocks through interactive charts, company information, and news analysis. It helps investors understand price movements by correlating significant market events with relevant news stories.

This document covers the **C#/.NET 8 implementation** with a custom HTML/CSS/JavaScript frontend.

### 1.2 Business Objectives

| Objective | Description |
|-----------|-------------|
| **Inform investment decisions** | Provide clear, visual stock data to support research |
| **Explain price movements** | Connect large price changes with news events |
| **Simplify technical analysis** | Make moving averages and trends accessible to non-experts |
| **Save research time** | Consolidate stock info, charts, and news in one place |

### 1.3 Target Users

| User Type | Description | Primary Use Case |
|-----------|-------------|------------------|
| Individual Investor | Person managing personal portfolio | Research stocks before buying/selling |
| Financial Analyst | Professional reviewing securities | Quick visual analysis of price history |
| Student | Learning about markets | Educational exploration of stock behavior |

---

## 2. Product Overview

### 2.1 What the System Does

The Stock Analyzer Dashboard allows users to:

1. **Search** for any publicly traded stock by company name or ticker symbol
2. **View** interactive price charts with customizable time periods
3. **Analyze** price trends using moving average overlays
4. **Identify** significant price movements (days with ±3% change or custom threshold)
5. **Read** news headlines associated with major price swings
6. **Review** key company metrics (P/E ratio, dividend yield, market cap, etc.)

### 2.2 What the System Does NOT Do

- Does not provide real-time streaming prices (data has ~15 minute delay)
- Does not execute trades or connect to brokerage accounts
- Does not provide investment recommendations or advice
- Does not store user data, portfolios, or watchlists
- Does not require user registration or login

---

## 3. Functional Requirements

### 3.1 Stock Search (FR-001)

| ID | Requirement |
|----|-------------|
| FR-001.1 | The system must allow users to search for stocks by typing in a search box |
| FR-001.2 | The system must display search results as the user types (autocomplete) |
| FR-001.3 | The system must show both ticker symbol and company name in search results |
| FR-001.4 | The system must show the stock exchange for each search result |
| FR-001.5 | The system must require at least 2 characters before showing results |
| FR-001.6 | The system must display up to 8 search results at a time |
| FR-001.7 | The system must debounce search input (300ms delay) |

**User Story:** *As an investor, I want to search for stocks by company name so that I don't need to memorize ticker symbols.*

### 3.2 Chart Display (FR-002)

| ID | Requirement |
|----|-------------|
| FR-002.1 | The system must display an interactive price chart for the selected stock |
| FR-002.2 | The system must support Candlestick chart type |
| FR-002.3 | The system must support Line chart type |
| FR-002.4 | The system must allow users to switch between chart types |
| FR-002.5 | The system must allow zooming via mouse scroll or touch pinch |
| FR-002.6 | The system must allow panning via mouse drag or touch swipe |
| FR-002.7 | The system must show price details on hover (Open, High, Low, Close) |
| FR-002.8 | The system must display volume bars below candlestick charts |

**User Story:** *As an investor, I want to see an interactive chart so that I can zoom into specific time periods of interest.*

### 3.3 Time Period Selection (FR-003)

| ID | Requirement |
|----|-------------|
| FR-003.1 | The system must allow users to select the chart time period |
| FR-003.2 | The system must support: YTD, 1 month, 3 months, 6 months, 1 year, 2 years, 5 years, 10 years |
| FR-003.3 | The system must default to 1 year when first loading a stock |
| FR-003.4 | The system must refresh the chart when the period is changed |

**Supported Periods:**

| Selection | Data Range |
|-----------|------------|
| YTD | January 1st of current year to today |
| 1mo | Last 30 calendar days |
| 3mo | Last 90 calendar days |
| 6mo | Last 180 calendar days |
| 1y | Last 365 calendar days |
| 2y | Last 730 calendar days |
| 5y | Last 1,825 calendar days |
| 10y | Last 3,650 calendar days |

### 3.4 Moving Averages (FR-004)

| ID | Requirement |
|----|-------------|
| FR-004.1 | The system must support overlay of 20-day moving average |
| FR-004.2 | The system must support overlay of 50-day moving average |
| FR-004.3 | The system must support overlay of 200-day moving average |
| FR-004.4 | The system must allow users to toggle each moving average independently |
| FR-004.5 | The system must display MA-20 and MA-50 by default |
| FR-004.6 | The system must display MA-200 only when user enables it |
| FR-004.7 | The system must use distinct colors for each moving average line |

**Moving Average Colors:**

| Indicator | Color |
|-----------|-------|
| SMA-20 | Orange (#FF9800) |
| SMA-50 | Purple (#9C27B0) |
| SMA-200 | Cyan (#00BCD4) |

### 3.5 Significant Move Detection (FR-005)

| ID | Requirement |
|----|-------------|
| FR-005.1 | The system must identify days where the stock moved by a configurable threshold (default ±5%) |
| FR-005.2 | The system must display significant moves in a dedicated panel |
| FR-005.3 | The system must show the date and percentage change for each move |
| FR-005.4 | The system must color-code moves (green for up, red for down) |
| FR-005.5 | The system must display triangle markers on the chart for significant moves |
| FR-005.6 | The system must allow users to adjust the threshold via a slider (3% to 10%) |
| FR-005.7 | The system must display a Wikipedia-style hover popup when hovering on chart markers |
| FR-005.8 | The hover popup must show: date, return %, news headline, summary, source, and thumbnail |
| FR-005.9 | The hover popup headline must be a clickable link to the full news article |
| FR-005.10 | The hover popup must remain visible when the user moves their mouse to interact with it |
| FR-005.11 | The system must allow users to choose between cat or dog images for popup thumbnails |
| FR-005.12 | The system must pre-cache 50 images of each type on page load for instant display |
| FR-005.13 | The system must automatically refill the image cache when it drops below 10 images |
| FR-005.14 | The system must use each cached image only once (no repeats) |
| FR-005.15 | The system must clear the previous image when hiding the popup to prevent flash |

**Calculation Method:** Daily return = (Today's Close - Today's Open) / Today's Open

**Chart Markers:**
| Direction | Symbol | Color |
|-----------|--------|-------|
| Positive (+N%) | Triangle Up | Green (#10B981) |
| Negative (-N%) | Triangle Down | Red (#EF4444) |

### 3.6 Company Information (FR-006)

| ID | Requirement |
|----|-------------|
| FR-006.1 | The system must display the company's full name as the title |
| FR-006.2 | The system must display the stock exchange and currency |
| FR-006.3 | The system must display the sector when available |
| FR-006.4 | The system must display security identifiers (Ticker, ISIN, CUSIP, SEDOL) when available |
| FR-006.5 | The system must display a company description/bio when available |
| FR-006.6 | The system must truncate long descriptions at sentence boundaries |
| FR-006.7 | The system must display the current price with day change |

### 3.7 Key Metrics (FR-007)

| ID | Requirement |
|----|-------------|
| FR-007.1 | The system must display market capitalization |
| FR-007.2 | The system must display the P/E (Price-to-Earnings) ratio |
| FR-007.3 | The system must display 52-week high and low |
| FR-007.4 | The system must display average volume |
| FR-007.5 | The system must display dividend yield as a percentage |
| FR-007.6 | The system must display "N/A" when a metric is unavailable |

### 3.8 Performance Summary (FR-008)

| ID | Requirement |
|----|-------------|
| FR-008.1 | The system must calculate and display total return for the selected period |
| FR-008.2 | The system must calculate and display annualized volatility |
| FR-008.3 | The system must display the highest close during the selected period |
| FR-008.4 | The system must display the lowest close during the selected period |
| FR-008.5 | The system must display average volume for the period |
| FR-008.6 | The system must color-code return (green for positive, red for negative) |

### 3.9 News Integration (FR-009)

| ID | Requirement |
|----|-------------|
| FR-009.1 | The system must display a "Recent News" section |
| FR-009.2 | The system must show up to 5 recent news articles |
| FR-009.3 | The system must display headline, source, and date for each article |
| FR-009.4 | The system must display article summary when available |
| FR-009.5 | The system must make headlines clickable links to the full article |
| FR-009.6 | The system must display "No recent news available" when no news exists |

### 3.10 Dark Mode (FR-010)

| ID | Requirement |
|----|-------------|
| FR-010.1 | The system must provide a dark mode toggle button in the header |
| FR-010.2 | The system must display a moon icon when in light mode (click to switch to dark) |
| FR-010.3 | The system must display a sun icon when in dark mode (click to switch to light) |
| FR-010.4 | The system must persist the user's dark mode preference across page reloads |
| FR-010.5 | The system must respect the user's system preference (prefers-color-scheme) on first visit |
| FR-010.6 | The system must apply dark mode styling to all UI elements (backgrounds, text, borders) |
| FR-010.7 | The system must apply dark mode styling to the Plotly chart (background, gridlines, text) |
| FR-010.8 | The system must provide smooth color transitions when toggling between modes |

**User Story:** *As a user who works at night, I want a dark mode so that the bright interface doesn't strain my eyes.*

**Color Scheme:**

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | Gray-50 (#F9FAFB) | Gray-900 (#111827) |
| Card Background | White (#FFFFFF) | Gray-800 (#1F2937) |
| Primary Text | Gray-900 (#111827) | White (#FFFFFF) |
| Secondary Text | Gray-600 (#4B5563) | Gray-300 (#D1D5DB) |
| Borders | Gray-200 (#E5E7EB) | Gray-700 (#374151) |
| Chart Background | White (#FFFFFF) | Gray-800 (#1F2937) |
| Chart Gridlines | Gray-200 (#E5E7EB) | Gray-700 (#374151) |

### 3.11 Technical Indicators (FR-011)

| ID | Requirement |
|----|-------------|
| FR-011.1 | The system must support RSI (Relative Strength Index) indicator |
| FR-011.2 | The system must support MACD (Moving Average Convergence Divergence) indicator |
| FR-011.3 | The system must allow users to toggle RSI display independently |
| FR-011.4 | The system must allow users to toggle MACD display independently |
| FR-011.5 | The system must display RSI in a separate panel below the price chart |
| FR-011.6 | The system must display MACD in a separate panel below the price chart |
| FR-011.7 | The RSI panel must show overbought (70) and oversold (30) reference lines |
| FR-011.8 | The MACD panel must show the MACD line, signal line, and histogram |
| FR-011.9 | The chart must dynamically resize to accommodate indicator panels |
| FR-011.10 | The system must use 14-period RSI calculation by default |
| FR-011.11 | The system must use standard MACD parameters (12, 26, 9) by default |

**User Story:** *As a technical trader, I want to see RSI and MACD indicators so that I can identify overbought/oversold conditions and momentum trends.*

**RSI Configuration:**

| Setting | Value |
|---------|-------|
| Default Period | 14 days |
| Range | 0-100 |
| Overbought Level | 70 |
| Oversold Level | 30 |
| Line Color | Purple (#8B5CF6) |

**MACD Configuration:**

| Setting | Value |
|---------|-------|
| Fast EMA Period | 12 days |
| Slow EMA Period | 26 days |
| Signal Period | 9 days |
| MACD Line Color | Blue (#3B82F6) |
| Signal Line Color | Orange (#F59E0B) |
| Histogram (Positive) | Green (rgba(16, 185, 129, 0.7)) |
| Histogram (Negative) | Red (rgba(239, 68, 68, 0.7)) |

**Chart Layout (Dynamic):**

| Configuration | Price Panel | RSI Panel | MACD Panel | Total Height |
|---------------|-------------|-----------|------------|--------------|
| No indicators | 100% | - | - | 400px |
| RSI only | 68% | 28% | - | 550px |
| MACD only | 68% | - | 28% | 550px |
| Both indicators | 50% | 21% | 25% | 700px |

### 3.12 Stock Comparison (FR-012)

| ID | Requirement |
|----|-------------|
| FR-012.1 | The system must allow users to compare the primary stock to a second stock or index |
| FR-012.2 | The system must provide a second search box labeled "Compare to (Optional)" |
| FR-012.3 | The system must provide quick benchmark buttons for SPY, QQQ, and ^DJI |
| FR-012.4 | The system must display both stocks as normalized percentage change from period start |
| FR-012.5 | The system must disable technical indicators (RSI/MACD) when comparing |
| FR-012.6 | The system must provide a "Clear Comparison" button to return to single-stock view |
| FR-012.7 | The system must re-fetch comparison data when the time period changes |
| FR-012.8 | The system must prevent comparing a stock to itself |
| FR-012.9 | The comparison chart must show a zero baseline reference line |
| FR-012.10 | The comparison chart title must show both stock symbols |

**User Story:** *As an investor, I want to compare a stock's performance to major indices so that I can evaluate relative performance.*

**Chart Layout (Comparison Mode):**

```
┌────────────────────────────────────────────────────┐
│  AAPL vs SPY - 1Y                                  │
├────────────────────────────────────────────────────┤
│                                                    │
│  % Change                                          │
│     ^                                              │
│     |    /\    /\          ── Primary (blue)       │
│  +10|   /  \  /  \    ___  -- Compare (orange)     │
│     |  /    \/    \  /   \                        │
│    0|------------------\---/--- (baseline)        │
│     |                   \/                        │
│  -10|                                              │
│     +---------------------------------> Date       │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Colors:**

| Element | Color | Hex |
|---------|-------|-----|
| Primary stock line | Blue (solid) | #3B82F6 |
| Comparison stock line | Orange (dashed) | #F59E0B |
| Baseline (0%) | Gray (dotted) | Theme-dependent |

---

## 4. User Interface Specifications

### 4.1 Page Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📈 Stock Analyzer             Powered by .NET 8 + Plotly.js  [🌙/☀️]   │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ [Search Box with Autocomplete] [Period ▼] [Chart Type ▼] [Analyze]│  │
│  │ ☑ SMA 20   ☑ SMA 50   ☐ SMA 200                                   │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────────┐  ┌────────────────────────────────┐│
│  │ SYMBOL                          │  │ Key Metrics                    ││
│  │ Company Name                    │  │ - Market Cap                   ││
│  │ Exchange • Currency             │  │ - P/E Ratio                    ││
│  │                    $XXX.XX      │  │ - 52W High/Low                 ││
│  │                    +X.XX (+X%)  │  │ - Avg Volume                   ││
│  └─────────────────────────────────┘  │ - Dividend Yield               ││
│                                       └────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    INTERACTIVE PLOTLY CHART                        │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │ Performance                 │  │ Significant Moves (>3%)          │  │
│  │ - Total Return              │  │ Date | +X.XX%                    │  │
│  │ - Volatility                │  │ Date | -X.XX%                    │  │
│  │ - Highest/Lowest Close      │  │ ...                              │  │
│  └─────────────────────────────┘  └──────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Recent News                                                        │ │
│  │ [Headline - Source • Date]                                         │ │
│  │ [Summary...]                                                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│  Stock Analyzer © 2026 | Data from Yahoo Finance & Finnhub              │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Search Controls

| Control | Type | Options | Default |
|---------|------|---------|---------|
| Search Stock | Text input with autocomplete dropdown | Any ticker/company | Empty |
| Time Period | Dropdown | 1mo, 3mo, 6mo, 1y, 2y, 5y | 1y |
| Chart Type | Dropdown | Candlestick, Line | Candlestick |
| SMA-20 | Checkbox | On/Off | On |
| SMA-50 | Checkbox | On/Off | On |
| SMA-200 | Checkbox | On/Off | Off |
| RSI (14) | Checkbox | On/Off | Off |
| MACD | Checkbox | On/Off | Off |
| Compare to | Text input with autocomplete | Any ticker/company | Empty |
| Quick Compare | Buttons | SPY, QQQ, ^DJI | - |
| Clear Comparison | Button | Click to remove comparison | Hidden |
| Threshold | Slider | 3% - 10% | 5% |
| Show Markers | Checkbox | On/Off | On |
| Popup Thumbnails | Radio | Cats, Dogs | Cats |
| Analyze | Button | Click to load data | - |

### 4.3 Color Scheme

| Element | Color | Hex Code |
|---------|-------|----------|
| Primary (buttons, links) | Blue | #3B82F6 |
| Success (positive) | Green | #10B981 |
| Danger (negative) | Red | #EF4444 |
| SMA-20 | Orange | #FF9800 |
| SMA-50 | Purple | #9C27B0 |
| SMA-200 | Cyan | #00BCD4 |

---

## 5. User Workflows

### 5.1 Basic Stock Research

**Goal:** View price chart and company info for a specific stock

**Steps:**
1. User opens application (http://localhost:5000)
2. User types company name in search box (e.g., "Apple")
3. System displays autocomplete suggestions after 300ms
4. User clicks on "AAPL - Apple Inc. (NMS)"
5. Ticker populates in search box
6. User clicks "Analyze" button
7. System loads chart, company info, metrics, and news
8. User reviews displayed information

**Success Criteria:** Chart and all info panels display correctly

### 5.2 Technical Analysis

**Goal:** Analyze stock using moving averages

**Steps:**
1. User searches for and analyzes a stock
2. User enables SMA-200 checkbox
3. System updates chart with 200-day moving average line
4. User changes period to "2y" for longer-term view
5. User clicks "Analyze" to refresh
6. User hovers over chart to see values at specific dates

**Success Criteria:** All selected MAs display with correct values

### 5.3 News Research

**Goal:** Understand recent news affecting a stock

**Steps:**
1. User searches for a stock (e.g., "Tesla")
2. User clicks "Analyze"
3. User scrolls to "Significant Moves" section to see large price changes
4. User scrolls to "Recent News" section
5. User reads headlines and summaries
6. User clicks headline link to read full article

**Success Criteria:** News displays with working links

---

## 6. Business Rules

### 6.1 Data Validation Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-001 | Dividend yield values above 10% are assumed to be data errors and divided by 100 |
| BR-002 | Missing numeric values display as "N/A" rather than 0 or blank |
| BR-003 | Market cap formats as Millions (M), Billions (B), or Trillions (T) based on size |
| BR-004 | All prices display in USD with exactly 2 decimal places |

### 6.2 Significant Move Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-005 | Default threshold for "significant move" is ±3% (configurable via API) |
| BR-006 | Daily return is calculated using close-to-close prices |
| BR-007 | Top 10 significant moves are displayed in the UI |

### 6.3 Search Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-008 | Search requires minimum 2 characters |
| BR-009 | Search is debounced by 300ms to prevent excessive API calls |
| BR-010 | Maximum 8 search results are displayed |

---

## 7. Acceptance Criteria

### 7.1 Search Functionality

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Type "AAPL" | Shows Apple Inc. in dropdown | |
| Type "Apple" | Shows AAPL - Apple Inc. in dropdown | |
| Type "A" (1 char) | No results shown | |
| Select result from dropdown | Ticker populates in search box | |
| Click Analyze after selection | Chart loads for selected ticker | |

### 7.2 Chart Functionality

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Analyze AAPL with default settings | Candlestick chart with SMA-20, SMA-50 | |
| Switch to Line chart | Chart changes to line format | |
| Change period to 5y | Chart shows 5 years of data after Analyze | |
| Enable SMA-200 | Cyan MA line appears on chart | |
| Zoom with scroll | Chart zooms in/out | |
| Hover on candle | Shows OHLC values | |

### 7.3 Error Handling

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Analyze invalid ticker "XXXXX" | Error message displayed | |
| Analyze stock with no dividends | Dividend Yield shows "N/A" | |
| No news available | Shows "No recent news available" | |

---

## 8. Constraints and Limitations

### 8.1 Data Constraints

| Constraint | Description | Impact |
|------------|-------------|--------|
| Data delay | Stock prices have ~15 minute delay | Not suitable for real-time trading |
| Historical limit | Maximum 10 years of daily data | Long-term analysis limited |
| Coverage | US and major international stocks only | Some markets not available |

### 8.2 Technical Constraints

| Constraint | Description | Impact |
|------------|-------------|--------|
| News rate limit | 60 news requests per minute (Finnhub free tier) | Heavy use may cause news delays |
| Browser-based | Requires modern browser with JavaScript | No mobile app version |
| Single user | No multi-user or login support | Not for team/enterprise use |

---

## 9. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.6 | 2026-01-17 | Added Stock Comparison (FR-012): Compare to second stock/index with normalized % change | Claude |
| 1.5 | 2026-01-16 | Added Technical Indicators (FR-011): RSI and MACD with dynamic chart panels | Claude |
| 1.4 | 2026-01-16 | Added Dark Mode (FR-010) with system preference detection | Claude |
| 1.1 | 2026-01-16 | Added cats/dogs toggle (FR-005.11), image pre-caching (FR-005.12-15) | Claude |
| 1.0 | 2026-01-16 | Initial .NET functional specification | Claude |

---

## 10. References

- [ASP.NET Core Documentation](https://docs.microsoft.com/en-us/aspnet/core/)
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Finnhub API Documentation](https://finnhub.io/docs/api)
