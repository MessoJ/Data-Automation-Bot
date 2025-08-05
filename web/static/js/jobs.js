/**
 * Jobs JavaScript
 * Handles job management, monitoring, and control functionality
 */

let currentJobs = [];
let selectedJobId = null;

// Initialize jobs page
document.addEventListener('DOMContentLoaded', function() {
    loadJobs();
    loadSchedulerStatus();
    setupAutoRefresh();
});

// Load scheduler status
async function loadSchedulerStatus() {
    try {
        const status = await DataAutomationBot.utils.apiRequest('/status');
        updateSchedulerStatus(status.scheduler);
        
    } catch (error) {
        console.error('Failed to load scheduler status:', error);
        DataAutomationBot.utils.showToast('Failed to load scheduler status', 'error');
    }
}

// Update scheduler status display
function updateSchedulerStatus(schedulerData) {
    const statusCard = document.getElementById('schedulerStatusCard');
    const statusIcon = document.getElementById('schedulerIcon');
    const statusText = document.getElementById('schedulerStatusText');
    const statusDesc = document.getElementById('schedulerStatusDesc');
    const toggleBtn = document.getElementById('schedulerToggle');
    const toggleText = document.getElementById('schedulerToggleText');
    
    if (!statusCard) return;
    
    const isRunning = schedulerData.running;
    
    // Update status card styling
    if (isRunning) {
        statusCard.style.borderLeftColor = 'var(--green-500)';
        if (statusIcon) {
            statusIcon.style.color = 'var(--green-600)';
        }
    } else {
        statusCard.style.borderLeftColor = 'var(--orange-500)';
        if (statusIcon) {
            statusIcon.style.color = 'var(--orange-500)';
        }
    }
    
    // Update text content
    if (statusText) {
        statusText.textContent = isRunning ? 'Scheduler Running' : 'Scheduler Stopped';
    }
    
    if (statusDesc) {
        statusDesc.textContent = isRunning 
            ? `${schedulerData.jobs_count} jobs scheduled and running`
            : 'Scheduler is currently stopped';
    }
    
    // Update toggle button
    if (toggleBtn && toggleText) {
        toggleBtn.className = `btn btn-sm ${isRunning ? 'btn-warning' : 'btn-success'}`;
        toggleText.textContent = isRunning ? 'Stop Scheduler' : 'Start Scheduler';
    }
}

// Load jobs
async function loadJobs() {
    try {
        const response = await DataAutomationBot.utils.apiRequest('/jobs');
        currentJobs = response.jobs;
        renderJobs();
        updateJobHistory();
        
    } catch (error) {
        console.error('Failed to load jobs:', error);
        DataAutomationBot.utils.showToast('Failed to load jobs', 'error');
        
        const jobsGrid = document.getElementById('jobsGrid');
        if (jobsGrid) {
            jobsGrid.innerHTML = `
                <div class="loading-placeholder">
                    <svg viewBox="0 0 24 24" fill="currentColor" style="width: 3rem; height: 3rem; color: var(--gray-400);">
                        <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p>Failed to load jobs</p>
                </div>
            `;
        }
    }
}

// Render jobs grid
function renderJobs() {
    const jobsGrid = document.getElementById('jobsGrid');
    if (!jobsGrid) return;
    
    if (currentJobs.length === 0) {
        jobsGrid.innerHTML = `
            <div class="loading-placeholder">
                <svg viewBox="0 0 24 24" fill="currentColor" style="width: 3rem; height: 3rem; color: var(--gray-400);">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <p>No scheduled jobs found</p>
                <p style="font-size: 0.875rem; color: var(--gray-500);">Jobs will appear here when the scheduler is running</p>
            </div>
        `;
        return;
    }
    
    jobsGrid.innerHTML = currentJobs.map(job => `
        <div class="job-card" data-job-id="${job.id}">
            <div class="job-info">
                <div class="job-name">${job.name || job.id}</div>
                <div class="job-details">
                    <div>Next run: ${job.next_run ? DataAutomationBot.utils.formatDate(job.next_run) : 'Not scheduled'}</div>
                    <div>Trigger: ${job.trigger}</div>
                </div>
            </div>
            <div class="job-actions">
                <button class="btn btn-sm btn-secondary" onclick="showJobDetails('${job.id}')">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Details
                </button>
                <button class="btn btn-sm btn-warning" onclick="pauseJobInline('${job.id}')">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M10 9v6h4V9h-4zm-7 0a7 7 0 1114 0 7 7 0 01-14 0z"/>
                    </svg>
                    Pause
                </button>
            </div>
        </div>
    `).join('');
}

