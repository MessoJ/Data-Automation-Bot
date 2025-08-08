export default function Onboarding() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold">Onboarding</h1>
      <p className="mt-2 text-neutral-400">Connect your platforms to begin syncing.</p>
      <div className="mt-6 grid gap-3">
        <button className="btn btn-primary">Connect Shopify</button>
        <button className="btn btn-secondary">Connect Amazon</button>
      </div>
    </div>
  )
}