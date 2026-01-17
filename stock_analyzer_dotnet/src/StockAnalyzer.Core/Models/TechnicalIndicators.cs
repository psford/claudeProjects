namespace StockAnalyzer.Core.Models;

/// <summary>
/// RSI (Relative Strength Index) data point.
/// RSI measures the speed and magnitude of price changes on a scale of 0-100.
/// Values above 70 typically indicate overbought conditions.
/// Values below 30 typically indicate oversold conditions.
/// </summary>
public record RsiData
{
    public required DateTime Date { get; init; }

    /// <summary>
    /// RSI value (0-100). Null when insufficient data for calculation.
    /// </summary>
    public decimal? Rsi { get; init; }
}

/// <summary>
/// MACD (Moving Average Convergence Divergence) data point.
/// MACD shows the relationship between two EMAs of a security's price.
/// </summary>
public record MacdData
{
    public required DateTime Date { get; init; }

    /// <summary>
    /// MACD Line = 12-period EMA - 26-period EMA.
    /// Null when insufficient data for calculation.
    /// </summary>
    public decimal? MacdLine { get; init; }

    /// <summary>
    /// Signal Line = 9-period EMA of MACD Line.
    /// Null when insufficient data for calculation.
    /// </summary>
    public decimal? SignalLine { get; init; }

    /// <summary>
    /// Histogram = MACD Line - Signal Line.
    /// Positive values indicate bullish momentum, negative values indicate bearish momentum.
    /// Null when insufficient data for calculation.
    /// </summary>
    public decimal? Histogram { get; init; }
}
