/**
 * Stock Analyzer API Client
 * Handles all API calls to the .NET backend
 */
const API = {
    baseUrl: '/api',

    /**
     * Get stock information
     * @param {string} ticker - Stock ticker symbol
     */
    async getStockInfo(ticker) {
        const response = await fetch(`${this.baseUrl}/stock/${ticker}`);
        if (!response.ok) {
            throw new Error(`Stock not found: ${ticker}`);
        }
        return response.json();
    },

    /**
     * Get historical price data
     * @param {string} ticker - Stock ticker symbol
     * @param {string} period - Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
     */
    async getHistory(ticker, period = '1y') {
        const response = await fetch(`${this.baseUrl}/stock/${ticker}/history?period=${period}`);
        if (!response.ok) {
            throw new Error('Failed to fetch historical data');
        }
        return response.json();
    },

    /**
     * Get stock analysis (performance metrics + moving averages)
     * @param {string} ticker - Stock ticker symbol
     * @param {string} period - Time period
     */
    async getAnalysis(ticker, period = '1y') {
        const response = await fetch(`${this.baseUrl}/stock/${ticker}/analysis?period=${period}`);
        if (!response.ok) {
            throw new Error('Failed to fetch analysis data');
        }
        return response.json();
    },

    /**
     * Get significant price moves
     * @param {string} ticker - Stock ticker symbol
     * @param {number} threshold - Minimum percentage change to consider significant
     */
    async getSignificantMoves(ticker, threshold = 3) {
        const response = await fetch(`${this.baseUrl}/stock/${ticker}/significant?threshold=${threshold}`);
        if (!response.ok) {
            throw new Error('Failed to fetch significant moves');
        }
        return response.json();
    },

    /**
     * Get company news
     * @param {string} ticker - Stock ticker symbol
     * @param {number} days - Number of days of news to fetch
     */
    async getNews(ticker, days = 30) {
        const response = await fetch(`${this.baseUrl}/stock/${ticker}/news?days=${days}`);
        if (!response.ok) {
            throw new Error('Failed to fetch news');
        }
        return response.json();
    },

    /**
     * Search for tickers
     * @param {string} query - Search query
     */
    async search(query) {
        const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Search failed');
        }
        return response.json();
    },

    /**
     * Get trending stocks
     * @param {number} count - Number of stocks to fetch
     */
    async getTrending(count = 10) {
        const response = await fetch(`${this.baseUrl}/trending?count=${count}`);
        if (!response.ok) {
            throw new Error('Failed to fetch trending stocks');
        }
        return response.json();
    },

    /**
     * Health check
     */
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }
};
