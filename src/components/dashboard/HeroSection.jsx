import { motion } from 'framer-motion'
import { User, TrendingUp, Zap } from 'lucide-react'

const HeroSection = ({ onQuickSync, syncInProgress, isConnected }) => {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-8 relative overflow-hidden"
    >
      {/* Background Shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="floating-shape floating-shape-1" />
        <div className="floating-shape floating-shape-2" />
        <div className="floating-shape floating-shape-3" />
        <div className="floating-shape floating-shape-4" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex items-center justify-between">
        {/* Left Side - Main Content */}
        <div className="flex items-center gap-8">
          {/* User Greeting */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center border-3 border-white/80 shadow-lg">
                <User className="w-8 h-8 text-white" />
              </div>
              {isConnected && (
                <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-success-500 border-2 border-white rounded-full animate-pulse" />
              )}
            </div>
            
            <div>
              <h1 className="text-3xl font-bold text-neutral-800 mb-1">
                Welcome back, <span className="text-gradient">Alex</span>! ??
              </h1>
              <p className="text-lg text-neutral-600 font-medium">
                Your e-commerce empire is thriving today
              </p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex gap-6">
            <div className="flex items-center gap-3 px-4 py-3 bg-white/60 backdrop-blur-sm border border-white/20 rounded-xl">
              <div className="w-10 h-10 bg-gradient-to-r from-success-400 to-success-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-lg font-bold text-neutral-800">+24%</div>
                <div className="text-sm text-neutral-600">Revenue Growth</div>
              </div>
            </div>
            
            <div className="flex items-center gap-3 px-4 py-3 bg-white/60 backdrop-blur-sm border border-white/20 rounded-xl">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-400 to-primary-500 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-lg font-bold text-neutral-800">All Synced</div>
                <div className="text-sm text-neutral-600">Platform Status</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Actions */}
        <div className="flex items-center gap-4">
          <motion.button
            onClick={onQuickSync}
            disabled={syncInProgress}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`btn-primary btn-glow ${syncInProgress ? 'animate-pulse-glow' : ''}`}
          >
            <Zap className={`w-5 h-5 ${syncInProgress ? 'animate-spin' : ''}`} />
            <span>{syncInProgress ? 'Syncing...' : 'Quick Sync'}</span>
          </motion.button>
          
          <button className="btn-secondary">
            <TrendingUp className="w-5 h-5" />
            <span>Analytics</span>
          </button>
        </div>
      </div>
    </motion.section>
  )
}

export default HeroSection