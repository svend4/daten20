// Document Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm deletion
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Number formatting
    var currencyInputs = document.querySelectorAll('[data-format="currency"]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Table row click
    var tableRows = document.querySelectorAll('[data-href]');
    tableRows.forEach(function(row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'A') {
                window.location.href = this.dataset.href;
            }
        });
    });
});

// API Helper Functions
const API = {
    baseUrl: '/api',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async get(endpoint) {
        return this.request(endpoint);
    },

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Services API
const ServicesAPI = {
    async list(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return API.get(`/services?${queryString}`);
    },

    async get(id) {
        return API.get(`/services/${id}`);
    },

    async create(data) {
        return API.post('/services', data);
    },

    async update(id, data) {
        return API.put(`/services/${id}`, data);
    },

    async delete(id) {
        return API.delete(`/services/${id}`);
    },

    async search(query) {
        return API.get(`/search?q=${encodeURIComponent(query)}`);
    }
};

// Calculator API
const CalculatorAPI = {
    async calculate(params) {
        return API.post('/calculate', params);
    }
};

// Statistics API
const StatisticsAPI = {
    async get() {
        return API.get('/statistics');
    }
};

// Utility Functions
const Utils = {
    formatCurrency(value) {
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
        }).format(value);
    },

    formatPercentage(value) {
        return `${value.toFixed(2)}%`.replace('.', ',');
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('de-DE').format(date);
    },

    showToast(message, type = 'info') {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    showSpinner(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm';
        spinner.setAttribute('role', 'status');
        element.disabled = true;
        element.appendChild(spinner);
        return spinner;
    },

    hideSpinner(spinner) {
        spinner.remove();
    }
};

// Export to global scope
window.API = API;
window.ServicesAPI = ServicesAPI;
window.CalculatorAPI = CalculatorAPI;
window.StatisticsAPI = StatisticsAPI;
window.Utils = Utils;
