import { Component, type ReactNode } from 'react'

interface ErrorBoundaryState { hasError: boolean; error?: Error }

export default class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }
  static getDerivedStateFromError(error: Error): ErrorBoundaryState { return { hasError: true, error } }
  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-xl mx-auto mt-20 text-center">
          <h1 className="text-2xl font-semibold">Something went wrong.</h1>
          <p className="mt-2 text-neutral-400">{this.state.error?.message ?? 'An unexpected error occurred.'}</p>
        </div>
      )
    }
    return this.props.children
  }
}