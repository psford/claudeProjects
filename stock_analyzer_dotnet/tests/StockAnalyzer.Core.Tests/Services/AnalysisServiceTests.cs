using FluentAssertions;
using Moq;
using StockAnalyzer.Core.Models;
using StockAnalyzer.Core.Services;
using StockAnalyzer.Core.Tests.TestHelpers;
using Xunit;

namespace StockAnalyzer.Core.Tests.Services;

public class AnalysisServiceTests
{
    private readonly AnalysisService _sut;

    public AnalysisServiceTests()
    {
        // System under test - no news service dependency for pure calculation tests
        _sut = new AnalysisService(newsService: null);
    }

    #region CalculateMovingAverages Tests

    [Fact]
    public void CalculateMovingAverages_WithSufficientData_ReturnsCorrectSma20()
    {
        // Arrange - Create 25 data points with predictable values
        var data = new List<OhlcvData>();
        for (int i = 0; i < 25; i++)
        {
            data.Add(TestDataFactory.CreateOhlcvData(
                date: DateTime.Today.AddDays(-25 + i),
                open: 100m,
                high: 105m,
                low: 95m,
                close: 100m + i,  // Close prices: 100, 101, 102, ... 124
                volume: 1000000
            ));
        }

        // Act
        var result = _sut.CalculateMovingAverages(data);

        // Assert
        result.Should().HaveCount(25);

        // First 19 points should have null SMA20 (not enough data)
        for (int i = 0; i < 19; i++)
        {
            result[i].Sma20.Should().BeNull($"index {i} should not have enough data for SMA20");
        }

        // Point at index 19 (20th point) should have SMA20
        // SMA20 at index 19 = average of closes[0..19] = average of 100..119 = 109.5
        result[19].Sma20.Should().Be(109.5m);

        // Point at index 24 should have SMA20
        // SMA20 at index 24 = average of closes[5..24] = average of 105..124 = 114.5
        result[24].Sma20.Should().Be(114.5m);
    }

    [Fact]
    public void CalculateMovingAverages_WithInsufficientData_ReturnsNullForMissingSmas()
    {
        // Arrange - Only 15 data points (not enough for SMA20, SMA50, or SMA200)
        var data = TestDataFactory.CreateOhlcvDataList(15);

        // Act
        var result = _sut.CalculateMovingAverages(data);

        // Assert
        result.Should().HaveCount(15);

        // All SMA values should be null since we don't have enough data
        result.Should().AllSatisfy(ma =>
        {
            ma.Sma20.Should().BeNull();
            ma.Sma50.Should().BeNull();
            ma.Sma200.Should().BeNull();
        });
    }

    [Fact]
    public void CalculateMovingAverages_WithEmptyData_ReturnsEmptyList()
    {
        // Arrange
        var data = new List<OhlcvData>();

        // Act
        var result = _sut.CalculateMovingAverages(data);

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public void CalculateMovingAverages_ReturnsDatesMatchingInput()
    {
        // Arrange
        var data = TestDataFactory.CreateOhlcvDataList(30);

        // Act
        var result = _sut.CalculateMovingAverages(data);

        // Assert
        result.Should().HaveCount(30);
        for (int i = 0; i < 30; i++)
        {
            result[i].Date.Should().Be(data[i].Date);
        }
    }

    #endregion

    #region DetectSignificantMovesAsync Tests

    [Fact]
    public async Task DetectSignificantMoves_WithLargeMove_DetectsMove()
    {
        // Arrange - Create data with a 6% move on day 5
        var data = TestDataFactory.CreateOhlcvDataWithSignificantMove(
            count: 10,
            significantMoveDay: 5,
            percentChange: 6.0m
        );

        // Act
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 5.0m, includeNews: false);

        // Assert
        result.Symbol.Should().Be("TEST");
        result.Threshold.Should().Be(5.0m);
        result.Moves.Should().HaveCount(1);
        result.Moves[0].PercentChange.Should().BeApproximately(6.0m, 0.5m);
    }

    [Fact]
    public async Task DetectSignificantMoves_WithSmallMove_IgnoresMove()
    {
        // Arrange - Create data with only a 2% move (below 3% default threshold)
        var data = TestDataFactory.CreateOhlcvDataWithSignificantMove(
            count: 10,
            significantMoveDay: 5,
            percentChange: 2.0m
        );

        // Act
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 3.0m, includeNews: false);

