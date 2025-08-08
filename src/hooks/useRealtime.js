import { useState, useEffect } from 'react'

export const useRealtime = () => {
  const [isConnected, setIsConnected] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    // Simulate real-time connection status
    const interval = setInterval(() => {
      setLastUpdate(new Date())
      
      // Simulate occasional connection issues (5% chance)
      if (Math.random() < 0.05) {
        setIsConnected(false)
        setTimeout(() => setIsConnected(true), 2000)
      }
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  return {
    isConnected,
    lastUpdate
  }
}