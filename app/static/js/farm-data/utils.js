/**
 * Utility functions for Farm Data application
 */

// Format timestamp to readable date and time
export function formatTimestamp(timestamp) {
    try {
        const date = new Date(Number(timestamp) * 1000);
        return date.toLocaleString();
    } catch (e) {
        console.error('Error formatting timestamp:', e);
        return 'Invalid date';
    }
}

// Convert timestamp to date only string (YYYY-MM-DD)
export function formatDateOnly(timestamp) {
    try {
        const date = new Date(Number(timestamp) * 1000);
        return date.toISOString().split('T')[0];
    } catch (e) {
        console.error('Error formatting date only:', e);
        return '';
    }
}

// Helper function to get chart title
export function getChartTitle(chartType) {
    switch (chartType) {
        case 'temperature': return 'Nhiệt độ (°C)';
        case 'humidity': return 'Độ ẩm (%)';
        case 'waterLevel': return 'Độ ẩm đất (%)';
        case 'lightLevel': return 'Độ sáng (%)';
        default: return 'Dữ liệu';
    }
}

// Helper function to get chart Y-axis label
export function getChartYAxisLabel(chartType) {
    switch (chartType) {
        case 'temperature': return 'Nhiệt độ (°C)';
        case 'humidity': return 'Độ ẩm (%)';
        case 'waterLevel': return 'Độ ẩm đất (%)';
        case 'lightLevel': return 'Độ sáng (%)';
        default: return 'Giá trị';
    }
}

// Helper function to get chart data info
export function getChartDataInfo(chartType) {
    switch (chartType) {
        case 'temperature':
            return {
                title: 'Nhiệt độ (°C)',
                color: 'rgba(255, 99, 132, 1)'
            };
        case 'humidity':
            return {
                title: 'Độ ẩm (%)',
                color: 'rgba(54, 162, 235, 1)'
            };
        case 'waterLevel':
            return {
                title: 'Độ ẩm đất (%)',
                color: 'rgba(75, 192, 192, 1)'
            };
        case 'lightLevel':
            return {
                title: 'Độ sáng (%)',
                color: 'rgba(255, 159, 64, 1)'
            };
        default:
            return {
                title: 'Dữ liệu',
                color: 'rgba(153, 102, 255, 1)'
            };
    }
}

// Validate DOM elements
export function validateDomElements(elements) {
    for (const element of elements) {
        if (!element) {
            console.error('Phần tử DOM không tồn tại:', element);
            return false;
        }
    }
    return true;
} 