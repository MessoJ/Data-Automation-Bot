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

export default function ReportsPage() {
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