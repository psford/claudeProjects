# Technical Specification: Stock Analyzer Dashboard (.NET)

**Version:** 1.9
**Last Updated:** 2026-01-17
**Author:** Claude (AI Assistant)
**Status:** Production

---

## 1. Overview

### 1.1 Purpose

The Stock Analyzer Dashboard is a web-based application that provides interactive stock market analysis, visualization, and news integration. It enables users to research equity securities through charts, financial metrics, and news correlation for significant price movements.

This document covers the **C#/.NET 8 implementation** with a custom HTML/CSS/JavaScript frontend using Tailwind CSS and Plotly.js.

### 1.2 Scope

This specification covers:
- System architecture and component interactions
- Data sources and API integrations
- Deployment and runtime requirements
- Configuration and environment setup
- Troubleshooting procedures

### 1.3 Glossary

| Term | Definition |
|------|------------|
| OHLCV | Open, High, Low, Close, Volume - standard price data format |
| SMA | Simple Moving Average - trend indicator calculated over N periods |
| EMA | Exponential Moving Average - weighted moving average with more recent emphasis |
| RSI | Relative Strength Index - momentum oscillator measuring overbought/oversold conditions (0-100) |
| MACD | Moving Average Convergence Divergence - trend-following momentum indicator |
| Ticker | Unique stock symbol (e.g., AAPL for Apple Inc.) |
| Significant Move | Daily price change of ±3% or greater (configurable) |
| Minimal APIs | ASP.NET Core lightweight API approach without controllers |
| Finnhub | Third-party financial news API service |
| Dog CEO API | Third-party random dog image API |
| cataas | Cat as a Service - random cat image API |
| ONNX | Open Neural Network Exchange - portable ML model format |
| YOLOv8 | You Only Look Once v8 - object detection model |
| COCO | Common Objects in Context - ML dataset with 80 object classes |
| ISIN | International Securities Identification Number (12-char global identifier) |
| CUSIP | Committee on Uniform Securities Identification Procedures (9-char US/Canada) |
| SEDOL | Stock Exchange Daily Official List (7-char UK/Ireland identifier) |
| OpenFIGI | Bloomberg's free identifier mapping API |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Browser                                │
│                        (localhost:5000)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ASP.NET Core Web API                             │
│                   (StockAnalyzer.Api)                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐ │
│  │ wwwroot/       │  │ Minimal APIs   │  │ Static Files           │ │
│  │ - index.html   │  │ - /api/stock/* │  │ - Tailwind CSS CDN     │ │
│  │ - js/*.js      │  │ - /api/search  │  │ - Plotly.js CDN        │ │
│  │               │  │ - /api/trending│  │                        │ │
│  └────────────────┘  └────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    StockAnalyzer.Core Library                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Models:                    Services:                           │ │
│  │ - StockInfo               - StockDataService (Yahoo Finance)   │ │
│  │ - OhlcvData               - NewsService (Finnhub)              │ │
│  │ - HistoricalDataResult    - AnalysisService (MAs, Volatility)  │ │
│  │ - NewsItem/NewsResult     - ImageProcessingService (ML/ONNX)   │ │
│  │ - SignificantMove         - ImageCacheService (Background)     │ │
│  │ - SearchResult                                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌────────────────────────────┐    ┌────────────────────────────────────┐
│   OoplesFinance.Yahoo      │    │         Finnhub REST API           │
│   FinanceAPI (NuGet)       │    │                                    │
│                             │    │                                    │
│  - GetSummaryDetailsAsync  │    │  - Company news                    │
│  - GetAssetProfileAsync    │    │  - Company profile (ISIN, CUSIP)   │
│  - GetHistoricalDataAsync  │    │  - News images                     │
│  - GetTopTrendingStocks    │    │  - Article URLs                    │
│                             │    │                                    │
└────────────────────────────┘    └────────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌────────────────────────────┐    ┌────────────────────────────────────┐
│  Yahoo Finance Search API  │    │       OpenFIGI REST API            │
│  (Direct HTTP Client)      │    │       (Bloomberg)                   │
│                             │    │                                    │
│  - Ticker search by name   │    │  - SEDOL lookup from ISIN          │
│  - Company name lookup     │    │  - Identifier mapping              │
└────────────────────────────┘    └────────────────────────────────────┘
         │
         ▼
┌────────────────────────────┐
│  Yahoo Finance Search API  │
│  (Direct HTTP Client)      │
│                             │
│  - Ticker search by name   │
│  - Company name lookup     │
└────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     Image Processing (Server-Side)                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  ImageProcessingService             ImageCacheService           │ │
│  │  ┌──────────────────────┐          ┌──────────────────────┐   │ │
│  │  │ YOLOv8n ONNX Model   │          │ BackgroundService    │   │ │
│  │  │ - Detect cat/dog     │    ───>  │ - Maintain 50+ cache │   │ │
│  │  │ - Crop to center     │          │ - Auto-refill < 10   │   │ │
│  │  │ - Resize 320×150     │          │ - Thread-safe queue  │   │ │
│  │  └──────────────────────┘          └──────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│              ┌───────────────┴───────────────┐                      │
│              ▼                               ▼                      │
│  ┌────────────────────────────┐    ┌────────────────────────────┐  │
│  │   Dog CEO API              │    │   cataas.com               │  │
│  │   (dog.ceo)                │    │   (Cat as a Service)       │  │
│  │  - /api/breeds/image/     │    │  - /cat?width=640&height=  │  │
│  │    random                  │    │    640&{cacheBuster}       │  │
│  └────────────────────────────┘    └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Description

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Web API | `StockAnalyzer.Api/Program.cs` | REST endpoints, static file serving |
| Core Library | `StockAnalyzer.Core/` | Business logic, data models, services |
| Frontend | `StockAnalyzer.Api/wwwroot/` | HTML/CSS/JS user interface |
| Configuration | `appsettings.json` | API keys, environment settings |

### 2.3 Technology Stack

| Layer | Technology | Version/Notes |
|-------|------------|---------------|
| Runtime | .NET | 8.0 LTS |
| Web Framework | ASP.NET Core Minimal APIs | Built-in |
| Stock Data | OoplesFinance.YahooFinanceAPI | NuGet 1.7.1 |
| Ticker Search | Yahoo Finance Search API | Direct HttpClient |
| News Data | Finnhub REST API | Custom HttpClient |
| ML Runtime | Microsoft.ML.OnnxRuntime | NuGet 1.17.0 |
| Image Processing | SixLabors.ImageSharp | NuGet 3.1.7 |
| Object Detection | YOLOv8n ONNX | ~12MB model |
| Charting | Plotly.js | 2.27.0 (CDN) |
| CSS Framework | Tailwind CSS | CDN |
| Serialization | System.Text.Json | Built-in |

---

## 3. API Endpoints

### 3.1 Endpoint Reference

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/stock/{ticker}` | GET | Stock information | `ticker`: Stock symbol |
| `/api/stock/{ticker}/history` | GET | Historical OHLCV data | `ticker`, `period` (optional, default: 1y) |
| `/api/stock/{ticker}/news` | GET | Company news | `ticker`, `days` (optional, default: 30) |
| `/api/stock/{ticker}/significant` | GET | Significant price moves | `ticker`, `threshold` (optional, default: 3.0) |
| `/api/stock/{ticker}/analysis` | GET | Performance metrics + MAs | `ticker`, `period` (optional) |
| `/api/search` | GET | Ticker search | `q`: Search query (min 2 chars) |
| `/api/trending` | GET | Trending stocks | `count` (optional, default: 10) |
| `/api/images/cat` | GET | ML-processed cat image | None |
| `/api/images/dog` | GET | ML-processed dog image | None |
| `/api/images/status` | GET | Image cache status | None |
| `/api/health` | GET | Health check | None |

### 3.2 Response Examples

**GET /api/stock/AAPL**
```json
{
  "symbol": "AAPL",
  "shortName": "Apple Inc",
  "longName": "Apple Inc",
  "sector": "Technology",
  "industry": "Technology",
  "website": "https://www.apple.com/",
  "country": "US",
  "currency": "USD",
  "exchange": "NASDAQ NMS - GLOBAL MARKET",
  "isin": null,
  "cusip": null,
  "sedol": null,
  "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...",
  "fullTimeEmployees": 164000,
  "currentPrice": 198.50,
  "previousClose": 197.25,
  "dayHigh": 199.00,
  "dayLow": 196.50,
  "marketCap": 3050000000000,
  "peRatio": 31.25,
  "dividendYield": 0.0044,
  "fiftyTwoWeekHigh": 199.62,
  "fiftyTwoWeekLow": 164.08
}
```

**Note:** ISIN/CUSIP/SEDOL availability depends on data source (Finnhub free tier may not include all identifiers).

**GET /api/search?q=apple**
```json
{
  "query": "apple",
  "results": [
    {
      "symbol": "AAPL",
      "shortName": "Apple Inc.",
      "longName": "Apple Inc.",
      "exchange": "NMS",
      "type": "EQUITY",
      "displayName": "AAPL - Apple Inc. (NMS)"
    }
  ]
}
```

**GET /api/stock/AAPL/history?period=1mo**
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "startDate": "2025-12-16",
  "endDate": "2026-01-16",
  "data": [
    {
      "date": "2025-12-16",
      "open": 195.50,
      "high": 197.00,
      "low": 195.00,
      "close": 196.75,
      "volume": 45000000
    }
  ]
}
```

---

## 4. Data Models

### 4.1 StockInfo

```csharp
public record StockInfo
{
    public required string Symbol { get; init; }
    public string? ShortName { get; init; }
    public string? LongName { get; init; }
    public string? Sector { get; init; }
    public string? Industry { get; init; }
    public string? Website { get; init; }
    public string? Country { get; init; }
    public string? Currency { get; init; }
    public string? Exchange { get; init; }

    // Security identifiers
    public string? Isin { get; init; }
    public string? Cusip { get; init; }
    public string? Sedol { get; init; }

    // Company profile
    public string? Description { get; init; }
    public int? FullTimeEmployees { get; init; }

    public decimal? CurrentPrice { get; init; }
    public decimal? PreviousClose { get; init; }
    public decimal? Open { get; init; }
    public decimal? DayHigh { get; init; }
    public decimal? DayLow { get; init; }
    public long? Volume { get; init; }
    public long? AverageVolume { get; init; }

    public decimal? MarketCap { get; init; }
    public decimal? PeRatio { get; init; }
    public decimal? DividendYield { get; init; }
    public decimal? FiftyTwoWeekHigh { get; init; }
    public decimal? FiftyTwoWeekLow { get; init; }
}
```

### 4.2 SearchResult

```csharp
public record SearchResult
{
    public required string Symbol { get; init; }
    public required string ShortName { get; init; }
    public string? LongName { get; init; }
    public string? Exchange { get; init; }
    public string? Type { get; init; }
    public string DisplayName => $"{Symbol} - {ShortName}" +
        (Exchange != null ? $" ({Exchange})" : "");
}
```

### 4.3 OhlcvData

```csharp
public record OhlcvData
{
    public DateTime Date { get; init; }
    public decimal Open { get; init; }
    public decimal High { get; init; }
    public decimal Low { get; init; }
    public decimal Close { get; init; }
    public long Volume { get; init; }
    public decimal? AdjustedClose { get; init; }
}
```

### 4.4 SignificantMove

```csharp
public record SignificantMove
{
    public DateTime Date { get; init; }
    public decimal PercentChange { get; init; }
    public decimal ClosePrice { get; init; }
    public long Volume { get; init; }
    public NewsItem? RelatedNews { get; init; }
}
```

### 4.5 RsiData

```csharp
public record RsiData
{
    public required DateTime Date { get; init; }
    public decimal? Rsi { get; init; }  // 0-100, null when insufficient data
}
```

### 4.6 MacdData

```csharp
public record MacdData
{
    public required DateTime Date { get; init; }
    public decimal? MacdLine { get; init; }     // Fast EMA - Slow EMA
    public decimal? SignalLine { get; init; }   // 9-period EMA of MACD line
    public decimal? Histogram { get; init; }    // MACD line - Signal line
}
```

### 4.7 CompanyProfile

```csharp
public record CompanyProfile
{
    public required string Symbol { get; init; }
    public string? Name { get; init; }
    public string? Country { get; init; }
    public string? Currency { get; init; }
    public string? Exchange { get; init; }
    public string? Industry { get; init; }
    public string? WebUrl { get; init; }
    public string? Logo { get; init; }
    public string? IpoDate { get; init; }
    public decimal? MarketCapitalization { get; init; }
    public decimal? ShareOutstanding { get; init; }

    // Security identifiers
    public string? Isin { get; init; }
    public string? Cusip { get; init; }
    public string? Sedol { get; init; }
}
```

---

## 5. Services

### 5.1 StockDataService

**File:** `StockAnalyzer.Core/Services/StockDataService.cs`

| Method | Description |
|--------|-------------|
| `GetStockInfoAsync(symbol)` | Fetch stock info + asset profile via OoplesFinance |
| `GetHistoricalDataAsync(symbol, period)` | Fetch OHLCV history |
| `SearchAsync(query)` | Search tickers via Yahoo Finance API |
| `GetTrendingStocksAsync(count)` | Get trending stocks |

**Stock Info Implementation:**
Fetches both summary details and asset profile from Yahoo Finance:
- `GetSummaryDetailsAsync(symbol)` - Price data, ratios, metrics
- `GetAssetProfileAsync(symbol)` - Company description, sector, industry, employees

**Search Implementation:**
Uses direct HTTP call to Yahoo Finance Search API since OoplesFinance doesn't provide search:
```
https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=8&newsCount=0
```

### 5.2 NewsService

**File:** `StockAnalyzer.Core/Services/NewsService.cs`

| Method | Description |
|--------|-------------|
| `GetCompanyNewsAsync(symbol, fromDate)` | Fetch news from Finnhub |
| `GetCompanyProfileAsync(symbol)` | Fetch company profile with identifiers from Finnhub |
| `GetSedolFromIsinAsync(isin)` | Look up SEDOL via OpenFIGI API |

**Finnhub News Endpoint:**
```
GET https://finnhub.io/api/v1/company-news?symbol={symbol}&from={date}&to={date}&token={api_key}
```

**Finnhub Profile Endpoint:**
```
GET https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}
```
Returns: name, country, currency, exchange, industry, weburl, logo, isin, cusip

**OpenFIGI Endpoint:**
```
POST https://api.openfigi.com/v3/mapping
Body: [{"idType": "ID_ISIN", "idValue": "{isin}"}]
```
Used to look up SEDOL for UK/Irish securities from ISIN.

### 5.3 AnalysisService

**File:** `StockAnalyzer.Core/Services/AnalysisService.cs`

| Method | Description |
|--------|-------------|
| `CalculateMovingAverages(data)` | Calculate SMA-20, SMA-50, SMA-200 |
| `CalculatePerformance(data)` | Calculate return, volatility, high/low |
| `DetectSignificantMovesAsync(...)` | Find moves exceeding threshold |
| `CalculateRsi(data, period)` | Calculate RSI using Wilder's smoothing |
| `CalculateMacd(data, fast, slow, signal)` | Calculate MACD line, signal line, histogram |
| `CalculateEma(values, period)` | Private helper for EMA calculation |

**RSI Calculation (Wilder's Smoothing Method):**
```
1. Calculate price changes (gains and losses)
2. Initial average: SMA of first N gains/losses
3. Subsequent: avgGain = (prevAvgGain × (period-1) + currentGain) / period
4. RS = avgGain / avgLoss
5. RSI = 100 - (100 / (1 + RS))
```

**MACD Calculation:**
```
1. Fast EMA = 12-period EMA of close prices
2. Slow EMA = 26-period EMA of close prices
3. MACD Line = Fast EMA - Slow EMA
4. Signal Line = 9-period EMA of MACD Line
5. Histogram = MACD Line - Signal Line
```

**EMA Formula:**
```
Multiplier = 2 / (period + 1)
EMA = (Current Price - Previous EMA) × Multiplier + Previous EMA
```

### 5.4 ImageProcessingService

**File:** `StockAnalyzer.Core/Services/ImageProcessingService.cs`

| Method | Description |
|--------|-------------|
| `GetProcessedCatImageAsync()` | Fetch, detect, crop, and return cat image |
| `GetProcessedDogImageAsync()` | Fetch, detect, crop, and return dog image |
| `ProcessImage(imageData, classId)` | Run YOLO detection and crop |
| `DetectAnimal(image, classId)` | Find animal bounding box via ONNX inference |
| `CropToTarget(image, detection)` | Crop 320×150 centered on detection |

**ML Model:**
- **Model:** YOLOv8n (nano) exported to ONNX
- **Input:** 640×640 RGB image, normalized to 0-1
- **Output:** (1, 84, 8400) tensor - 4 bbox coords + 80 COCO class probabilities
- **Classes:** Cat=15, Dog=16 (COCO class indices)
- **Threshold:** 0.25 confidence for detection

### 5.5 ImageCacheService

**File:** `StockAnalyzer.Core/Services/ImageCacheService.cs`

Implements `BackgroundService` for continuous cache maintenance.

| Method | Description |
|--------|-------------|
| `GetCatImage()` | Dequeue processed cat image from cache |
| `GetDogImage()` | Dequeue processed dog image from cache |
| `GetCacheStatus()` | Return (cats, dogs) count tuple |
| `ExecuteAsync(token)` | Background loop monitoring cache levels |

**Cache Configuration:**
- **Cache Size:** 50 images per type (configurable)
- **Refill Threshold:** 10 images (triggers background refill)
- **Storage:** `ConcurrentQueue<byte[]>` for thread-safe access
- **Refill Delay:** 500ms between cache checks

---

## 6. Frontend Architecture

### 6.1 File Structure

```
wwwroot/
├── index.html          # Main page with Tailwind CSS layout
├── docs.html           # Documentation viewer page
├── docs/               # Markdown documentation files
│   ├── CLAUDE.md
│   ├── FUNCTIONAL_SPEC.md
│   └── TECHNICAL_SPEC.md
└── js/
    ├── api.js          # API client wrapper
    ├── app.js          # Main application logic
    └── charts.js       # Plotly chart configuration
```

### 6.2 JavaScript Modules

**api.js** - REST API client:
```javascript
const API = {
    baseUrl: '/api',
    getStockInfo(ticker) { ... },
    getHistory(ticker, period) { ... },
    getAnalysis(ticker, period) { ... },
    getSignificantMoves(ticker, threshold) { ... },
    getNews(ticker, days) { ... },
    search(query) { ... }
};
```

**app.js** - Application controller:
- Event binding (search, period change, chart type)
- Autocomplete with debouncing (300ms)
- Data rendering (stock info, metrics, news)
- State management (currentTicker, historyData)
- Image cache management (prefetch, refill, consume)
- Hover card display with cached images

**charts.js** - Plotly configuration:
- Candlestick chart traces
- Line chart traces
- Moving average overlays
- Responsive layout
- Theme-aware colors (light/dark mode)

### 6.3 Dark Mode Implementation

The application supports light and dark color themes via Tailwind CSS class-based dark mode.

**Configuration:**
```javascript
// tailwind.config in index.html
tailwind.config = {
    darkMode: 'class',  // Enable class-based dark mode
    ...
}
```

**Implementation Details:**

| Component | Implementation |
|-----------|---------------|
| Toggle Button | Sun/moon icons in header, click handler toggles `dark` class on `<html>` |
| Persistence | localStorage key `darkMode` stores `'true'` or `'false'` |
| System Preference | `window.matchMedia('(prefers-color-scheme: dark)')` for initial state |
| Static Elements | Tailwind `dark:` prefix classes (e.g., `dark:bg-gray-800 dark:text-white`) |
| Dynamic Elements | JavaScript renders `dark:` classes in template strings |
| Plotly Charts | `Charts.getThemeColors()` returns colors based on `document.documentElement.classList.contains('dark')` |

**Initialization Flow:**
```
Page Load → initDarkMode()
                ↓
    Check localStorage('darkMode')
                ↓
    If null → Check system preference
                ↓
    Apply 'dark' class to <html> if needed
                ↓
    Update icon visibility (sun/moon)
```

**Theme Toggle Flow:**
```
User clicks toggle → Toggle 'dark' class on <html>
                          ↓
                   Save to localStorage
                          ↓
                   Update icons
                          ↓
                   If chart exists → Re-render with new theme colors
```

### 6.4 Autocomplete Flow

```
User types → 300ms debounce → API.search(query) → Show dropdown
                                    ↓
User clicks result → Populate input → Hide dropdown
                                    ↓
User clicks Analyze → analyzeStock() → Load all data
```

### 6.5 Image Caching System

The application pre-caches ML-processed animal images for instant display in hover popups.
Images are fetched from the backend API, which handles ML detection and cropping server-side.

**Cache Configuration:**
```javascript
imageCache: {
    cats: [],           // Array of blob URLs from backend
    dogs: [],           // Array of blob URLs from backend
    isRefilling: { cats: false, dogs: false }  // Prevent concurrent refills
},
IMAGE_CACHE_SIZE: 50,       // Number of images to fetch per refill
IMAGE_CACHE_THRESHOLD: 10   // Trigger refill when cache drops below this
```

**Cache Flow:**
```
Page Load → prefetchImages()
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
fetchImagesFromBackend    fetchImagesFromBackend
('dogs', 50)              ('cats', 50)
    ↓                       ↓
GET /api/images/dog       GET /api/images/cat
(×50 requests)            (×50 requests)
    ↓                       ↓
Convert blob to URL       Convert blob to URL
    ↓                       ↓
Add to imageCache.dogs    Add to imageCache.cats
```

**Image Consumption:**
```
Hover on marker → getImageFromCache(type)
                        ↓
                  Remove blob URL from cache (no repeats)
                        ↓
                  Check cache.length < 10?
                        ↓ Yes
                  Trigger background refill from backend
```

**Backend Image Processing:**

| Endpoint | Response | Processing |
|----------|----------|------------|
| `GET /api/images/cat` | JPEG 320×150 | YOLOv8n detection → center crop |
| `GET /api/images/dog` | JPEG 320×150 | YOLOv8n detection → center crop |
| `GET /api/images/status` | JSON | Cache counts and timestamp |

---

## 7. Configuration

### 7.1 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FINNHUB_API_KEY` | Yes | Finnhub API authentication key |

**Configuration Priority:**
1. `appsettings.json` → `Finnhub:ApiKey`
2. Environment variable `FINNHUB_API_KEY`

### 7.2 appsettings.json

```json
{
  "Finnhub": {
    "ApiKey": "your_api_key_here"
  },
  "ImageProcessing": {
    "ModelPath": "MLModels/yolov8n.onnx",
    "CacheSize": 50,
    "RefillThreshold": 10,
    "TargetWidth": 320,
    "TargetHeight": 150
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

### 7.3 Program.cs Configuration

```csharp
// CORS for frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Service registration
builder.Services.AddSingleton<StockDataService>();
builder.Services.AddSingleton<NewsService>();
builder.Services.AddSingleton<AnalysisService>();
builder.Services.AddSingleton<ImageProcessingService>();
builder.Services.AddSingleton<ImageCacheService>();
builder.Services.AddHostedService(sp => sp.GetRequiredService<ImageCacheService>());
```

---

## 8. Testing

### 8.1 Test Project Structure

```
tests/
└── StockAnalyzer.Core.Tests/
    ├── StockAnalyzer.Core.Tests.csproj
    ├── Services/
    │   ├── AnalysisServiceTests.cs      # 14 tests
    │   ├── NewsServiceTests.cs          # 11 tests
    │   └── StockDataServiceTests.cs     # 15 tests (3 skipped integration)
    ├── Models/
    │   └── ModelCalculationTests.cs     # 27 tests
    └── TestHelpers/
        └── TestDataFactory.cs           # Test data generators
```

### 8.2 Test Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| xUnit | 2.6.6 | Test framework |
| xUnit.runner.visualstudio | 2.5.6 | Test runner |
| Microsoft.NET.Test.Sdk | 17.9.0 | Test SDK |
| Moq | 4.20.70 | Mocking framework |
| FluentAssertions | 6.12.0 | Assertion library |
| coverlet.collector | 6.0.0 | Code coverage |

### 8.3 Test Coverage

| Category | Tests | Description |
|----------|-------|-------------|
| AnalysisService | 27 | Moving averages, significant moves, performance, RSI, MACD calculations |
| NewsService | 11 | HTTP mocking, date range handling, JSON parsing |
| StockDataService | 12 | Query validation, period mapping, dividend yield fix |
| Model Calculations | 27 | Calculated properties on record types |
| **Total** | **77** | Plus 3 skipped integration tests |

### 8.4 Running Tests

```bash
# Run all tests
cd stock_analyzer_dotnet
dotnet test

# Run with verbose output
dotnet test --logger "console;verbosity=detailed"

# Run specific test class
dotnet test --filter "FullyQualifiedName~AnalysisServiceTests"

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

### 8.5 Mocking Strategy

**NewsService:** Constructor accepts optional `HttpClient` for dependency injection:
```csharp
public NewsService(string apiKey, HttpClient? httpClient = null)
```

**AnalysisService:** Constructor accepts optional `NewsService`:
```csharp
public AnalysisService(NewsService? newsService = null)
```

**StockDataService:** Uses concrete `YahooClient` from OoplesFinance. Full mocking would require introducing an interface wrapper. Current tests focus on:
- Query validation logic
- Internal helper method behavior (documented via tests)
- Integration tests marked as skipped

---

## 9. Deployment

### 9.1 Prerequisites

- .NET 8.0 SDK
- Finnhub API key (free tier: https://finnhub.io/)

### 9.2 Installation Steps

```bash
# 1. Navigate to project
cd stock_analyzer_dotnet

# 2. Configure API key (choose one method)
# Option A: Set environment variable
set FINNHUB_API_KEY=your_key_here

# Option B: Edit appsettings.json
# Add key under Finnhub:ApiKey

# 3. Build the solution
dotnet build

# 4. Run the application
dotnet run --project src/StockAnalyzer.Api

# 5. Open browser
# http://localhost:5000
```

### 9.3 File Structure

```
stock_analyzer_dotnet/
├── StockAnalyzer.sln
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── DEPLOYMENT_ORACLE.md
├── docs/
│   ├── FUNCTIONAL_SPEC.md
│   └── TECHNICAL_SPEC.md
├── src/
│   ├── StockAnalyzer.Api/
│   │   ├── Program.cs
│   │   ├── appsettings.json
│   │   ├── StockAnalyzer.Api.csproj
│   │   ├── MLModels/
│   │   │   └── yolov8n.onnx           # YOLOv8 nano model (~12MB)
│   │   └── wwwroot/
│   │       ├── index.html
│   │       └── js/
│   │           ├── api.js
│   │           ├── app.js
│   │           └── charts.js
│   └── StockAnalyzer.Core/
│       ├── StockAnalyzer.Core.csproj
│       ├── Models/
│       │   ├── StockInfo.cs
│       │   ├── CompanyProfile.cs
│       │   ├── HistoricalData.cs
│       │   ├── NewsItem.cs
│       │   ├── SearchResult.cs
│       │   ├── SignificantMove.cs
│       │   └── TechnicalIndicators.cs    # RsiData, MacdData records
│       └── Services/
│           ├── StockDataService.cs
│           ├── NewsService.cs
│           ├── AnalysisService.cs
│           ├── ImageProcessingService.cs   # ML detection + cropping
│           └── ImageCacheService.cs        # Background cache management
└── tests/
    └── StockAnalyzer.Core.Tests/
        ├── StockAnalyzer.Core.Tests.csproj
        ├── Services/
        ├── Models/
        └── TestHelpers/
```

---

## 10. Known Issues and Workarounds

### 10.1 Dividend Yield Inconsistency

**Issue:** Yahoo Finance returns dividend yield in inconsistent formats.

**Workaround:** Validation in `StockDataService`:
```csharp
private static decimal? ValidateDividendYield(decimal? yield)
{
    if (!yield.HasValue) return null;
    if (yield.Value > 0.10m)
        return yield.Value / 100;  // Correct inflated value
    return yield;
}
```

### 10.2 OoplesFinance API Wrapper Types

**Issue:** The library returns wrapper types with `Raw` properties instead of primitive values.

**Workaround:** Reflection-based extraction:
```csharp
private static decimal? TryGetDecimal(object? value)
{
    if (value == null) return null;
    var rawProp = value.GetType().GetProperty("Raw");
    if (rawProp != null)
    {
        var rawValue = rawProp.GetValue(value);
        if (rawValue is double d) return (decimal)d;
    }
    // Direct conversion fallback...
}
```

### 10.3 Search Not in OoplesFinance

**Issue:** OoplesFinance library doesn't provide ticker search functionality.

**Workaround:** Direct HTTP call to Yahoo Finance search API in `SearchAsync()`.

---

## 11. Troubleshooting

### 11.1 Application Won't Start

| Error | Cause | Solution |
|-------|-------|----------|
| `Port 5000 already in use` | Another process using port | Kill process or change port in launchSettings.json |
| `Unable to find package` | NuGet restore needed | Run `dotnet restore` |
| Build errors | SDK version mismatch | Ensure .NET 8.0 SDK installed |

### 11.2 No Data Displayed

| Cause | Solution |
|-------|----------|
| Invalid ticker symbol | Verify ticker exists on Yahoo Finance |
| Network connectivity | Check internet connection |
| API rate limit | Wait and retry |

### 11.3 News Not Loading

| Cause | Solution |
|-------|----------|
| Missing API key | Check appsettings.json or environment variable |
| API rate limit exceeded | Wait 1 minute (free tier: 60 req/min) |
| Invalid API key | Verify key at https://finnhub.io/dashboard |

### 11.4 Search Not Working

| Cause | Solution |
|-------|----------|
| Query too short | Type at least 2 characters |
| Yahoo Finance API down | Check Yahoo Finance directly |
| Network timeout | Check connectivity, try again |

---

## 12. Security Considerations

### 12.1 API Key Storage

- API keys stored in `appsettings.json` (not committed to git)
- `.gitignore` includes `appsettings.Development.json`
- Production should use environment variables or secret management

### 12.2 Data Privacy

- No user data is stored or transmitted
- All data requests are read-only
- No authentication/login system

### 12.3 Network Security

- Default: localhost only (safe for development)
- Production deployment should use HTTPS
- CORS configured to allow any origin (restrict in production)

### 12.4 Content Security Policy

The application uses CSP headers to restrict resource loading. Since images are now
processed server-side, the client only connects to our own backend.

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.plot.ly;
  style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com;
  img-src 'self' data: blob:;
  font-src 'self' https:;
  connect-src 'self'
```

| Directive | Allowed Sources | Purpose |
|-----------|-----------------|---------|
| `script-src` | CDN for Tailwind, Plotly | Chart and styling libraries |
| `img-src` | `'self'`, `data:`, `blob:` | Images from backend + blob URLs |
| `connect-src` | `'self'` only | All API calls to own backend |

### 12.5 Subresource Integrity (SRI)

SRI hashes verify that CDN-loaded scripts haven't been tampered with.

**Plotly.js** - SRI enabled:
```html
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"
        integrity="sha384-Hl48Kq2HifOWdXEjMsKo6qxqvRLTYqIGbvlENBmkHAxZKIGCXv43H6W1jA671RzC"
        crossorigin="anonymous"></script>
```

**Tailwind CSS CDN** - SRI not applicable:
- `cdn.tailwindcss.com` is a JIT (Just-In-Time) compiler
- Generates CSS dynamically based on classes used in the page
- Content changes per request, so hash verification would fail
- For production, pre-build Tailwind locally: `npx tailwindcss -o styles.css`

| Resource | SRI Status | Reason |
|----------|------------|--------|
| Plotly.js 2.27.0 | ✅ Enabled | Static versioned file |
| Tailwind CSS CDN | ❌ Not applicable | Dynamic JIT compiler |

---

## 13. Performance Considerations

### 13.1 Caching

**Backend:** Currently no caching implemented. Each request fetches fresh data.
**Future Enhancement:** Add `IMemoryCache` for API responses.

**Server-Side Image Processing:**
- YOLOv8n ONNX model loaded once at startup (~12MB)
- Inference time: ~10-50ms per image on CPU
- Background cache: 50 cat + 50 dog images pre-processed
- Automatic refill when cache drops below 10 images
- Images stored as compressed JPEG byte arrays (~10-30KB each)

**Frontend Image Caching:**
- Fetches blob URLs from `/api/images/{type}` endpoints
- Images converted to blob URLs for instant display
- Automatic refill when cache drops below 10 images
- Each image used once to ensure variety

### 13.2 API Rate Limits

| Service | Limit | Impact |
|---------|-------|--------|
| Finnhub | 60/min | News fetching may fail under heavy use |
| Yahoo Finance | Undocumented | Occasional request failures possible |

### 13.3 Parallel Requests

Frontend fetches all data in parallel for better performance:
```javascript
const [stockInfo, history, analysis, significantMoves, news] = await Promise.all([
    API.getStockInfo(ticker),
    API.getHistory(ticker, period),
    API.getAnalysis(ticker, period),
    API.getSignificantMoves(ticker, 3),
    API.getNews(ticker, 30)
]);
```

---

## 14. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.9 | 2026-01-17 | Documentation page: docs.html with tabbed markdown viewer, marked.js integration, TOC sidebar |
| 1.8 | 2026-01-17 | Stock comparison: normalizeToPercentChange helper, comparison mode in charts.js, benchmark buttons, indicator disable logic |
| 1.7 | 2026-01-16 | Technical indicators: RSI and MACD calculation methods, RsiData/MacdData models, Plotly subplot support, dynamic chart resizing |
| 1.6 | 2026-01-16 | Dark mode implementation with Tailwind CSS class-based theming, localStorage persistence |
| 1.5 | 2026-01-16 | Added YTD and 10-year time periods to chart dropdown |
| 1.4 | 2026-01-16 | Company profile integration: ISIN/CUSIP/SEDOL identifiers, company bio, Finnhub profile endpoint, OpenFIGI SEDOL lookup, chart legend/width fixes |
| 1.3 | 2026-01-16 | Server-side ML image processing with YOLOv8n ONNX, ImageProcessingService, ImageCacheService, new /api/images/* endpoints |
| 1.2 | 2026-01-16 | Added unit test documentation (Section 8), SRI for Plotly.js (Section 12.5) |
| 1.1 | 2026-01-16 | Added image caching system, Dog CEO API, CSP configuration |
| 1.0 | 2026-01-16 | Initial .NET technical specification |

---

## 15. References

- [ASP.NET Core Minimal APIs](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis)
- [OoplesFinance.YahooFinanceAPI](https://github.com/ooples/OoplesFinance.YahooFinanceAPI)
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Finnhub API Documentation](https://finnhub.io/docs/api)
- [Dog CEO API Documentation](https://dog.ceo/dog-api/documentation/)
- [Cat as a Service (cataas)](https://cataas.com/)
- [OpenFIGI API Documentation](https://www.openfigi.com/api)
