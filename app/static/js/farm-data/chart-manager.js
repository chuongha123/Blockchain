/**
 * Chart Manager for Farm Data application
 * Manages chart creation and rendering
 */
import { getChartDataInfo, getChartTitle, getChartYAxisLabel } from './utils.js';

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

            // Debug log to check data structure
            console.log('Sample data item:', data[0]);
            console.log('Total data points:', data.length);

            const normalizedData = this._normalizeData(data);

            const chartData = [...normalizedData].sort(
                (a, b) => Number(a.timestamp) - Number(b.timestamp)
            );

            const shouldUseSteppedLine = this._shouldUseSteppedLine(chartData);
            console.log('Using stepped line:', shouldUseSteppedLine);

            // Prepare data for chart - tạo nhãn đầy đủ hơn cho trục X
            const labels = this._createTimeLabels(chartData);

            // Destroy existing chart if it exists
            this._destroyExistingChart();

            // Reset the canvas to ensure a clean state
            this._resetCanvas();

            try {
                // Create the chart configuration
                const config = this._createChartConfig(chartData, labels, shouldUseSteppedLine);

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

    // Chuẩn hóa dữ liệu để đảm bảo tất cả các trường đều có mặt
    _normalizeData(data) {
        // Bỏ qua việc lọc dữ liệu và chỉ chuẩn hóa các giá trị
        return data.map(item => {
            return {
                timestamp: item.timestamp || 0,
                farmId: item.farmId || '',
                temperature: parseFloat(item.temperature || 0),
                humidity: parseFloat(item.humidity || 0),
                waterLevel: parseFloat(item.waterLevel || 0),
                lightLevel: parseFloat(item.lightLevel || 0),
                productId: item.productId || '',
            };
        });
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
        ctx.fillText(
            'Không có dữ liệu để hiển thị trong khoảng thời gian đã chọn',
            this.chartCanvas.width / 2,
            this.chartCanvas.height / 2
        );
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

    // Phân tích dữ liệu để quyết định xem có nên sử dụng stepped line hay không
    _shouldUseSteppedLine(data) {
        // Nếu dữ liệu quá nhiều và có khoảng cách thời gian không đều
        if (data.length > 50) {
            // Kiểm tra khoảng cách thời gian giữa các điểm
            const timeGaps = [];
            for (let i = 1; i < data.length; i++) {
                timeGaps.push(Number(data[i].timestamp) - Number(data[i - 1].timestamp));
            }

            // Tính khoảng cách trung bình và độ lệch chuẩn
            const avgGap = timeGaps.reduce((sum, gap) => sum + gap, 0) / timeGaps.length;
            const stdDev = Math.sqrt(
                timeGaps.reduce((sum, gap) => sum + Math.pow(gap - avgGap, 2), 0) / timeGaps.length
            );

            // Nếu độ lệch chuẩn lớn (dữ liệu không đều), sử dụng stepped line
            return stdDev / avgGap > 0.5;
        }

        return false;
    }

    // Create chart configuration
    _createChartConfig(chartData, labels, useSteppedLine = false) {
        // Create title with grouping info if applicable
        let titleText =
            this.chartType === 'all'
                ? `Biểu đồ tổng hợp tất cả dữ liệu - Nông trại ${chartData[0]?.farmId || ''}`
                : `Biểu đồ ${getChartTitle(this.chartType)} theo thời gian - Nông trại ${chartData[0]?.farmId || ''}`;

        // Add grouping info if data is grouped
        if (chartData[0]?.groupedCount > 1) {
            titleText += ` (Giá trị trung bình ${chartData[0].groupedCount} điểm dữ liệu/nhóm)`;
        }

        // Điều chỉnh tiêu đề hiện số lượng điểm dữ liệu
        titleText += ` (${chartData.length} điểm dữ liệu)`;

        // Các điểm nhãn chuyển đổi sang số
        const labelIndices = this._calculateLabelIndices(labels.length);
        console.log('Hiển thị nhãn tại các vị trí:', labelIndices);

        // Create chart config
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: titleText,
                        font: {
                            size: 18,
                        },
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function (tooltipItems) {
                                // Show more detailed time in tooltip
                                const index = tooltipItems[0].dataIndex;
                                const timestamp = Number(chartData[index].timestamp) * 1000;
                                const date = new Date(timestamp);
                                return date.toLocaleString();
                            },
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(1);
                                }
                                return label;
                            },
                            footer: function (tooltipItems) {
                                const index = tooltipItems[0].dataIndex;
                                if (chartData[index].groupedCount > 1) {
                                    return `Trung bình từ ${chartData[index].groupedCount} điểm dữ liệu`;
                                }
                                return '';
                            },
                        },
                    },
                    legend: {
                        display: true,
                        position: 'top',
                    },
                },
                scales: {
                    x: {
                        type: 'category', // Quan trọng: đảm bảo sử dụng loại trục category
                        display: true,
                        title: {
                            display: true,
                            text: 'Thời gian',
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            // Buộc hiển thị nhiều nhãn thời gian hơn
                            autoSkip: false, // Không bỏ qua nhãn tự động
                            // Hiển thị có chọn lọc nhãn
                            callback: function (val, index) {
                                // Hiển thị nhãn tại các vị trí đã tính toán
                                return labelIndices.includes(index) ? labels[index] : '';
                            },
                        },
                        grid: {
                            display: true,
                            drawOnChartArea: true,
                        },
                        // Hiển thị nhiều dữ liệu hơn trên trục X
                        distribution: 'linear',
                        offset: false,
                    },
                    y: {
                        title: {
                            display: true,
                            text:
                                this.chartType === 'all'
                                    ? 'Giá trị'
                                    : getChartYAxisLabel(this.chartType),
                        },
                        beginAtZero: true,
                    },
                },
                // Đảm bảo tất cả các điểm dữ liệu đều hiển thị
                elements: {
                    point: {
                        radius: this._getOptimalPointRadius(chartData.length),
                        hoverRadius: 8,
                    },
                    line: {
                        tension: useSteppedLine ? 0 : 0.2,
                        stepped: useSteppedLine,
                    },
                },
                animation: {
                    duration: 1000, // Đặt thời gian animation ngắn hơn để hiển thị nhanh hơn
                },
            },
        };

        // Add datasets based on chart type
        if (this.chartType === 'all') {
            this._addAllDatasets(config, chartData, useSteppedLine);
        } else {
            this._addSingleDataset(config, chartData, useSteppedLine);
        }

        return config;
    }

    // Tính toán vị trí các nhãn nên hiển thị trên trục X
    _calculateLabelIndices(totalLabels) {
        const indices = [];

        // Luôn hiển thị điểm đầu và điểm cuối
        indices.push(0);
        if (totalLabels > 1) {
            indices.push(totalLabels - 1);
        }

        // Nếu ít nhãn, hiện tất cả
        if (totalLabels <= 15) {
            for (let i = 1; i < totalLabels - 1; i++) {
                indices.push(i);
            }
            return indices;
        }

        // Số lượng nhãn trung gian cần hiển thị
        const internalLabels = Math.min(10, Math.ceil(totalLabels / 5));
        const step = Math.max(1, Math.floor(totalLabels / (internalLabels + 1)));

        // Thêm các nhãn trung gian
        for (let i = step; i < totalLabels - 1; i += step) {
            indices.push(i);
        }

        // Sắp xếp lại các chỉ số
        return indices.sort((a, b) => a - b);
    }

    // Add all datasets for the "all" chart type
    _addAllDatasets(config, chartData, useSteppedLine) {
        // Điều chỉnh kích thước điểm dựa trên số lượng dữ liệu
        const pointRadius = this._getOptimalPointRadius(chartData.length);

        // Add dataset for temperature
        config.data.datasets.push({
            label: 'Nhiệt độ (°C)',
            data: chartData.map(item => (item.temperature !== undefined ? item.temperature : null)),
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            pointRadius: pointRadius,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6,
        });

        // Add dataset for humidity
        config.data.datasets.push({
            label: 'Độ ẩm (%)',
            data: chartData.map(item => (item.humidity !== undefined ? item.humidity : null)),
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointRadius: pointRadius,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6,
        });

        // Add dataset for water level
        config.data.datasets.push({
            label: 'Độ ẩm đất (%)',
            data: chartData.map(item => (item.waterLevel !== undefined ? item.waterLevel : null)),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            pointRadius: pointRadius,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6,
        });

        // Add dataset for light level
        config.data.datasets.push({
            label: 'Độ sáng (%)',
            data: chartData.map(item => (item.lightLevel !== undefined ? item.lightLevel : null)),
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 2,
            pointRadius: pointRadius,
            tension: 0.3,
            yAxisID: 'y',
            pointHoverRadius: 6,
        });
    }

    // Add a single dataset for specific chart types
    _addSingleDataset(config, chartData, useSteppedLine) {
        const dataInfo = getChartDataInfo(this.chartType);
        // Điểm lớn hơn cho biểu đồ đơn
        const pointRadius = this._getOptimalPointRadius(chartData.length, true);

        config.data.datasets.push({
            label: dataInfo.title,
            data: chartData.map(item =>
                item[this.chartType] !== undefined ? item[this.chartType] : null
            ),
            backgroundColor: dataInfo.color.replace('1)', '0.2)'),
            borderColor: dataInfo.color,
            borderWidth: 3, // Make single dataset lines thicker
            pointRadius: pointRadius,
            tension: 0.2,
            fill: true, // Add area fill for better visibility
            pointHoverRadius: 8,
        });
    }

    // Tối ưu hóa kích thước điểm dựa trên số lượng dữ liệu
    _getOptimalPointRadius(dataLength, isSingleDataset = false) {
        // Đối với biểu đồ đơn, cho phép điểm lớn hơn
        const multiplier = isSingleDataset ? 1.5 : 1;

        if (dataLength > 100) {
            return 1 * multiplier; // Rất nhỏ nếu có quá nhiều điểm
        } else if (dataLength > 50) {
            return 2 * multiplier; // Nhỏ
        } else if (dataLength > 25) {
            return 3 * multiplier; // Trung bình
        } else {
            return 4 * multiplier; // Lớn nếu ít điểm
        }
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
                    datasets: [
                        {
                            label: 'Dữ liệu mẫu',
                            data: [5],
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                        },
                    },
                },
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
                ctx.fillText(
                    'Lỗi khi hiển thị biểu đồ',
                    this.chartCanvas.width / 2,
                    this.chartCanvas.height / 2
                );
            }
        } catch (canvasError) {
            console.error('Could not display error on canvas:', canvasError);
        }
    }

    // Tạo nhãn thời gian chi tiết hơn cho trục X
    _createTimeLabels(data) {
        // Hiển thị nhiều thông tin hơn để phân biệt các mốc thời gian
        return data.map(item => {
            const date = new Date(Number(item.timestamp) * 1000);

            // Format: "HH:MM MM/DD" hoặc "HH:MM:SS MM/DD" nếu cần
            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');

            return `${hours}:${minutes} ${month}/${day}`;
        });
    }
}
