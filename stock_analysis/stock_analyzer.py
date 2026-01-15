"""
Stock Analysis Tool using yfinance
A basic utility for fetching and analyzing stock data.
"""

import yfinance as yf
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional
import finnhub
from dotenv import load_dotenv
import os

# Load environment variables for API keys
load_dotenv()
_finnhub_client = None


def _get_finnhub_client():
    """Get or create Finnhub client (singleton)."""
    global _finnhub_client
    if _finnhub_client is None:
        api_key = os.getenv("FINNHUB_API_KEY")
        if api_key:
            _finnhub_client = finnhub.Client(api_key=api_key)
    return _finnhub_client


def search_tickers(query: str, max_results: int = 10) -> list:
    """
    Search for ticker symbols by company name or symbol.

    Args:
        query: Search term (company name or partial ticker)
        max_results: Maximum number of results to return

    Returns:
        List of dicts with 'symbol', 'name', 'exchange', 'type' keys
    """
    if not query or len(query) < 1:
        return []

    try:
        search = yf.Search(query, max_results=max_results)
        results = []

        for quote in search.quotes:
            results.append({
                "symbol": quote.get("symbol", ""),
                "name": quote.get("longname") or quote.get("shortname", ""),
                "exchange": quote.get("exchDisp", ""),
                "type": quote.get("typeDisp", "Equity"),
            })

        return results
    except Exception:
        return []


def get_news_for_date(ticker: str, target_date: datetime, lookback_days: int = 2) -> Optional[str]:
    """
    Get the most relevant news headline for a stock on or before a specific date.

    News that causes price moves often comes out after market close the prior day,
    so we look back up to lookback_days before the target date.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        target_date: The date of the significant price move
        lookback_days: Number of days to look back for news (default 2)

    Returns:
        Most relevant headline string, or None if no news found
    """
    client = _get_finnhub_client()
    if not client:
        return None

    try:
        # Convert target_date to datetime if it's a pandas Timestamp
        if hasattr(target_date, 'to_pydatetime'):
            target_date = target_date.to_pydatetime()

        # Search from lookback_days before to the target date
        start_date = target_date - timedelta(days=lookback_days)
        end_date = target_date

        news = client.company_news(
            ticker,
            _from=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )

        if news:
            # Sort by datetime (newest first) and return the most recent headline
            news_sorted = sorted(news, key=lambda x: x.get('datetime', 0), reverse=True)
            return news_sorted[0].get('headline', None)

        return None

    except Exception:
        return None


def get_news_for_dates(ticker: str, dates: list) -> dict:
    """
    Batch fetch news headlines for multiple dates.

    Args:
        ticker: Stock symbol
        dates: List of datetime objects

    Returns:
        Dict mapping date to headline (or None if no news)
    """
    if not dates:
        return {}

    client = _get_finnhub_client()
    if not client:
        return {d: None for d in dates}

    try:
        # Find the overall date range
        min_date = min(dates)
        max_date = max(dates)

        # Convert to datetime if pandas Timestamp
        if hasattr(min_date, 'to_pydatetime'):
            min_date = min_date.to_pydatetime()
        if hasattr(max_date, 'to_pydatetime'):
            max_date = max_date.to_pydatetime()

        # Fetch all news in the range (with 2 day buffer for lookback)
        start_date = min_date - timedelta(days=2)
        end_date = max_date

        all_news = client.company_news(
            ticker,
            _from=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )

        # Build a lookup by date
        news_by_date = {}
        for item in all_news:
            news_ts = item.get('datetime', 0)
            if news_ts:
                news_date = datetime.fromtimestamp(news_ts).date()
                if news_date not in news_by_date:
                    news_by_date[news_date] = []
                news_by_date[news_date].append(item.get('headline', ''))

        # For each target date, find news from that day or 1-2 days prior
        results = {}
        for target in dates:
            target_dt = target.to_pydatetime() if hasattr(target, 'to_pydatetime') else target
            target_d = target_dt.date()

            # Check target date, then day before, then 2 days before
            headline = None
            for offset in range(3):
                check_date = target_d - timedelta(days=offset)
                if check_date in news_by_date and news_by_date[check_date]:
                    headline = news_by_date[check_date][0]  # Most recent on that day
                    break

            results[target] = headline

        return results

    except Exception:
        return {d: None for d in dates}


