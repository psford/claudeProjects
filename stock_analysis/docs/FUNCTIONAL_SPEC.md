# Functional Specification: Stock Analyzer Dashboard (Python)

**Version:** 1.0
**Last Updated:** 2026-01-14
**Author:** Claude (AI Assistant)
**Status:** Production
**Audience:** Business Users, Product Owners, QA Testers

---

## 1. Executive Summary

### 1.1 Purpose

The Stock Analyzer Dashboard is a web-based tool that allows users to research publicly traded stocks through interactive charts, company information, and news analysis. It helps investors understand price movements by correlating significant market events with relevant news stories.

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
4. **Identify** significant price movements (days with ±5% change)
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
| FR-001.7 | The system must clear the display when the user clears the search box |

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
| FR-002.9 | The system must allow users to toggle volume display on/off |

**User Story:** *As an investor, I want to see an interactive chart so that I can zoom into specific time periods of interest.*

### 3.3 Time Period Selection (FR-003)

| ID | Requirement |
|----|-------------|
| FR-003.1 | The system must allow users to select the chart time period |
| FR-003.2 | The system must support: 1 month, 3 months, 6 months, 1 year, 2 years, 5 years |
| FR-003.3 | The system must default to 1 year when first loading a stock |
| FR-003.4 | The system must refresh the chart when the period is changed |

**Supported Periods:**

| Selection | Data Range |
|-----------|------------|
| 1mo | Last 30 calendar days |
| 3mo | Last 90 calendar days |
| 6mo | Last 180 calendar days |
| 1y | Last 365 calendar days |
| 2y | Last 730 calendar days |
| 5y | Last 1,825 calendar days |

### 3.4 Moving Averages (FR-004)

| ID | Requirement |
|----|-------------|
| FR-004.1 | The system must support overlay of 20-day moving average |
| FR-004.2 | The system must support overlay of 50-day moving average |
| FR-004.3 | The system must support overlay of 200-day moving average |
| FR-004.4 | The system must allow users to toggle each moving average independently |
| FR-004.5 | The system must display MA-20 and MA-50 by default |
| FR-004.6 | The system must display MA-200 only when user enables it |
| FR-004.7 | The system must show moving average values on hover |
| FR-004.8 | The system must use distinct colors for each moving average line |

**Moving Average Colors:**

