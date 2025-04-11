/**
 * Chart Manager for Farm Data application
 * Manages chart creation and rendering
 */
import { formatTimestamp, getChartTitle, getChartYAxisLabel, getChartDataInfo } from './utils.js';

export class ChartManager {
    constructor() {
        this.chartCanvas = document.getElementById('farmDataChart');
        this.chartInstance = null;
        this.chartType = 'all'; // Default to showing all data
    }

    // Set the chart type 
    setChartType(type) {
        this.chartType = type;
    }

    // Render chart with given data
    renderChart(data) {
        try {
            console.log('Rendering chart - Starting');
            
            if (!this.chartCanvas) {
                console.error('Chart canvas element not found');
                return;
            }
            
            console.log('Canvas dimensions:', this.chartCanvas.width, 'x', this.chartCanvas.height);
            
            // Check if Chart.js is available
            if (typeof Chart === 'undefined') {
                console.error('Chart.js library is not loaded');
                return;
            }
            
            console.log('Selected chart type:', this.chartType);
            
            // Check if we have data to display
            if (!data || data.length === 0) {
                this._handleEmptyData();
                return;
            }
            
            // Get time-sorted data (oldest to newest for proper display)
            const chartData = [...data].sort((a, b) => Number(a.timestamp) - Number(b.timestamp));
            
            // Prepare data for chart
            const labels = chartData.map(item => formatTimestamp(item.timestamp));
            
            // Destroy existing chart if it exists
            this._destroyExistingChart();
            
            // Reset the canvas to ensure a clean state
            this._resetCanvas();
            
            try {
                // Create the chart configuration
                const config = this._createChartConfig(chartData, labels);
                
                console.log('Chart configuration created, now instantiating Chart');
                
                // Create new chart with the config
                this.chartInstance = new Chart(this.chartCanvas, config);
                
                console.log('Chart created successfully');
            } catch (chartError) {
                console.error('Error creating chart:', chartError);
                this._createFallbackChart();
            }
        } catch (e) {
            console.error('Error rendering chart:', e);
            this._displayErrorMessage();
        }
    }

    // Handle empty data set
    _handleEmptyData() {
        console.warn('No data available for chart');
        // Clear any existing chart
        this._destroyExistingChart();
        
        // Display a message
        const ctx = this.chartCanvas.getContext('2d');
        ctx.clearRect(0, 0, this.chartCanvas.width, this.chartCanvas.height);
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#666';
        ctx.fillText('Không có dữ liệu để hiển thị trong khoảng thời gian đã chọn', this.chartCanvas.width / 2, this.chartCanvas.height / 2);
    }

    // Destroy existing chart instance
    _destroyExistingChart() {
        if (this.chartInstance) {
            console.log('Destroying existing chart');
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }

    // Reset canvas
    _resetCanvas() {
        console.log('Resetting canvas');
        this.chartCanvas.width = this.chartCanvas.width;
        
        // Set canvas dimensions to ensure it's visible
        this.chartCanvas.style.width = '100%';
        this.chartCanvas.style.height = '400px';
    }

    // Create chart configuration
    _createChartConfig(chartData, labels) {
        // Create chart config
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: this.chartType === 'all' 
                            ? `Biểu đồ tổng hợp tất cả dữ liệu - Nông trại ${chartData[0]?.farmId || ''}`
                            : `Biểu đồ ${getChartTitle(this.chartType)} theo thời gian - Nông trại ${chartData[0]?.farmId || ''}`,
                        font: {
                            size: 18
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Thời gian'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: this.chartType === 'all' ? 'Giá trị' : getChartYAxisLabel(this.chartType)
                        },
                        beginAtZero: true
                    }
                }
            }
        };
        
        // Add datasets based on chart type
        if (this.chartType === 'all') {
            this._addAllDatasets(config, chartData);
        } else {
            this._addSingleDataset(config, chartData);
        }
        
        return config;
    }

    // Add all datasets for the "all" chart type
    _addAllDatasets(config, chartData) {
        // Add dataset for temperature
        config.data.datasets.push({
            label: 'Nhiệt độ (°C)',
            data: chartData.map(item => item.temperature),
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            yAxisID: 'y'
        });
        
        // Add dataset for humidity
        config.data.datasets.push({
            label: 'Độ ẩm (%)',
            data: chartData.map(item => item.humidity),
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            yAxisID: 'y'
        });
        
        // Add dataset for water level
        config.data.datasets.push({
            label: 'Độ ẩm đất (%)',
            data: chartData.map(item => item.waterLevel),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            yAxisID: 'y'
        });
        
        // Add dataset for light level
        config.data.datasets.push({
            label: 'Độ sáng (%)',
            data: chartData.map(item => item.lightLevel),
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            yAxisID: 'y'
        });
    }

    // Add a single dataset for specific chart types
    _addSingleDataset(config, chartData) {
        const dataInfo = getChartDataInfo(this.chartType);
        config.data.datasets.push({
            label: dataInfo.title,
            data: chartData.map(item => item[this.chartType]),
            backgroundColor: dataInfo.color.replace('1)', '0.2)'),
            borderColor: dataInfo.color,
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3
        });
    }

    // Create a simple fallback chart in case of error
    _createFallbackChart() {
        try {
            this._destroyExistingChart();
            
            // Very basic chart as fallback
            this.chartInstance = new Chart(this.chartCanvas, {
                type: 'bar',
                data: {
                    labels: ['Dữ liệu'],
                    datasets: [{
                        label: 'Dữ liệu mẫu',
                        data: [5],
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            console.log('Created fallback chart');
        } catch (fallbackError) {
            console.error('Even fallback chart failed:', fallbackError);
        }
    }

    // Display error message on canvas
    _displayErrorMessage() {
        try {
            if (this.chartCanvas) {
                const ctx = this.chartCanvas.getContext('2d');
                ctx.clearRect(0, 0, this.chartCanvas.width, this.chartCanvas.height);
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillStyle = '#dc3545';
                ctx.fillText('Lỗi khi hiển thị biểu đồ', this.chartCanvas.width / 2, this.chartCanvas.height / 2);
            }
        } catch (canvasError) {
            console.error('Could not display error on canvas:', canvasError);
        }
    }
} 