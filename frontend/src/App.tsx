import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'

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

function useApi<T>(endpoint: string, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetch(`/api${endpoint}`)
      .then(async (r) => {
        if (!r.ok) throw new Error(`${r.status}`)
        return r.json()
      })
      .then((j) => { if (!cancelled) setData(j) })
      .catch((e) => { if (!cancelled) setError(e.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  return { data, loading, error }
}

function DashboardPage() {
  const { data, loading } = useApi<any>('/status', [])
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-sm text-neutral-400">Database</div>
          <div className="text-3xl font-bold">{loading ? '—' : data?.database?.total_records ?? 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-400">Scheduler</div>
          <div className="text-3xl font-bold">{loading ? '—' : (data?.scheduler?.running ? 'Running' : 'Stopped')}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-400">Unread Notifications</div>
          <div className="text-3xl font-bold">{loading ? '—' : data?.notifications?.unread ?? 0}</div>
        </div>
      </div>
    </div>
  )
}

function ReportsPage() {
  const { data, loading } = useApi<any>('/reports', [])
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Reports</h1>
        <button className="btn btn-primary" onClick={async () => {
          await fetch('/api/reports/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ report_type: 'daily', format: 'html' }) })
          location.reload()
        }}>Generate Daily</button>
      </div>
      <div className="grid gap-3">
        {loading ? <div className="text-neutral-400">Loading…</div> :
          (data?.reports ?? []).map((r: any) => (
            <div key={r.filename} className="card p-4 flex items-center justify-between">
              <div>
                <div className="font-medium">{r.filename}</div>
                <div className="text-xs text-neutral-400">{new Date(r.modified).toLocaleString()}</div>
              </div>
              <a className="btn btn-secondary" href={`/api/reports/download/${r.filename}`}>Download</a>
            </div>
          ))}
      </div>
    </div>
  )
}

function JobsPage() {
  const { data, loading } = useApi<any>('/jobs', [])
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Jobs</h1>
      <div className="grid gap-3">
        {loading ? <div className="text-neutral-400">Loading…</div> :
          (data?.jobs ?? []).map((j: any) => (
            <div key={j.id} className="card p-4 flex items-center justify-between">
              <div>
                <div className="font-medium">{j.name ?? j.id}</div>
                <div className="text-xs text-neutral-400">Next: {j.next_run ? new Date(j.next_run).toLocaleString() : '—'}</div>
              </div>
              <button className="btn btn-secondary" onClick={async () => {
                try {
                  await fetch(`/api/jobs/${j.id}/${j.paused ? 'resume' : 'pause'}`, { method: 'POST' })
                  location.reload()
                } catch (e) {
                  alert('Action failed')
                }
              }}>{j.paused ? 'Resume' : 'Pause'}</button>
            </div>
          ))}
      </div>
    </div>
  )
}

function ConfigPage() {
  const { data, loading } = useApi<any>('/config', [])
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <div className="card p-4 grid sm:grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-neutral-400">API Base URL</div>
          <div className="font-medium">{loading ? '—' : data?.api?.base_url}</div>
        </div>
      <div>
          <div className="text-sm text-neutral-400">Report Dir</div>
          <div className="font-medium">{loading ? '—' : data?.reporting?.output_dir}</div>
        </div>
      </div>
    </div>
  )
}

function ProductsPage() {
  const { data, loading } = useApi<any>('/products', [])
  const [name, setName] = useState('')
  const [sku, setSku] = useState('')
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Products</h1>
        <div className="flex gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="input" />
          <input value={sku} onChange={(e) => setSku(e.target.value)} placeholder="SKU" className="input" />
          <button className="btn btn-primary" onClick={async () => {
            await fetch('/api/products', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, sku }) })
            setName(''); setSku(''); location.reload()
          }}>Add</button>
        </div>
      </div>
      <div className="grid gap-3">
        {loading ? <div className="text-neutral-400">Loading…</div> :
          (data?.products ?? []).map((p: any) => (
            <div key={p.id} className="card p-4 flex items-center justify-between">
              <div>
                <div className="font-medium">{p.name}</div>
                <div className="text-xs text-neutral-400">SKU: {p.sku}</div>
              </div>
            </div>
          ))}
      </div>
    </div>
  )
}

function ThemeToggle() {
  const [dark, setDark] = useState<boolean>(() => document.documentElement.classList.contains('dark'))
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try { localStorage.setItem('theme', dark ? 'dark' : 'light') } catch {}
  }, [dark])
  return (
    <button className="btn btn-secondary" onClick={() => setDark((d) => !d)}>
      {dark ? 'Light' : 'Dark'}
    </button>
  )
}

function Layout() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="sticky top-0 z-10 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="font-bold text-lg">E-commerce Hub</div>
          <nav className="flex gap-1">
            <NavItem to="/" label="Dashboard" />
            <NavItem to="/reports" label="Reports" />
            <NavItem to="/jobs" label="Jobs" />
            <NavItem to="/config" label="Settings" />
            <NavItem to="/products" label="Products" />
          </nav>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/config" element={<ConfigPage />} />
          <Route path="/products" element={<ProductsPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
