import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Jobs from './pages/Jobs'
import Config from './pages/Config'
import Onboarding from './pages/Onboarding'
import LandingPage from './pages/LandingPage'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Routes>
            {/* Landing Page - No Layout */}
            <Route path="/landing" element={<LandingPage />} />
            <Route path="/onboarding" element={<Onboarding />} />
            
            {/* Dashboard Routes - With Layout */}
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="reports" element={<Reports />} />
              <Route path="jobs" element={<Jobs />} />
              <Route path="config" element={<Config />} />
            </Route>
          </Routes>
          
          {/* Global Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#ffffff',
                color: '#1e293b',
                boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                border: '1px solid #e2e8f0',
                borderRadius: '0.75rem',
                padding: '1rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
              },
              success: {
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#ffffff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#ffffff',
                },
              },
            }}
          />
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App