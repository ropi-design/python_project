// Main JavaScript for InstaInsight

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload preview
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                // Show file info
                const fileInfo = document.createElement('div');
                fileInfo.className = 'mt-2 p-2 bg-light rounded';
                fileInfo.innerHTML = `
                    <small class="text-muted">
                        <i class="fas fa-file-csv me-1"></i>
                        ${fileName} (${fileSize} MB)
                    </small>
                `;
                
                // Remove existing file info
                const existingInfo = fileInput.parentNode.querySelector('.mt-2');
                if (existingInfo) {
                    existingInfo.remove();
                }
                
                fileInput.parentNode.appendChild(fileInfo);
            }
        });
    }

    // Chart loading states
    const chartContainers = document.querySelectorAll('[id$="-chart"]');
    chartContainers.forEach(container => {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">読み込み中...</span>
                </div>
                <p class="mt-2 text-muted">チャートを読み込み中...</p>
            </div>
        `;
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-box, .kpi-card, .card').forEach(el => {
        observer.observe(el);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Table row hover effects
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8fafc';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i>コピーしました';
                this.classList.add('btn-success');
                this.classList.remove('btn-outline-secondary');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            });
        });
    });

    // Responsive table handling
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (table.scrollWidth > table.clientWidth) {
            table.style.border = '1px solid #e5e7eb';
            table.style.borderRadius = '8px';
        }
    });

    // Chart resize handling
    window.addEventListener('resize', function() {
        // Trigger Plotly resize for all charts
        if (typeof Plotly !== 'undefined') {
            const chartDivs = document.querySelectorAll('[id$="-chart"]');
            chartDivs.forEach(div => {
                if (div.data) {
                    Plotly.Plots.resize(div);
                }
            });
        }
    });
});

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat('ja-JP').format(num);
}

function formatPercentage(num) {
    return new Intl.NumberFormat('ja-JP', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num / 100);
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Export functions for global use
window.InstaInsight = {
    formatNumber,
    formatPercentage,
    showToast
};
