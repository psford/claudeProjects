"""
Stock Analysis Tool using yfinance
A basic utility for fetching and analyzing stock data.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def get_stock_info(ticker: str) -> dict:
    """Get basic information about a stock."""
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": info.get("longName", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
        "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "dividend_yield": info.get("dividendYield", "N/A"),
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


if __name__ == "__main__":
    # Example usage
    print_stock_summary("AAPL")
