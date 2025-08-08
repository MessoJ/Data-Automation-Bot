import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Clock, 
  Play, 
  Pause, 
  RefreshCw, 
  Settings,
  CheckCircle,
  AlertCircle,
  Info,
  Calendar
} from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const Jobs = () => {
  const [jobs, setJobs] = useState([])
  const [schedulerStatus, setSchedulerStatus] = useState({ running: false, jobs_count: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadJobs()
    loadSchedulerStatus()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await axios.get('/api/jobs')
      setJobs(response.data.jobs || [])
    } catch (error) {
      toast.error('Failed to load jobs')
      console.error('Error loading jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSchedulerStatus = async () => {
    try {
      const response = await axios.get('/api/status')
      setSchedulerStatus(response.data.scheduler || { running: false, jobs_count: 0 })
    } catch (error) {
      console.error('Error loading scheduler status:', error)
    }
  }

  const pauseJob = async (jobId) => {
    try {
      await axios.post(`/api/jobs/${jobId}/pause`)
      toast.success(`Job ${jobId} paused successfully`)
      loadJobs()
    } catch (error) {
      toast.error('Failed to pause job')
      console.error('Error pausing job:', error)
    }
  }

  const resumeJob = async (jobId) => {
    try {
      await axios.post(`/api/jobs/${jobId}/resume`)
      toast.success(`Job ${jobId} resumed successfully`)
      loadJobs()
    } catch (error) {
      toast.error('Failed to resume job')
      console.error('Error resuming job:', error)
    }
  }

  const refreshJobs = () => {
    setLoading(true)
    Promise.all([loadJobs(), loadSchedulerStatus()]).finally(() => {
      toast.success('Jobs refreshed')
    })
  }

  const getJobIcon = (jobName) => {
    if (jobName.toLowerCase().includes('sync')) return '??'
    if (jobName.toLowerCase().includes('report')) return '??'
    if (jobName.toLowerCase().includes('inventory')) return '??'
    if (jobName.toLowerCase().includes('price')) return '??'
    return '??'
  }

  const activityItems = [
    {
      type: 'success',
      title: 'Inventory sync completed',
      description: 'Synchronized 1,247 products across all platforms',
      time: '2 minutes ago',
      icon: '?'
    },
    {
      type: 'success',
      title: 'Price monitoring job finished',
      description: 'Checked pricing across 5 platforms',
      time: '15 minutes ago',
      icon: '??'
    },
    {
      type: 'warning',
      title: 'Discrepancy detection alert',
      description: 'Found 3 pricing discrepancies requiring attention',
      time: '1 hour ago',
      icon: '??'
    },
    {
      type: 'info',
      title: 'Daily report generated',
      description: 'Performance report for 2025-01-08 created',
      time: '2 hours ago',
      icon: '??'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-r from-warning-500 to-warning-600 rounded-xl flex items-center justify-center">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-neutral-800">Job Scheduler</h1>
            <p className="text-neutral-600">Monitor and manage your automated e-commerce sync jobs</p>
          </div>
        </div>

        <button
          onClick={refreshJobs}
          disabled={loading}
          className="btn-secondary"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </motion.div>

      {/* Scheduler Status Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-neutral-800">Scheduler Status</h2>
          
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
            schedulerStatus.running 
              ? 'bg-success-100 text-success-700' 
              : 'bg-error-100 text-error-700'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              schedulerStatus.running ? 'bg-success-500 animate-pulse' : 'bg-error-500'
            }`} />
            <span className="font-medium">
              {schedulerStatus.running ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center gap-4 p-4 bg-neutral-50 rounded-xl">
            <div className="w-10 h-10 bg-gradient-to-r from-info-500 to-info-600 rounded-lg flex items-center justify-center">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-800">{schedulerStatus.jobs_count}</div>
              <div className="text-sm text-neutral-600">Total Jobs</div>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 bg-neutral-50 rounded-xl">
            <div className="w-10 h-10 bg-gradient-to-r from-success-500 to-success-600 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-800">
                {jobs.filter(job => job.next_run).length}
              </div>
              <div className="text-sm text-neutral-600">Active Jobs</div>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 bg-neutral-50 rounded-xl">
            <div className="w-10 h-10 bg-gradient-to-r from-warning-500 to-warning-600 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-2xl font-bold text-neutral-800">
                {jobs.length - jobs.filter(job => job.next_run).length}
              </div>
              <div className="text-sm text-neutral-600">Paused Jobs</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Jobs List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-8"
      >
        {/* Active Jobs */}
        <div className="card">
          <h2 className="text-xl font-bold text-neutral-800 mb-6">Active Jobs</h2>
          
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="loading-ring w-6 h-6" />
              <span className="ml-3 text-neutral-600">Loading jobs...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
              <p className="text-neutral-600">No scheduled jobs found</p>
              <p className="text-sm text-neutral-500 mt-1">Jobs will appear here when the scheduler is running</p>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job, index) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-4 bg-neutral-50 rounded-xl hover:bg-neutral-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl flex items-center justify-center text-lg">
                      {getJobIcon(job.name)}
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-neutral-800">{job.name || job.id}</h4>
                      <div className="text-sm text-neutral-600">
                        <div>Next run: {job.next_run ? new Date(job.next_run).toLocaleString() : 'Not scheduled'}</div>
                        <div>Trigger: {job.trigger}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => pauseJob(job.id)}
                      className="p-2 text-warning-600 hover:bg-warning-100 rounded-lg transition-colors"
                      title="Pause Job"
                    >
                      <Pause className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => resumeJob(job.id)}
                      className="p-2 text-success-600 hover:bg-success-100 rounded-lg transition-colors"
                      title="Resume Job"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-bold text-neutral-800 mb-6">Recent Activity</h2>
          
          <div className="space-y-4">
            {activityItems.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-start gap-4 p-4 rounded-xl border-l-4 ${
                  item.type === 'success' ? 'bg-success-50 border-success-500' :
                  item.type === 'warning' ? 'bg-warning-50 border-warning-500' :
                  item.type === 'error' ? 'bg-error-50 border-error-500' :
                  'bg-info-50 border-info-500'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  item.type === 'success' ? 'bg-success-100' :
                  item.type === 'warning' ? 'bg-warning-100' :
                  item.type === 'error' ? 'bg-error-100' :
                  'bg-info-100'
                }`}>
                  {item.icon}
                </div>
                
                <div className="flex-1">
                  <h4 className="font-medium text-neutral-800 mb-1">{item.title}</h4>
                  <p className="text-sm text-neutral-600 mb-2">{item.description}</p>
                  <span className="text-xs text-neutral-500 font-medium">{item.time}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Job Statistics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <div className="card text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-800 mb-1">24/7</h3>
          <p className="text-neutral-600">Monitoring</p>
        </div>

        <div className="card text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-success-500 to-success-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-800 mb-1">99.9%</h3>
          <p className="text-neutral-600">Uptime</p>
        </div>

        <div className="card text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-info-500 to-info-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <RefreshCw className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-800 mb-1">15min</h3>
          <p className="text-neutral-600">Sync Interval</p>
        </div>

        <div className="card text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-warning-500 to-warning-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-800 mb-1">0</h3>
          <p className="text-neutral-600">Failed Jobs</p>
        </div>
      </motion.div>
    </div>
  )
}

export default Jobs