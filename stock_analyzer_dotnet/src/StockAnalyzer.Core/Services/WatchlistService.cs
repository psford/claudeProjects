using Microsoft.Extensions.Logging;
using StockAnalyzer.Core.Models;

namespace StockAnalyzer.Core.Services;

/// <summary>
/// Service for managing stock watchlists with business logic.
/// </summary>
public class WatchlistService
{
    private readonly IWatchlistRepository _repository;
    private readonly StockDataService _stockDataService;
    private readonly ILogger<WatchlistService> _logger;

    public WatchlistService(
        IWatchlistRepository repository,
        StockDataService stockDataService,
        ILogger<WatchlistService> logger)
    {
        _repository = repository;
        _stockDataService = stockDataService;
        _logger = logger;
    }

    /// <summary>
    /// Get all watchlists for a user (or all if single-user mode).
    /// </summary>
    public Task<List<Watchlist>> GetAllAsync(string? userId = null)
    {
        return _repository.GetAllAsync(userId);
    }

    /// <summary>
    /// Get a watchlist by ID.
    /// </summary>
    public Task<Watchlist?> GetByIdAsync(string id, string? userId = null)
    {
        return _repository.GetByIdAsync(id, userId);
    }

    /// <summary>
    /// Create a new watchlist.
    /// </summary>
    public async Task<Watchlist> CreateAsync(string name, string? userId = null)
    {
        var watchlist = new Watchlist
        {
            Id = string.Empty, // Will be set by repository
            Name = name.Trim(),
            Tickers = new List<string>(),
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow,
            UserId = userId
        };

        return await _repository.CreateAsync(watchlist);
    }

    /// <summary>
    /// Rename a watchlist.
    /// </summary>
    public async Task<Watchlist?> RenameAsync(string id, string newName, string? userId = null)
    {
        var watchlist = await _repository.GetByIdAsync(id, userId);
        if (watchlist == null)
        {
            return null;
        }

        var updated = watchlist with { Name = newName.Trim() };
        return await _repository.UpdateAsync(updated);
    }

    /// <summary>
    /// Delete a watchlist.
    /// </summary>
    public Task<bool> DeleteAsync(string id, string? userId = null)
    {
        return _repository.DeleteAsync(id, userId);
    }

    /// <summary>
    /// Add a ticker to a watchlist.
    /// </summary>
    public Task<Watchlist?> AddTickerAsync(string id, string ticker, string? userId = null)
    {
        return _repository.AddTickerAsync(id, ticker, userId);
    }

    /// <summary>
    /// Remove a ticker from a watchlist.
    /// </summary>
    public Task<Watchlist?> RemoveTickerAsync(string id, string ticker, string? userId = null)
    {
        return _repository.RemoveTickerAsync(id, ticker, userId);
    }

    /// <summary>
    /// Get current quotes for all tickers in a watchlist.
    /// </summary>
    public async Task<WatchlistQuotes?> GetQuotesAsync(string id, string? userId = null)
    {
        var watchlist = await _repository.GetByIdAsync(id, userId);
        if (watchlist == null)
        {
            return null;
        }

        var quotes = new List<TickerQuote>();

        foreach (var ticker in watchlist.Tickers)
        {
            try
            {
                var stockInfo = await _stockDataService.GetStockInfoAsync(ticker);
                if (stockInfo != null)
                {
                    quotes.Add(new TickerQuote
                    {
                        Symbol = ticker,
                        Name = stockInfo.LongName ?? stockInfo.ShortName,
                        Price = stockInfo.CurrentPrice,
                        Change = stockInfo.DayChange,
                        ChangePercent = stockInfo.DayChangePercent
                    });
                }
                else
                {
                    quotes.Add(new TickerQuote
                    {
                        Symbol = ticker,
                        Name = null,
                        Price = null,
                        Change = null,
                        ChangePercent = null,
                        Error = "Quote unavailable"
                    });
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to fetch quote for {Ticker}", ticker);
                quotes.Add(new TickerQuote
                {
                    Symbol = ticker,
                    Name = null,
                    Price = null,
                    Change = null,
                    ChangePercent = null,
                    Error = "Failed to fetch quote"
                });
            }
        }

        return new WatchlistQuotes
        {
            WatchlistId = watchlist.Id,
            WatchlistName = watchlist.Name,
            Quotes = quotes,
            FetchedAt = DateTime.UtcNow
        };
    }
}

/// <summary>
/// Quote information for a single ticker.
/// </summary>
public record TickerQuote
{
    public required string Symbol { get; init; }
    public string? Name { get; init; }
    public decimal? Price { get; init; }
    public decimal? Change { get; init; }
    public decimal? ChangePercent { get; init; }
    public string? Error { get; init; }
}

/// <summary>
/// Quotes for all tickers in a watchlist.
/// </summary>
public record WatchlistQuotes
{
    public required string WatchlistId { get; init; }
    public required string WatchlistName { get; init; }
    public required List<TickerQuote> Quotes { get; init; }
    public DateTime FetchedAt { get; init; }
}
