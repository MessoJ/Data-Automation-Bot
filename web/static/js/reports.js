/**
 * Reports JavaScript
 * Handles report generation, management, and viewing functionality
 */

let availableReports = [];

// Initialize reports page
document.addEventListener('DOMContentLoaded', function() {
    setupReportForm();
    loadReports();
    
    // Setup form submission
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', handleReportGeneration);
    }
    
    // Setup report type change handler
    const reportType = document.getElementById('reportType');
    if (reportType) {
        reportType.addEventListener('change', handleReportTypeChange);
        handleReportTypeChange(); // Initial call
    }
});

// Setup report form
function setupReportForm() {
    // Add form validation and UI enhancements
    const form = document.getElementById('reportForm');
    if (!form) return;
    
    // Add loading state to submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.dataset.originalText = submitBtn.textContent;
    }
}

// Handle report type change
function handleReportTypeChange() {
    const reportType = document.getElementById('reportType');
    const trendOptions = document.getElementById('trendOptions');
    
    if (!reportType || !trendOptions) return;
    
    if (reportType.value === 'trend') {
        trendOptions.style.display = 'flex';
        const dataTypeInput = document.getElementById('dataType');
        if (dataTypeInput) {
            dataTypeInput.required = true;
        }
    } else {
        trendOptions.style.display = 'none';
        const dataTypeInput = document.getElementById('dataType');
        if (dataTypeInput) {
            dataTypeInput.required = false;
        }
    }
}

// Handle report generation
async function handleReportGeneration(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    
    // Prepare request data
    const requestData = {
        type: formData.get('type'),
        format: formData.get('format'),
        data_type: formData.get('data_type') || null,
        days: parseInt(formData.get('days')) || 30
    };
    
    // Validate trend report requirements
    if (requestData.type === 'trend' && !requestData.data_type) {
        DataAutomationBot.utils.showToast('Data type is required for trend reports', 'error');
        return;
    }
    
    try {
        // Update button state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <div class="loading-spinner" style="width: 1rem; height: 1rem; margin-right: 8px;"></div>
                Generating...
            `;
        }
        
        // Generate report
        const response = await DataAutomationBot.utils.apiRequest('/reports/generate', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
        
        DataAutomationBot.utils.showToast(response.message || 'Report generated successfully!', 'success');
        
        // Refresh reports list
        setTimeout(() => {
            loadReports();
        }, 1000);
        
        // Reset form
        form.reset();
        handleReportTypeChange();
        
    } catch (error) {
        DataAutomationBot.utils.showToast('Failed to generate report', 'error');
    } finally {
        // Restore button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 2a1 1 0 000 2h6a1 1 0 100-2H9z"/>
                    <path d="M4 5a2 2 0 012-2h12a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V5z"/>
                </svg>
                Generate Report
            `;
        }
    }
}

// Load available reports
async function loadReports() {
    try {
        const response = await DataAutomationBot.utils.apiRequest('/reports');
        availableReports = response.reports;
        renderReports();
        
    } catch (error) {
        console.error('Failed to load reports:', error);
        DataAutomationBot.utils.showToast('Failed to load reports', 'error');
        
        const reportsGrid = document.getElementById('reportsGrid');
        if (reportsGrid) {
            reportsGrid.innerHTML = `
                <div class="loading-placeholder">
                    <svg viewBox="0 0 24 24" fill="currentColor" style="width: 3rem; height: 3rem; color: var(--gray-400);">
                        <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p>Failed to load reports</p>
                </div>
            `;
        }
    }
}

// Render reports grid
function renderReports() {
    const reportsGrid = document.getElementById('reportsGrid');
    if (!reportsGrid) return;
    
    if (availableReports.length === 0) {
        reportsGrid.innerHTML = `
            <div class="loading-placeholder">
                <svg viewBox="0 0 24 24" fill="currentColor" style="width: 3rem; height: 3rem; color: var(--gray-400);">
                    <path d="M9 2a1 1 0 000 2h6a1 1 0 100-2H9z"/>
                    <path d="M4 5a2 2 0 012-2h12a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V5z"/>
                </svg>
                <p>No reports available</p>
                <p style="font-size: 0.875rem; color: var(--gray-500);">Generate your first report using the form above</p>
            </div>
        `;
        return;
    }
    
    reportsGrid.innerHTML = availableReports.map(report => `
        <div class="report-card">
            <div class="report-header">
                <div class="report-name" title="${report.filename}">${truncateFilename(report.filename)}</div>
                <div class="report-size">${DataAutomationBot.utils.formatFileSize(report.size)}</div>
            </div>
            <div class="report-meta">
                <div>Created: ${DataAutomationBot.utils.formatDate(report.created)}</div>
                <div>Modified: ${DataAutomationBot.utils.formatRelativeTime(report.modified)}</div>
            </div>
            <div class="report-actions">
                ${getReportActions(report)}
            </div>
        </div>
    `).join('');
}

// Get report actions based on file type
function getReportActions(report) {
    const actions = [];
    
    // Preview for HTML files
    if (report.filename.endsWith('.html')) {
        actions.push(`
            <button class="btn btn-sm btn-secondary" onclick="previewReport('${report.filename}')">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                Preview
            </button>
        `);
    }
    
    // Download button
    actions.push(`
        <a href="/api/reports/download/${report.filename}" class="btn btn-sm btn-primary" download>
            <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 17a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"/>
            </svg>
            Download
        </a>
    `);
    
    return actions.join('');
}

// Truncate filename for display
function truncateFilename(filename) {
    if (filename.length <= 30) return filename;
    const extension = filename.split('.').pop();
    const basename = filename.substring(0, filename.lastIndexOf('.'));
    const truncated = basename.substring(0, 25) + '...';
    return `${truncated}.${extension}`;
}

// Preview report in modal
function previewReport(filename) {
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modalTitle');
    const reportPreview = document.getElementById('reportPreview');
    const downloadLink = document.getElementById('downloadLink');
    
    if (!modal) return;
    
    // Set modal content
    if (modalTitle) {
        modalTitle.textContent = `Preview: ${filename}`;
    }
    
    if (reportPreview) {
        reportPreview.src = `/api/reports/download/${filename}`;
        reportPreview.style.width = '100%';
        reportPreview.style.height = '400px';
        reportPreview.style.border = 'none';
    }
    
    if (downloadLink) {
        downloadLink.href = `/api/reports/download/${filename}`;
        downloadLink.download = filename;
    }
    
    // Show modal
    modal.classList.add('show');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

// Close report modal
function closeModal() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        
        // Clear iframe src to stop loading
        const reportPreview = document.getElementById('reportPreview');
        if (reportPreview) {
            reportPreview.src = '';
        }
    }
}

// Refresh reports
window.refreshReports = function() {
    loadReports();
    DataAutomationBot.utils.showToast('Reports refreshed', 'success');
};

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});

// Export for global use
window.previewReport = previewReport;
window.closeModal = closeModal;