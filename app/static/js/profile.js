document.addEventListener('DOMContentLoaded', function() {
    // Find all harvest buttons
    const harvestButtons = document.querySelectorAll('.harvest-btn');
    
    // Add click handler to each button
    harvestButtons.forEach(button => {
        button.addEventListener('click', function() {
            const farmId = this.getAttribute('data-farm-id');
            const farmCard = this.closest('.farm-card');
            const qrContainer = farmCard.querySelector('.qr-container');
            
            // Show loading state
            this.disabled = true;
            this.innerText = 'Đang xử lý...';
            
            // Send AJAX request to harvest endpoint
            fetch(`/farm/harvest-ajax/${farmId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Handle success
                    // Change button style
                    this.classList.add('disabled');
                    this.innerText = 'Đã thu hoạch';
                    
                    // Update card style
                    farmCard.classList.remove('not-harvested');
                    farmCard.classList.add('harvested');
                    
                    // Update badge text
                    const badge = farmCard.querySelector('.badge');
                    if (badge) {
                        badge.classList.remove('badge-not-harvested');
                        badge.classList.add('badge-harvested');
                        badge.innerText = 'Đã thu hoạch';
                    }
                    
                    // Show QR code
                    if (qrContainer) {
                        // Create QR code image
                        qrContainer.innerHTML = `
                            <div class="text-center mt-3">
                                <h6>Mã QR truy xuất</h6>
                                <div class="qr-image-container">
                                    <img src="data:image/png;base64,${data.qr_code}" 
                                         alt="QR Code" class="img-fluid" 
                                         style="max-width: 150px;">
                                </div>
                                <p class="mt-2">
                                    <a href="${data.farm_url}" target="_blank" class="btn btn-sm btn-info">
                                        <i class="fas fa-external-link-alt"></i> Xem dữ liệu
                                    </a>
                                </p>
                            </div>
                        `;
                        qrContainer.style.display = 'block';
                        
                        // Replace harvest button with QR button
                        const footerButtons = farmCard.querySelector('.card-footer');
                        const harvestBtn = footerButtons.querySelector('.harvest-btn');
                        const qrButton = document.createElement('button');
                        qrButton.className = 'btn btn-info btn-sm show-qr-btn';
                        qrButton.setAttribute('data-farm-id', farmId);
                        qrButton.innerHTML = '<i class="fas fa-qrcode"></i> Xem mã QR';
                        qrButton.onclick = function() {
                            window.open(`/farm/${farmId}`, '_blank');
                        };
                        
                        if (harvestBtn) {
                            footerButtons.replaceChild(qrButton, harvestBtn);
                        }
                        
                        // Show success message
                        showToast('Thành công', 'Đã đánh dấu nông trại là đã thu hoạch.', 'success');
                    }
                } else {
                    // Handle error
                    this.disabled = false;
                    this.innerText = 'Đánh dấu thu hoạch';
                    showToast('Lỗi', data.message || 'Có lỗi xảy ra khi xử lý yêu cầu.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.disabled = false;
                this.innerText = 'Đánh dấu thu hoạch';
                showToast('Lỗi kết nối', 'Không thể kết nối đến máy chủ.', 'error');
            });
        });
    });
    
    // Handle show QR buttons for already harvested farms
    const showQrButtons = document.querySelectorAll('.show-qr-btn');
    showQrButtons.forEach(button => {
        // These buttons already have onclick handlers to open the farm data page
        // We can add additional functionality here if needed
    });
    
    // Toast notification function
    function showToast(title, message, type) {
        // Check if we have Bootstrap Toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            // Create toast element
            const toastEl = document.createElement('div');
            toastEl.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
            toastEl.setAttribute('role', 'alert');
            toastEl.setAttribute('aria-live', 'assertive');
            toastEl.setAttribute('aria-atomic', 'true');
            
            toastEl.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${title}</strong>: ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            // Append to document
            const toastContainer = document.getElementById('toast-container') || document.body;
            toastContainer.appendChild(toastEl);
            
            // Initialize and show toast
            const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
            toast.show();
            
            // Remove after hidden
            toastEl.addEventListener('hidden.bs.toast', function() {
                toastEl.remove();
            });
        } else {
            // Fallback to alert
            alert(`${title}: ${message}`);
        }
    }
}); 