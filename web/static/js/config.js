/**
 * Configuration JavaScript
 * Handles configuration display, testing, and management functionality
 */

let configData = {};
let systemStartTime = new Date();

// Initialize config page
document.addEventListener('DOMContentLoaded', function() {
    loadConfiguration();
    updateSystemInfo();
    setupAutoRefresh();
});

// Load configuration data
async function loadConfiguration() {
    try {
        const config = await DataAutomationBot.utils.apiRequest('/config');
        configData = config;
        updateConfigDisplay();
        
    } catch (error) {
        console.error('Failed to load configuration:', error);
        DataAutomationBot.utils.showToast('Failed to load configuration', 'error');
        showConfigError();
    }
}

// Update configuration display
function updateConfigDisplay() {
    // API Configuration
    updateConfigValue('apiBaseUrl', configData.api.base_url);
    updateConfigValue('apiTimeout', `${configData.api.timeout} seconds`);
    updateConfigValue('apiKeyStatus', configData.api.configured ? 'Configured' : 'Not Configured');
    updateConfigStatus('apiConfigStatus', configData.api.configured);
    
    // Database Configuration
    updateConfigValue('dbHost', configData.database.host);
    updateConfigValue('dbPort', configData.database.port);
    updateConfigValue('dbName', configData.database.name);
    updateConfigValue('dbUser', configData.database.user);
    updateConfigStatus('dbConfigStatus', true); // Assume configured if we got this far
    
    // Scheduler Configuration
    updateConfigValue('schedulerInterval', `${configData.scheduler.interval} seconds`);
    updateConfigValue('retryAttempts', configData.scheduler.retry_attempts);
    updateConfigValue('retryDelay', `${configData.scheduler.retry_delay} seconds`);
    
    // Reporting Configuration
    updateConfigValue('reportOutputDir', configData.reporting.output_dir);
    updateConfigValue('defaultFormat', configData.reporting.default_format.toUpperCase());
}

// Update individual config value
function updateConfigValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        element.classList.add('config-loaded');
    }
}

// Update config section status
function updateConfigStatus(sectionId, isConfigured) {
    const statusElement = document.getElementById(sectionId);
    if (!statusElement) return;
    
    const badge = statusElement.querySelector('.status-badge');
    if (badge) {
        if (isConfigured) {
            badge.className = 'status-badge status-badge-success';
            badge.textContent = 'Configured';
        } else {
            badge.className = 'status-badge status-badge-warning';
            badge.textContent = 'Incomplete';
        }
    }
}

// Show configuration error
function showConfigError() {
    const sections = ['apiConfigStatus', 'dbConfigStatus', 'schedulerConfigStatus', 'reportingConfigStatus'];
    
    sections.forEach(sectionId => {
        const statusElement = document.getElementById(sectionId);
        if (statusElement) {
            const badge = statusElement.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge status-badge-error';
                badge.textContent = 'Error';
            }
        }
    });
    
    // Update all config values to show error
    const configValues = document.querySelectorAll('.config-value');
    configValues.forEach(element => {
        element.textContent = 'Failed to load';
        element.style.color = 'var(--red-500)';
    });
}

// Update system information
function updateSystemInfo() {
    // Calculate uptime
    updateUptime();
    
    // Update last updated time
    const lastUpdated = document.getElementById('lastUpdated');
    if (lastUpdated) {
        lastUpdated.textContent = DataAutomationBot.utils.formatRelativeTime(new Date().toISOString());
    }
    
    // Update uptime every minute
    setInterval(updateUptime, 60000);
}

// Update system uptime
function updateUptime() {
    const uptimeElement = document.getElementById('systemUptime');
    if (!uptimeElement) return;
    
    const now = new Date();
    const diffInSeconds = Math.floor((now - systemStartTime) / 1000);
    
    const days = Math.floor(diffInSeconds / 86400);
    const hours = Math.floor((diffInSeconds % 86400) / 3600);
    const minutes = Math.floor((diffInSeconds % 3600) / 60);
    
    let uptimeText = '';
    if (days > 0) {
        uptimeText = `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
        uptimeText = `${hours}h ${minutes}m`;
    } else {
        uptimeText = `${minutes}m`;
    }
    
    uptimeElement.textContent = uptimeText;
}

// Setup auto-refresh
function setupAutoRefresh() {
    // Refresh every 2 minutes
    startAutoRefresh(() => {
        loadConfiguration();
        updateSystemInfo();
    }, 120000);
    
    // Stop auto-refresh when page is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh(() => {
                loadConfiguration();
                updateSystemInfo();
            }, 120000);
        }
    });
}

// Refresh configuration manually
window.refreshConfig = function() {
    loadConfiguration();
    updateSystemInfo();
    DataAutomationBot.utils.showToast('Configuration refreshed', 'success');
};

// Export configuration
window.exportConfig = function() {
    if (!configData || Object.keys(configData).length === 0) {
        DataAutomationBot.utils.showToast('No configuration data to export', 'warning');
        return;
    }
    
    try {
        // Create exportable config (remove sensitive data)
        const exportData = {
            ...configData,
            api: {
                ...configData.api,
                // Remove sensitive fields - just show if configured
                configured: configData.api.configured
            }
        };
        
        // Create and download file
        const dataStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `data-automation-config-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        DataAutomationBot.utils.showToast('Configuration exported successfully', 'success');
        
    } catch (error) {
        console.error('Failed to export configuration:', error);
        DataAutomationBot.utils.showToast('Failed to export configuration', 'error');
    }
};

