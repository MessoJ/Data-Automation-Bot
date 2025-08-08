import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  ShoppingBag, 
  Package, 
  Globe,
  Zap,
  BarChart3,
  RefreshCw,
  Activity
} from 'lucide-react'
import HeroSection from '../components/dashboard/HeroSection'
import KPIGrid from '../components/dashboard/KPIGrid'
import ChartsSection from '../components/dashboard/ChartsSection'
import ActionsHub from '../components/dashboard/ActionsHub'
import ActivityFeed from '../components/dashboard/ActivityFeed'
import LoadingOverlay from '../components/ui/LoadingOverlay'
import { useDashboard } from '../hooks/useDashboard'
import { useRealtime } from '../hooks/useRealtime'

const Dashboard = () => {
  const { 
    dashboardData, 
    loading, 
    error, 
    refreshData, 
    runSync 
  } = useDashboard()
  
  const { isConnected } = useRealtime()
  const [syncInProgress, setSyncInProgress] = useState(false)

  const handleQuickSync = async () => {
    setSyncInProgress(true)
    try {
      await runSync()
    } finally {
      setSyncInProgress(false)
    }
  }

  const kpiData = [
    {
      id: 'revenue',
      title: 'Total Revenue',
      value: '$84,392',
      change: '+18.2%',
      trend: 'up',
      icon: TrendingUp,
      color: 'success',
      detail: '$2,813 daily average',
      sparklineData: [2000, 2400, 2100, 2800, 3200, 2900, 3400]
    },
    {
      id: 'orders',
      title: 'Orders Today',
      value: '1,247',
      change: '+12.7%',
      trend: 'up',
      icon: ShoppingBag,
      color: 'info',
      detail: '156 pending fulfillment',
      sparklineData: [120, 140, 110, 180, 160, 190, 200]
    },
    {
      id: 'inventory',
      title: 'Active Products',
      value: '3,842',
      change: 'Excellent',
      trend: 'neutral',
      icon: Package,
      color: 'warning',
      detail: '2 alerts need attention'
    },
    {
      id: 'platforms',
      title: 'Connected Platforms',
      value: '5',
      change: 'All Online',
      trend: 'up',
      icon: Globe,
      color: 'primary',
      detail: 'Shopify, Amazon, eBay, WooCommerce, Etsy'
    }
  ]

  const priorityActions = [
    {
      id: 'inventory-issues',
      title: 'Fix Inventory Issues',
      description: '2 critical discrepancies found',
      urgency: 'critical',
      icon: '??',
      action: 'fixInventoryIssues'
    },
    {
      id: 'pricing-update',
      title: 'Update Pricing',
      description: 'Competitor analysis ready',
      urgency: 'high',
      icon: '??',
      action: 'updatePricing'
    }
  ]

  const quickActions = [
    {
      id: 'sync-platforms',
      title: 'Sync All Platforms',
      description: 'Last sync: 3 minutes ago',
      icon: '??',
      action: handleQuickSync
    },
    {
      id: 'generate-report',
      title: 'Generate Report',
      description: 'Export performance data',
      icon: '??',
      action: 'generateReport'
    },
    {
      id: 'add-product',
      title: 'Add New Product',
      description: 'Cross-platform listing',
      icon: '?',
      action: 'addNewProduct'
    },
    {
      id: 'view-analytics',
      title: 'View Analytics',
      description: 'Detailed insights',
      icon: '??',
      action: 'viewAnalytics'
    }
  ]

  if (loading) {
    return <LoadingOverlay />
  }

  return (
    <div className="dashboard-container">
      {/* Floating Background Shapes */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="floating-shape floating-shape-1" />
        <div className="floating-shape floating-shape-2" />
        <div className="floating-shape floating-shape-3" />
        <div className="floating-shape floating-shape-4" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 space-y-8">
        {/* Hero Section */}
        <HeroSection
          onQuickSync={handleQuickSync}
          syncInProgress={syncInProgress}
          isConnected={isConnected}
        />

        {/* Live Performance Dashboard */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-primary-600" />
              <div>
                <h2 className="text-2xl font-bold text-neutral-800">Live Performance</h2>
                <p className="text-neutral-600">Real-time metrics across all your channels</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Time Period Selector */}
              <div className="flex bg-white rounded-lg p-1 shadow-sm border border-neutral-200">
                <button className="px-4 py-2 text-sm font-medium bg-primary-500 text-white rounded-md">
                  Today
                </button>
                <button className="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800">
                  7 Days
                </button>
                <button className="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800">
                  30 Days
                </button>
              </div>
              
              {/* Refresh Button */}
              <button
                onClick={refreshData}
                className="p-2 bg-white rounded-lg shadow-sm border border-neutral-200 hover:bg-neutral-50 transition-colors"
              >
                <RefreshCw className={`w-5 h-5 text-neutral-600 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* KPI Cards Grid */}
          <KPIGrid data={kpiData} />
        </motion.section>

        {/* Charts Section */}
        <ChartsSection />

        {/* Actions Hub */}
        <ActionsHub
          priorityActions={priorityActions}
          quickActions={quickActions}
        />

        {/* Activity Feed */}
        <ActivityFeed />
      </div>

      {/* Loading Overlay for Sync */}
      {syncInProgress && (
        <LoadingOverlay
          title="Syncing all platforms..."
          subtitle="Please wait while we update your platforms"
          steps={[
            { text: '? Connected to Shopify', completed: true },
            { text: '?? Syncing inventory...', active: true },
            { text: '? Updating prices', pending: true }
          ]}
        />
      )}
    </div>
  )
}

export default Dashboard