        // Assert
        result.Moves.Should().BeEmpty("2% move is below 3% threshold");
    }

    [Fact]
    public async Task DetectSignificantMoves_WithCustomThreshold_UsesThreshold()
    {
        // Arrange - Create data with a 7% move
        var data = TestDataFactory.CreateOhlcvDataWithSignificantMove(
            count: 10,
            significantMoveDay: 5,
            percentChange: 7.0m
        );

        // Act - Use 10% threshold
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 10.0m, includeNews: false);

        // Assert - 7% move should NOT be detected with 10% threshold
        result.Moves.Should().BeEmpty("7% move is below 10% threshold");
    }

    [Fact]
    public async Task DetectSignificantMoves_CorrectlyIdentifiesDirection()
    {
        // Arrange - Create data with both positive and negative moves
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-2), 100m, 110m, 95m, 106m), // +6%
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 100m, 105m, 90m, 94m),  // -6%
            TestDataFactory.CreateOhlcvData(DateTime.Today, 100m, 102m, 98m, 101m)              // +1% (below threshold)
        };

        // Act
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 5.0m, includeNews: false);

        // Assert
        result.Moves.Should().HaveCount(2);

        var positiveMove = result.Moves.First(m => m.IsPositive);
        positiveMove.Direction.Should().Be("up");
        positiveMove.PercentChange.Should().BePositive();

        var negativeMove = result.Moves.First(m => !m.IsPositive);
        negativeMove.Direction.Should().Be("down");
        negativeMove.PercentChange.Should().BeNegative();
    }

    [Fact]
    public async Task DetectSignificantMoves_WithZeroOpenPrice_SkipsDay()
    {
        // Arrange - Include a day with zero open price
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 0m, 105m, 95m, 100m),  // Zero open - should skip
            TestDataFactory.CreateOhlcvData(DateTime.Today, 100m, 110m, 95m, 108m)             // Valid +8%
        };

        // Act
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 5.0m, includeNews: false);

        // Assert - Only the valid day should be detected
        result.Moves.Should().HaveCount(1);
    }

    [Fact]
    public async Task DetectSignificantMoves_OrdersResultsByDateDescending()
    {
        // Arrange
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-3), 100m, 110m, 95m, 107m), // +7%
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-2), 100m, 110m, 95m, 106m), // +6%
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 100m, 110m, 95m, 108m), // +8%
        };

        // Act
        var result = await _sut.DetectSignificantMovesAsync("TEST", data, threshold: 5.0m, includeNews: false);

        // Assert - Results should be ordered by date descending (most recent first)
        result.Moves.Should().BeInDescendingOrder(m => m.Date);
    }

    #endregion

    #region CalculatePerformance Tests

    [Fact]
    public void CalculatePerformance_ReturnsCorrectTotalReturn()
    {
        // Arrange - First close: 100, Last close: 150 = 50% return
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-2), 95m, 105m, 90m, 100m),
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 100m, 120m, 95m, 120m),
            TestDataFactory.CreateOhlcvData(DateTime.Today, 120m, 155m, 115m, 150m)
        };

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result["totalReturn"].Should().Be(50m); // (150 - 100) / 100 * 100 = 50%
    }

    [Fact]
    public void CalculatePerformance_ReturnsCorrectHighAndLow()
    {
        // Arrange
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-2), 95m, 105m, 90m, 100m),
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 100m, 120m, 95m, 80m),  // Lowest
            TestDataFactory.CreateOhlcvData(DateTime.Today, 80m, 155m, 75m, 200m)               // Highest
        };

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result["highestClose"].Should().Be(200m);
        result["lowestClose"].Should().Be(80m);
    }

    [Fact]
    public void CalculatePerformance_ReturnsAverageVolume()
    {
        // Arrange
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-2), 100m, 105m, 95m, 100m, volume: 1000000),
            TestDataFactory.CreateOhlcvData(DateTime.Today.AddDays(-1), 100m, 105m, 95m, 100m, volume: 2000000),
            TestDataFactory.CreateOhlcvData(DateTime.Today, 100m, 105m, 95m, 100m, volume: 3000000)
        };

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result["averageVolume"].Should().Be(2000000m); // (1M + 2M + 3M) / 3 = 2M
    }

    [Fact]
    public void CalculatePerformance_WithEmptyData_ReturnsEmptyDictionary()
    {
        // Arrange
        var data = new List<OhlcvData>();

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public void CalculatePerformance_WithSingleDataPoint_ReturnsEmptyDictionary()
    {
        // Arrange
        var data = new List<OhlcvData>
        {
            TestDataFactory.CreateOhlcvData(DateTime.Today, 100m, 105m, 95m, 100m)
        };

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result.Should().BeEmpty("need at least 2 data points");
    }

    [Fact]
    public void CalculatePerformance_ReturnsVolatility()
    {
        // Arrange - Create data with known price movements
        var data = TestDataFactory.CreateOhlcvDataList(30);

        // Act
        var result = _sut.CalculatePerformance(data);

        // Assert
        result.Should().ContainKey("volatility");
        result["volatility"].Should().NotBeNull();
        result["volatility"].Should().BeGreaterOrEqualTo(0);
    }

    #endregion
}
