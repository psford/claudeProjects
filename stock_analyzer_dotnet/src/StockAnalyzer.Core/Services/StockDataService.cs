using OoplesFinance.YahooFinanceAPI;
using OoplesFinance.YahooFinanceAPI.Enums;
using StockAnalyzer.Core.Models;

namespace StockAnalyzer.Core.Services;

/// <summary>
/// Service for fetching stock data from Yahoo Finance.
/// Uses OoplesFinance.YahooFinanceAPI NuGet package.
/// </summary>
public class StockDataService
{
    /// <summary>
    /// Get basic stock information for a ticker.
    /// </summary>
    public async Task<StockInfo?> GetStockInfoAsync(string symbol)
    {
        try
        {
            var yahooClient = new YahooClient();
            var summary = await yahooClient.GetSummaryDetailsAsync(symbol);

            if (summary == null)
                return null;

            // Extract numeric values safely using reflection or direct property access
            // The API returns wrapper types, we need to extract the actual values
            return new StockInfo
            {
                Symbol = symbol.ToUpper(),
                ShortName = symbol.ToUpper(),
                LongName = null,
                Sector = null,
                Industry = null,
                Website = null,
                Country = null,
                Currency = summary.Currency,
                Exchange = null,

                CurrentPrice = TryGetDecimal(summary.Open),
                PreviousClose = TryGetDecimal(summary.PreviousClose),
                Open = TryGetDecimal(summary.Open),
                DayHigh = TryGetDecimal(summary.DayHigh),
                DayLow = TryGetDecimal(summary.DayLow),
                Volume = TryGetLong(summary.Volume),
                AverageVolume = TryGetLong(summary.AverageVolume),

                MarketCap = TryGetDecimal(summary.MarketCap),
                PeRatio = TryGetDecimal(summary.TrailingPE),
                ForwardPeRatio = TryGetDecimal(summary.ForwardPE),
                PegRatio = null,
                PriceToBook = null,

                DividendYield = ValidateDividendYield(TryGetDecimal(summary.DividendYield)),
                DividendRate = TryGetDecimal(summary.DividendRate),

                FiftyTwoWeekHigh = TryGetDecimal(summary.FiftyTwoWeekHigh),
                FiftyTwoWeekLow = TryGetDecimal(summary.FiftyTwoWeekLow),
                FiftyDayAverage = TryGetDecimal(summary.FiftyDayAverage),
                TwoHundredDayAverage = TryGetDecimal(summary.TwoHundredDayAverage)
            };
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// Get historical OHLCV data for a ticker.
    /// </summary>
    public async Task<HistoricalDataResult?> GetHistoricalDataAsync(
        string symbol,
        string period = "1y")
    {
        try
        {
            var yahooClient = new YahooClient();
            var startDate = GetStartDate(period);

            // Use GetHistoricalDataAsync which returns IEnumerable<HistoricalDataInfo>
            var history = await yahooClient.GetHistoricalDataAsync(
                symbol,
                DataFrequency.Daily,
                startDate);

            if (history == null || !history.Any())
                return null;

            var ohlcvData = history.Select(h => new OhlcvData
            {
                Date = h.Date,
                Open = (decimal)h.Open,
                High = (decimal)h.High,
                Low = (decimal)h.Low,
                Close = (decimal)h.Close,
                Volume = (long)h.Volume,
                AdjustedClose = null
            }).OrderBy(d => d.Date).ToList();

            return new HistoricalDataResult
            {
                Symbol = symbol.ToUpper(),
                Period = period,
                StartDate = ohlcvData.First().Date,
                EndDate = ohlcvData.Last().Date,
                Data = ohlcvData
            };
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static DateTime GetStartDate(string period)
    {
        var now = DateTime.Now;
        return period.ToLower() switch
        {
            "1d" => now.AddDays(-1),
            "5d" => now.AddDays(-5),
            "1mo" => now.AddMonths(-1),
            "3mo" => now.AddMonths(-3),
            "6mo" => now.AddMonths(-6),
            "1y" => now.AddYears(-1),
            "2y" => now.AddYears(-2),
            "5y" => now.AddYears(-5),
            "10y" => now.AddYears(-10),
            _ => now.AddYears(-1)
        };
    }

    /// <summary>
    /// Search for tickers - validates if a symbol exists.
    /// </summary>
    public async Task<List<(string Symbol, string Name)>> SearchAsync(string query)
    {
        try
        {
            var yahooClient = new YahooClient();
            var summary = await yahooClient.GetSummaryDetailsAsync(query.ToUpper());

            if (summary != null)
            {
                return new List<(string, string)>
                {
                    (query.ToUpper(), query.ToUpper())
                };
            }

            return new List<(string, string)>();
        }
        catch (Exception)
        {
            return new List<(string, string)>();
        }
    }

    /// <summary>
    /// Get top trending stocks.
    /// </summary>
    public async Task<List<(string Symbol, string Name)>> GetTrendingStocksAsync(int count = 10)
    {
        try
        {
            var yahooClient = new YahooClient();
            var trending = await yahooClient.GetTopTrendingStocksAsync(Country.UnitedStates, count);

            if (trending == null)
                return new List<(string, string)>();

            return trending
                .Select(t => (t, t))
                .Where(t => !string.IsNullOrEmpty(t.Item1))
                .ToList();
        }
        catch (Exception)
        {
            return new List<(string, string)>();
        }
    }

    private static decimal? TryGetDecimal(object? value)
    {
        if (value == null) return null;

        // Handle wrapper types that have a numeric value
        var type = value.GetType();
        var rawProp = type.GetProperty("Raw");
        if (rawProp != null)
        {
            var rawValue = rawProp.GetValue(value);
            if (rawValue is double d) return (decimal)d;
            if (rawValue is decimal dec) return dec;
            if (rawValue is float f) return (decimal)f;
        }

        // Try direct conversion
        try
        {
            if (value is double d) return (decimal)d;
            if (value is decimal dec) return dec;
            if (value is float f) return (decimal)f;
            if (value is int i) return i;
            if (value is long l) return l;
        }
        catch { }

        return null;
    }

    private static long? TryGetLong(object? value)
    {
        if (value == null) return null;

        var type = value.GetType();
        var rawProp = type.GetProperty("Raw");
        if (rawProp != null)
        {
            var rawValue = rawProp.GetValue(value);
            if (rawValue is long l) return l;
            if (rawValue is double d) return (long)d;
            if (rawValue is int i) return i;
        }

        try
        {
            if (value is long l) return l;
            if (value is int i) return i;
            if (value is double d) return (long)d;
        }
        catch { }

        return null;
    }

    private static decimal? ValidateDividendYield(decimal? yield)
    {
        if (!yield.HasValue) return null;

        // Same logic as Python version - values > 10% are likely inflated by 100x
        if (yield.Value > 0.10m)
        {
            return yield.Value / 100;
        }

        return yield;
    }
}