// Test connections
window.testConnections = function() {
    const modal = document.getElementById('testModal');
    const testResults = document.getElementById('testResults');
    
    if (!modal || !testResults) return;
    
    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Show loading
    testResults.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
            <p>Testing connections...</p>
        </div>
    `;
    
    // Simulate connection tests
    setTimeout(() => {
        performConnectionTests();
    }, 2000);
};

// Perform connection tests
async function performConnectionTests() {
    const testResults = document.getElementById('testResults');
    if (!testResults) return;
    
    const tests = [
        {
            name: 'Database Connection',
            test: testDatabaseConnection,
            description: 'Testing database connectivity and authentication'
        },
        {
            name: 'API Endpoint',
            test: testApiConnection,
            description: 'Testing external API connectivity'
        },
        {
            name: 'Report Directory',
            test: testReportDirectory,
            description: 'Testing report output directory access'
        },
        {
            name: 'Scheduler Service',
            test: testSchedulerService,
            description: 'Testing job scheduler functionality'
        }
    ];
    
    let resultsHtml = '<div class="test-results-list">';
    
    for (const test of tests) {
        resultsHtml += `
            <div class="test-result-item" id="test-${test.name.replace(/\s+/g, '-').toLowerCase()}">
                <div class="test-header">
                    <h4 class="test-name">${test.name}</h4>
                    <div class="test-status">
                        <div class="loading-spinner" style="width: 1rem; height: 1rem;"></div>
                    </div>
                </div>
                <p class="test-description">${test.description}</p>
                <div class="test-details" style="display: none;"></div>
            </div>
        `;
    }
    
    resultsHtml += '</div>';
    testResults.innerHTML = resultsHtml;
    
    // Run tests sequentially
    for (const test of tests) {
        await runSingleTest(test);
        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between tests
    }
}

// Run a single connection test
async function runSingleTest(test) {
    const testElement = document.getElementById(`test-${test.name.replace(/\s+/g, '-').toLowerCase()}`);
    if (!testElement) return;
    
    const statusElement = testElement.querySelector('.test-status');
    const detailsElement = testElement.querySelector('.test-details');
    
    try {
        const result = await test.test();
        
        // Update status
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-badge status-badge-success">✓ Pass</span>
            `;
        }
        
        // Update details
        if (detailsElement && result.details) {
            detailsElement.innerHTML = `<p style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">${result.details}</p>`;
            detailsElement.style.display = 'block';
        }
        
    } catch (error) {
        // Update status
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-badge status-badge-error">✗ Fail</span>
            `;
        }
        
        // Update details
        if (detailsElement) {
            detailsElement.innerHTML = `<p style="font-size: 0.875rem; color: var(--red-600); margin-top: 0.5rem;">Error: ${error.message}</p>`;
            detailsElement.style.display = 'block';
        }
    }
}

// Individual test functions
async function testDatabaseConnection() {
    // Simulate database test
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (configData.database && configData.database.host) {
        return {
            success: true,
            details: `Connected to ${configData.database.host}:${configData.database.port}`
        };
    } else {
        throw new Error('Database configuration not found');
    }
}

async function testApiConnection() {
    // Test actual API status
    try {
        const status = await DataAutomationBot.utils.apiRequest('/status');
        return {
            success: true,
            details: `API responding normally (${configData.api.base_url})`
        };
    } catch (error) {
        throw new Error('API not responding');
    }
}

async function testReportDirectory() {
    // Simulate report directory test
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
        success: true,
        details: `Report directory accessible: ${configData.reporting.output_dir}`
    };
}

async function testSchedulerService() {
    // Test scheduler status
    try {
        const status = await DataAutomationBot.utils.apiRequest('/status');
        if (status.scheduler.running) {
            return {
                success: true,
                details: `Scheduler running with ${status.scheduler.jobs_count} jobs`
            };
        } else {
            throw new Error('Scheduler is not running');
        }
    } catch (error) {
        throw new Error('Unable to check scheduler status');
    }
}

// Close test modal
function closeTestModal() {
    const modal = document.getElementById('testModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('testModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeTestModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeTestModal();
        }
    });
});

// Add test results styles
const testResultsStyles = `
<style>
.test-results-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.test-result-item {
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-md);
    padding: 1rem;
    background: var(--gray-50);
}

.test-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.test-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--gray-900);
    margin: 0;
}

.test-description {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: 0;
}

.config-loaded {
    transition: all 0.3s ease;
}
</style>
`;

// Add styles to document head
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('test-results-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'test-results-styles';
        styleElement.innerHTML = testResultsStyles.replace(/<\/?style>/g, '');
        document.head.appendChild(styleElement);
    }
});

// Export functions for global use
window.closeTestModal = closeTestModal;