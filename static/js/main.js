/**
 * Placement Management System - Main JavaScript
 * Handles client-side functionality and interactions
 */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-1rem)';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

/**
 * Confirm delete actions
 */
function confirmDelete(message = 'Are you sure? This action cannot be undone.') {
    return confirm(message);
}

/**
 * Format phone number to +91 format
 */
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 10) {
        value = value.substring(0, 10);
    }
    
    if (value.length === 10) {
        input.value = '+91 ' + value.substring(0, 5) + ' ' + value.substring(5);
    } else if (value.length > 0) {
        input.value = '+91 ' + value;
    }
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate USN format (alphanumeric)
 */
function validateUSN(usn) {
    const re = /^[A-Z0-9]+$/i;
    return re.test(usn) && usn.length > 0;
}

/**
 * Validate password strength
 */
function validatePassword(password) {
    return password.length >= 6;
}

/**
 * Show loading state on buttons
 */
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = '⏳ Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <span class="alert-close" onclick="this.parentElement.style.display='none';">&times;</span>
    `;
    
    const container = document.querySelector('main');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy', 'danger');
    });
}

/**
 * Format currency/package amount
 */
function formatPackage(amount) {
    if (!amount) return '-';
    // Remove any non-numeric characters except decimals
    const num = parseFloat(amount.replace(/[^\d.]/g, ''));
    if (isNaN(num)) return amount;
    return num.toFixed(2) + ' LPA';
}

/**
 * Form validation helpers
 */
const FormValidator = {
    /**
     * Validate student form
     */
    validateStudentForm: function(formData) {
        const errors = [];
        
        if (!formData.usn || !formData.usn.trim()) {
            errors.push('USN is required');
        } else if (!validateUSN(formData.usn)) {
            errors.push('USN must contain only alphanumeric characters');
        }
        
        if (!formData.full_name || !formData.full_name.trim()) {
            errors.push('Full Name is required');
        }
        
        if (!formData.email_id || !formData.email_id.trim()) {
            errors.push('Email ID is required');
        } else if (!validateEmail(formData.email_id)) {
            errors.push('Invalid email format');
        }
        
        if (!formData.phone_number || !formData.phone_number.trim()) {
            errors.push('Phone Number is required');
        }
        
        if (!formData.parent_name || !formData.parent_name.trim()) {
            errors.push('Parent Name is required');
        }
        
        if (!formData.parent_email || !formData.parent_email.trim()) {
            errors.push('Parent Email is required');
        } else if (!validateEmail(formData.parent_email)) {
            errors.push('Invalid parent email format');
        }
        
        if (!formData.parent_phone || !formData.parent_phone.trim()) {
            errors.push('Parent Phone is required');
        }
        
        return errors;
    },
    
    /**
     * Validate teacher form
     */
    validateTeacherForm: function(formData) {
        const errors = [];
        
        if (!formData.username || !formData.username.trim()) {
            errors.push('Username is required');
        } else if (formData.username.length < 3) {
            errors.push('Username must be at least 3 characters');
        }
        
        if (!formData.password || !formData.password.trim()) {
            errors.push('Password is required');
        } else if (!validatePassword(formData.password)) {
            errors.push('Password must be at least 6 characters');
        }
        
        return errors;
    },
    
    /**
     * Validate class form
     */
    validateClassForm: function(formData) {
        const errors = [];
        
        if (!formData.course || !formData.course.trim()) {
            errors.push('Course is required');
        }
        
        if (!formData.specialisation || !formData.specialisation.trim()) {
            errors.push('Specialisation is required');
        }
        
        return errors;
    }
};

/**
 * Table utilities
 */
const TableUtils = {
    /**
     * Sort table by column
     */
    sortTable: function(table, columnIndex, ascending = true) {
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try numeric comparison
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return ascending ? aNum - bNum : bNum - aNum;
            }
            
            // Fall back to string comparison
            return ascending 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });
        
        rows.forEach(row => table.querySelector('tbody').appendChild(row));
    },
    
    /**
     * Filter table rows
     */
    filterTable: function(table, searchValue) {
        const rows = table.querySelectorAll('tbody tr');
        searchValue = searchValue.toLowerCase();
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchValue) ? '' : 'none';
        });
    }
};

/**
 * Status indicator helpers
 */
const StatusIndicators = {
    /**
     * Get placement status
     */
    getPlacementStatus: function(companyName, package) {
        if (companyName && package) {
            return { status: 'placed', label: '✅ Placed', color: 'success' };
        }
        return { status: 'unplaced', label: '⏳ Unplaced', color: 'warning' };
    },
    
    /**
     * Get notification status
     */
    getNotificationStatus: function(notificationSent) {
        if (notificationSent) {
            return { status: 'sent', label: '✓ Sent', color: 'success' };
        }
        return { status: 'pending', label: '⏸ Pending', color: 'warning' };
    }
};

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    
    // Add headers
    const headers = Array.from(table.querySelectorAll('thead th'))
        .map(th => th.textContent.trim());
    csv.push(headers.join(','));
    
    // Add rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'))
            .slice(0, -1) // Exclude action column
            .map(td => `"${td.textContent.trim()}"`);
        csv.push(cells.join(','));
    });
    
    // Download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * Initialize tooltips (if needed)
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseover', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.position = 'absolute';
            tooltip.style.background = '#333';
            tooltip.style.color = 'white';
            tooltip.style.padding = '0.5rem';
            tooltip.style.borderRadius = '0.25rem';
            tooltip.style.fontSize = '0.875rem';
            tooltip.style.zIndex = '1000';
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        });
    });
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
});

// Export functions for use in HTML
window.confirmDelete = confirmDelete;
window.showNotification = showNotification;
window.copyToClipboard = copyToClipboard;
window.setButtonLoading = setButtonLoading;
window.exportTableToCSV = exportTableToCSV;
window.FormValidator = FormValidator;
window.TableUtils = TableUtils;
window.StatusIndicators = StatusIndicators;
