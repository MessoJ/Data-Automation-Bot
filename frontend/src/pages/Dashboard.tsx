import { useEffect, useState } from 'react'

function useApi<T>(endpoint: string, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetch(`/api${endpoint}`)
      .then(async (r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json() })
      .then((j) => { if (!cancelled) setData(j) })
      .catch((e) => { if (!cancelled) setError(e.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  return { data, loading, error }
}

export default function DashboardPage() {
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