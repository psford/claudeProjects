using System.Net.Http.Json;
using System.Text.Json.Serialization;
using StockAnalyzer.Core.Models;

namespace StockAnalyzer.Core.Services;

/// <summary>
/// Service for fetching stock news from Finnhub API.
/// </summary>
public class NewsService
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;
    private const string BaseUrl = "https://finnhub.io/api/v1";

    public NewsService(string apiKey, HttpClient? httpClient = null)
    {
        _apiKey = apiKey;
        _httpClient = httpClient ?? new HttpClient();
    }

    /// <summary>
    /// Get company news for a symbol within a date range.
    /// </summary>
    public async Task<NewsResult> GetCompanyNewsAsync(
        string symbol,
        DateTime? from = null,
        DateTime? to = null)
    {
        var fromDate = from ?? DateTime.Now.AddMonths(-1);
        var toDate = to ?? DateTime.Now;

        var url = $"{BaseUrl}/company-news?symbol={symbol.ToUpper()}" +
                  $"&from={fromDate:yyyy-MM-dd}&to={toDate:yyyy-MM-dd}" +
                  $"&token={_apiKey}";

        try
        {
            var response = await _httpClient.GetFromJsonAsync<List<FinnhubNewsItem>>(url);

            var articles = (response ?? new List<FinnhubNewsItem>())
                .Select(item => new NewsItem
                {
                    Headline = item.Headline ?? "",
                    Summary = item.Summary,
                    Source = item.Source ?? "Unknown",
                    PublishedAt = DateTimeOffset.FromUnixTimeSeconds(item.Datetime).DateTime,
                    Url = item.Url,
                    ImageUrl = item.Image,
                    Category = item.Category,
                    RelatedSymbols = new List<string> { symbol.ToUpper() }
                })
                .OrderByDescending(a => a.PublishedAt)
                .ToList();

            return new NewsResult
            {
                Symbol = symbol.ToUpper(),
                FromDate = fromDate,
                ToDate = toDate,
                Articles = articles
            };
        }
        catch (Exception)
        {
            return new NewsResult
            {
                Symbol = symbol.ToUpper(),
                FromDate = fromDate,
                ToDate = toDate,
                Articles = new List<NewsItem>()
            };
        }
    }

    /// <summary>
    /// Get news for a specific date (for correlating with significant moves).
    /// </summary>
    public async Task<List<NewsItem>> GetNewsForDateAsync(string symbol, DateTime date)
    {
        // Get news from 2 days before to 1 day after to capture related stories
        var result = await GetCompanyNewsAsync(symbol, date.AddDays(-2), date.AddDays(1));
        return result.Articles;
    }

    /// <summary>
    /// Finnhub API response model.
    /// </summary>
    private class FinnhubNewsItem
    {
        [JsonPropertyName("category")]
        public string? Category { get; set; }

        [JsonPropertyName("datetime")]
        public long Datetime { get; set; }

        [JsonPropertyName("headline")]
        public string? Headline { get; set; }

        [JsonPropertyName("id")]
        public long Id { get; set; }

        [JsonPropertyName("image")]
        public string? Image { get; set; }

        [JsonPropertyName("related")]
        public string? Related { get; set; }

        [JsonPropertyName("source")]
        public string? Source { get; set; }

        [JsonPropertyName("summary")]
        public string? Summary { get; set; }

        [JsonPropertyName("url")]
        public string? Url { get; set; }
    }
}
