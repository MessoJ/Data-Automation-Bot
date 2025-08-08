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

export default function ProductsPage() {
  const { data, loading } = useApi<any>('/products', [])
  const [name, setName] = useState('')
  const [sku, setSku] = useState('')
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Products</h1>
        <div className="flex gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="bg-neutral-900 border border-neutral-800 rounded px-3 py-2" />
          <input value={sku} onChange={(e) => setSku(e.target.value)} placeholder="SKU" className="bg-neutral-900 border border-neutral-800 rounded px-3 py-2" />
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