| Indicator | Color |
|-----------|-------|
| MA-20 | Blue (#2196F3) |
| MA-50 | Orange (#FF9800) |
| MA-200 | Purple (#9C27B0) |

**User Story:** *As a technical analyst, I want to overlay moving averages on the chart so that I can identify trend direction and support/resistance levels.*

### 3.5 Significant Move Markers (FR-005)

| ID | Requirement |
|----|-------------|
| FR-005.1 | The system must identify days where the stock moved ±5% or more |
| FR-005.2 | The system must display green circle markers for +5% up days |
| FR-005.3 | The system must display red circle markers for -5% down days |
| FR-005.4 | The system must position up markers above the price bar |
| FR-005.5 | The system must position down markers below the price bar |
| FR-005.6 | The system must show the date and percentage change on marker hover |
| FR-005.7 | The system must show associated news headline on marker hover |

**Calculation Method:** Daily return = (Today's Close - Yesterday's Close) / Yesterday's Close

**User Story:** *As an investor, I want to see which days had big price moves so that I can understand what caused volatility.*

### 3.6 Company Information (FR-006)

| ID | Requirement |
|----|-------------|
| FR-006.1 | The system must display the company's full name |
| FR-006.2 | The system must display the company's business sector |
| FR-006.3 | The system must display the company's industry classification |
| FR-006.4 | The system must display the market capitalization |
| FR-006.5 | The system must format market cap in billions (B) or trillions (T) |

**Example Display:**
```
Company Info
Sector: Technology
Industry: Consumer Electronics
Market Cap: $2.89T
```

### 3.7 Price Data (FR-007)

| ID | Requirement |
|----|-------------|
| FR-007.1 | The system must display the current/latest stock price |
| FR-007.2 | The system must display the 52-week high price |
| FR-007.3 | The system must display the 52-week low price |
| FR-007.4 | The system must format all prices in USD with 2 decimal places |

### 3.8 Key Metrics (FR-008)

| ID | Requirement |
|----|-------------|
| FR-008.1 | The system must display the P/E (Price-to-Earnings) ratio |
| FR-008.2 | The system must display the dividend yield as a percentage |
| FR-008.3 | The system must display the beta coefficient |
| FR-008.4 | The system must display "N/A" when a metric is unavailable |

**Metric Definitions (for business users):**

| Metric | What It Means |
|--------|---------------|
| P/E Ratio | How much investors pay for $1 of company earnings. Higher = more expensive. |
| Dividend Yield | Annual dividend payment as % of stock price. Higher = more income. |
| Beta | How much the stock moves vs. the market. Beta > 1 = more volatile. |

### 3.9 Performance Summary (FR-009)

| ID | Requirement |
|----|-------------|
| FR-009.1 | The system must calculate and display total return for the selected period |
| FR-009.2 | The system must calculate and display annualized volatility |
| FR-009.3 | The system must display the highest price during the selected period |
| FR-009.4 | The system must display the lowest price during the selected period |
| FR-009.5 | The system must color-code return (green for positive, red for negative) |

### 3.10 News Integration (FR-010)

| ID | Requirement |
|----|-------------|
| FR-010.1 | The system must display a "Significant Moves" section below the chart |
| FR-010.2 | The system must list all days with ±5% price changes |
| FR-010.3 | The system must show the date and percentage for each significant move |
| FR-010.4 | The system must display a news thumbnail image when available |
| FR-010.5 | The system must display the news headline for each significant move |
| FR-010.6 | The system must make headlines clickable links to the full article |
| FR-010.7 | The system must display the news source name |
| FR-010.8 | The system must display "No news found" when no relevant news exists |
| FR-010.9 | The system must sort significant moves by date (most recent first) |

**News Sources:** Yahoo Finance, SeekingAlpha, CNBC, IBD, Zacks, Barrons, Benzinga

**User Story:** *As an investor, I want to see news headlines for big price moves so that I can understand what caused the stock to rise or fall.*

---

## 4. Data Mappings

### 4.1 Stock Info Data Mapping

| Display Field | Source | Transformation |
|---------------|--------|----------------|
| Company Name | `longName` | None |
| Sector | `sector` | None |
| Industry | `industry` | None |
| Market Cap | `marketCap` | Format as $X.XXB or $X.XXT |
| Current Price | `currentPrice` or `regularMarketPrice` | Format as $X.XX |
| 52-Week High | `fiftyTwoWeekHigh` | Format as $X.XX |
| 52-Week Low | `fiftyTwoWeekLow` | Format as $X.XX |
| P/E Ratio | `trailingPE` | Format as X.XX |
| Dividend Yield | `dividendYield` | Convert to %, validate range |
| Beta | `beta` | Format as X.XX |

### 4.2 Historical Price Data Mapping

| Display Field | Source Column | Description |
|---------------|---------------|-------------|
| Date | DataFrame index | Trading date |
| Open | `Open` | Opening price |
| High | `High` | Highest price of day |
| Low | `Low` | Lowest price of day |
| Close | `Close` | Closing price |
| Volume | `Volume` | Shares traded |

### 4.3 News Data Mapping

| Display Field | Source Field | Fallback |
|---------------|--------------|----------|
| Headline | `headline` or `title` | "No headline" |
| URL | `url` or `canonicalUrl.url` | None (not clickable) |
| Thumbnail | `image` or `thumbnail.originalUrl` | No image shown |
| Source | `source` or `provider.displayName` | "Unknown" |
| Summary | `summary` | Not displayed |

### 4.4 Calculated Fields

| Field | Formula | Example |
|-------|---------|---------|
| Daily Return | (Close[t] - Close[t-1]) / Close[t-1] | 0.05 = +5% |
| Cumulative Return | Product of (1 + daily returns) - 1 | 0.15 = +15% |
| Moving Average | Mean of last N closing prices | MA-20 = avg of last 20 days |
| Annualized Volatility | Std Dev of daily returns × √252 | 0.25 = 25% annual volatility |

---

## 5. User Interface Specifications

### 5.1 Page Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📈 Stock Analyzer Dashboard                                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐   ┌───────────────────────────────────────────────────┐│
│  │   SIDEBAR    │   │                                                   ││
│  │              │   │              MAIN CONTENT AREA                    ││
│  │ [Search Box] │   │                                                   ││
│  │              │   │   Company Name (TICKER)                           ││
│  │ Period: [▼]  │   │   ┌───────────────────────────────────────────┐  ││
│  │              │   │   │                                           │  ││
│  │ Chart: [▼]   │   │   │         INTERACTIVE CHART                 │  ││
│  │              │   │   │                                           │  ││
│  │ ☑ MA-20     │   │   │                                           │  ││
│  │ ☑ MA-50     │   │   └───────────────────────────────────────────┘  ││
│  │ ☐ MA-200    │   │                                                   ││
│  │              │   │   ┌─────────────┬─────────────┬─────────────┐    ││
│  │ ☑ Volume    │   │   │ Company     │ Price       │ Key         │    ││
│  │              │   │   │ Info        │ Data        │ Metrics     │    ││
│  │ [🔍 Analyze]│   │   └─────────────┴─────────────┴─────────────┘    ││
│  │              │   │                                                   ││
│  └──────────────┘   │   Performance Metrics                             ││
│                     │   [Return] [Volatility] [High] [Low]              ││
│                     │                                                   ││
│                     │   Significant Moves (±5%)                         ││
│                     │   ┌───────────────────────────────────────────┐  ││
│                     │   │ Date | Return | [Thumb] Headline [Source] │  ││
│                     │   │ Date | Return | [Thumb] Headline [Source] │  ││
│                     │   └───────────────────────────────────────────┘  ││
│                     └───────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────────┤
│  Data provided by Yahoo Finance. For informational purposes only.        │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Sidebar Controls

| Control | Type | Options | Default |
|---------|------|---------|---------|
| Search Stock | Text input with autocomplete | Any ticker/company | Empty |
| Time Period | Dropdown | 1mo, 3mo, 6mo, 1y, 2y, 5y | 1y |
| Chart Type | Dropdown | Candlestick, Line | Candlestick |
| MA-20 | Checkbox | On/Off | On |
| MA-50 | Checkbox | On/Off | On |
| MA-200 | Checkbox | On/Off | Off |
| Show Volume | Checkbox | On/Off | On |
| Analyze | Button | Click to refresh | - |

### 5.3 Color Scheme

| Element | Color | Hex Code |
|---------|-------|----------|
| Up candle / Positive | Green | #26a69a |
| Down candle / Negative | Red | #ef5350 |
| +5% marker | Green | #4CAF50 |
| -5% marker | Red | #F44336 |
| Close price line | Blue | #2196F3 |
| MA-20 | Blue | #2196F3 |
| MA-50 | Orange | #FF9800 |
| MA-200 | Purple | #9C27B0 |

---

## 6. User Workflows

### 6.1 Basic Stock Research

**Goal:** View price chart and company info for a specific stock

**Steps:**
1. User opens application (localhost:8501)
2. User types company name in search box (e.g., "Apple")
3. System displays autocomplete suggestions
4. User selects "AAPL - Apple Inc. (NASDAQ)"
5. System loads chart, company info, and performance metrics
6. User reviews displayed information

**Success Criteria:** Chart and all info panels display correctly

### 6.2 Technical Analysis

**Goal:** Analyze stock using moving averages

**Steps:**
1. User searches for and selects a stock
2. User enables MA-200 checkbox
3. System adds 200-day moving average line to chart
4. User changes period to "2y" for longer-term view
5. User hovers over chart to see MA values at specific dates
6. User identifies when price crosses above/below moving averages

**Success Criteria:** All selected MAs display with correct values

### 6.3 News Research

**Goal:** Understand why a stock had a large price movement

**Steps:**
1. User searches for a volatile stock (e.g., "Tesla")
2. User notices red/green markers on the chart
3. User hovers over a marker to see date, % change, and headline preview
4. User scrolls to "Significant Moves" section
5. User views thumbnail and full headline for the move
6. User clicks headline link to read full article

**Success Criteria:** News appears for significant move dates

---

## 7. Business Rules

### 7.1 Data Validation Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-001 | Dividend yield values above 10% are assumed to be data errors and divided by 100 |
| BR-002 | Missing numeric values display as "N/A" rather than 0 or blank |
| BR-003 | Market cap formats as Millions (M), Billions (B), or Trillions (T) based on size |
| BR-004 | All prices display in USD with exactly 2 decimal places |

### 7.2 Significant Move Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-005 | A "significant move" is defined as daily return ≥ +5% or ≤ -5% |
| BR-006 | Daily return is calculated using close-to-close prices |
| BR-007 | News lookup searches the move date plus 2 days prior |
| BR-008 | When multiple news articles exist, the most relevant one is selected |

### 7.3 News Relevance Rules

| Rule ID | Rule Description |
|---------|------------------|
| BR-009 | News mentioning the ticker symbol directly is prioritized (+100 score) |
| BR-010 | News mentioning company name or key executives is prioritized (+50 score) |
| BR-011 | Generic market news is deprioritized (-10 score per generic term) |
| BR-012 | Generic terms include: "market", "dow", "s&p", "nasdaq", "stocks", "wall street" |

---

## 8. Acceptance Criteria

### 8.1 Search Functionality

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Type "AAPL" | Shows Apple Inc. in results | |
| Type "Apple" | Shows AAPL - Apple Inc. in results | |
| Type "A" (1 char) | No results shown | |
| Clear search box | Chart and info panels clear | |
| Select result | Chart loads for selected ticker | |

### 8.2 Chart Functionality

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Load AAPL with default settings | Candlestick chart with volume, MA-20, MA-50 | |
| Switch to Line chart | Chart changes to line format | |
| Change period to 5y | Chart shows 5 years of data | |
| Enable MA-200 | Purple MA line appears | |
| Zoom with scroll | Chart zooms in/out | |
| Hover on candle | Shows OHLC values | |

### 8.3 Significant Moves

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Load volatile stock (TSLA, 1y) | Green/red markers visible on chart | |
| Hover on green marker | Shows date, +% change, news headline | |
| Hover on red marker | Shows date, -% change, news headline | |
| Check Significant Moves section | Lists moves with thumbnails and links | |
| Click news headline | Opens article in new tab | |

### 8.4 Error Handling

| Test | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Search invalid ticker "XXXXX" | "No data found" error message | |
| Load stock with no dividends | Dividend Yield shows "N/A" | |
| News unavailable for date | Shows "No news found for this date" | |

---

## 9. Constraints and Limitations

### 9.1 Data Constraints

| Constraint | Description | Impact |
|------------|-------------|--------|
| Data delay | Stock prices have ~15 minute delay | Not suitable for real-time trading |
| Historical limit | Maximum 5 years of daily data | Long-term analysis limited |
| Coverage | US and major international stocks only | Some markets not available |

### 9.2 Technical Constraints

| Constraint | Description | Impact |
|------------|-------------|--------|
| News rate limit | 60 news requests per minute | Heavy use may cause news delays |
| Browser-based | Requires modern browser with JavaScript | No mobile app version |
| Single user | No multi-user or login support | Not for team/enterprise use |

---

## 10. Future Enhancements

| Enhancement | Business Value | Status |
|-------------|----------------|--------|
| Technical indicators (RSI, MACD) | Advanced analysis for traders | Planned |
| Multi-stock comparison | Compare multiple stocks side-by-side | Planned |
| Portfolio tracker | Track holdings and performance | Planned |
| Export to Excel | Save data for offline analysis | Planned |
| Real-time prices | Live updates for active monitoring | Planned |

---

## 11. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-14 | Initial functional specification | Claude |
| 1.1 | 2026-01-16 | Separated into Python-specific spec (.NET moved to separate doc) | Claude |

---

## 12. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| Business Analyst | | | |
| QA Lead | | | |

---

## 13. References (Python)

- [Nuclino: Guide to Functional Requirements](https://www.nuclino.com/articles/functional-requirements)
- [AltexSoft: Functional and Non-Functional Requirements](https://www.altexsoft.com/blog/functional-and-non-functional-requirements-specification-and-types/)
- [TechTarget: Functional Specification Document Definition](https://www.techtarget.com/searchsoftwarequality/definition/functional-specification)
