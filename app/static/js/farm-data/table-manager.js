/**
 * Table Manager for Farm Data application
 * Manages the data table, sorting, and pagination
 */
import { formatTimestamp } from './utils.js';

export class TableManager {
    constructor(data, itemsPerPage = 10) {
        this.data = data;
        this.filteredData = [...data];
        this.itemsPerPage = itemsPerPage;
        this.currentPage = 1;
        this.currentSortField = 'timestamp';
        this.currentSortDirection = 'desc';

        // DOM elements
        this.tableBody = document.getElementById('dataTableBody');
        this.paginationElement = document.getElementById('pagination');
    }

    // Sort the data
    sortData(field) {
        try {
            console.log('Sorting by field:', field);
            if (this.currentSortField === field) {
                // Toggle direction if clicking the same field
                this.currentSortDirection = this.currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.currentSortField = field;
                this.currentSortDirection = 'asc';
            }

            console.log('Sort direction:', this.currentSortDirection);

            this.data.sort((a, b) => {
                let valueA = a[field];
                let valueB = b[field];

                // Special handling for timestamp
                if (field === 'timestamp') {
                    valueA = Number(valueA);
                    valueB = Number(valueB);
                }

                // String comparison for non-numeric values
                if (typeof valueA === 'string') {
                    valueA = valueA.toLowerCase();
                    valueB = valueB.toLowerCase();
                }

                // Actual comparison
                if (valueA < valueB) return this.currentSortDirection === 'asc' ? -1 : 1;
                if (valueA > valueB) return this.currentSortDirection === 'asc' ? 1 : -1;
                return 0;
            });

            // Update UI
            this.updateSortIndicators();
            this.updateTable();

            console.log('Sorting complete');
        } catch (e) {
            console.error('Error during sorting:', e);
        }
    }

    // Update sort indicators in table headers
    updateSortIndicators() {
        try {
            const sortIcons = document.querySelectorAll('.sort-icon');
            sortIcons.forEach(icon => {
                icon.innerHTML = '';
            });

            if (this.currentSortField) {
                const currentHeader = document.querySelector(
                    `th[data-sort="${this.currentSortField}"] .sort-icon`
                );
                if (currentHeader) {
                    currentHeader.innerHTML =
                        this.currentSortDirection === 'asc'
                            ? '<i class="bi bi-caret-up-fill"></i>'
                            : '<i class="bi bi-caret-down-fill"></i>';
                }
            }
        } catch (e) {
            console.error('Error updating sort indicators:', e);
        }
    }

    // Update the table with current data and pagination
    updateTable() {
        try {
            console.log('Updating table with', this.filteredData.length, 'records');
            if (!this.tableBody) {
                console.error('Table body element not found');
                return;
            }

            this.tableBody.innerHTML = '';

            // Calculate pagination
            const startIndex = (this.currentPage - 1) * this.itemsPerPage;
            const endIndex = Math.min(startIndex + this.itemsPerPage, this.filteredData.length);
            const paginatedData = this.filteredData.slice(startIndex, endIndex);

            console.log(
                `Showing records ${startIndex + 1} to ${endIndex} of ${this.filteredData.length}`
            );

            if (paginatedData.length === 0) {
                // Display a message when no data is available
                this._createEmptyTableMessage();
            } else {
                // Create table rows
                paginatedData.forEach(item => {
                    this._createTableRow(item);
                });
            }

            // Update pagination controls
            this.updatePagination();

            console.log('Table updated successfully');
        } catch (e) {
            console.error('Error updating table:', e);
        }
    }

    // Create empty table message row
    _createEmptyTableMessage() {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = 7; // Span all columns
        emptyCell.textContent = 'Không có dữ liệu trong khoảng thời gian đã chọn';
        emptyCell.className = 'text-center p-3';
        emptyRow.appendChild(emptyCell);
        this.tableBody.appendChild(emptyRow);
    }

