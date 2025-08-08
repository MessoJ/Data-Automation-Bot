import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft, 
  Zap,
  Store,
  RefreshCw,
  AlertTriangle,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'

const Onboarding = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedPlatforms, setSelectedPlatforms] = useState([])
  const navigate = useNavigate()

  const platforms = [
    {
      id: 'shopify',
      name: 'Shopify',
      description: 'Sync your online store inventory and orders',
      icon: '???',
      color: 'from-green-400 to-green-500'
    },
    {
      id: 'amazon',
      name: 'Amazon',
      description: 'Manage your Amazon seller inventory',
      icon: '??',
      color: 'from-orange-400 to-orange-500'
    },
    {
      id: 'ebay',
      name: 'eBay',
      description: 'Sync your eBay listings and inventory',
      icon: '??',
      color: 'from-blue-400 to-blue-500'
    },
    {
      id: 'woocommerce',
      name: 'WooCommerce',
      description: 'Connect your WordPress store',
      icon: '??',
      color: 'from-purple-400 to-purple-500'
    }
  ]

  const togglePlatform = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    )
  }

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const completeTrial = () => {
    toast.success('?? Welcome to your E-commerce Command Center!')
    setTimeout(() => {
      navigate('/')
    }, 1500)
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <WelcomeStep onNext={nextStep} />
      case 2:
        return (
          <PlatformSelectionStep
            platforms={platforms}
            selectedPlatforms={selectedPlatforms}
            togglePlatform={togglePlatform}
            onNext={nextStep}
            onPrev={prevStep}
          />
        )
      case 3:
        return (
          <CompletionStep
            selectedPlatforms={selectedPlatforms}
            platforms={platforms}
            onComplete={completeTrial}
            onPrev={prevStep}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-info-50 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Floating Background Shapes */}
      <div className="floating-shape floating-shape-1" />
      <div className="floating-shape floating-shape-2" />
      <div className="floating-shape floating-shape-3" />
      <div className="floating-shape floating-shape-4" />

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-4xl">
        {renderStep()}

        {/* Progress Indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-8 left-1/2 transform -translate-x-1/2"
        >
          <div className="glass-card px-6 py-4">
            <div className="flex items-center gap-8 mb-4">
              {[1, 2, 3].map((step) => (
                <div key={step} className="flex flex-col items-center gap-2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                    step < currentStep ? 'bg-success-500 text-white' :
                    step === currentStep ? 'bg-primary-500 text-white' :
                    'bg-neutral-300 text-neutral-600'
                  }`}>
                    {step < currentStep ? <CheckCircle className="w-5 h-5" /> : step}
                  </div>
                  <span className="text-xs font-medium text-neutral-600">
                    {step === 1 ? 'Welcome' : step === 2 ? 'Connect' : 'Complete'}
                  </span>
                </div>
              ))}
            </div>
            <div className="w-48 h-1 bg-neutral-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '33%' }}
                animate={{ width: `${(currentStep / 3) * 100}%` }}
                transition={{ duration: 0.3 }}
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

// Welcome Step Component
const WelcomeStep = ({ onNext }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    className="glass-card p-12 text-center"
  >
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.2 }}
      className="text-8xl mb-6"
    >
      ??
    </motion.div>
    
    <h1 className="text-4xl font-bold text-neutral-800 mb-4">
      Welcome to Your E-commerce Command Center!
    </h1>
    
    <p className="text-xl text-neutral-600 mb-8 max-w-2xl mx-auto">
      You're about to save 20+ hours per week and increase your revenue by 15-25%. 
      Let's get your platforms connected in just 3 simple steps.
    </p>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {[
        { icon: '?', text: 'Real-time inventory sync' },
        { icon: '??', text: 'Automatic price corrections' },
        { icon: '??', text: 'Advanced analytics dashboard' }
      ].map((benefit, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 + index * 0.1 }}
          className="flex items-center gap-3 p-4 bg-white/50 rounded-xl"
        >
          <span className="text-2xl">{benefit.icon}</span>
          <span className="font-medium text-neutral-800">{benefit.text}</span>
        </motion.div>
      ))}
    </div>

    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onNext}
      className="btn-primary text-lg px-8 py-4"
    >
      Let's Get Started!
      <ArrowRight className="w-5 h-5" />
    </motion.button>
  </motion.div>
)

// Platform Selection Step Component
const PlatformSelectionStep = ({ platforms, selectedPlatforms, togglePlatform, onNext, onPrev }) => (
  <motion.div
    initial={{ opacity: 0, x: 100 }}
    animate={{ opacity: 1, x: 0 }}
    className="glass-card p-12"
  >
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-neutral-800 mb-4">
        Connect Your E-commerce Platforms
      </h2>
      <p className="text-lg text-neutral-600">
        Select the platforms you want to sync. You can always add more later.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {platforms.map((platform) => {
        const isSelected = selectedPlatforms.includes(platform.id)
        return (
          <motion.div
            key={platform.id}
            whileHover={{ y: -4, scale: 1.02 }}
            onClick={() => togglePlatform(platform.id)}
            className={`relative p-6 rounded-2xl border-2 cursor-pointer transition-all ${
              isSelected 
                ? 'border-primary-500 bg-primary-50 shadow-lg shadow-primary-500/25' 
                : 'border-neutral-200 bg-white/80 hover:border-primary-300'
            }`}
          >
            <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${platform.color} flex items-center justify-center text-2xl mb-4 mx-auto`}>
              {platform.icon}
            </div>
            <h3 className="text-xl font-bold text-neutral-800 text-center mb-2">
              {platform.name}
            </h3>
            <p className="text-neutral-600 text-center text-sm mb-4">
              {platform.description}
            </p>
            <div className="flex items-center justify-center gap-2">
              <div className={`w-3 h-3 rounded-full transition-all ${
                isSelected ? 'bg-success-500 animate-pulse' : 'bg-neutral-400'
              }`} />
              <span className="text-sm font-medium">
                {isSelected ? 'Connected' : 'Click to connect'}
              </span>
            </div>
            {isSelected && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-2 -right-2 w-8 h-8 bg-success-500 rounded-full flex items-center justify-center"
              >
                <CheckCircle className="w-5 h-5 text-white" />
              </motion.div>
            )}
          </motion.div>
        )
      })}
    </div>

    <div className="flex items-center justify-center gap-4">
      <button onClick={onPrev} className="btn-secondary">
        <ArrowLeft className="w-5 h-5" />
        Back
      </button>
      <button
        onClick={onNext}
        disabled={selectedPlatforms.length === 0}
        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Continue with {selectedPlatforms.length} Platform{selectedPlatforms.length !== 1 ? 's' : ''}
        <ArrowRight className="w-5 h-5" />
      </button>
    </div>
  </motion.div>
)

// Completion Step Component
const CompletionStep = ({ selectedPlatforms, platforms, onComplete, onPrev }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="glass-card p-12 text-center"
  >
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.2 }}
      className="text-8xl mb-6"
    >
      ?
    </motion.div>

    <h2 className="text-3xl font-bold text-neutral-800 mb-4">
      You're All Set!
    </h2>
    
    <p className="text-lg text-neutral-600 mb-8">
      Your platforms are connected and syncing. Here's what you can expect:
    </p>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {[
        {
          icon: RefreshCw,
          title: 'Automatic Syncing',
          description: 'Your inventory updates every 15 minutes across all platforms'
        },
        {
          icon: AlertTriangle,
          title: 'Smart Alerts',
          description: 'Get notified instantly when discrepancies are found'
        },
        {
          icon: BarChart3,
          title: 'Performance Insights',
          description: 'Track revenue and identify your best-performing products'
        }
      ].map((feature, index) => {
        const Icon = feature.icon
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + index * 0.1 }}
            className="p-6 bg-white/80 rounded-xl"
          >
            <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
              <Icon className="w-6 h-6 text-white" />
            </div>
            <h4 className="font-bold text-neutral-800 mb-2">{feature.title}</h4>
            <p className="text-sm text-neutral-600">{feature.description}</p>
          </motion.div>
        )
      })}
    </div>

    <div className="flex items-center justify-center gap-4">
      <button onClick={onPrev} className="btn-secondary">
        <ArrowLeft className="w-5 h-5" />
        Back
      </button>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onComplete}
        className="btn-primary text-lg px-8 py-4"
      >
        Go to Dashboard
        <Store className="w-5 h-5" />
      </motion.button>
    </div>

    <div className="mt-8 pt-8 border-t border-neutral-200">
      <p className="text-neutral-600 mb-4">Need help getting started?</p>
      <div className="flex items-center justify-center gap-4">
        <button className="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-primary-600 transition-colors">
          ?? Contact Support
        </button>
        <button className="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-primary-600 transition-colors">
          ?? View Guide
        </button>
      </div>
    </div>
  </motion.div>
)

export default Onboarding