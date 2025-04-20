/**
 * Farm Data Application
 * Main entry point that coordinates all modules
 */
import { validateDomElements } from './utils.js';
import { TableManager } from './table-manager.js';
import { FilterManager } from './filter-manager.js';
import { ChartManager } from './chart-manager.js';
import { ViewManager } from './view-manager.js';

// Initialize when DOM content is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM content loaded');

    // Check if data exists
    if (!originalData || !Array.isArray(originalData)) {
        console.error('Không có dữ liệu hoặc dữ liệu không đúng định dạng', originalData);
        originalData = [];
    } else {
        console.log('Loaded data:', originalData.length, 'records');
    }

    // Initialize all managers
    initApplication(originalData);
});

// Initialize the application
function initApplication(data) {
    try {
        console.log('Initializing farm data application...');

        // Create module instances
        const tableManager = new TableManager(data);
        const filterManager = new FilterManager(data);
        const chartManager = new ChartManager();
        const viewManager = new ViewManager();

        // Check if all DOM elements are present through managers
        const domElementsValid = validateDomElements([
            viewManager.tableViewBtn,
            viewManager.chartViewBtn,
            viewManager.tableView,
            viewManager.chartView,
            viewManager.chartTypeContainer,
            viewManager.chartTypeSelect,
            filterManager.startDateInput,
            filterManager.endDateInput,
            filterManager.applyFilterBtn,
            filterManager.resetFilterBtn,
        ]);

        if (!domElementsValid) {
            console.error('Không thể tìm thấy tất cả các phần tử DOM cần thiết');
            return; // Stop execution if elements are missing
        }

        // Set up event handlers for view switching
        viewManager.init(
            // View change handler
            view => {
                if (view === 'chart') {
                    // Small delay to ensure chart container is visible
                    setTimeout(() => {
                        chartManager.setChartType(viewManager.getChartType());
                        chartManager.renderChart(filterManager.applyDateFilter());
                    }, 300);
                }
            },
            // Chart type change handler
            chartType => {
                chartManager.setChartType(chartType);
                chartManager.renderChart(filterManager.applyDateFilter());
            }
        );

        // Set up filter manager event handlers
        document.getElementById('applyFilter').onclick = function () {
            console.log('Apply filter button clicked');
            const filteredData = filterManager.applyDateFilter();
            tableManager.setFilteredData(filteredData);

            // Update chart if in chart view
            if (viewManager.getCurrentView() === 'chart') {
                chartManager.renderChart(filteredData);
            }
        };

        document.getElementById('resetFilter').onclick = function () {
            console.log('Reset filter button clicked');
            const resetData = filterManager.resetDateFilter();
            tableManager.setFilteredData(resetData);

            // Update chart if in chart view
            if (viewManager.getCurrentView() === 'chart') {
                chartManager.renderChart(resetData);
            }
        };

        // Set up sort handlers
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const field = header.getAttribute('data-sort');
                tableManager.sortData(field);

                // Update filtered data in filter manager after sort
                filterManager.setCurrentData(tableManager.data);

                // Apply filters again to maintain consistency
                const filteredData = filterManager.applyDateFilter();
                tableManager.setFilteredData(filteredData);
            });
        });

        // Initial sorting and table display
        tableManager.sortData('timestamp');
        filterManager.setDateRangeFromData();

        console.log('Farm data application initialized');
    } catch (e) {
        console.error('Error initializing application:', e);
    }
}