    // Create a single table row
    _createTableRow(item) {
        const row = document.createElement('tr');

        // Create cells
        const timestampCell = document.createElement('td');
        timestampCell.textContent = formatTimestamp(item.timestamp);

        const farmIdCell = document.createElement('td');
        farmIdCell.textContent = item.farmId;

        const tempCell = document.createElement('td');
        tempCell.textContent = item.temperature;

        const humidityCell = document.createElement('td');
        humidityCell.textContent = item.humidity;

        const waterLevelCell = document.createElement('td');
        waterLevelCell.textContent = item.waterLevel;

        const lightLevelCell = document.createElement('td');
        lightLevelCell.textContent = item.lightLevel;

        const productIdCell = document.createElement('td');
        productIdCell.textContent = item.productId;

        // Append cells to row
        row.appendChild(timestampCell);
        row.appendChild(farmIdCell);
        row.appendChild(tempCell);
        row.appendChild(humidityCell);
        row.appendChild(waterLevelCell);
        row.appendChild(lightLevelCell);
        row.appendChild(productIdCell);

        // Append row to table
        this.tableBody.appendChild(row);
    }

    // Update pagination controls with ellipsis
    updatePagination() {
        try {
            console.log('Updating pagination');
            if (!this.paginationElement) {
                console.error('Pagination element not found');
                return;
            }

            this.paginationElement.innerHTML = '';

            const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
            console.log('Total pages:', totalPages);

            // Previous button
            this._addPreviousButton();

            // First page
            if (totalPages > 0) {
                this._addPageItem(1);
            }

            // Ellipsis and page numbers logic
            this._addPageNumbersWithEllipsis(totalPages);

            // Next button
            this._addNextButton(totalPages);

            console.log('Pagination updated successfully');
        } catch (e) {
            console.error('Error updating pagination:', e);
        }
    }

    // Add previous button
    _addPreviousButton() {
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.textContent = 'Trước';
        prevLink.addEventListener('click', e => {
            e.preventDefault();
            if (this.currentPage > 1) {
                this.currentPage--;
                this.updateTable();
            }
        });
        prevLi.appendChild(prevLink);
        this.paginationElement.appendChild(prevLi);
    }

    // Add next button
    _addNextButton(totalPages) {
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.textContent = 'Sau';
        nextLink.addEventListener('click', e => {
            e.preventDefault();
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.updateTable();
            }
        });
        nextLi.appendChild(nextLink);
        this.paginationElement.appendChild(nextLi);
    }

    // Add page numbers with ellipsis for large number of pages
    _addPageNumbersWithEllipsis(totalPages) {
        if (totalPages > 1) {
            const maxPagesWithoutEllipsis = 7; // Show max 7 pages without ellipsis

            if (totalPages <= maxPagesWithoutEllipsis) {
                // Show all pages without ellipsis
                for (let i = 2; i < totalPages; i++) {
                    this._addPageItem(i);
                }
            } else {
                // Show pages with ellipsis
                if (this.currentPage > 3) {
                    // First ellipsis
                    this._addEllipsis();
                }

                // Pages around current page
                const startPage = Math.max(2, this.currentPage - 1);
                const endPage = Math.min(totalPages - 1, this.currentPage + 1);

                for (let i = startPage; i <= endPage; i++) {
                    this._addPageItem(i);
                }

                if (this.currentPage < totalPages - 2) {
                    // Last ellipsis
                    this._addEllipsis();
                }
            }

            // Last page
            this._addPageItem(totalPages);
        }
    }

    // Helper to add page number item
    _addPageItem(pageNum) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${pageNum === this.currentPage ? 'active' : ''}`;
        const pageLink = document.createElement('a');
        pageLink.className = 'page-link';
        pageLink.href = '#';
        pageLink.textContent = pageNum;
        pageLink.addEventListener('click', e => {
            e.preventDefault();
            this.currentPage = pageNum;
            this.updateTable();
        });
        pageLi.appendChild(pageLink);
        this.paginationElement.appendChild(pageLi);
    }

    // Helper to add ellipsis
    _addEllipsis() {
        const ellipsisLi = document.createElement('li');
        ellipsisLi.className = 'page-item disabled';
        const ellipsisSpan = document.createElement('span');
        ellipsisSpan.className = 'page-link';
        ellipsisSpan.innerHTML = '&hellip;';
        ellipsisLi.appendChild(ellipsisSpan);
        this.paginationElement.appendChild(ellipsisLi);
    }

    // Update filtered data
    setFilteredData(data) {
        this.filteredData = data;
        this.currentPage = 1; // Reset to first page
        this.updateTable();
    }
}
