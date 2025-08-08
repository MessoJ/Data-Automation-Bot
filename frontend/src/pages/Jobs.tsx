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

export default function JobsPage() {
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
              <button className="btn btn-secondary" onClick={() => alert('Pause/Resume not implemented')}>Pause</button>
            </div>
          ))}
      </div>
    </div>
  )
}