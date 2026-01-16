using StockAnalyzer.Core.Models;

namespace StockAnalyzer.Core.Services;

/// <summary>
/// Service for performing stock analysis calculations.
/// </summary>
public class AnalysisService
{
    private readonly NewsService? _newsService;

    public AnalysisService(NewsService? newsService = null)
    {
        _newsService = newsService;
    }

    /// <summary>
    /// Calculate moving averages for historical data.
    /// </summary>
    public List<MovingAverageData> CalculateMovingAverages(List<OhlcvData> data)
    {
        var result = new List<MovingAverageData>();
        var closes = data.Select(d => d.Close).ToList();

        for (int i = 0; i < data.Count; i++)
        {
            result.Add(new MovingAverageData
            {
                Date = data[i].Date,
                Sma20 = CalculateSma(closes, i, 20),
                Sma50 = CalculateSma(closes, i, 50),
                Sma200 = CalculateSma(closes, i, 200)
            });
        }

        return result;
    }

    /// <summary>
    /// Detect significant price moves.
    /// </summary>
    public async Task<SignificantMovesResult> DetectSignificantMovesAsync(
        string symbol,
        List<OhlcvData> data,
        decimal threshold = 3.0m,
        bool includeNews = true)
    {
        var moves = new List<SignificantMove>();

        foreach (var day in data)
        {
            if (day.Open == 0) continue;

            var percentChange = ((day.Close - day.Open) / day.Open) * 100;

            if (Math.Abs(percentChange) >= threshold)
            {
                var move = new SignificantMove
                {
                    Date = day.Date,
                    OpenPrice = day.Open,
                    ClosePrice = day.Close,
                    PercentChange = percentChange,
                    Volume = day.Volume,
                    RelatedNews = null
                };

                // Fetch related news if requested and service is available
                if (includeNews && _newsService != null)
                {
                    try
                    {
                        var news = await _newsService.GetNewsForDateAsync(symbol, day.Date);
                        move = move with { RelatedNews = news.Take(5).ToList() };
                    }
                    catch
                    {
                        // Ignore news errors, continue without news
                    }
                }

                moves.Add(move);
            }
        }

        return new SignificantMovesResult
        {
            Symbol = symbol.ToUpper(),
            Threshold = threshold,
            Moves = moves.OrderByDescending(m => m.Date).ToList()
        };
    }

    /// <summary>
    /// Calculate basic performance metrics.
    /// </summary>
    public Dictionary<string, decimal?> CalculatePerformance(List<OhlcvData> data)
    {
        if (data.Count < 2)
            return new Dictionary<string, decimal?>();

        var first = data.First();
        var last = data.Last();

        var totalReturn = first.Close > 0
            ? ((last.Close - first.Close) / first.Close) * 100
            : 0;

        // Calculate daily returns for volatility
        var dailyReturns = new List<decimal>();
        for (int i = 1; i < data.Count; i++)
        {
            if (data[i - 1].Close > 0)
            {
                var dailyReturn = (data[i].Close - data[i - 1].Close) / data[i - 1].Close;
                dailyReturns.Add(dailyReturn);
            }
        }

        // Calculate volatility (annualized standard deviation)
        var volatility = CalculateVolatility(dailyReturns);

        return new Dictionary<string, decimal?>
        {
            ["totalReturn"] = totalReturn,
            ["volatility"] = volatility,
            ["highestClose"] = data.Max(d => d.Close),
            ["lowestClose"] = data.Min(d => d.Close),
            ["averageVolume"] = (decimal)data.Average(d => d.Volume)
        };
    }

    private static decimal? CalculateSma(List<decimal> values, int index, int period)
    {
        if (index + 1 < period)
            return null;

        var sum = 0m;
        for (int i = index - period + 1; i <= index; i++)
        {
            sum += values[i];
        }
        return sum / period;
    }

    private static decimal? CalculateVolatility(List<decimal> dailyReturns)
    {
        if (dailyReturns.Count < 2)
            return null;

        var mean = dailyReturns.Average();
        var sumSquares = dailyReturns.Sum(r => (r - mean) * (r - mean));
        var variance = sumSquares / (dailyReturns.Count - 1);
        var stdDev = (decimal)Math.Sqrt((double)variance);

        // Annualize (assuming 252 trading days)
        return stdDev * (decimal)Math.Sqrt(252) * 100;
    }
}