def get_stock_info(ticker: str) -> dict:
    """Get basic information about a stock."""
    stock = yf.Ticker(ticker)
    info = stock.info

    # Validate dividend yield - yfinance can return inconsistent values
    # Expected format: decimal (0.004 = 0.4%), but sometimes returns 100x higher
    raw_yield = info.get("dividendYield", "N/A")
    if isinstance(raw_yield, (int, float)):
        if raw_yield > 0.10:
            # Value > 10% is likely inflated by 100x, correct it
            dividend_yield = raw_yield / 100
        else:
            dividend_yield = raw_yield
    else:
        dividend_yield = "N/A"

    return {
        "name": info.get("longName", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
        "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "dividend_yield": dividend_yield,
        "beta": info.get("beta", "N/A"),
    }


def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical price data.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo

    Returns:
        DataFrame with OHLCV data
    """
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)


def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily and cumulative returns."""
    df = df.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Cumulative_Return"] = (1 + df["Daily_Return"]).cumprod() - 1
    return df


def calculate_moving_averages(df: pd.DataFrame, windows: list = [20, 50, 200]) -> pd.DataFrame:
    """Add moving averages to the dataframe."""
    df = df.copy()
    for window in windows:
        df[f"MA_{window}"] = df["Close"].rolling(window=window).mean()
    return df


def calculate_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """Calculate annualized volatility."""
    daily_returns = df["Close"].pct_change().dropna()
    return daily_returns.std() * (252 ** 0.5)  # Annualized


def get_financials(ticker: str) -> dict:
    """Get financial statements."""
    stock = yf.Ticker(ticker)
    return {
        "income_statement": stock.income_stmt,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow,
    }


def compare_stocks(tickers: list, period: str = "1y") -> pd.DataFrame:
    """Compare multiple stocks' performance."""
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if not hist.empty:
            # Normalize to starting price
            data[ticker] = hist["Close"] / hist["Close"].iloc[0] * 100

    return pd.DataFrame(data)


def print_stock_summary(ticker: str):
    """Print a formatted summary of stock information."""
    print(f"\n{'='*50}")
    print(f"Stock Analysis: {ticker.upper()}")
    print(f"{'='*50}\n")

    # Basic info
    info = get_stock_info(ticker)
    print("COMPANY INFO:")
    print(f"  Name: {info['name']}")
    print(f"  Sector: {info['sector']}")
    print(f"  Industry: {info['industry']}")
    print(f"  Market Cap: ${info['market_cap']:,}" if isinstance(info['market_cap'], (int, float)) else f"  Market Cap: {info['market_cap']}")

    print("\nPRICE DATA:")
    print(f"  Current Price: ${info['current_price']:.2f}" if isinstance(info['current_price'], (int, float)) else f"  Current Price: {info['current_price']}")
    print(f"  52-Week High: ${info['52_week_high']:.2f}" if isinstance(info['52_week_high'], (int, float)) else f"  52-Week High: {info['52_week_high']}")
    print(f"  52-Week Low: ${info['52_week_low']:.2f}" if isinstance(info['52_week_low'], (int, float)) else f"  52-Week Low: {info['52_week_low']}")

    print("\nKEY METRICS:")
    print(f"  P/E Ratio: {info['pe_ratio']:.2f}" if isinstance(info['pe_ratio'], (int, float)) else f"  P/E Ratio: {info['pe_ratio']}")
    print(f"  Dividend Yield: {info['dividend_yield']*100:.2f}%" if isinstance(info['dividend_yield'], (int, float)) else f"  Dividend Yield: {info['dividend_yield']}")
    print(f"  Beta: {info['beta']:.2f}" if isinstance(info['beta'], (int, float)) else f"  Beta: {info['beta']}")

    # Historical data analysis
    hist = get_historical_data(ticker, period="1y")
    if not hist.empty:
        volatility = calculate_volatility(hist)
        hist_with_returns = calculate_returns(hist)
        total_return = hist_with_returns["Cumulative_Return"].iloc[-1] * 100

        print("\nPERFORMANCE (1 Year):")
        print(f"  Total Return: {total_return:.2f}%")
        print(f"  Annualized Volatility: {volatility*100:.2f}%")

    print(f"\n{'='*50}\n")


def plot_candlestick(ticker: str, period: str = "6mo", volume: bool = True,
                     style: str = "tradingview", save_path: str = None):
    """
    Plot a candlestick chart for a stock.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        volume: Include volume bars below chart
        style: Chart style (charles, yahoo, nightclouds, blueskies, etc.)
        save_path: Optional file path to save the chart (e.g., 'chart.png')
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        print(f"No data available for {ticker}")
        return

    title = f"{ticker.upper()} - {period} Candlestick Chart"

    kwargs = {
        "type": "candle",
        "volume": volume,
        "style": style,
        "title": title,
        "ylabel": "Price ($)",
        "ylabel_lower": "Volume" if volume else "",
    }

    if save_path:
        kwargs["savefig"] = save_path
        mpf.plot(df, **kwargs)
        print(f"Chart saved to {save_path}")
    else:
        mpf.plot(df, **kwargs)


def plot_with_moving_averages(ticker: str, period: str = "1y",
                               mav: tuple = (20, 50, 200), volume: bool = True,
                               style: str = "tradingview", save_path: str = None):
    """
    Plot candlestick chart with moving average overlays.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        mav: Tuple of moving average windows (default: 20, 50, 200)
        volume: Include volume bars below chart
        style: Chart style
        save_path: Optional file path to save the chart
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        print(f"No data available for {ticker}")
        return

    title = f"{ticker.upper()} with MA-{', '.join(map(str, mav))}"

    kwargs = {
        "type": "candle",
        "volume": volume,
        "style": style,
        "title": title,
        "ylabel": "Price ($)",
        "mav": mav,
    }

    if save_path:
        kwargs["savefig"] = save_path
        mpf.plot(df, **kwargs)
        print(f"Chart saved to {save_path}")
    else:
        mpf.plot(df, **kwargs)


def plot_ohlc(ticker: str, period: str = "6mo", volume: bool = True,
              style: str = "tradingview", save_path: str = None):
    """
    Plot an OHLC (Open-High-Low-Close) bar chart.

    Args:
        ticker: Stock symbol
        period: Time period
        volume: Include volume bars
        style: Chart style
        save_path: Optional file path to save the chart
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        print(f"No data available for {ticker}")
        return

    title = f"{ticker.upper()} - {period} OHLC Chart"

    kwargs = {
        "type": "ohlc",
        "volume": volume,
        "style": style,
        "title": title,
        "ylabel": "Price ($)",
    }

    if save_path:
        kwargs["savefig"] = save_path
        mpf.plot(df, **kwargs)
        print(f"Chart saved to {save_path}")
    else:
        mpf.plot(df, **kwargs)


def plot_line(ticker: str, period: str = "1y", volume: bool = False,
              style: str = "tradingview", save_path: str = None):
    """
    Plot a simple line chart of closing prices.

    Args:
        ticker: Stock symbol
        period: Time period
        volume: Include volume bars
        style: Chart style
        save_path: Optional file path to save the chart
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        print(f"No data available for {ticker}")
        return

    title = f"{ticker.upper()} - {period} Price History"

    kwargs = {
        "type": "line",
        "volume": volume,
        "style": style,
        "title": title,
        "ylabel": "Price ($)",
    }

    if save_path:
        kwargs["savefig"] = save_path
        mpf.plot(df, **kwargs)
        print(f"Chart saved to {save_path}")
    else:
        mpf.plot(df, **kwargs)


def list_chart_styles():
    """List all available mplfinance chart styles."""
    styles = mpf.available_styles()
    print("Available chart styles:")
    for s in styles:
        print(f"  - {s}")
    return styles


# =============================================================================
# Plotly Interactive Charts (for web interface)
# =============================================================================

def create_plotly_candlestick(ticker: str, period: str = "6mo",
                               show_volume: bool = True,
                               moving_averages: list = None) -> go.Figure:
    """
    Create an interactive Plotly candlestick chart.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        show_volume: Include volume subplot
        moving_averages: List of MA windows to display (e.g., [20, 50, 200])

    Returns:
        Plotly Figure object
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        return None

    # Create figure with secondary y-axis for volume
    if show_volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{ticker.upper()} - {period}", "Volume")
        )
    else:
        fig = go.Figure()

    # Add candlestick trace
    candlestick = go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350"
    )

    if show_volume:
        fig.add_trace(candlestick, row=1, col=1)
    else:
        fig.add_trace(candlestick)

    # Add moving averages
    if moving_averages:
        colors = ["#2196F3", "#FF9800", "#9C27B0", "#4CAF50"]
        for i, window in enumerate(moving_averages):
            if len(df) >= window:
                ma = df["Close"].rolling(window=window).mean()
                ma_trace = go.Scatter(
                    x=df.index,
                    y=ma,
                    mode="lines",
                    name=f"MA-{window}",
                    line=dict(color=colors[i % len(colors)], width=1.5)
                )
                if show_volume:
                    fig.add_trace(ma_trace, row=1, col=1)
                else:
                    fig.add_trace(ma_trace)

    # Add markers for significant daily moves (>= 5% change)
    daily_returns = df["Close"].pct_change()
    significant_up = daily_returns >= 0.05
    significant_down = daily_returns <= -0.05

    # Batch fetch news for all significant dates
    all_significant_dates = list(df.index[significant_up | significant_down])
    news_headlines = get_news_for_dates(ticker, all_significant_dates) if all_significant_dates else {}

    # Markers for +5% days (green circles above the high)
    if significant_up.any():
        up_dates = df.index[significant_up]
        up_prices = df.loc[significant_up, "High"] * 1.02  # Slightly above high
        up_returns = daily_returns[significant_up] * 100

        # Build hover text with news
        up_hover_text = []
        for date, ret in zip(up_dates, up_returns):
            headline = news_headlines.get(date, None)
            text = f"{date.strftime('%Y-%m-%d')}<br>Change: +{ret:.1f}%"
            if headline:
                # Truncate long headlines
                if len(headline) > 80:
                    headline = headline[:77] + "..."
                text += f"<br><br><b>News:</b> {headline}"
            up_hover_text.append(text)

        up_trace = go.Scatter(
            x=up_dates,
            y=up_prices,
            mode="markers",
            name="+5% Move",
            marker=dict(
                symbol="circle",
                size=12,
                color="#4CAF50",
                line=dict(color="white", width=1)
            ),
            hovertemplate="%{text}<extra></extra>",
            text=up_hover_text
        )
        if show_volume:
            fig.add_trace(up_trace, row=1, col=1)
        else:
            fig.add_trace(up_trace)

    # Markers for -5% days (red circles below the low)
    if significant_down.any():
        down_dates = df.index[significant_down]
        down_prices = df.loc[significant_down, "Low"] * 0.98  # Slightly below low
        down_returns = daily_returns[significant_down] * 100

        # Build hover text with news
        down_hover_text = []
        for date, ret in zip(down_dates, down_returns):
            headline = news_headlines.get(date, None)
            text = f"{date.strftime('%Y-%m-%d')}<br>Change: {ret:.1f}%"
            if headline:
                # Truncate long headlines
                if len(headline) > 80:
                    headline = headline[:77] + "..."
                text += f"<br><br><b>News:</b> {headline}"
            down_hover_text.append(text)

        down_trace = go.Scatter(
            x=down_dates,
            y=down_prices,
            mode="markers",
            name="-5% Move",
            marker=dict(
                symbol="circle",
                size=12,
                color="#F44336",
                line=dict(color="white", width=1)
            ),
            hovertemplate="%{text}<extra></extra>",
            text=down_hover_text
        )
        if show_volume:
            fig.add_trace(down_trace, row=1, col=1)
        else:
            fig.add_trace(down_trace)

    # Add volume bars
    if show_volume:
        colors = ["#ef5350" if df["Close"].iloc[i] < df["Open"].iloc[i]
                  else "#26a69a" for i in range(len(df))]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                marker_color=colors,
                name="Volume",
                showlegend=False
            ),
            row=2, col=1
        )

    # Update layout
    fig.update_layout(
        title=f"{ticker.upper()} Stock Price",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    if show_volume:
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_plotly_line(ticker: str, period: str = "1y",
                        moving_averages: list = None) -> go.Figure:
    """
    Create an interactive Plotly line chart.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        period: Time period
        moving_averages: List of MA windows to display

    Returns:
        Plotly Figure object
    """
    df = get_historical_data(ticker, period=period)
    if df.empty:
        return None

    fig = go.Figure()

    # Add closing price line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Close",
        line=dict(color="#2196F3", width=2)
    ))

    # Add moving averages
    if moving_averages:
        colors = ["#FF9800", "#9C27B0", "#4CAF50", "#F44336"]
        for i, window in enumerate(moving_averages):
            if len(df) >= window:
                ma = df["Close"].rolling(window=window).mean()
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=ma,
                    mode="lines",
                    name=f"MA-{window}",
                    line=dict(color=colors[i % len(colors)], width=1.5)
                ))

    # Add markers for significant daily moves (>= 5% change)
    daily_returns = df["Close"].pct_change()
    significant_up = daily_returns >= 0.05
    significant_down = daily_returns <= -0.05

    # Batch fetch news for all significant dates
    all_significant_dates = list(df.index[significant_up | significant_down])
    news_headlines = get_news_for_dates(ticker, all_significant_dates) if all_significant_dates else {}

    # Markers for +5% days (green circles on the close price)
    if significant_up.any():
        up_dates = df.index[significant_up]
        up_prices = df.loc[significant_up, "Close"]
        up_returns = daily_returns[significant_up] * 100

        # Build hover text with news
        up_hover_text = []
        for date, ret in zip(up_dates, up_returns):
            headline = news_headlines.get(date, None)
            text = f"{date.strftime('%Y-%m-%d')}<br>Change: +{ret:.1f}%"
            if headline:
                if len(headline) > 80:
                    headline = headline[:77] + "..."
                text += f"<br><br><b>News:</b> {headline}"
            up_hover_text.append(text)

        fig.add_trace(go.Scatter(
            x=up_dates,
            y=up_prices,
            mode="markers",
            name="+5% Move",
            marker=dict(
                symbol="circle",
                size=12,
                color="#4CAF50",
                line=dict(color="white", width=1)
            ),
            hovertemplate="%{text}<extra></extra>",
            text=up_hover_text
        ))

    # Markers for -5% days (red circles on the close price)
    if significant_down.any():
        down_dates = df.index[significant_down]
        down_prices = df.loc[significant_down, "Close"]
        down_returns = daily_returns[significant_down] * 100

        # Build hover text with news
        down_hover_text = []
        for date, ret in zip(down_dates, down_returns):
            headline = news_headlines.get(date, None)
            text = f"{date.strftime('%Y-%m-%d')}<br>Change: {ret:.1f}%"
            if headline:
                if len(headline) > 80:
                    headline = headline[:77] + "..."
                text += f"<br><br><b>News:</b> {headline}"
            down_hover_text.append(text)

        fig.add_trace(go.Scatter(
            x=down_dates,
            y=down_prices,
            mode="markers",
            name="-5% Move",
            marker=dict(
                symbol="circle",
                size=12,
                color="#F44336",
                line=dict(color="white", width=1)
            ),
            hovertemplate="%{text}<extra></extra>",
            text=down_hover_text
        ))

    fig.update_layout(
        title=f"{ticker.upper()} - {period} Price History",
        yaxis_title="Price ($)",
        xaxis_title="Date",
        template="plotly_white",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


if __name__ == "__main__":
    # Example usage
    print_stock_summary("AAPL")
