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

// Register image processing services
builder.Services.AddSingleton(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var modelPath = config["ImageProcessing:ModelPath"] ?? "MLModels/yolov8n.onnx";
    var targetWidth = config.GetValue<int>("ImageProcessing:TargetWidth", 320);
    var targetHeight = config.GetValue<int>("ImageProcessing:TargetHeight", 150);
    return new ImageProcessingService(modelPath, targetWidth, targetHeight);
});
builder.Services.AddSingleton(sp =>
{
    var processor = sp.GetRequiredService<ImageProcessingService>();
    var logger = sp.GetRequiredService<ILogger<ImageCacheService>>();
    var config = sp.GetRequiredService<IConfiguration>();
    var cacheSize = config.GetValue<int>("ImageProcessing:CacheSize", 50);
    var refillThreshold = config.GetValue<int>("ImageProcessing:RefillThreshold", 10);
    return new ImageCacheService(processor, logger, cacheSize, refillThreshold);
});
builder.Services.AddHostedService(sp => sp.GetRequiredService<ImageCacheService>());

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

// Security headers middleware
app.Use(async (context, next) =>
{
    // Anti-clickjacking
    context.Response.Headers["X-Frame-Options"] = "DENY";
    // Prevent MIME type sniffing
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    // XSS protection (legacy browsers)
    context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
    // Referrer policy
    context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    // Permissions policy
    context.Response.Headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()";
    // Content Security Policy - allow CDN scripts for Tailwind and Plotly
    // Images now served from our own backend (no external image fetches from client)
    context.Response.Headers["Content-Security-Policy"] =
        "default-src 'self'; " +
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.plot.ly; " +
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; " +
        "img-src 'self' data: blob:; " +
        "font-src 'self' https:; " +
        "connect-src 'self'";

    await next();
});

app.UseDefaultFiles();
app.UseStaticFiles();

// API Endpoints

// GET /api/stock/{ticker} - Get stock information with company profile and identifiers
app.MapGet("/api/stock/{ticker}", async (string ticker, StockDataService stockService, NewsService newsService) =>
{
    var info = await stockService.GetStockInfoAsync(ticker);
    if (info == null)
        return Results.NotFound(new { error = "Stock not found", symbol = ticker });

    // Fetch company profile from Finnhub (includes ISIN, CUSIP, company name)
    var profile = await newsService.GetCompanyProfileAsync(ticker);

    // Try to get SEDOL from OpenFIGI if we have an ISIN
    string? sedol = null;
    if (!string.IsNullOrEmpty(profile?.Isin))
    {
        sedol = await newsService.GetSedolFromIsinAsync(profile.Isin);
    }

    // Merge profile data with stock info
    var enrichedInfo = info with
    {
        LongName = profile?.Name ?? info.LongName,
        ShortName = profile?.Name ?? info.ShortName,
        Exchange = profile?.Exchange ?? info.Exchange,
        Industry = profile?.Industry ?? info.Industry,
        Country = profile?.Country ?? info.Country,
        Website = profile?.WebUrl ?? info.Website,
        Isin = profile?.Isin,
        Cusip = profile?.Cusip,
        Sedol = sedol
    };

    return Results.Ok(enrichedInfo);
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

// GET /api/stock/{ticker}/analysis - Get performance metrics, moving averages, and technical indicators
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
    var rsi = analysisService.CalculateRsi(history.Data);
    var macd = analysisService.CalculateMacd(history.Data);

    return Results.Ok(new
    {
        symbol = ticker.ToUpper(),
        period = period ?? "1y",
        performance,
        movingAverages,
        rsi,
        macd
    });
})
.WithName("GetStockAnalysis")
.WithOpenApi()
.Produces(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// GET /api/search - Search for tickers by symbol or company name
app.MapGet("/api/search", async (string q, StockDataService stockService) =>
{
    if (string.IsNullOrWhiteSpace(q))
        return Results.BadRequest(new { error = "Query parameter 'q' is required" });

    var results = await stockService.SearchAsync(q);
    return Results.Ok(new
    {
        query = q,
        results = results.Select(r => new
        {
            symbol = r.Symbol,
            shortName = r.ShortName,
            longName = r.LongName,
            exchange = r.Exchange,
            type = r.Type,
            displayName = r.DisplayName
        })
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

// Image API endpoints

// GET /api/images/cat - Get a processed cat image
app.MapGet("/api/images/cat", (ImageCacheService cache) =>
{
    var image = cache.GetCatImage();
    return image != null
        ? Results.File(image, "image/jpeg")
        : Results.NotFound(new { error = "No cat images available. Cache may be warming up." });
})
.WithName("GetCatImage")
.WithOpenApi()
.Produces(StatusCodes.Status200OK, contentType: "image/jpeg")
.Produces(StatusCodes.Status404NotFound);

// GET /api/images/dog - Get a processed dog image
app.MapGet("/api/images/dog", (ImageCacheService cache) =>
{
    var image = cache.GetDogImage();
    return image != null
        ? Results.File(image, "image/jpeg")
        : Results.NotFound(new { error = "No dog images available. Cache may be warming up." });
})
.WithName("GetDogImage")
.WithOpenApi()
.Produces(StatusCodes.Status200OK, contentType: "image/jpeg")
.Produces(StatusCodes.Status404NotFound);

// GET /api/images/status - Get cache status
app.MapGet("/api/images/status", (ImageCacheService cache) =>
{
    var (cats, dogs) = cache.GetCacheStatus();
    return Results.Ok(new
    {
        cats,
        dogs,
        timestamp = DateTime.UtcNow
    });
})
.WithName("GetImageCacheStatus")
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
