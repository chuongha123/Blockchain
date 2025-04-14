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
            
            // Group data to reduce number of points
            const groupedData = this._groupDataByTimeInterval(chartData);
            
            // Prepare data for chart
            const labels = groupedData.map(item => formatTimestamp(item.timestamp));
            
            // Destroy existing chart if it exists
            this._destroyExistingChart();
            
            // Reset the canvas to ensure a clean state
            this._resetCanvas();
            
            try {
                // Create the chart configuration
                const config = this._createChartConfig(groupedData, labels);
                
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

    // Group data by time intervals to reduce chart complexity
    _groupDataByTimeInterval(data) {
        // If data length is reasonable, return as is
        if (data.length <= 24) {
            return data;
        }
        
        // Determine grouping interval based on data size
        let intervalMinutes;
        if (data.length > 100) {
            intervalMinutes = 240; // 4 hours if very large dataset
        } else if (data.length > 50) {
            intervalMinutes = 120; // 2 hours if large dataset
        } else {
            intervalMinutes = 60; // 1 hour otherwise
        }
        
        console.log(`Grouping data by ${intervalMinutes} minute intervals`);
        
        const intervals = {};
        const intervalMs = intervalMinutes * 60 * 1000;
        
        // Group data into time intervals
        data.forEach(item => {
            const timestamp = Number(item.timestamp) * 1000;
            const intervalKey = Math.floor(timestamp / intervalMs) * intervalMs; // Round to interval
            
            if (!intervals[intervalKey]) {
                intervals[intervalKey] = {
                    count: 0,
                    temperature: 0,
                    humidity: 0,
                    waterLevel: 0,
                    lightLevel: 0,
                    farmId: item.farmId,
                    timestamp: Math.floor(intervalKey / 1000) // Convert back to seconds for consistency
                };
            }
            
            intervals[intervalKey].count++;
            intervals[intervalKey].temperature += Number(item.temperature || 0);
            intervals[intervalKey].humidity += Number(item.humidity || 0);
            intervals[intervalKey].waterLevel += Number(item.waterLevel || 0);
            intervals[intervalKey].lightLevel += Number(item.lightLevel || 0);
        });
        
        // Calculate averages and create result array
        const result = Object.values(intervals).map(interval => {
            return {
                timestamp: interval.timestamp,
                temperature: interval.temperature / interval.count,
                humidity: interval.humidity / interval.count,
                waterLevel: interval.waterLevel / interval.count,
                lightLevel: interval.lightLevel / interval.count,
                farmId: interval.farmId,
                groupedCount: interval.count
            };
        });
        
        console.log(`Reduced data points from ${data.length} to ${result.length}`);
        return result;
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
        // Create title with grouping info if applicable
        let titleText = this.chartType === 'all' 
            ? `Biểu đồ tổng hợp tất cả dữ liệu - Nông trại ${chartData[0]?.farmId || ''}`
            : `Biểu đồ ${getChartTitle(this.chartType)} theo thời gian - Nông trại ${chartData[0]?.farmId || ''}`;
            
        // Add grouping info if data is grouped
        if (chartData[0]?.groupedCount > 1) {
            titleText += ` (Giá trị trung bình ${chartData[0].groupedCount} điểm dữ liệu/nhóm)`;
        }
        
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
                        text: titleText,
                        font: {
                            size: 18
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function(tooltipItems) {
                                // Show more detailed time in tooltip
                                const index = tooltipItems[0].dataIndex;
                                const timestamp = Number(chartData[index].timestamp) * 1000;
                                const date = new Date(timestamp);
                                return date.toLocaleString();
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(1);
                                }
                                return label;
                            },
                            footer: function(tooltipItems) {
                                const index = tooltipItems[0].dataIndex;
                                if (chartData[index].groupedCount > 1) {
                                    return `Trung bình từ ${chartData[index].groupedCount} điểm dữ liệu`;
                                }
                                return '';
                            }
                        }
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
                            minRotation: 45,
                            maxTicksLimit: 10 // Limit number of ticks on x-axis
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
            pointRadius: chartData.length > 30 ? 1 : 3, // Smaller points for large datasets
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6
        });
        
        // Add dataset for humidity
        config.data.datasets.push({
            label: 'Độ ẩm (%)',
            data: chartData.map(item => item.humidity),
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointRadius: chartData.length > 30 ? 1 : 3,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6
        });
        
        // Add dataset for water level
        config.data.datasets.push({
            label: 'Độ ẩm đất (%)',
            data: chartData.map(item => item.waterLevel),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            pointRadius: chartData.length > 30 ? 1 : 3,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6
        });
        
        // Add dataset for light level
        config.data.datasets.push({
            label: 'Độ sáng (%)',
            data: chartData.map(item => item.lightLevel),
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 2,
            pointRadius: chartData.length > 30 ? 1 : 3,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6
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
            borderWidth: 3, // Make single dataset lines thicker
            pointRadius: chartData.length > 30 ? 2 : 4, // Slightly larger points for single dataset
            tension: 0.2,
            fill: true, // Add area fill for better visibility
            pointHoverRadius: 8
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