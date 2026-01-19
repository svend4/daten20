/**
 * BI Dashboard Controller
 *
 * Main controller for BI Dashboard functionality
 * Handles data fetching, KPI updates, filters, and user interactions
 */

class BIDashboardController {
    constructor() {
        this.biCharts = new BICharts();
        this.apiBaseUrl = '/api/v1/analytics';
        this.currentFilters = {
            dateRange: 30,
            tenant: 'all',
            comparisonPeriod: 'previous'
        };
        this.refreshInterval = null;
        this.autoRefreshEnabled = false;
    }

    /**
     * Initialize dashboard
     */
    async init() {
        this.setupEventListeners();
        await this.loadDashboard();
        this.biCharts.initializeAllCharts();
        this.startAutoRefresh(300000); // 5 minutes
    }

    /**
     * Setup event listeners for dashboard interactions
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Apply filters button
        const applyFiltersBtn = document.getElementById('applyFilters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        }

        // Export functionality
        const executeExportBtn = document.getElementById('executeExport');
        if (executeExportBtn) {
            executeExportBtn.addEventListener('click', () => this.executeExport());
        }

        // Save customization
        const saveCustomizationBtn = document.getElementById('saveCustomization');
        if (saveCustomizationBtn) {
            saveCustomizationBtn.addEventListener('click', () => this.saveCustomization());
        }

        // Chart action buttons
        document.querySelectorAll('[data-chart][data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chart = e.currentTarget.dataset.chart;
                const action = e.currentTarget.dataset.action;
                this.handleChartAction(chart, action);
            });
        });

        // Cohort metric selector
        const cohortMetricSelect = document.getElementById('cohortMetric');
        if (cohortMetricSelect) {
            cohortMetricSelect.addEventListener('change', (e) => {
                this.updateCohortChart(e.target.value);
            });
        }

        // Date range selector
        const dateRangeSelect = document.getElementById('dateRange');
        if (dateRangeSelect) {
            dateRangeSelect.addEventListener('change', (e) => {
                if (e.target.value === 'custom') {
                    this.showCustomDateRangePicker();
                }
            });
        }

        // Window resize handler
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.biCharts.resizeAllCharts();
            }, 250);
        });
    }

    /**
     * Load dashboard data
     */
    async loadDashboard() {
        try {
            this.showLoadingState();

            const filters = this.getCurrentFilters();
            const response = await this.fetchDashboardData(filters);

            if (response && response.success) {
                this.updateKPIs(response.kpis);
                this.updateCharts(response.charts);
                this.hideLoadingState();
            } else {
                throw new Error('Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data. Please try again.');
        }
    }

    /**
     * Fetch dashboard data from API
     */
    async fetchDashboardData(filters) {
        try {
            const queryParams = new URLSearchParams(filters);
            const response = await fetch(`${this.apiBaseUrl}/dashboard?${queryParams}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API fetch error:', error);
            // Return mock data for demo purposes
            return this.getMockDashboardData();
        }
    }

    /**
     * Update KPI cards with new data
     */
    updateKPIs(kpis) {
        if (!kpis) return;

        // Update MRR
        if (kpis.mrr) {
            this.updateKPICard('mrr', kpis.mrr);
        }

        // Update ARR
        if (kpis.arr) {
            this.updateKPICard('arr', kpis.arr);
        }

        // Update Churn Rate
        if (kpis.churn) {
            this.updateKPICard('churn', kpis.churn);
        }

        // Update CLV
        if (kpis.clv) {
            this.updateKPICard('clv', kpis.clv);
        }

        // Update NRR
        if (kpis.nrr) {
            this.updateKPICard('nrr', kpis.nrr);
        }

        // Update CAC
        if (kpis.cac) {
            this.updateKPICard('cac', kpis.cac);
        }
    }

    /**
     * Update individual KPI card
     */
    updateKPICard(kpiName, kpiData) {
        const valueElement = document.getElementById(`${kpiName}-value`);
        const changeElement = document.getElementById(`${kpiName}-change`);

        if (valueElement) {
            const formattedValue = this.formatKPIValue(kpiName, kpiData.value, kpiData.unit);
            valueElement.innerHTML = formattedValue;
        }

        if (changeElement && kpiData.change !== undefined) {
            const changeClass = kpiData.change > 0 ? 'positive' : (kpiData.change < 0 ? 'negative' : 'neutral');
            const changeIcon = kpiData.change > 0 ? '↑' : (kpiData.change < 0 ? '↓' : '→');
            const changeText = Math.abs(kpiData.change).toFixed(1);

            changeElement.className = `kpi-change ${changeClass}`;
            changeElement.innerHTML = `${changeIcon} ${changeText}% vs ${this.currentFilters.comparisonPeriod}`;
        }
    }

    /**
     * Format KPI value based on type
     */
    formatKPIValue(kpiName, value, unit) {
        if (unit === 'EUR' || unit === 'currency') {
            return '€' + this.formatCurrency(value);
        } else if (unit === '%' || unit === 'percentage') {
            return value.toFixed(1) + '%';
        } else {
            return value.toLocaleString();
        }
    }

    /**
     * Format currency values
     */
    formatCurrency(value) {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(2) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'k';
        } else {
            return value.toLocaleString();
        }
    }

    /**
     * Update charts with new data
     */
    updateCharts(chartsData) {
        if (!chartsData) return;

        if (chartsData.revenue) {
            this.biCharts.renderRevenueTrendChart(chartsData.revenue);
        }

        if (chartsData.breakdown) {
            this.biCharts.renderRevenueBreakdownChart(chartsData.breakdown);
        }

        if (chartsData.customers) {
            this.biCharts.renderCustomerGrowthChart(chartsData.customers);
        }

        if (chartsData.churn) {
            this.biCharts.renderChurnAnalysisChart(chartsData.churn);
        }

        if (chartsData.cohort) {
            this.biCharts.renderCohortAnalysisChart(chartsData.cohort);
        }
    }

    /**
     * Apply filters and refresh dashboard
     */
    async applyFilters() {
        this.currentFilters = {
            dateRange: document.getElementById('dateRange').value,
            tenant: document.getElementById('tenantFilter').value,
            comparisonPeriod: document.getElementById('comparisonPeriod').value
        };

        await this.loadDashboard();
    }

    /**
     * Get current filter values
     */
    getCurrentFilters() {
        return this.currentFilters;
    }

    /**
     * Refresh dashboard data
     */
    async refreshDashboard() {
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.classList.add('spinning');
        }

        await this.loadDashboard();

        if (refreshBtn) {
            setTimeout(() => {
                refreshBtn.classList.remove('spinning');
            }, 500);
        }
    }

    /**
     * Handle chart-specific actions
     */
    handleChartAction(chartName, action) {
        switch (action) {
            case 'download':
                this.downloadChart(chartName);
                break;
            case 'fullscreen':
                this.toggleFullscreen(chartName);
                break;
            default:
                console.warn(`Unknown action: ${action}`);
        }
    }

    /**
     * Download chart as image
     */
    downloadChart(chartName) {
        const filename = `${chartName}-chart-${new Date().toISOString().split('T')[0]}.png`;
        this.biCharts.downloadChart(chartName, filename);
    }

    /**
     * Toggle fullscreen mode for chart
     */
    toggleFullscreen(chartName) {
        // TODO: Implement fullscreen modal for charts
        console.log(`Fullscreen for ${chartName} chart`);
    }

    /**
     * Update cohort chart based on selected metric
     */
    updateCohortChart(metric) {
        // TODO: Fetch cohort data for specific metric
        console.log(`Update cohort chart for metric: ${metric}`);
        this.biCharts.renderCohortAnalysisChart();
    }

    /**
     * Execute export functionality
     */
    async executeExport() {
        const format = document.getElementById('exportFormat').value;
        const includeKPIs = document.getElementById('includeKPIs').checked;
        const includeCharts = document.getElementById('includeCharts').checked;
        const includeRawData = document.getElementById('includeRawData').checked;

        try {
            const response = await fetch(`${this.apiBaseUrl}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    format,
                    include: {
                        kpis: includeKPIs,
                        charts: includeCharts,
                        rawData: includeRawData
                    },
                    filters: this.currentFilters
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `bi-dashboard-${new Date().toISOString().split('T')[0]}.${format}`;
                a.click();
                window.URL.revokeObjectURL(url);

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
                if (modal) modal.hide();
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export dashboard. Please try again.');
        }
    }

    /**
     * Save dashboard customization
     */
    async saveCustomization() {
        // TODO: Implement customization save logic
        console.log('Save customization');

        const modal = bootstrap.Modal.getInstance(document.getElementById('customizeModal'));
        if (modal) modal.hide();
    }

    /**
     * Show custom date range picker
     */
    showCustomDateRangePicker() {
        // TODO: Implement custom date range picker
        console.log('Show custom date range picker');
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh(intervalMs = 300000) {
        this.stopAutoRefresh();

        this.autoRefreshEnabled = true;
        this.refreshInterval = setInterval(() => {
            if (this.autoRefreshEnabled) {
                this.refreshDashboard();
            }
        }, intervalMs);
    }

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        this.autoRefreshEnabled = false;
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        // Loading indicators are already in HTML as spinners
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        // Handled by updateKPIs
    }

    /**
     * Show error message
     */
    showError(message) {
        // TODO: Implement better error UI
        alert(message);
    }

    /**
     * Get mock dashboard data (for demo/testing)
     */
    getMockDashboardData() {
        return {
            success: true,
            kpis: {
                mrr: {
                    value: 122000,
                    unit: 'EUR',
                    change: 3.4,
                    trend: 'up'
                },
                arr: {
                    value: 1464000,
                    unit: 'EUR',
                    change: 3.4,
                    trend: 'up'
                },
                churn: {
                    value: 3.5,
                    unit: '%',
                    change: -1.7,
                    trend: 'down'
                },
                clv: {
                    value: 8500,
                    unit: 'EUR',
                    change: 5.2,
                    trend: 'up'
                },
                nrr: {
                    value: 108.5,
                    unit: '%',
                    change: 2.1,
                    trend: 'up'
                },
                cac: {
                    value: 850,
                    unit: 'EUR',
                    change: -4.3,
                    trend: 'down'
                }
            },
            charts: {}
        };
    }

    /**
     * Cleanup when dashboard is destroyed
     */
    destroy() {
        this.stopAutoRefresh();
        this.biCharts.destroyAllCharts();
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new BIDashboardController();
    dashboard.init();

    // Make dashboard accessible globally for debugging
    window.biDashboard = dashboard;
});
