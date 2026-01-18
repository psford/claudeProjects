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
    },

    // ============================================
    // Watchlist API Methods
    // ============================================

    /**
     * Get all watchlists
     */
    async getWatchlists() {
        const response = await fetch(`${this.baseUrl}/watchlists`);
        if (!response.ok) {
            throw new Error('Failed to fetch watchlists');
        }
        return response.json();
    },

    /**
     * Create a new watchlist
     * @param {string} name - Watchlist name
     */
    async createWatchlist(name) {
        const response = await fetch(`${this.baseUrl}/watchlists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) {
            throw new Error('Failed to create watchlist');
        }
        return response.json();
    },

    /**
     * Get a watchlist by ID
     * @param {string} id - Watchlist ID
     */
    async getWatchlist(id) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}`);
        if (!response.ok) {
            throw new Error('Watchlist not found');
        }
        return response.json();
    },

    /**
     * Rename a watchlist
     * @param {string} id - Watchlist ID
     * @param {string} name - New name
     */
    async renameWatchlist(id, name) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) {
            throw new Error('Failed to rename watchlist');
        }
        return response.json();
    },

    /**
     * Delete a watchlist
     * @param {string} id - Watchlist ID
     */
    async deleteWatchlist(id) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error('Failed to delete watchlist');
        }
        return true;
    },

    /**
     * Add a ticker to a watchlist
     * @param {string} id - Watchlist ID
     * @param {string} ticker - Ticker symbol
     */
    async addTickerToWatchlist(id, ticker) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}/tickers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker })
        });
        if (!response.ok) {
            throw new Error('Failed to add ticker to watchlist');
        }
        return response.json();
    },

    /**
     * Remove a ticker from a watchlist
     * @param {string} id - Watchlist ID
     * @param {string} ticker - Ticker symbol
     */
    async removeTickerFromWatchlist(id, ticker) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}/tickers/${ticker}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error('Failed to remove ticker from watchlist');
        }
        return response.json();
    },

    /**
     * Get quotes for all tickers in a watchlist
     * @param {string} id - Watchlist ID
     */
    async getWatchlistQuotes(id) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}/quotes`);
        if (!response.ok) {
            throw new Error('Failed to fetch watchlist quotes');
        }
        return response.json();
    },

    /**
     * Update holdings for a watchlist
     * @param {string} id - Watchlist ID
     * @param {string} weightingMode - "equal", "shares", or "dollars"
     * @param {Array} holdings - Array of {ticker, shares, dollarValue}
     */
    async updateWatchlistHoldings(id, weightingMode, holdings) {
        const response = await fetch(`${this.baseUrl}/watchlists/${id}/holdings`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ weightingMode, holdings })
        });
        if (!response.ok) {
            throw new Error('Failed to update holdings');
        }
        return response.json();
    },

    /**
     * Get combined portfolio performance for a watchlist
     * @param {string} id - Watchlist ID
     * @param {string} period - Time period (1mo, 3mo, 6mo, 1y, 2y)
     * @param {string} benchmark - Optional benchmark ticker (SPY, QQQ)
     */
    async getCombinedPortfolio(id, period = '1y', benchmark = null) {
        let url = `${this.baseUrl}/watchlists/${id}/combined?period=${period}`;
        if (benchmark) {
            url += `&benchmark=${benchmark}`;
        }
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch combined portfolio');
        }
        return response.json();
    },

    /**
     * Get general market news
     * @param {string} category - News category: general, forex, crypto, merger
     */
    async getMarketNews(category = 'general') {
        const response = await fetch(`${this.baseUrl}/news/market?category=${category}`);
        if (!response.ok) {
            throw new Error('Failed to fetch market news');
        }
        return response.json();
    }
};
