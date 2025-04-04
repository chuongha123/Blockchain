/**
 * Farm Data Page JavaScript
 */

// Initialize when DOM content is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Original data is imported from the template

    // Current state
    let currentData = [...originalData];
    let currentPage = 1;
    let itemsPerPage = 10;
    let currentSortField = null;
    let currentSortDirection = 'asc';

    // Format timestamp function
    function formatTimestamp(timestamp) {
        const date = new Date(Number(timestamp) * 1000);
        return date.toLocaleString();
    }

    // Sort function
    function sortData(field) {
        if (currentSortField === field) {
            // Toggle direction if clicking the same field
            currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            currentSortField = field;
            currentSortDirection = 'asc';
        }

        currentData.sort((a, b) => {
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
            if (valueA < valueB) return currentSortDirection === 'asc' ? -1 : 1;
            if (valueA > valueB) return currentSortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        // Update UI
        updateSortIndicators();
        updateTable();
    }

    // Update sort indicators in table headers
    function updateSortIndicators() {
        const sortIcons = document.querySelectorAll('.sort-icon');
        sortIcons.forEach(icon => {
            icon.innerHTML = '';
        });

        if (currentSortField) {
            const currentHeader = document.querySelector(
                `th[data-sort="${currentSortField}"] .sort-icon`
            );
            currentHeader.innerHTML =
                currentSortDirection === 'asc'
                    ? '<i class="bi bi-caret-up-fill"></i>'
                    : '<i class="bi bi-caret-down-fill"></i>';
        }
    }

    // Render table with current data and pagination
    function updateTable() {
        const tableBody = document.getElementById('dataTableBody');
        tableBody.innerHTML = '';

        // Calculate pagination
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = Math.min(startIndex + itemsPerPage, currentData.length);
        const paginatedData = currentData.slice(startIndex, endIndex);

        // Create table rows
        paginatedData.forEach(item => {
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
            tableBody.appendChild(row);
        });

        // Update pagination controls
        updatePagination();
    }

    // Update pagination controls
    function updatePagination() {
        const paginationElement = document.getElementById('pagination');
        paginationElement.innerHTML = '';

        const totalPages = Math.ceil(currentData.length / itemsPerPage);

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.textContent = 'Trước';
        prevLink.addEventListener('click', e => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                updateTable();
            }
        });
        prevLi.appendChild(prevLink);
        paginationElement.appendChild(prevLi);

        // Page numbers
        const maxPagesToShow = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

        if (endPage - startPage + 1 < maxPagesToShow && startPage > 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            const pageLink = document.createElement('a');
            pageLink.className = 'page-link';
            pageLink.href = '#';
            pageLink.textContent = i;
            pageLink.addEventListener('click', e => {
                e.preventDefault();
                currentPage = i;
                updateTable();
            });
            pageLi.appendChild(pageLink);
            paginationElement.appendChild(pageLi);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.textContent = 'Sau';
        nextLink.addEventListener('click', e => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                updateTable();
            }
        });
        nextLi.appendChild(nextLink);
        paginationElement.appendChild(nextLi);
    }

    // Set up sort event listeners
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const field = header.getAttribute('data-sort');
            sortData(field);
        });
    });

    // Initial render
    updateTable();
});
