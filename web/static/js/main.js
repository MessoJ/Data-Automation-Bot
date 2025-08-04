/**
 * Main JavaScript for Data Automation Bot
 * Handles global functionality, navigation, and common utilities
 */

// Global app object
window.DataAutomationBot = {
    version: '1.0.0',
    apiBaseUrl: '/api',
    
    // Utility functions
    utils: {
        // Show loading overlay
        showLoading() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.add('show');
            }
        },
        
        // Hide loading overlay
        hideLoading() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.remove('show');
            }
        },
        
        // Format file size
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        // Format date
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        },
        
        // Format relative time
        formatRelativeTime(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            
            if (diffInSeconds < 60) return 'Just now';
            if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
            if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
            return `${Math.floor(diffInSeconds / 86400)} days ago`;
        },
        
        // Show toast notification
        showToast(message, type = 'info') {
            // Create toast element if it doesn't exist
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                `;
                document.body.appendChild(toastContainer);
            }
            
            // Create toast
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.style.cssText = `
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                max-width: 400px;
                min-width: 300px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            `;
            
            const colors = {
                success: '#10b981',
                error: '#ef4444',
                warning: '#f59e0b',
                info: '#3b82f6'
            };
            
            toast.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 4px; height: 40px; background: ${colors[type] || colors.info}; border-radius: 2px;"></div>
                    <div style="flex: 1;">
                        <p style="margin: 0; color: #374151; font-weight: 500;">${message}</p>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: #6b7280; cursor: pointer; font-size: 18px;">&times;</button>
                </div>
            `;
            
            toastContainer.appendChild(toast);
            
            // Animate in
            setTimeout(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateX(0)';
            }, 10);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        },
        
        // Make API requests
        async apiRequest(endpoint, options = {}) {
            this.showLoading();
            
            try {
                const response = await fetch(`${DataAutomationBot.apiBaseUrl}${endpoint}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('API Request failed:', error);
                this.showToast(`Request failed: ${error.message}`, 'error');
                throw error;
            } finally {
                this.hideLoading();
            }
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('show');
            }
        });
    }
    
    // Add click-to-copy functionality for configuration values
    document.querySelectorAll('.config-value').forEach(element => {
        element.style.cursor = 'pointer';
        element.title = 'Click to copy';
        
        element.addEventListener('click', function() {
            const text = this.textContent.trim();
            if (text && text !== 'Loading...') {
                navigator.clipboard.writeText(text).then(() => {
                    DataAutomationBot.utils.showToast('Copied to clipboard!', 'success');
                }).catch(() => {
                    DataAutomationBot.utils.showToast('Failed to copy to clipboard', 'error');
                });
            }
        });
    });
    
    // Auto-refresh functionality
    let autoRefreshInterval;
    
    window.startAutoRefresh = function(callback, interval = 30000) {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
        autoRefreshInterval = setInterval(callback, interval);
    };
    
    window.stopAutoRefresh = function() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    };
    
    // Initialize tooltips for buttons
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.title;
            tooltip.style.cssText = `
                position: absolute;
                background: #374151;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
                z-index: 10001;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.bottom + 8 + 'px';
            
            setTimeout(() => tooltip.style.opacity = '1', 10);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    console.log('Data Automation Bot initialized successfully');
});

// Global functions for common actions
window.generateReport = async function(type) {
    try {
        const data = await DataAutomationBot.utils.apiRequest('/reports/generate', {
            method: 'POST',
            body: JSON.stringify({ type, format: 'html' })
        });
        
        DataAutomationBot.utils.showToast(data.message || 'Report generated successfully!', 'success');
        
        // Refresh reports if on reports page
        if (window.refreshReports) {
            setTimeout(refreshReports, 1000);
        }
    } catch (error) {
        DataAutomationBot.utils.showToast('Failed to generate report', 'error');
    }
};

window.refreshData = async function() {
    try {
        // This would trigger a manual data refresh
        DataAutomationBot.utils.showToast('Data refresh initiated', 'info');
        
        // Refresh current page data
        if (window.location.pathname === '/') {
            if (window.loadDashboardData) {
                loadDashboardData();
            }
        }
    } catch (error) {
        DataAutomationBot.utils.showToast('Failed to refresh data', 'error');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataAutomationBot;
}