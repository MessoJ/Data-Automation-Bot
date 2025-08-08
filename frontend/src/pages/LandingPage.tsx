export default function LandingPage() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center">
      <h1 className="text-4xl font-extrabold tracking-tight">E-commerce Data Automation</h1>
      <p className="mt-3 text-neutral-400 max-w-2xl">
        Automate inventory sync and reporting across all your platforms.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <a href="/onboarding" className="btn btn-primary">Get Started</a>
        <a href="/dashboard" className="btn btn-secondary">View Dashboard</a>
      </div>
    </div>
  )
}