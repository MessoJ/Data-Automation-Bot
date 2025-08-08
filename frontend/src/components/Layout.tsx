import { NavLink, Outlet } from 'react-router-dom'

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 rounded-lg transition ${isActive ? 'bg-brand/15 text-brand' : 'text-neutral-300 hover:text-white hover:bg-neutral-800'}`
      }
    >
      {label}
    </NavLink>
  )
}

export default function Layout() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="sticky top-0 z-10 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="font-bold text-lg">E-commerce Hub</div>
          <nav className="flex gap-1">
            <NavItem to="/dashboard" label="Dashboard" />
            <NavItem to="/reports" label="Reports" />
            <NavItem to="/jobs" label="Jobs" />
            <NavItem to="/config" label="Settings" />
            <NavItem to="/products" label="Products" />
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}