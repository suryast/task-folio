'use client'

import { useEffect, useState } from 'react'
import { TreemapVisualization } from '@/components/TreemapVisualization'

interface Occupation {
  anzsco_code: string
  title: string
  employment: number
  median_pay_aud: number
  ai_exposure: number
  outlook: string
  source: string
}

export default function Home() {
  const [occupations, setOccupations] = useState<Occupation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/occupations')
      .then(res => res.json())
      .then(data => {
        setOccupations(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="text-zinc-600 dark:text-zinc-400">Loading occupations...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="text-red-600">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-4xl">
            TaskFolio
          </h1>
          <p className="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
            See exactly which parts of your job AI will affect — task by task, with timeframes.
          </p>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-500">
            {occupations.length} Australian occupations analyzed • Click to explore
          </p>
        </header>

        <TreemapVisualization occupations={occupations} />

        <footer className="mt-8 text-center text-sm text-zinc-500 dark:text-zinc-500">
          <p>
            Data: Australian Bureau of Statistics (ANZSCO) + Anthropic Economic Index (1M conversations)
          </p>
          <p className="mt-1">
            Built with Next.js, Cloudflare D1, and Claude Sonnet 4.5
          </p>
        </footer>
      </div>
    </div>
  )
}