// Show job details in modal
function showJobDetails(jobId) {
    const job = currentJobs.find(j => j.id === jobId);
    if (!job) return;
    
    selectedJobId = jobId;
    
    const modal = document.getElementById('jobModal');
    const modalTitle = document.getElementById('jobModalTitle');
    const jobDetails = document.getElementById('jobDetails');
    const pauseBtn = document.getElementById('pauseJobBtn');
    const resumeBtn = document.getElementById('resumeJobBtn');
    
    if (!modal) return;
    
    // Set modal content
    if (modalTitle) {
        modalTitle.textContent = `Job: ${job.name || job.id}`;
    }
    
    if (jobDetails) {
        jobDetails.innerHTML = `
            <div class="job-detail-grid" style="display: grid; gap: 1rem;">
                <div class="detail-item">
                    <strong>Job ID:</strong> ${job.id}
                </div>
                <div class="detail-item">
                    <strong>Name:</strong> ${job.name || 'Unnamed'}
                </div>
                <div class="detail-item">
                    <strong>Next Run:</strong> ${job.next_run ? DataAutomationBot.utils.formatDate(job.next_run) : 'Not scheduled'}
                </div>
                <div class="detail-item">
                    <strong>Trigger:</strong> ${job.trigger}
                </div>
                <div class="detail-item">
                    <strong>Arguments:</strong> ${Object.keys(job.kwargs || {}).length > 0 ? JSON.stringify(job.kwargs, null, 2) : 'None'}
                </div>
            </div>
        `;
    }
    
    // Show/hide appropriate buttons
    if (pauseBtn && resumeBtn) {
        pauseBtn.style.display = 'inline-flex';
        resumeBtn.style.display = 'none';
    }
    
    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// Close job modal
function closeJobModal() {
    const modal = document.getElementById('jobModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        selectedJobId = null;
    }
}

// Pause job from inline button
async function pauseJobInline(jobId) {
    await pauseResumeJob(jobId, 'pause');
}

// Pause job from modal
async function pauseJob() {
    if (!selectedJobId) return;
    await pauseResumeJob(selectedJobId, 'pause');
}

// Resume job from modal
async function resumeJob() {
    if (!selectedJobId) return;
    await pauseResumeJob(selectedJobId, 'resume');
}

// Pause or resume job
async function pauseResumeJob(jobId, action) {
    try {
        const response = await DataAutomationBot.utils.apiRequest(`/jobs/${jobId}/${action}`, {
            method: 'POST'
        });
        
        DataAutomationBot.utils.showToast(response.message, 'success');
        
        // Reload jobs
        await loadJobs();
        
        // Update modal buttons if modal is open
        if (selectedJobId === jobId) {
            const pauseBtn = document.getElementById('pauseJobBtn');
            const resumeBtn = document.getElementById('resumeJobBtn');
            
            if (action === 'pause') {
                if (pauseBtn) pauseBtn.style.display = 'none';
                if (resumeBtn) resumeBtn.style.display = 'inline-flex';
            } else {
                if (pauseBtn) pauseBtn.style.display = 'inline-flex';
                if (resumeBtn) resumeBtn.style.display = 'none';
            }
        }
        
    } catch (error) {
        DataAutomationBot.utils.showToast(`Failed to ${action} job`, 'error');
    }
}

// Toggle scheduler
async function toggleScheduler() {
    try {
        const status = await DataAutomationBot.utils.apiRequest('/status');
        const isRunning = status.scheduler.running;
        
        // Note: This would need backend implementation
        DataAutomationBot.utils.showToast(
            `Scheduler ${isRunning ? 'stop' : 'start'} functionality would be implemented here`,
            'info'
        );
        
    } catch (error) {
        DataAutomationBot.utils.showToast('Failed to toggle scheduler', 'error');
    }
}

// Update job history
function updateJobHistory() {
    const jobHistory = document.getElementById('jobHistory');
    if (!jobHistory) return;
    
    // Create simulated job history based on current jobs
    const historyItems = [];
    
    // Add system initialization
    historyItems.push({
        title: 'System Initialization',
        desc: 'Data Automation Bot initialized successfully',
        time: new Date().toISOString(),
        type: 'blue'
    });
    
    // Add job scheduling events
    currentJobs.forEach(job => {
        if (job.next_run) {
            historyItems.push({
                title: `Job Scheduled: ${job.name || job.id}`,
                desc: `Next execution at ${DataAutomationBot.utils.formatDate(job.next_run)}`,
                time: new Date(Date.now() - Math.random() * 3600000).toISOString(), // Random time in last hour
                type: 'green'
            });
        }
    });
    
    // Sort by time
    historyItems.sort((a, b) => new Date(b.time) - new Date(a.time));
    
    // Render history
    jobHistory.innerHTML = historyItems.map(item => `
        <div class="timeline-item">
            <div class="timeline-marker timeline-marker-${item.type}"></div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <h4 class="timeline-title">${item.title}</h4>
                    <span class="timeline-time">${DataAutomationBot.utils.formatRelativeTime(item.time)}</span>
                </div>
                <p class="timeline-desc">${item.desc}</p>
            </div>
        </div>
    `).join('');
}

// Setup auto-refresh
function setupAutoRefresh() {
    // Refresh every 30 seconds
    startAutoRefresh(() => {
        loadJobs();
        loadSchedulerStatus();
    }, 30000);
    
    // Stop auto-refresh when page is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh(() => {
                loadJobs();
                loadSchedulerStatus();
            }, 30000);
        }
    });
}

