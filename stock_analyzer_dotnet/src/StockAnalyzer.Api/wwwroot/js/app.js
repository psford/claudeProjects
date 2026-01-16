/**
 * Stock Analyzer Application
 * Main application logic
 */
const App = {
    currentTicker: null,
    currentPeriod: '1y',
    currentThreshold: 5,
    currentAnimal: 'cats',
    historyData: null,
    analysisData: null,
    significantMovesData: null,
    searchTimeout: null,
    hoverTimeout: null,
    hideTimeout: null,
    isHoverCardHovered: false,

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

        // Threshold slider
        const thresholdSlider = document.getElementById('threshold-slider');
        const thresholdValue = document.getElementById('threshold-value');
        thresholdSlider.addEventListener('input', (e) => {
            this.currentThreshold = parseInt(e.target.value);
            thresholdValue.textContent = `${this.currentThreshold}%`;
        });
        thresholdSlider.addEventListener('change', async () => {
            if (this.currentTicker) {
                await this.refreshSignificantMoves();
            }
        });

        // Show markers toggle
        document.getElementById('show-markers').addEventListener('change', () => this.updateChart());

        // Animal type toggle (cats vs dogs)
        document.querySelectorAll('input[name="animal-type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentAnimal = e.target.value;
            });
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
                API.getSignificantMoves(ticker, this.currentThreshold),
                API.getNews(ticker, 30)
            ]);

            this.historyData = history;
            this.analysisData = analysis;
            this.significantMovesData = significantMoves;

            this.renderStockInfo(stockInfo);
            this.renderKeyMetrics(stockInfo);
            this.renderPerformance(analysis.performance);
            this.renderChart();
            this.attachChartHoverListeners();
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
            showMa200: document.getElementById('ma-200').checked,
            significantMoves: this.significantMovesData,
            showMarkers: document.getElementById('show-markers').checked
        };

        Charts.renderStockChart('stock-chart', this.historyData, this.analysisData, options);
    },

    /**
     * Update chart with new options
     */
    updateChart() {
        if (this.historyData) {
            this.renderChart();
            this.attachChartHoverListeners();
        }
    },

    /**
     * Refresh significant moves with new threshold
     */
    async refreshSignificantMoves() {
        if (!this.currentTicker) return;

        try {
            this.significantMovesData = await API.getSignificantMoves(
                this.currentTicker,
                this.currentThreshold
            );
            this.renderChart();
            this.attachChartHoverListeners();
            this.renderSignificantMoves(this.significantMovesData);
        } catch (error) {
            console.error('Failed to refresh significant moves:', error);
        }
    },

    /**
     * Attach Plotly hover event listeners for significant move markers
     */
    attachChartHoverListeners() {
        const plot = document.getElementById('stock-chart');
        if (!plot) return;

        // Remove existing listeners by getting fresh reference
        plot.removeAllListeners?.('plotly_hover');
        plot.removeAllListeners?.('plotly_unhover');

        plot.on('plotly_hover', (data) => {
            const point = data.points[0];
            // Check if this is a marker trace (significant move)
            if (point.data.name && point.data.name.includes('Move') && point.customdata) {
                // Cancel any pending hide immediately
                if (this.hideTimeout) {
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = null;
                }
                // Cancel any pending show and reschedule
                if (this.hoverTimeout) clearTimeout(this.hoverTimeout);
                this.hoverTimeout = setTimeout(() => {
                    this.showHoverCard(data.event, point.customdata);
                }, 150); // Reduced from 200ms for snappier response
            }
        });

        plot.on('plotly_unhover', () => {
            if (this.hoverTimeout) {
                clearTimeout(this.hoverTimeout);
                this.hoverTimeout = null;
            }
            // Delay hiding to allow moving to the card
            this.scheduleHideHoverCard();
        });

        // Setup hover card mouse events (only once)
        const card = document.getElementById('wiki-hover-card');
        if (card && !card.dataset.listenersAttached) {
            card.dataset.listenersAttached = 'true';
            card.addEventListener('mouseenter', () => {
                this.isHoverCardHovered = true;
                if (this.hideTimeout) {
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = null;
                }
            });
            card.addEventListener('mouseleave', () => {
                this.isHoverCardHovered = false;
                this.scheduleHideHoverCard();
            });
        }
    },

    /**
     * Show Wikipedia-style hover card for significant move
     */
    showHoverCard(event, moveData) {
        // Cancel any pending hide when showing
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }

        const card = document.getElementById('wiki-hover-card');
        const image = document.getElementById('wiki-hover-image');
        const placeholder = document.getElementById('wiki-hover-placeholder');
        const dateEl = document.getElementById('wiki-hover-date');
        const returnEl = document.getElementById('wiki-hover-return');
        const headlineEl = document.getElementById('wiki-hover-headline');
        const summaryEl = document.getElementById('wiki-hover-summary');
        const sourceEl = document.getElementById('wiki-hover-source');

        // Format date
        const moveDate = new Date(moveData.date);
        dateEl.textContent = moveDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Format return
        const isPositive = moveData.percentChange >= 0;
        returnEl.textContent = `${isPositive ? '+' : ''}${moveData.percentChange.toFixed(2)}% ${moveData.magnitude} move`;
        returnEl.className = `text-sm font-bold mb-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`;

        // Check for related news
        const news = moveData.relatedNews && moveData.relatedNews.length > 0
            ? moveData.relatedNews[0]
            : null;

        // Get image URL based on selected animal type
        const setAnimalImage = async () => {
            const cacheBuster = Date.now() + Math.floor(Math.random() * 1000);

            // Set up error handler
            image.onerror = () => {
                image.classList.add('hidden');
                placeholder.classList.remove('hidden');
            };

            if (this.currentAnimal === 'dogs') {
                // Dog CEO API returns JSON with random dog image URL
                try {
                    const response = await fetch('https://dog.ceo/api/breeds/image/random');
                    const data = await response.json();
                    if (data.status === 'success') {
                        image.src = data.message;
                        image.classList.remove('hidden');
                        placeholder.classList.add('hidden');
                        return;
                    }
                } catch (e) {
                    console.error('Failed to fetch dog image:', e);
                }
                // Fallback to placeholder on error
                image.classList.add('hidden');
                placeholder.classList.remove('hidden');
                return;
            }

            // Cats - direct URL works
            image.src = `https://cataas.com/cat?width=320&height=150&${cacheBuster}`;
            image.classList.remove('hidden');
            placeholder.classList.add('hidden');
        };

        if (news) {
            // Show animal image (Finnhub images are just publisher logos)
            setAnimalImage();

            // Populate news content
            headlineEl.textContent = news.headline;
            headlineEl.href = news.url || '#';
            headlineEl.style.display = 'block';

            summaryEl.textContent = news.summary || '';
            summaryEl.style.display = news.summary ? 'block' : 'none';

            const newsDate = new Date(news.publishedAt);
            sourceEl.textContent = `${news.source} • ${newsDate.toLocaleDateString()}`;
        } else {
            // No news available - still show an animal
            setAnimalImage();

            headlineEl.textContent = 'No related news found';
            headlineEl.href = '#';
            headlineEl.style.display = 'block';

            summaryEl.textContent = 'No news articles were found for this date range.';
            summaryEl.style.display = 'block';

            sourceEl.textContent = '';
        }

        // Position the card near the cursor
        const x = event.clientX || event.pageX;
        const y = event.clientY || event.pageY;
        const cardWidth = 320;
        const cardHeight = 280;
        const padding = 15;

        let left = x + padding;
        let top = y - cardHeight / 2;

        // Keep within viewport
        if (left + cardWidth > window.innerWidth) {
            left = x - cardWidth - padding;
        }
        if (top < padding) {
            top = padding;
        }
        if (top + cardHeight > window.innerHeight) {
            top = window.innerHeight - cardHeight - padding;
        }

        card.style.left = `${left}px`;
        card.style.top = `${top}px`;
        card.classList.remove('hidden');
    },

    /**
     * Schedule hiding the hover card with delay
     */
    scheduleHideHoverCard() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
        }
        this.hideTimeout = setTimeout(() => {
            if (!this.isHoverCardHovered) {
                this.hideHoverCard();
            }
        }, 400); // 400ms delay to allow moving to card
    },

    /**
     * Hide the hover card
     */
    hideHoverCard() {
        document.getElementById('wiki-hover-card').classList.add('hidden');
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
