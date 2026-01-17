/**
 * Watchlist UI Manager
 * Handles all watchlist-related UI functionality
 */
const Watchlist = {
    watchlists: [],
    expandedWatchlists: new Set(),
    editingWatchlistId: null,

    /**
     * Initialize watchlist functionality
     */
    init() {
        this.bindEvents();
        this.loadWatchlists();
    },

    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Create watchlist buttons
        document.getElementById('create-watchlist-btn')?.addEventListener('click', () => this.openCreateModal());
        document.getElementById('create-first-watchlist')?.addEventListener('click', () => this.openCreateModal());
        document.getElementById('create-watchlist-from-dropdown')?.addEventListener('click', () => {
            this.hideWatchlistDropdown();
            this.openCreateModal();
        });

        // Modal events
        document.getElementById('watchlist-modal-close')?.addEventListener('click', () => this.closeModal());
        document.getElementById('watchlist-modal-cancel')?.addEventListener('click', () => this.closeModal());
        document.getElementById('watchlist-modal-overlay')?.addEventListener('click', () => this.closeModal());
        document.getElementById('watchlist-modal-save')?.addEventListener('click', () => this.saveWatchlist());

        // Enter key in modal input
        document.getElementById('watchlist-name-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.saveWatchlist();
            }
        });

        // Add to watchlist button
        document.getElementById('add-to-watchlist-btn')?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleWatchlistDropdown();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('watchlist-dropdown');
            const btn = document.getElementById('add-to-watchlist-btn');
            if (dropdown && !dropdown.contains(e.target) && !btn?.contains(e.target)) {
                this.hideWatchlistDropdown();
            }
        });
    },

    /**
     * Load all watchlists from API
     */
    async loadWatchlists() {
        const loadingEl = document.getElementById('watchlist-loading');
        const emptyEl = document.getElementById('watchlist-empty');
        const containerEl = document.getElementById('watchlist-container');
        const sidebarEl = document.getElementById('watchlist-sidebar');

        if (loadingEl) loadingEl.classList.remove('hidden');
        if (emptyEl) emptyEl.classList.add('hidden');
        if (containerEl) containerEl.innerHTML = '';

        try {
            this.watchlists = await API.getWatchlists();

            if (loadingEl) loadingEl.classList.add('hidden');

            if (this.watchlists.length === 0) {
                if (emptyEl) emptyEl.classList.remove('hidden');
            } else {
                this.renderWatchlists();
            }

            // Show sidebar
            if (sidebarEl) sidebarEl.classList.remove('hidden');

        } catch (error) {
            console.error('Failed to load watchlists:', error);
            if (loadingEl) loadingEl.classList.add('hidden');
            if (emptyEl) emptyEl.classList.remove('hidden');
        }
    },

    /**
     * Render all watchlists
     */
    renderWatchlists() {
        const containerEl = document.getElementById('watchlist-container');
        const emptyEl = document.getElementById('watchlist-empty');

        if (!containerEl) return;

        if (this.watchlists.length === 0) {
            containerEl.innerHTML = '';
            if (emptyEl) emptyEl.classList.remove('hidden');
            return;
        }

        if (emptyEl) emptyEl.classList.add('hidden');

        containerEl.innerHTML = this.watchlists.map(watchlist => this.renderWatchlistItem(watchlist)).join('');

        // Bind watchlist-specific events
        this.bindWatchlistEvents();
    },

    /**
     * Render a single watchlist item
     */
    renderWatchlistItem(watchlist) {
        const isExpanded = this.expandedWatchlists.has(watchlist.id);
        const tickerList = watchlist.tickers.map(ticker => `
            <div class="flex items-center justify-between py-1.5 px-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded group">
                <button class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary dark:hover:text-primary watchlist-ticker-btn" data-ticker="${ticker}">
                    ${ticker}
                </button>
                <button class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity remove-ticker-btn" data-watchlist-id="${watchlist.id}" data-ticker="${ticker}" title="Remove ${ticker}">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `).join('');

        return `
            <div class="border-b border-gray-200 dark:border-gray-700 last:border-b-0" data-watchlist-id="${watchlist.id}">
                <div class="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 watchlist-header" data-watchlist-id="${watchlist.id}">
                    <div class="flex items-center gap-2 flex-1 min-w-0">
                        <svg class="w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''} expand-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        <span class="font-medium text-gray-900 dark:text-white truncate">${this.escapeHtml(watchlist.name)}</span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">(${watchlist.tickers.length})</span>
                    </div>
                    <div class="flex items-center gap-1">
                        <button class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rename-watchlist-btn" data-watchlist-id="${watchlist.id}" title="Rename">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="p-1 text-gray-400 hover:text-red-500 delete-watchlist-btn" data-watchlist-id="${watchlist.id}" title="Delete">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="watchlist-tickers ${isExpanded ? '' : 'hidden'} px-3 pb-2">
                    ${watchlist.tickers.length > 0 ? tickerList : '<p class="text-sm text-gray-500 dark:text-gray-400 italic py-2">No tickers yet</p>'}
                </div>
            </div>
        `;
    },

    /**
     * Bind events for watchlist items
     */
    bindWatchlistEvents() {
        // Toggle expand/collapse
        document.querySelectorAll('.watchlist-header').forEach(header => {
            header.addEventListener('click', (e) => {
                // Don't toggle if clicking buttons
                if (e.target.closest('button')) return;

                const watchlistId = header.dataset.watchlistId;
                this.toggleWatchlist(watchlistId);
            });
        });

        // Rename buttons
        document.querySelectorAll('.rename-watchlist-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const watchlistId = btn.dataset.watchlistId;
                this.openRenameModal(watchlistId);
            });
        });

        // Delete buttons
        document.querySelectorAll('.delete-watchlist-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const watchlistId = btn.dataset.watchlistId;
                this.deleteWatchlist(watchlistId);
            });
        });

        // Ticker click to analyze
        document.querySelectorAll('.watchlist-ticker-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const ticker = btn.dataset.ticker;
                if (window.App && typeof window.App.analyzeStock === 'function') {
                    window.App.analyzeStock(ticker);
                } else {
                    // Fallback: set input and trigger search
                    const input = document.getElementById('ticker-input');
                    if (input) {
                        input.value = ticker;
                        document.getElementById('search-btn')?.click();
                    }
                }
            });
        });

        // Remove ticker buttons
        document.querySelectorAll('.remove-ticker-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const watchlistId = btn.dataset.watchlistId;
                const ticker = btn.dataset.ticker;
                await this.removeTicker(watchlistId, ticker);
            });
        });
    },

    /**
     * Toggle watchlist expand/collapse
     */
    toggleWatchlist(watchlistId) {
        const container = document.querySelector(`[data-watchlist-id="${watchlistId}"]`);
        if (!container) return;

        const tickersEl = container.querySelector('.watchlist-tickers');
        const iconEl = container.querySelector('.expand-icon');

        if (this.expandedWatchlists.has(watchlistId)) {
            this.expandedWatchlists.delete(watchlistId);
            tickersEl?.classList.add('hidden');
            iconEl?.classList.remove('rotate-90');
        } else {
            this.expandedWatchlists.add(watchlistId);
            tickersEl?.classList.remove('hidden');
            iconEl?.classList.add('rotate-90');
        }
    },

    /**
     * Open create watchlist modal
     */
    openCreateModal() {
        this.editingWatchlistId = null;
        const modal = document.getElementById('watchlist-modal');
        const title = document.getElementById('watchlist-modal-title');
        const input = document.getElementById('watchlist-name-input');

        if (title) title.textContent = 'Create Watchlist';
        if (input) input.value = '';
        if (modal) modal.classList.remove('hidden');

        setTimeout(() => input?.focus(), 100);
    },

    /**
     * Open rename watchlist modal
     */
    openRenameModal(watchlistId) {
        const watchlist = this.watchlists.find(w => w.id === watchlistId);
        if (!watchlist) return;

        this.editingWatchlistId = watchlistId;
        const modal = document.getElementById('watchlist-modal');
        const title = document.getElementById('watchlist-modal-title');
        const input = document.getElementById('watchlist-name-input');

        if (title) title.textContent = 'Rename Watchlist';
        if (input) input.value = watchlist.name;
        if (modal) modal.classList.remove('hidden');

        setTimeout(() => {
            input?.focus();
            input?.select();
        }, 100);
    },

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('watchlist-modal');
        if (modal) modal.classList.add('hidden');
        this.editingWatchlistId = null;
    },

    /**
     * Save watchlist (create or rename)
     */
    async saveWatchlist() {
        const input = document.getElementById('watchlist-name-input');
        const name = input?.value?.trim();

        if (!name) {
            input?.focus();
            return;
        }

        try {
            if (this.editingWatchlistId) {
                await API.renameWatchlist(this.editingWatchlistId, name);
            } else {
                await API.createWatchlist(name);
            }

            this.closeModal();
            await this.loadWatchlists();
        } catch (error) {
            console.error('Failed to save watchlist:', error);
            alert('Failed to save watchlist. Please try again.');
        }
    },

    /**
     * Delete a watchlist
     */
    async deleteWatchlist(watchlistId) {
        const watchlist = this.watchlists.find(w => w.id === watchlistId);
        if (!watchlist) return;

        if (!confirm(`Delete "${watchlist.name}"? This cannot be undone.`)) {
            return;
        }

        try {
            await API.deleteWatchlist(watchlistId);
            this.expandedWatchlists.delete(watchlistId);
            await this.loadWatchlists();
        } catch (error) {
            console.error('Failed to delete watchlist:', error);
            alert('Failed to delete watchlist. Please try again.');
        }
    },

    /**
     * Add current stock to a watchlist
     */
    async addCurrentStockToWatchlist(watchlistId) {
        const currentTicker = window.App?.currentTicker;
        if (!currentTicker) {
            alert('No stock selected. Please analyze a stock first.');
            return;
        }

        try {
            await API.addTickerToWatchlist(watchlistId, currentTicker);
            this.hideWatchlistDropdown();
            await this.loadWatchlists();

            // Expand the watchlist we just added to
            this.expandedWatchlists.add(watchlistId);
            this.renderWatchlists();
        } catch (error) {
            console.error('Failed to add ticker to watchlist:', error);
            alert('Failed to add ticker to watchlist. Please try again.');
        }
    },

    /**
     * Remove a ticker from a watchlist
     */
    async removeTicker(watchlistId, ticker) {
        try {
            await API.removeTickerFromWatchlist(watchlistId, ticker);
            await this.loadWatchlists();

            // Keep the watchlist expanded
            this.expandedWatchlists.add(watchlistId);
            this.renderWatchlists();
        } catch (error) {
            console.error('Failed to remove ticker:', error);
            alert('Failed to remove ticker. Please try again.');
        }
    },

    /**
     * Toggle the "Add to Watchlist" dropdown
     */
    toggleWatchlistDropdown() {
        const dropdown = document.getElementById('watchlist-dropdown');
        if (!dropdown) return;

        if (dropdown.classList.contains('hidden')) {
            this.showWatchlistDropdown();
        } else {
            this.hideWatchlistDropdown();
        }
    },

    /**
     * Show the "Add to Watchlist" dropdown
     */
    showWatchlistDropdown() {
        const dropdown = document.getElementById('watchlist-dropdown');
        const itemsContainer = document.getElementById('watchlist-dropdown-items');

        if (!dropdown || !itemsContainer) return;

        // Populate dropdown with watchlists
        if (this.watchlists.length === 0) {
            itemsContainer.innerHTML = '<p class="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">No watchlists yet</p>';
        } else {
            const currentTicker = window.App?.currentTicker?.toUpperCase();

            itemsContainer.innerHTML = this.watchlists.map(watchlist => {
                const hasTicker = watchlist.tickers.some(t => t.toUpperCase() === currentTicker);
                return `
                    <button class="w-full flex items-center justify-between px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 ${hasTicker ? 'opacity-50 cursor-not-allowed' : ''}"
                            data-watchlist-id="${watchlist.id}"
                            ${hasTicker ? 'disabled' : ''}>
                        <span>${this.escapeHtml(watchlist.name)}</span>
                        ${hasTicker ? '<span class="text-green-500 text-xs">Added</span>' : ''}
                    </button>
                `;
            }).join('');

            // Bind click events
            itemsContainer.querySelectorAll('button:not([disabled])').forEach(btn => {
                btn.addEventListener('click', () => {
                    const watchlistId = btn.dataset.watchlistId;
                    this.addCurrentStockToWatchlist(watchlistId);
                });
            });
        }

        dropdown.classList.remove('hidden');
    },

    /**
     * Hide the "Add to Watchlist" dropdown
     */
    hideWatchlistDropdown() {
        const dropdown = document.getElementById('watchlist-dropdown');
        if (dropdown) dropdown.classList.add('hidden');
    },

    /**
     * Show the "Add to Watchlist" button (called when a stock is loaded)
     */
    showAddToWatchlistButton() {
        const container = document.getElementById('add-to-watchlist-container');
        if (container) container.classList.remove('hidden');
    },

    /**
     * Hide the "Add to Watchlist" button
     */
    hideAddToWatchlistButton() {
        const container = document.getElementById('add-to-watchlist-container');
        if (container) container.classList.add('hidden');
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Watchlist.init();
});
