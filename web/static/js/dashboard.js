/**
 * Dashboard JavaScript
 * Handles dashboard-specific functionality including charts, metrics, and real-time updates
 */

let trendChart = null;
let dashboardData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setupCharts();
    setupAutoRefresh();
    
    // Setup period selector
    const chartPeriod = document.getElementById('chartPeriod');
    if (chartPeriod) {
        chartPeriod.addEventListener('change', function() {
            updateTrendChart(this.value);
        });
    }
});

// Load all dashboard data
async function loadDashboardData() {
    try {
        // Load system status
        const status = await DataAutomationBot.utils.apiRequest('/status');
        updateStatusCards(status);
        
        // Load recent activity
        await loadRecentActivity();
        
        // Load chart data
        await updateTrendChart();
        
        // Load reports count
        await loadReportsCount();
        
        dashboardData.lastUpdated = new Date();
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        DataAutomationBot.utils.showToast('Failed to load dashboard data', 'error');
    }
}

// Update status cards with real data
function updateStatusCards(status) {
    // Update database card
    const totalRecords = document.getElementById('totalRecords');
    const recentChange = document.getElementById('recentChange');
    const databaseCard = document.getElementById('databaseCard');
    
    if (totalRecords) {
        totalRecords.textContent = status.database.total_records.toLocaleString();
    }
    if (recentChange) {
        const change = status.database.recent_24h;
        recentChange.textContent = `+${change} in last 24h`;
        recentChange.style.color = change > 0 ? 'var(--green-600)' : 'var(--gray-500)';
    }
    
    // Update scheduler card
    const schedulerStatus = document.getElementById('schedulerStatus');
    const jobsCount = document.getElementById('jobsCount');
    const schedulerCard = document.getElementById('schedulerCard');
    
    if (schedulerStatus) {
        schedulerStatus.textContent = status.scheduler.running ? 'Running' : 'Stopped';
    }
    if (jobsCount) {
        jobsCount.textContent = `${status.scheduler.jobs_count} active jobs`;
    }
    
    // Update scheduler card styling
    if (schedulerCard) {
        const icon = schedulerCard.querySelector('.stat-icon');
        if (status.scheduler.running) {
            icon.className = 'stat-icon stat-icon-green';
        } else {
            icon.className = 'stat-icon stat-icon-orange';
        }
    }
    
    // Update API card
    const apiStatus = document.getElementById('apiStatus');
    const apiUrl = document.getElementById('apiUrl');
    const apiCard = document.getElementById('apiCard');
    
    if (apiStatus) {
        apiStatus.textContent = status.api.configured ? 'Configured' : 'Not Configured';
    }
    if (apiUrl) {
        apiUrl.textContent = status.api.base_url;
    }
    
    // Update API card styling
    if (apiCard) {
        const icon = apiCard.querySelector('.stat-icon');
        if (status.api.configured) {
            icon.className = 'stat-icon stat-icon-purple';
        } else {
            icon.className = 'stat-icon stat-icon-orange';
        }
    }
}

// Setup charts
function setupCharts() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Data Records',
                data: [],
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

// Update trend chart
async function updateTrendChart(days = 7) {
    if (!trendChart) return;
    
    try {
        const data = await DataAutomationBot.utils.apiRequest(`/data?days=${days}&limit=1000`);
        
        // Process data for chart
        const processedData = processDataForChart(data.data, days);
        
        trendChart.data.labels = processedData.labels;
        trendChart.data.datasets[0].data = processedData.values;
        trendChart.update('none');
        
    } catch (error) {
        console.error('Failed to update trend chart:', error);
    }
}

// Process data for chart display
function processDataForChart(data, days) {
    const now = new Date();
    const labels = [];
    const values = [];
    
    // Create date buckets
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Count records for this date
        const count = data.filter(record => {
            const recordDate = new Date(record.timestamp).toISOString().split('T')[0];
            return recordDate === dateStr;
        }).length;
        
        values.push(count);
    }
    
    return { labels, values };
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const activityList = document.getElementById('activityList');
        if (!activityList) return;
        
        // Get recent data and jobs for activity
        const [recentData, jobs] = await Promise.all([
            DataAutomationBot.utils.apiRequest('/data?limit=5'),
            DataAutomationBot.utils.apiRequest('/jobs')
        ]);
        
        const activities = [];
        
        // Add recent data processing activities
        recentData.data.slice(0, 3).forEach(record => {
            activities.push({
                icon: 'data',
                text: `Processed ${record.data_type} data`,
                time: record.processed_at || record.timestamp,
                type: 'blue'
            });
        });
        
        // Add job activities
        jobs.jobs.forEach(job => {
            if (job.next_run) {
                activities.push({
                    icon: 'clock',
                    text: `Job "${job.name}" scheduled`,
                    time: job.next_run,
                    type: 'green'
                });
            }
        });
        
        // Sort by time and take latest 5
        activities.sort((a, b) => new Date(b.time) - new Date(a.time));
        const latestActivities = activities.slice(0, 5);
        
        // Render activities
        activityList.innerHTML = latestActivities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon activity-icon-${activity.type}">
                    ${getActivityIcon(activity.icon)}
                </div>
                <div class="activity-content">
                    <p class="activity-text">${activity.text}</p>
                    <span class="activity-time">${DataAutomationBot.utils.formatRelativeTime(activity.time)}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load recent activity:', error);
        const activityList = document.getElementById('activityList');
        if (activityList) {
            activityList.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon activity-icon-blue">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="activity-content">
                        <p class="activity-text">Unable to load recent activity</p>
                        <span class="activity-time">Just now</span>
                    </div>
                </div>
            `;
        }
    }
}

// Get activity icon SVG
function getActivityIcon(type) {
    const icons = {
        data: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h16v2H4v-2z"/></svg>',
        clock: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
        report: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 2a1 1 0 000 2h6a1 1 0 100-2H9z"/><path d="M4 5a2 2 0 012-2h12a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V5z"/></svg>'
    };
    return icons[type] || icons.data;
}

// Load reports count
async function loadReportsCount() {
    try {
        const reports = await DataAutomationBot.utils.apiRequest('/reports');
        const reportsCount = document.getElementById('reportsCount');
        
        if (reportsCount) {
            reportsCount.textContent = reports.reports.length;
        }
        
    } catch (error) {
        console.error('Failed to load reports count:', error);
    }
}

// Setup auto-refresh
function setupAutoRefresh() {
    // Refresh every 30 seconds
    startAutoRefresh(loadDashboardData, 30000);
    
    // Stop auto-refresh when page is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh(loadDashboardData, 30000);
        }
    });
}

// Refresh activity manually
window.refreshActivity = function() {
    loadRecentActivity();
    DataAutomationBot.utils.showToast('Activity refreshed', 'success');
};

// Export loadDashboardData for global use
window.loadDashboardData = loadDashboardData;