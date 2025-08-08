import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import Onboarding from './pages/Onboarding'
import DashboardPage from './pages/Dashboard'
import ReportsPage from './pages/Reports'
import JobsPage from './pages/Jobs'
import ConfigPage from './pages/Config'
import ProductsPage from './pages/Products'

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/landing" element={<LandingPage />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="jobs" element={<JobsPage />} />
            <Route path="config" element={<ConfigPage />} />
            <Route path="products" element={<ProductsPage />} />
          </Route>
        </Routes>
        <Toaster position="top-right" />
      </ErrorBoundary>
    </BrowserRouter>
  )
}
