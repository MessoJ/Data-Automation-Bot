import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import toast from 'react-hot-toast'

export const useDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    status: null,
    revenue: null,
    discrepancies: null
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all dashboard data concurrently
      const [statusRes, revenueRes, discrepanciesRes] = await Promise.all([
        axios.get('/api/status'),
        axios.get('/api/ecommerce/revenue'),
        axios.get('/api/ecommerce/discrepancies')
      ])

      setDashboardData({
        status: statusRes.data,
        revenue: revenueRes.data,
        discrepancies: discrepanciesRes.data
      })
    } catch (err) {
      console.error('Dashboard data fetch error:', err)
      setError(err.message)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const refreshData = () => {
    toast.promise(fetchData(), {
      loading: 'Refreshing dashboard data...',
      success: 'Dashboard updated!',
      error: 'Failed to refresh data'
    })
  }

  const runSync = async () => {
    try {
      const response = await axios.post('/api/ecommerce/sync', {
        platforms: [
          { name: 'Shopify', type: 'shopify' },
          { name: 'Amazon', type: 'amazon' },
          { name: 'eBay', type: 'ebay' }
        ]
      })
      
      toast.success('Sync completed successfully!')
      
      // Refresh data after sync
      await fetchData()
      
      return response.data
    } catch (err) {
      console.error('Sync error:', err)
      toast.error('Sync failed. Please try again.')
      throw err
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return {
    dashboardData,
    loading,
    error,
    refreshData,
    runSync
  }
}