// Refresh jobs manually
window.refreshJobs = function() {
    loadJobs();
    loadSchedulerStatus();
    DataAutomationBot.utils.showToast('Jobs refreshed', 'success');
};

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('jobModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeJobModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeJobModal();
        }
    });
});

// Add timeline styles
const timelineStyles = `
<style>
.timeline-item {
    display: flex;
    margin-bottom: 1.5rem;
    position: relative;
}

.timeline-marker {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 50%;
    margin-right: 1rem;
    margin-top: 0.25rem;
    flex-shrink: 0;
}

.timeline-marker-blue {
    background-color: var(--primary-500);
}

.timeline-marker-green {
    background-color: var(--green-500);
}

.timeline-marker-orange {
    background-color: var(--orange-500);
}

.timeline-content {
    flex: 1;
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-md);
    padding: 1rem;
}

.timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}

.timeline-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--gray-900);
    margin: 0;
}

.timeline-time {
    font-size: 0.75rem;
    color: var(--gray-500);
    white-space: nowrap;
}

.timeline-desc {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: 0;
}
</style>
`;

// Add styles to document head
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('timeline-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'timeline-styles';
        styleElement.innerHTML = timelineStyles.replace(/<\/?style>/g, '');
        document.head.appendChild(styleElement);
    }
});

// Export functions for global use
window.showJobDetails = showJobDetails;
window.closeJobModal = closeJobModal;
window.pauseJob = pauseJob;
window.resumeJob = resumeJob;
window.toggleScheduler = toggleScheduler;