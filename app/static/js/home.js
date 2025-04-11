/**
 * Home Page JavaScript
 */

// Handle logout functionality
document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // Clear cookies instead of localStorage
            document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            document.cookie = 'token_type=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            console.log('Cookies cleared, logging out');

            // Reload the page
            window.location.reload();
        });
    }

    // Initialize authentication header for fetch API calls
    initializeAuth();

    // Handle search form - only initialize if elements exist
    const submitDeviceIdBtn = document.getElementById('submitDeviceId');
    if (submitDeviceIdBtn) {
        submitDeviceIdBtn.addEventListener('click', function () {
            const deviceId = document.getElementById('deviceIdInput').value.trim();
            if (deviceId) {
                window.location.href = `/farm/${deviceId}`;
            }
        });
    }

    // Handle when press Enter - only initialize if element exists
    const deviceIdInput = document.getElementById('deviceIdInput');
    if (deviceIdInput) {
        deviceIdInput.addEventListener('keyup', function (event) {
            if (event.key === 'Enter') {
                const submitBtn = document.getElementById('submitDeviceId');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });
    }

    // Back to top button behavior
    const backToTopBtn = document.getElementById('backToTopBtn');
    if (backToTopBtn) {
        // Show button when user scrolls down 300px
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });

        // Scroll to top when button is clicked
        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth',
            });
        });
    }
});

// Helper function to get cookie value by name
function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (const element of ca) {
        let c = element;
        while (c.startsWith(' ')) c = c.substring(1, c.length);
        if (c.startsWith(nameEQ)) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// Attach authentication token to all API requests
function initializeAuth() {
    // Get token from cookie instead of localStorage
    const token = getCookie('access_token');

    console.log('initializeAuth() called, token exists:', !!token);

    if (token) {
        console.log('Token found in cookie');

        // Use fetch API interceptor pattern to attach auth headers
        const originalFetch = window.fetch;
        window.fetch = function (url, options = {}) {
            // Only attach auth header to same-origin requests
            if (url.startsWith('/') || url.startsWith(window.location.origin)) {
                options.headers = options.headers || {};
                options.headers['Authorization'] = `Bearer ${token}`;
                console.log(`Adding auth header to ${url}`);
            }
            return originalFetch(url, options);
        };

        console.log('Authentication initialized for fetch API');
    } else {
        console.log('No token found in cookies');
    }
}

// Smooth scrolling for anchor links with offset
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const targetId = this.getAttribute('href');
        if (!targetId || targetId === '#') return;

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            // Get the navbar height to use as offset (or use a fixed value)
            const navbarHeight = document.querySelector('.navbar').offsetHeight;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.scrollY - navbarHeight;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth',
            });
        }
    });
});

// handle contact form
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // get form elements
        const form = this;
        const formResult = document.getElementById('formResult');
        const submitBtn = document.getElementById('submitBtn');
        const submitText = document.getElementById('submitText');
        const submitSpinner = document.getElementById('submitSpinner');

        // Validate form
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        // show loading
        submitBtn.disabled = true;
        submitText.innerText = 'Đang gửi...';
        submitSpinner.classList.remove('d-none');
        formResult.innerHTML = '';

        // Get form data
        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            message: document.getElementById('message').value.trim(),
        };

        // send data to server
        fetch('/api/send-contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
            .then(response => response.json())
            .then(data => {
                // show result
                if (data.success) {
                    formResult.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i> ${data.message}
                        </div>
                    `;
                    // Reset form
                    form.reset();
                    form.classList.remove('was-validated');
                } else {
                    formResult.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> ${data.message}
                        </div>
                    `;
                }
            })
            .catch(error => {
                formResult.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i> Đã xảy ra lỗi: ${error.message}
                    </div>
                `;
            })
            .finally(() => {
                // restore button state
                submitBtn.disabled = false;
                submitText.innerText = 'Gửi tin nhắn';
                submitSpinner.classList.add('d-none');
            });
    });
}

// create QR code
const generateQRBtn = document.getElementById('generateQR');
if (generateQRBtn) {
    generateQRBtn.addEventListener('click', function () {
        const deviceId = document.getElementById('qrDeviceIdInput').value.trim();
        if (deviceId) {
            // show loading
            document.getElementById('qrResult').innerHTML = `
                <div class="spinner-border text-primary">
                    <span class="visually-hidden">Đang tạo mã QR...</span>
                </div>
                <p>Đang tạo mã QR...</p>
            `;

            // Cookies are automatically included in the request - no need to add them manually
            fetch(`/generate-qr/${deviceId}`)
                .then(response => response.json())
                .then(data => {
                    const qrResult = document.getElementById('qrResult');
                    if (data.error) {
                        qrResult.innerHTML = `
                            <div class="alert alert-danger">Lỗi: ${data.error}</div>
                        `;
                    } else {
                        qrResult.innerHTML = `
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle"></i> Mã QR đã được tạo thành công!
                            </div>
                            <div class="card shadow-sm">
                                <div class="card-body p-2">
                                    <img src="${data.qr_url}" class="img-fluid mb-2" alt="QR Code">
                                    <div class="d-grid gap-2">
                                        <a href="${data.qr_url}" download="qr_${deviceId}.png" class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-download"></i> Tải mã QR
                                        </a>
                                        <a href="/farm/${deviceId}" target="_blank" class="btn btn-sm btn-outline-success">
                                            <i class="fas fa-external-link-alt"></i> Xem trang thông tin
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <p class="mt-2 text-muted small">Quét mã QR này bằng điện thoại để xem thông tin chi tiết về sản phẩm</p>
                        `;
                    }
                })
                .catch(error => {
                    document.getElementById('qrResult').innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> Lỗi khi tạo mã QR: ${error}
                        </div>
                    `;
                });
        } else {
            document.getElementById('qrResult').innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> Vui lòng nhập mã sản phẩm
                </div>
            `;
        }
    });
}
