namespace StockAnalyzer.Core.Models;

/// <summary>
/// Represents a user's stock watchlist containing a collection of ticker symbols.
/// Designed for single-user now, with UserId field for future multi-user support.
/// </summary>
public record Watchlist
{
    public required string Id { get; init; }
    public required string Name { get; init; }
    public required List<string> Tickers { get; init; }
    public DateTime CreatedAt { get; init; }
    public DateTime UpdatedAt { get; init; }

    /// <summary>
    /// User ID for multi-user support. Null for single-user mode.
    /// </summary>
    public string? UserId { get; init; }
}

/// <summary>
/// DTO for creating a new watchlist.
/// </summary>
public record CreateWatchlistRequest
{
    public required string Name { get; init; }
}

/// <summary>
/// DTO for updating a watchlist.
/// </summary>
public record UpdateWatchlistRequest
{
    public required string Name { get; init; }
}

/// <summary>
/// DTO for adding a ticker to a watchlist.
/// </summary>
public record AddTickerRequest
{
    public required string Ticker { get; init; }
}

/// <summary>
/// Container for watchlist storage (JSON file format).
/// </summary>
public record WatchlistStorage
{
    public List<Watchlist> Watchlists { get; init; } = new();
}
