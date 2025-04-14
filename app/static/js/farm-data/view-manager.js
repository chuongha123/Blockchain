/**
 * View Manager for Farm Data application
 * Manages switching between table and chart views
 */

export class ViewManager {
    constructor() {
        // DOM Elements
        this.tableViewBtn = document.getElementById('tableViewBtn');
        this.chartViewBtn = document.getElementById('chartViewBtn');
        this.tableView = document.getElementById('tableView');
        this.chartView = document.getElementById('chartView');
        this.chartTypeContainer = document.getElementById('chartTypeContainer');
        this.chartTypeSelect = document.getElementById('chartType');

        this.currentView = 'table'; // Default view
    }

    // Initialize event listeners
    init(onViewChange, onChartTypeChange) {
        // View toggle buttons
        if (this.tableViewBtn) {
            this.tableViewBtn.onclick = () => {
                console.log('Table view button clicked');
                this.showTableView();
                if (onViewChange) onViewChange('table');
            };
        }

        if (this.chartViewBtn) {
            this.chartViewBtn.onclick = () => {
                console.log('Chart view button clicked');
                this.showChartView();
                if (onViewChange) onViewChange('chart');
            };
        }

        // Chart type change
        if (this.chartTypeSelect) {
            this.chartTypeSelect.onchange = () => {
                console.log('Chart type changed to:', this.chartTypeSelect.value);
                if (onChartTypeChange) onChartTypeChange(this.chartTypeSelect.value);
            };
        }
    }

    // Show table view
    showTableView() {
        this.tableViewBtn.classList.add('active');
        this.tableViewBtn.classList.remove('btn-outline-success');
        this.tableViewBtn.classList.add('btn-success');
        this.chartViewBtn.classList.remove('active');
        this.chartViewBtn.classList.add('btn-outline-success');
        this.chartViewBtn.classList.remove('btn-success');
        this.tableView.style.display = 'block';
        this.chartView.style.display = 'none';
        this.chartTypeContainer.style.display = 'none';

        this.currentView = 'table';
    }

    // Show chart view
    showChartView() {
        this.chartViewBtn.classList.add('active');
        this.chartViewBtn.classList.remove('btn-outline-success');
        this.chartViewBtn.classList.add('btn-success');
        this.tableViewBtn.classList.remove('active');
        this.tableViewBtn.classList.add('btn-outline-success');
        this.tableViewBtn.classList.remove('btn-success');
        this.tableView.style.display = 'none';
        this.chartView.style.display = 'block';
        this.chartTypeContainer.style.display = 'block';

        // Log DOM status
        console.log('chartView display style:', this.chartView.style.display);
        console.log('chartTypeContainer display style:', this.chartTypeContainer.style.display);

        this.currentView = 'chart';
    }

    // Get current chart type
    getChartType() {
        return this.chartTypeSelect.value;
    }

    // Get current view
    getCurrentView() {
        return this.currentView;
    }
}
