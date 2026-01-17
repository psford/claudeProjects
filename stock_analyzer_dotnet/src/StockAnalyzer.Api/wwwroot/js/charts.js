/**
 * Stock Chart Configuration
 * Handles Plotly.js chart rendering
 */
const Charts = {
    /**
     * Check if dark mode is currently enabled
     */
    isDarkMode() {
        return document.documentElement.classList.contains('dark');
    },

    /**
     * Get theme-aware colors
     */
    getThemeColors() {
        const isDark = this.isDarkMode();
        return {
            background: isDark ? '#1F2937' : '#FFFFFF',
            paper: isDark ? '#1F2937' : '#FFFFFF',
            text: isDark ? '#F9FAFB' : '#1F2937',
            gridColor: isDark ? '#374151' : '#E5E7EB',
            axisColor: isDark ? '#9CA3AF' : '#6B7280'
        };
    },

    /**
     * Render stock chart with OHLC data
     * @param {string} elementId - DOM element ID
     * @param {Object} historyData - Historical data from API
     * @param {Object} analysisData - Analysis data with moving averages
     * @param {Object} options - Chart options
     */
    renderStockChart(elementId, historyData, analysisData, options = {}) {
        const {
            chartType = 'candlestick',
            showMa20 = true,
            showMa50 = true,
            showMa200 = false,
            significantMoves = null,
            showMarkers = true
        } = options;

        const data = historyData.data;
        const dates = data.map(d => d.date);
        const opens = data.map(d => d.open);
        const highs = data.map(d => d.high);
        const lows = data.map(d => d.low);
        const closes = data.map(d => d.close);
        const volumes = data.map(d => d.volume);

        const traces = [];

        // Main price chart
        if (chartType === 'candlestick') {
            traces.push({
                type: 'candlestick',
                x: dates,
                open: opens,
                high: highs,
                low: lows,
                close: closes,
                name: historyData.symbol,
                increasing: { line: { color: '#10B981' } },
                decreasing: { line: { color: '#EF4444' } }
            });
        } else {
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: dates,
                y: closes,
                name: historyData.symbol,
                line: { color: '#3B82F6', width: 2 }
            });
        }

        // Moving averages
        if (analysisData && analysisData.movingAverages) {
            const maData = analysisData.movingAverages;
            const maDates = maData.map(d => d.date);

            if (showMa20) {
                const ma20 = maData.map(d => d.sma20).filter(v => v != null);
                const ma20Dates = maDates.slice(maDates.length - ma20.length);
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: ma20Dates,
                    y: ma20,
                    name: 'SMA 20',
                    line: { color: '#F59E0B', width: 1, dash: 'dot' }
                });
            }

            if (showMa50) {
                const ma50 = maData.map(d => d.sma50).filter(v => v != null);
                const ma50Dates = maDates.slice(maDates.length - ma50.length);
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: ma50Dates,
                    y: ma50,
                    name: 'SMA 50',
                    line: { color: '#8B5CF6', width: 1, dash: 'dot' }
                });
            }

            if (showMa200) {
                const ma200 = maData.map(d => d.sma200).filter(v => v != null);
                const ma200Dates = maDates.slice(maDates.length - ma200.length);
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: ma200Dates,
                    y: ma200,
                    name: 'SMA 200',
                    line: { color: '#EC4899', width: 1, dash: 'dot' }
                });
            }
        }

        // Add significant move markers
        if (showMarkers && significantMoves && significantMoves.moves && significantMoves.moves.length > 0) {
            const moves = significantMoves.moves;
            const threshold = significantMoves.threshold || 5;

            // Separate positive and negative moves
            const upMoves = moves.filter(m => m.isPositive);
            const downMoves = moves.filter(m => !m.isPositive);

            // Green markers for positive moves (positioned above the high)
            if (upMoves.length > 0) {
                // Find corresponding high prices for positioning
                const upY = upMoves.map(m => {
                    const dateStr = m.date.split('T')[0];
                    const dataPoint = data.find(d => d.date.startsWith(dateStr));
                    return dataPoint ? dataPoint.high * 1.02 : m.closePrice * 1.02;
                });

                const upTrace = {
                    type: 'scatter',
                    mode: 'markers',
                    x: upMoves.map(m => m.date.split('T')[0]),
                    y: upY,
                    name: `+${threshold}% Move`,
                    marker: {
                        color: '#10B981',
                        size: 22,
                        symbol: 'triangle-up',
                        line: { color: '#065F46', width: 2 }
                    },
                    customdata: upMoves,
                    hoverinfo: 'text',
                    hovertext: upMoves.map(m => `+${m.percentChange.toFixed(1)}%`),
                    showlegend: true
                };
                traces.push(upTrace);
            }

            // Red markers for negative moves (positioned below the low)
            if (downMoves.length > 0) {
                // Find corresponding low prices for positioning
                const downY = downMoves.map(m => {
                    const dateStr = m.date.split('T')[0];
                    const dataPoint = data.find(d => d.date.startsWith(dateStr));
                    return dataPoint ? dataPoint.low * 0.98 : m.closePrice * 0.98;
                });

                const downTrace = {
                    type: 'scatter',
                    mode: 'markers',
                    x: downMoves.map(m => m.date.split('T')[0]),
                    y: downY,
                    name: `-${threshold}% Move`,
                    marker: {
                        color: '#EF4444',
                        size: 22,
                        symbol: 'triangle-down',
                        line: { color: '#991B1B', width: 2 }
                    },
                    customdata: downMoves,
                    hoverinfo: 'text',
                    hovertext: downMoves.map(m => `${m.percentChange.toFixed(1)}%`),
                    showlegend: true
                };
                traces.push(downTrace);
            }
        }

        const themeColors = this.getThemeColors();

        const layout = {
            title: {
                text: `${historyData.symbol} - ${historyData.period.toUpperCase()}`,
                font: { size: 18, color: themeColors.text }
            },
            xaxis: {
                title: { text: 'Date', font: { color: themeColors.axisColor } },
                rangeslider: { visible: false },
                gridcolor: themeColors.gridColor,
                tickfont: { color: themeColors.axisColor },
                linecolor: themeColors.gridColor
            },
            yaxis: {
                title: { text: 'Price ($)', font: { color: themeColors.axisColor } },
                gridcolor: themeColors.gridColor,
                tickfont: { color: themeColors.axisColor },
                linecolor: themeColors.gridColor
            },
            plot_bgcolor: themeColors.background,
            paper_bgcolor: themeColors.paper,
            showlegend: true,
            legend: {
                orientation: 'h',
                yanchor: 'top',
                y: -0.15,
                xanchor: 'center',
                x: 0.5,
                font: { color: themeColors.axisColor }
            },
            autosize: true,
            margin: { t: 50, r: 30, b: 80, l: 60, autoexpand: true },
            hovermode: 'closest',
            hoverdistance: 20
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        Plotly.newPlot(elementId, traces, layout, config).then(() => {
            // Trigger resize after initial render to ensure full width
            const chartEl = document.getElementById(elementId);
            if (chartEl) {
                Plotly.Plots.resize(chartEl);
            }
        });
    },

    /**
     * Update chart with new options
     */
    updateChart(elementId, historyData, analysisData, options) {
        this.renderStockChart(elementId, historyData, analysisData, options);
    }
};
