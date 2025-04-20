/**
 * Filter Manager for Farm Data application
 * Manages data filtering operations
 */
import { formatDateOnly } from './utils.js';

export class FilterManager {
    constructor(data) {
        this.originalData = data;
        this.currentData = [...data];
        this.startDate = null;
        this.endDate = null;

        // DOM Elements
        this.startDateInput = document.getElementById('startDate');
        this.endDateInput = document.getElementById('endDate');
        this.applyFilterBtn = document.getElementById('applyFilter');
        this.resetFilterBtn = document.getElementById('resetFilter');
    }

    // Initialize event listeners
    init() {
        if (this.applyFilterBtn) {
            this.applyFilterBtn.addEventListener('click', () => this.applyDateFilter());
        }

        if (this.resetFilterBtn) {
            this.resetFilterBtn.addEventListener('click', () => this.resetDateFilter());
        }

        // Set initial date range
        this.setDateRangeFromData();
    }

    // Set min and max dates from data
    setDateRangeFromData() {
        try {
            console.log('Setting date range from data');
            if (this.currentData.length > 0) {
                // Find min and max dates in the data
                const timestamps = this.currentData.map(item => Number(item.timestamp));
                const minTimestamp = Math.min(...timestamps);
                const maxTimestamp = Math.max(...timestamps);

                console.log('Min timestamp:', minTimestamp, 'Max timestamp:', maxTimestamp);

                // Convert to YYYY-MM-DD for date input
                const minDate = formatDateOnly(minTimestamp);
                const maxDate = formatDateOnly(maxTimestamp);

                console.log('Min date:', minDate, 'Max date:', maxDate);

                // Set input values and attributes
                this.startDateInput.min = minDate;
                this.startDateInput.max = maxDate;
                this.startDateInput.value = minDate;

                this.endDateInput.min = minDate;
                this.endDateInput.max = maxDate;
                this.endDateInput.value = maxDate;

                console.log('Date inputs set successfully');
            } else {
                console.warn('No data available to set date range');
            }
        } catch (e) {
            console.error('Error setting date range:', e);
        }
    }

    // Apply date filter and return filtered data
    applyDateFilter() {
        try {
            console.log('Applying date filter');
            this.startDate = this.startDateInput.value ? new Date(this.startDateInput.value) : null;
            this.endDate = this.endDateInput.value ? new Date(this.endDateInput.value) : null;

            console.log('Filter dates - Start:', this.startDate, 'End:', this.endDate);

            // Add one day to end date to include the end date in range
            if (this.endDate) {
                this.endDate.setDate(this.endDate.getDate() + 1);
            }

            let filteredData = [...this.currentData];

            if (this.startDate || this.endDate) {
                filteredData = this.currentData.filter(item => {
                    const itemTimestamp = Number(item.timestamp);
                    if (isNaN(itemTimestamp)) {
                        console.warn('Invalid timestamp found:', item.timestamp);
                        return false;
                    }

                    const itemDate = new Date(itemTimestamp * 1000);

                    if (this.startDate && this.endDate) {
                        return itemDate >= this.startDate && itemDate <= this.endDate;
                    } else if (this.startDate) {
                        return itemDate >= this.startDate;
                    } else if (this.endDate) {
                        return itemDate <= this.endDate;
                    }

                    return true;
                });

                console.log('Filtered data:', filteredData.length, 'records');
            }

            return filteredData;
        } catch (e) {
            console.error('Error applying date filter:', e);
            return [...this.currentData]; // Return unfiltered data on error
        }
    }

    // Reset date filter
    resetDateFilter() {
        try {
            console.log('Resetting date filter');
            this.setDateRangeFromData();
            this.startDate = null;
            this.endDate = null;
            return [...this.currentData];
        } catch (e) {
            console.error('Error resetting date filter:', e);
            return [...this.currentData]; // Return unfiltered data on error
        }
    }

    // Update the base data
    setCurrentData(data) {
        this.currentData = [...data];
        // Optionally update date range
        this.setDateRangeFromData();
    }
}
