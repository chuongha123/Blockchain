// JavaScript for admin section

document.addEventListener('DOMContentLoaded', function () {
    // Confirm password check for user form
    const userForm = document.querySelector('form[action*="/admin/users"]');
    if (userForm) {
        userForm.addEventListener('submit', function (event) {
            const passwordField = document.getElementById('password');
            const confirmPasswordField = document.getElementById('confirm_password');

            // Only check if both fields exist and confirmPasswordField has a value
            if (passwordField && confirmPasswordField?.value) {
                if (passwordField.value !== confirmPasswordField.value) {
                    event.preventDefault();
                    alert('Mật khẩu và xác nhận mật khẩu không khớp!');
                }
            }
        });
    }

    // DataTables initialization for user list
    const userTable = document.querySelector('.table');
    if (userTable && typeof $.fn.DataTable !== 'undefined') {
        $(userTable).DataTable({
            language: {
                lengthMenu: 'Hiển thị _MENU_ bản ghi',
                zeroRecords: 'Không tìm thấy kết quả',
                info: 'Hiển thị _START_ đến _END_ của _TOTAL_ bản ghi',
                infoEmpty: 'Hiển thị 0 đến 0 của 0 bản ghi',
                infoFiltered: '(lọc từ _MAX_ bản ghi)',
                search: 'Tìm kiếm:',
                paginate: {
                    first: 'Đầu',
                    last: 'Cuối',
                    next: 'Tiếp',
                    previous: 'Trước',
                },
            },
            responsive: true,
        });
    }

    // Toast notifications
    const showToast = (message, type = 'success') => {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Create toast container if it doesn't exist
            const newToastContainer = document.createElement('div');
            newToastContainer.id = 'toast-container';
            newToastContainer.className = 'position-fixed top-0 end-0 p-3';
            newToastContainer.style.zIndex = '1050';
            document.body.appendChild(newToastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast bg-${type} text-white`;
        toast.role = 'alert';
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${type === 'success' ? 'Thành công' : 'Lỗi'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000,
        });

        bsToast.show();

        // Remove toast when hidden
        toast.addEventListener('hidden.bs.toast', function () {
            this.remove();
        });
    };

    // Check for success/error messages in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('success')) {
        showToast(decodeURIComponent(urlParams.get('success')));
    }
    if (urlParams.has('error')) {
        showToast(decodeURIComponent(urlParams.get('error')), 'danger');
    }
});
