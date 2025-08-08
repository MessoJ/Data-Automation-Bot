import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowRight, 
  CheckCircle, 
  TrendingUp, 
  Shield, 
  Clock,
  Star,
  Play,
  Menu,
  X,
  Zap,
  BarChart3,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState('professional')
  const navigate = useNavigate()

  const handleStartTrial = (plan) => {
    toast.success('?? Starting your free trial!')
    // In a real app, this would handle trial signup
    setTimeout(() => {
      navigate('/onboarding')
    }, 1500)
  }

  const pricingPlans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 99,
      period: 'month',
      description: 'Perfect for small businesses just getting started',
      features: [
        'Up to 2 platforms',
        '1,000 products',
        'Basic sync (hourly)',
        'Email support',
        'Basic analytics'
      ],
      popular: false
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 199,
      period: 'month',
      description: 'Most popular for growing e-commerce businesses',
      features: [
        'Up to 5 platforms',
        '10,000 products',
        'Real-time sync (15min)',
        'Priority support',
        'Advanced analytics',
        'Custom reports',
        'API access'
      ],
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 399,
      period: 'month',
      description: 'For large businesses with complex needs',
      features: [
        'Unlimited platforms',
        'Unlimited products',
        'Instant sync (real-time)',
        'Dedicated support',
        'White-label solution',
        'Custom integrations',
        'SLA guarantee'
      ],
      popular: false
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-info-50">
      {/* Navigation */}
      <nav className="relative z-50 glass backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold text-neutral-800">E-commerce Hub</span>
                <span className="text-xs text-neutral-600">Data Automation</span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-neutral-700 hover:text-primary-600 transition-colors">Features</a>
              <a href="#pricing" className="text-neutral-700 hover:text-primary-600 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-neutral-700 hover:text-primary-600 transition-colors">Testimonials</a>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-secondary text-sm"
              >
                Sign In
              </button>
              <button
                onClick={() => handleStartTrial('professional')}
                className="btn-primary text-sm"
              >
                Start Free Trial
              </button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-md text-neutral-600"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-white/20"
          >
            <div className="px-4 py-4 space-y-4">
              <a href="#features" className="block text-neutral-700 hover:text-primary-600">Features</a>
              <a href="#pricing" className="block text-neutral-700 hover:text-primary-600">Pricing</a>
              <a href="#testimonials" className="block text-neutral-700 hover:text-primary-600">Testimonials</a>
              <button
                onClick={() => navigate('/dashboard')}
                className="block w-full btn-secondary text-sm"
              >
                Sign In
              </button>
              <button
                onClick={() => handleStartTrial('professional')}
                className="block w-full btn-primary text-sm"
              >
                Start Free Trial
              </button>
            </div>
          </motion.div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        {/* Floating Background Shapes */}
        <div className="floating-shape floating-shape-1" />
        <div className="floating-shape floating-shape-2" />
        <div className="floating-shape floating-shape-3" />
        <div className="floating-shape floating-shape-4" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Hero Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-center lg:text-left"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-success-100 text-success-700 rounded-full text-sm font-medium mb-6">
                <Zap className="w-4 h-4" />
                <span>Save 20+ hours per week</span>
              </div>

              <h1 className="text-4xl lg:text-6xl font-bold text-neutral-800 mb-6 leading-tight">
                Automate Your 
                <span className="text-gradient"> E-commerce</span>
                <br />Data Management
              </h1>

              <p className="text-xl text-neutral-600 mb-8 max-w-xl">
                Sync inventory, pricing, and orders across all your sales channels. 
                Increase revenue by 15-25% while saving hours of manual work every week.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleStartTrial('professional')}
                  className="btn-primary text-lg px-8 py-4"
                >
                  Start 14-Day Free Trial
                  <ArrowRight className="w-5 h-5" />
                </motion.button>

                <button className="btn-secondary text-lg px-8 py-4">
                  <Play className="w-5 h-5" />
                  Watch Demo
                </button>
              </div>

              <div className="flex items-center gap-6 text-sm text-neutral-600">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-success-500" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-success-500" />
                  <span>14-day free trial</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-success-500" />
                  <span>Cancel anytime</span>
                </div>
              </div>
            </motion.div>

            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="relative"
            >
              <div className="glass-card p-8 transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-neutral-600">Revenue</span>
                    <span className="text-2xl font-bold text-success-600">+24%</span>
                  </div>
                  <div className="h-2 bg-neutral-200 rounded-full">
                    <div className="h-2 bg-gradient-to-r from-success-400 to-success-600 rounded-full w-3/4"></div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-6">
                    {['Shopify', 'Amazon', 'eBay'].map((platform, i) => (
                      <div key={platform} className="text-center">
                        <div className="w-8 h-8 bg-gradient-to-r from-primary-400 to-primary-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                          <CheckCircle className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-xs text-neutral-600">{platform}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-neutral-800 mb-4">
              Everything you need to automate your e-commerce
            </h2>
            <p className="text-xl text-neutral-600 max-w-3xl mx-auto">
              Our platform connects all your sales channels and keeps everything in perfect sync
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: RefreshCw,
                title: 'Real-time Sync',
                description: 'Automatically sync inventory, pricing, and orders across all platforms every 15 minutes',
                color: 'from-primary-500 to-primary-600'
              },
              {
                icon: BarChart3,
                title: 'Advanced Analytics',
                description: 'Track performance, identify trends, and make data-driven decisions with detailed reports',
                color: 'from-success-500 to-success-600'
              },
              {
                icon: Shield,
                title: 'Enterprise Security',
                description: 'Bank-level encryption and security measures to protect your sensitive business data',
                color: 'from-warning-500 to-warning-600'
              }
            ].map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -8 }}
                  className="card text-center group"
                >
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-neutral-800 mb-4">{feature.title}</h3>
                  <p className="text-neutral-600">{feature.description}</p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-neutral-800 mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-xl text-neutral-600 max-w-3xl mx-auto">
              Start with a 14-day free trial. No credit card required.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8 }}
                className={`card relative ${plan.popular ? 'border-primary-500 shadow-xl shadow-primary-500/25' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-2 rounded-full text-sm font-bold">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center">
                  <h3 className="text-2xl font-bold text-neutral-800 mb-2">{plan.name}</h3>
                  <p className="text-neutral-600 mb-6">{plan.description}</p>
                  
                  <div className="mb-8">
                    <span className="text-4xl font-bold text-neutral-800">${plan.price}</span>
                    <span className="text-neutral-600">/{plan.period}</span>
                  </div>

                  <ul className="text-left space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-success-500 flex-shrink-0" />
                        <span className="text-neutral-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => handleStartTrial(plan.id)}
                    className={`w-full ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    Start Free Trial
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-neutral-800 mb-4">
              Loved by e-commerce businesses
            </h2>
            <p className="text-xl text-neutral-600">
              See what our customers have to say about their results
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: 'Sarah Johnson',
                role: 'CEO, TrendyFashion',
                content: 'This platform saved us 25+ hours per week and increased our revenue by 30%. Game changer!',
                rating: 5,
                avatar: '?????'
              },
              {
                name: 'Mike Chen',
                role: 'Founder, TechGadgets',
                content: 'Finally, all our platforms stay in sync. No more inventory nightmares or lost sales.',
                rating: 5,
                avatar: '?????'
              },
              {
                name: 'Emma Davis',
                role: 'Owner, HomeDecorPlus',
                content: 'The analytics insights helped us identify our best products and optimize pricing strategy.',
                rating: 5,
                avatar: '?????'
              }
            ].map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="card"
              >
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-warning-500 fill-current" />
                  ))}
                </div>
                <p className="text-neutral-700 mb-6 italic">"{testimonial.content}"</p>
                <div className="flex items-center gap-4">
                  <div className="text-3xl">{testimonial.avatar}</div>
                  <div>
                    <div className="font-semibold text-neutral-800">{testimonial.name}</div>
                    <div className="text-sm text-neutral-600">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
              Ready to transform your e-commerce business?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Join thousands of businesses already saving time and increasing revenue
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleStartTrial('professional')}
              className="bg-white text-primary-600 hover:bg-primary-50 font-bold text-lg px-8 py-4 rounded-xl transition-colors inline-flex items-center gap-3"
            >
              Start Your Free Trial Now
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-neutral-900 text-neutral-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-white" />
                </div>
                <span className="text-white font-bold">E-commerce Hub</span>
              </div>
              <p className="text-sm">
                Automate your e-commerce data management and grow your business.
              </p>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-primary-400 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-primary-400 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Privacy</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-primary-400 transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Status</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-neutral-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; 2025 E-commerce Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage