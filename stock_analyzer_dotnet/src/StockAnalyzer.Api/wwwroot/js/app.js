/**
 * Stock Analyzer Application
 * Main application logic
 */
const App = {
    currentTicker: null,
    currentPeriod: '1y',
    historyData: null,
    analysisData: null,
    searchTimeout: null,

    /**
     * Initialize the application
     */
    init() {
        this.bindEvents();
        this.checkApiHealth();
    },

    /**
     * Bind UI event handlers
     */
    bindEvents() {
        const tickerInput = document.getElementById('ticker-input');
        const searchResults = document.getElementById('search-results');

        // Search button
        document.getElementById('search-btn').addEventListener('click', () => this.analyzeStock());

        // Autocomplete on input
        tickerInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (this.searchTimeout) clearTimeout(this.searchTimeout);

            if (query.length < 2) {
                this.hideSearchResults();
                return;
            }

            // Debounce search
            this.searchTimeout = setTimeout(() => this.performSearch(query), 300);
        });

        // Enter key in ticker input
        tickerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.hideSearchResults();
                this.analyzeStock();
            }
        });

        // Hide results on blur (with delay to allow click)
        tickerInput.addEventListener('blur', () => {
            setTimeout(() => this.hideSearchResults(), 200);
        });

        // Show results on focus if there's a query
        tickerInput.addEventListener('focus', (e) => {
            if (e.target.value.trim().length >= 2) {
                this.performSearch(e.target.value.trim());
            }
        });

        // Period change
        document.getElementById('period-select').addEventListener('change', (e) => {
            this.currentPeriod = e.target.value;
            if (this.currentTicker) this.analyzeStock();
        });

        // Chart type change
        document.getElementById('chart-type').addEventListener('change', () => this.updateChart());

        // Moving average toggles
        ['ma-20', 'ma-50', 'ma-200'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateChart());
        });
    },

    /**
     * Perform search for autocomplete
     */
    async performSearch(query) {
        const loader = document.getElementById('search-loader');
        loader.classList.remove('hidden');

        try {
            const data = await API.search(query);
            this.showSearchResults(data.results);
        } catch (error) {
            console.error('Search failed:', error);
            this.hideSearchResults();
        } finally {
            loader.classList.add('hidden');
        }
    },

    /**
     * Show search results dropdown
     */
    showSearchResults(results) {
        const container = document.getElementById('search-results');

        if (!results || results.length === 0) {
            container.innerHTML = '<div class="px-4 py-3 text-gray-500 text-sm">No results found</div>';
            container.classList.remove('hidden');
            return;
        }

        container.innerHTML = results.map(r => `
            <div class="search-result px-4 py-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-0"
                 data-symbol="${r.symbol}">
                <div class="font-medium text-gray-900">${r.symbol}</div>
                <div class="text-sm text-gray-600">${r.shortName || r.longName || ''}</div>
                <div class="text-xs text-gray-400">${r.exchange || ''} ${r.type ? `• ${r.type}` : ''}</div>
            </div>
        `).join('');

        // Add click handlers to results
        container.querySelectorAll('.search-result').forEach(el => {
            el.addEventListener('click', () => {
                const symbol = el.dataset.symbol;
                document.getElementById('ticker-input').value = symbol;
                this.hideSearchResults();
                this.analyzeStock();
            });
        });

        container.classList.remove('hidden');
    },

    /**
     * Hide search results dropdown
     */
    hideSearchResults() {
        document.getElementById('search-results').classList.add('hidden');
    },

    /**
     * Check if API is healthy
     */
    async checkApiHealth() {
        try {
            await API.healthCheck();
            console.log('API is healthy');
        } catch (error) {
            console.error('API health check failed:', error);
        }
    },

    /**
     * Main analysis function
     */
    async analyzeStock() {
        const ticker = document.getElementById('ticker-input').value.trim().toUpperCase();
        if (!ticker) {
            this.showError('Please enter a stock ticker');
            return;
        }

        this.currentTicker = ticker;
        this.currentPeriod = document.getElementById('period-select').value;
        this.showLoading();

        try {
            // Fetch all data in parallel
            const [stockInfo, history, analysis, significantMoves, news] = await Promise.all([
                API.getStockInfo(ticker),
                API.getHistory(ticker, this.currentPeriod),
                API.getAnalysis(ticker, this.currentPeriod),
                API.getSignificantMoves(ticker, 3),
                API.getNews(ticker, 30)
            ]);

            this.historyData = history;
            this.analysisData = analysis;

            this.renderStockInfo(stockInfo);
            this.renderKeyMetrics(stockInfo);
            this.renderPerformance(analysis.performance);
            this.renderChart();
            this.renderSignificantMoves(significantMoves);
            this.renderNews(news);

            this.showResults();
        } catch (error) {
            this.showError(error.message);
        }
    },

    /**
     * Render stock info section
     */
    renderStockInfo(info) {
        const priceChange = info.dayChange || 0;
        const priceChangePercent = info.dayChangePercent || 0;
        const isPositive = priceChange >= 0;

        document.getElementById('stock-info').innerHTML = `
            <div>
                <h2 class="text-2xl font-bold text-gray-900">${info.symbol}</h2>
                <p class="text-gray-600">${info.shortName || info.symbol}</p>
                <p class="text-sm text-gray-500">${info.exchange || ''} ${info.currency ? `• ${info.currency}` : ''}</p>
            </div>
            <div class="text-right">
                <div class="text-3xl font-bold text-gray-900">
                    $${this.formatNumber(info.currentPrice)}
                </div>
                <div class="text-lg ${isPositive ? 'text-success' : 'text-danger'}">
                    ${isPositive ? '+' : ''}${this.formatNumber(priceChange)} (${isPositive ? '+' : ''}${this.formatNumber(priceChangePercent)}%)
                </div>
            </div>
        `;
    },

    /**
     * Render key metrics
     */
    renderKeyMetrics(info) {
        const metrics = [
            { label: 'Market Cap', value: this.formatLargeNumber(info.marketCap) },
            { label: 'P/E Ratio', value: this.formatNumber(info.peRatio) },
            { label: '52W High', value: `$${this.formatNumber(info.fiftyTwoWeekHigh)}` },
            { label: '52W Low', value: `$${this.formatNumber(info.fiftyTwoWeekLow)}` },
            { label: 'Avg Volume', value: this.formatLargeNumber(info.averageVolume) },
            { label: 'Dividend Yield', value: info.dividendYield ? `${(info.dividendYield * 100).toFixed(2)}%` : 'N/A' }
        ];

        document.getElementById('key-metrics').innerHTML = metrics.map(m => `
            <div class="flex justify-between">
                <span class="text-gray-600">${m.label}</span>
                <span class="font-medium text-gray-900">${m.value || 'N/A'}</span>
            </div>
        `).join('');
    },

    /**
     * Render performance metrics
     */
    renderPerformance(performance) {
        if (!performance) {
            document.getElementById('performance-metrics').innerHTML = '<p class="text-gray-500">No performance data available</p>';
            return;
        }

        const metrics = [
            { label: 'Total Return', value: `${performance.totalReturn >= 0 ? '+' : ''}${this.formatNumber(performance.totalReturn)}%`, color: performance.totalReturn >= 0 ? 'text-success' : 'text-danger' },
            { label: 'Volatility (Ann.)', value: `${this.formatNumber(performance.volatility)}%` },
            { label: 'Highest Close', value: `$${this.formatNumber(performance.highestClose)}` },
            { label: 'Lowest Close', value: `$${this.formatNumber(performance.lowestClose)}` },
            { label: 'Avg Volume', value: this.formatLargeNumber(performance.averageVolume) }
        ];

        document.getElementById('performance-metrics').innerHTML = metrics.map(m => `
            <div class="flex justify-between">
                <span class="text-gray-600">${m.label}</span>
                <span class="font-medium ${m.color || 'text-gray-900'}">${m.value || 'N/A'}</span>
            </div>
        `).join('');
    },

    /**
     * Render significant moves
     */
    renderSignificantMoves(data) {
        if (!data || !data.moves || data.moves.length === 0) {
            document.getElementById('significant-moves').innerHTML = '<p class="text-gray-500">No significant moves found</p>';
            return;
        }

        document.getElementById('significant-moves').innerHTML = data.moves.slice(0, 10).map(move => {
            const isPositive = move.percentChange >= 0;
            const date = new Date(move.date).toLocaleDateString();
            return `
                <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-gray-600">${date}</span>
                    <span class="font-medium ${isPositive ? 'text-success' : 'text-danger'}">
                        ${isPositive ? '+' : ''}${this.formatNumber(move.percentChange)}%
                    </span>
                </div>
            `;
        }).join('');
    },

    /**
     * Render news
     */
    renderNews(data) {
        if (!data || !data.articles || data.articles.length === 0) {
            document.getElementById('news-list').innerHTML = '<p class="text-gray-500">No recent news available</p>';
            return;
        }

        document.getElementById('news-list').innerHTML = data.articles.slice(0, 5).map(article => {
            const date = new Date(article.publishedAt).toLocaleDateString();
            return `
                <div class="border-b border-gray-100 pb-4">
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer"
                       class="text-primary hover:text-blue-700 font-medium">
                        ${article.headline}
                    </a>
                    <p class="text-sm text-gray-500 mt-1">${article.source} • ${date}</p>
                    ${article.summary ? `<p class="text-gray-600 mt-2 text-sm">${article.summary.substring(0, 150)}...</p>` : ''}
                </div>
            `;
        }).join('');
    },

    /**
     * Render chart
     */
    renderChart() {
        const options = {
            chartType: document.getElementById('chart-type').value,
            showMa20: document.getElementById('ma-20').checked,
            showMa50: document.getElementById('ma-50').checked,
            showMa200: document.getElementById('ma-200').checked
        };

        Charts.renderStockChart('stock-chart', this.historyData, this.analysisData, options);
    },

    /**
     * Update chart with new options
     */
    updateChart() {
        if (this.historyData) {
            this.renderChart();
        }
    },

    /**
     * Show loading state
     */
    showLoading() {
        document.getElementById('results-section').classList.add('hidden');
        document.getElementById('error-section').classList.add('hidden');
        document.getElementById('loading-section').classList.remove('hidden');
    },

    /**
     * Show results
     */
    showResults() {
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('error-section').classList.add('hidden');
        document.getElementById('results-section').classList.remove('hidden');
    },

    /**
     * Show error
     */
    showError(message) {
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('results-section').classList.add('hidden');
        document.getElementById('error-section').classList.remove('hidden');
        document.getElementById('error-message').textContent = message;
    },

    /**
     * Format number
     */
    formatNumber(value) {
        if (value == null) return 'N/A';
        return Number(value).toFixed(2);
    },

    /**
     * Format large number (millions, billions)
     */
    formatLargeNumber(value) {
        if (value == null) return 'N/A';
        if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
        if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
        if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
        if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
        return value.toString();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());
