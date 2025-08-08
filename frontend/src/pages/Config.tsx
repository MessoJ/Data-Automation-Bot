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

export default function ConfigPage() {
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