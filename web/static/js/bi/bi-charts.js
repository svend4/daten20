/**
 * BI Dashboard Charts Module
 *
 * Provides chart rendering and data visualization for Business Intelligence Dashboard
 * Uses Chart.js library for rendering
 */

class BICharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#2563eb',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            secondary: '#6b7280',
            gradient: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd']
        };

        // Chart.js default configuration
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
    }

    /**
     * Initialize all charts on the dashboard
     */
    initializeAllCharts() {
        this.renderRevenueTrendChart();
        this.renderRevenueBreakdownChart();
        this.renderCustomerGrowthChart();
        this.renderChurnAnalysisChart();
        this.renderCohortAnalysisChart();
    }

    /**
     * Render Revenue Trend Line Chart
     */
    renderRevenueTrendChart(data = null) {
        const ctx = document.getElementById('revenueTrendChart');
        if (!ctx) return;

        // Default data if not provided
        const chartData = data || {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'MRR',
                    data: [85000, 88000, 92000, 95000, 97000, 100000, 103000, 107000, 110000, 115000, 118000, 122000],
                    borderColor: this.colors.primary,
                    backgroundColor: this.createGradient(ctx, this.colors.primary),
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Target',
                    data: Array(12).fill(100000),
                    borderColor: this.colors.warning,
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }
            ]
        };

        if (this.charts.revenueTrend) {
            this.charts.revenueTrend.destroy();
        }

        this.charts.revenueTrend = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': €' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '€' + (value / 1000) + 'k';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    /**
     * Render Revenue Breakdown Pie Chart
     */
    renderRevenueBreakdownChart(data = null) {
        const ctx = document.getElementById('revenueBreakdownChart');
        if (!ctx) return;

        const chartData = data || {
            labels: ['Enterprise', 'Professional', 'Starter', 'Trial'],
            datasets: [{
                data: [450000, 280000, 150000, 20000],
                backgroundColor: [
                    this.colors.primary,
                    this.colors.info,
                    this.colors.success,
                    this.colors.secondary
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        if (this.charts.revenueBreakdown) {
            this.charts.revenueBreakdown.destroy();
        }

        this.charts.revenueBreakdown = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return label + ': €' + value.toLocaleString() + ' (' + percentage + '%)';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    /**
     * Render Customer Growth Chart
     */
    renderCustomerGrowthChart(data = null) {
        const ctx = document.getElementById('customerGrowthChart');
        if (!ctx) return;

        const chartData = data || {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'New Customers',
                    data: [45, 52, 48, 65, 58, 70, 68, 75, 72, 80, 85, 90],
                    backgroundColor: this.colors.success,
                    borderColor: this.colors.success,
                    borderWidth: 1
                },
                {
                    label: 'Churned Customers',
                    data: [-8, -5, -10, -7, -12, -9, -11, -8, -10, -7, -9, -6],
                    backgroundColor: this.colors.danger,
                    borderColor: this.colors.danger,
                    borderWidth: 1
                },
                {
                    label: 'Net Growth',
                    data: [37, 47, 38, 58, 46, 61, 57, 67, 62, 73, 76, 84],
                    type: 'line',
                    borderColor: this.colors.primary,
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: this.colors.primary,
                    tension: 0.4
                }
            ]
        };

        if (this.charts.customerGrowth) {
            this.charts.customerGrowth.destroy();
        }

        this.charts.customerGrowth = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * Render Churn Analysis Chart
     */
    renderChurnAnalysisChart(data = null) {
        const ctx = document.getElementById('churnAnalysisChart');
        if (!ctx) return;

        const chartData = data || {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'Churn Rate (%)',
                    data: [5.2, 3.8, 6.1, 4.5, 7.2, 5.5, 6.3, 4.8, 5.9, 4.2, 5.1, 3.5],
                    borderColor: this.colors.danger,
                    backgroundColor: this.createGradient(ctx, this.colors.danger, 0.2),
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Total Customers',
                    data: [850, 890, 920, 975, 1015, 1070, 1125, 1185, 1235, 1300, 1365, 1440],
                    borderColor: this.colors.info,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        };

        if (this.charts.churnAnalysis) {
            this.charts.churnAnalysis.destroy();
        }

        this.charts.churnAnalysis = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Churn Rate (%)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Total Customers'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * Render Cohort Analysis Heatmap
     */
    renderCohortAnalysisChart(data = null) {
        const ctx = document.getElementById('cohortAnalysisChart');
        if (!ctx) return;

        // Generate cohort data matrix
        const cohorts = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const months = ['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'];

        const chartData = data || {
            labels: months,
            datasets: cohorts.map((cohort, i) => ({
                label: cohort,
                data: this.generateCohortData(6 - i),
                backgroundColor: this.generateHeatmapColors(6 - i),
                borderWidth: 1,
                borderColor: '#fff'
            }))
        };

        if (this.charts.cohortAnalysis) {
            this.charts.cohortAnalysis.destroy();
        }

        this.charts.cohortAnalysis = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ' - Month ' + context.dataIndex + ': ' +
                                       context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        title: {
                            display: true,
                            text: 'Retention Rate'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * Generate cohort data for demo
     */
    generateCohortData(length) {
        const data = [];
        let retention = 100;
        for (let i = 0; i < length; i++) {
            data.push(retention);
            retention = retention * (0.85 + Math.random() * 0.1); // Simulate decay
        }
        return data;
    }

    /**
     * Generate heatmap colors based on value
     */
    generateHeatmapColors(length) {
        const colors = [];
        for (let i = 0; i < length; i++) {
            const intensity = 1 - (i / length);
            colors.push(`rgba(37, 99, 235, ${intensity})`);
        }
        return colors;
    }

    /**
     * Create gradient for charts
     */
    createGradient(ctx, color, opacity = 0.3) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);

        if (color.startsWith('#')) {
            // Convert hex to rgba
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${opacity})`);
            gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
        } else {
            gradient.addColorStop(0, color.replace(')', `, ${opacity})`).replace('rgb', 'rgba'));
            gradient.addColorStop(1, color.replace(')', ', 0)').replace('rgb', 'rgba'));
        }

        return gradient;
    }

    /**
     * Update chart with new data
     */
    updateChart(chartName, newData) {
        const chart = this.charts[chartName];
        if (!chart) {
            console.error(`Chart "${chartName}" not found`);
            return;
        }

        chart.data = newData;
        chart.update('active');
    }

    /**
     * Download chart as image
     */
    downloadChart(chartName, filename = 'chart.png') {
        const chart = this.charts[chartName];
        if (!chart) {
            console.error(`Chart "${chartName}" not found`);
            return;
        }

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
    }

    /**
     * Destroy all charts (cleanup)
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Resize all charts (useful for responsive layouts)
     */
    resizeAllCharts() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].resize();
            }
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BICharts;
}
