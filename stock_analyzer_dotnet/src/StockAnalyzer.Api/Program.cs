using StockAnalyzer.Core.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS for frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register services
builder.Services.AddSingleton<StockDataService>();
builder.Services.AddSingleton(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var apiKey = config["Finnhub:ApiKey"] ?? Environment.GetEnvironmentVariable("FINNHUB_API_KEY") ?? "";
    return new NewsService(apiKey);
});
builder.Services.AddSingleton(sp =>
{
    var newsService = sp.GetRequiredService<NewsService>();
    return new AnalysisService(newsService);
});

// Serve static files from wwwroot
builder.Services.AddDirectoryBrowser();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowFrontend");
app.UseDefaultFiles();
app.UseStaticFiles();

// API Endpoints

// GET /api/stock/{ticker} - Get stock information
app.MapGet("/api/stock/{ticker}", async (string ticker, StockDataService stockService) =>
{
    var info = await stockService.GetStockInfoAsync(ticker);
    return info != null
        ? Results.Ok(info)
        : Results.NotFound(new { error = "Stock not found", symbol = ticker });
})
.WithName("GetStockInfo")
.WithOpenApi()
.Produces<StockAnalyzer.Core.Models.StockInfo>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// GET /api/stock/{ticker}/history - Get historical data
app.MapGet("/api/stock/{ticker}/history", async (
    string ticker,
    string? period,
    StockDataService stockService) =>
{
    var data = await stockService.GetHistoricalDataAsync(ticker, period ?? "1y");
    return data != null
        ? Results.Ok(data)
        : Results.NotFound(new { error = "Historical data not found", symbol = ticker });
})
.WithName("GetStockHistory")
.WithOpenApi()
.Produces<StockAnalyzer.Core.Models.HistoricalDataResult>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// GET /api/stock/{ticker}/news - Get company news
app.MapGet("/api/stock/{ticker}/news", async (
    string ticker,
    int? days,
    NewsService newsService) =>
{
    var fromDate = DateTime.Now.AddDays(-(days ?? 30));
    var result = await newsService.GetCompanyNewsAsync(ticker, fromDate);
    return Results.Ok(result);
})
.WithName("GetStockNews")
.WithOpenApi()
.Produces<StockAnalyzer.Core.Models.NewsResult>(StatusCodes.Status200OK);

// GET /api/stock/{ticker}/significant - Get significant price moves
app.MapGet("/api/stock/{ticker}/significant", async (
    string ticker,
    decimal? threshold,
    StockDataService stockService,
    AnalysisService analysisService) =>
{
    var history = await stockService.GetHistoricalDataAsync(ticker, "1y");
    if (history == null)
        return Results.NotFound(new { error = "Historical data not found", symbol = ticker });

    var moves = await analysisService.DetectSignificantMovesAsync(
        ticker,
        history.Data,
        threshold ?? 3.0m,
        includeNews: true);

    return Results.Ok(moves);
})
.WithName("GetSignificantMoves")
.WithOpenApi()
.Produces<StockAnalyzer.Core.Models.SignificantMovesResult>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// GET /api/stock/{ticker}/analysis - Get performance metrics and moving averages
app.MapGet("/api/stock/{ticker}/analysis", async (
    string ticker,
    string? period,
    StockDataService stockService,
    AnalysisService analysisService) =>
{
    var history = await stockService.GetHistoricalDataAsync(ticker, period ?? "1y");
    if (history == null)
        return Results.NotFound(new { error = "Historical data not found", symbol = ticker });

    var movingAverages = analysisService.CalculateMovingAverages(history.Data);
    var performance = analysisService.CalculatePerformance(history.Data);

    return Results.Ok(new
    {
        symbol = ticker.ToUpper(),
        period = period ?? "1y",
        performance,
        movingAverages = movingAverages.TakeLast(30) // Last 30 days of MAs
    });
})
.WithName("GetStockAnalysis")
.WithOpenApi()
.Produces(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// GET /api/search - Search for tickers
app.MapGet("/api/search", async (string q, StockDataService stockService) =>
{
    if (string.IsNullOrWhiteSpace(q))
        return Results.BadRequest(new { error = "Query parameter 'q' is required" });

    var results = await stockService.SearchAsync(q);
    return Results.Ok(new
    {
        query = q,
        results = results.Select(r => new { symbol = r.Symbol, name = r.Name })
    });
})
.WithName("SearchTickers")
.WithOpenApi()
.Produces(StatusCodes.Status200OK)
.Produces(StatusCodes.Status400BadRequest);

// GET /api/trending - Get trending stocks
app.MapGet("/api/trending", async (int? count, StockDataService stockService) =>
{
    var trending = await stockService.GetTrendingStocksAsync(count ?? 10);
    return Results.Ok(new
    {
        count = trending.Count,
        stocks = trending.Select(t => new { symbol = t.Symbol, name = t.Name })
    });
})
.WithName("GetTrendingStocks")
.WithOpenApi()
.Produces(StatusCodes.Status200OK);

// Health check
app.MapGet("/api/health", () => Results.Ok(new
{
    status = "healthy",
    timestamp = DateTime.UtcNow,
    version = "1.0.0"
}))
.WithName("HealthCheck")
.WithOpenApi();

app.Run();
