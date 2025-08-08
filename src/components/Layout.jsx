import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useAuth } from '../hooks/useAuth'

const Layout = () => {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-info-50">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header user={user} />
          
          {/* Page Content */}
          <main className="flex-1 p-6 overflow-auto">
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Layout