'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { TreemapVisualization } from '@/components/TreemapVisualization'
import { Footer } from '@/components/Footer'
import { ThemeToggle } from '@/components/ThemeToggle'

interface Occupation {
  anzsco_code: string
  title: string
  employment: number
  median_pay_aud: number
  ai_exposure: number
  outlook: string
  source: string
  mapping_confidence: number | null
}

export default function Home() {
  const router = useRouter()
  const [occupations, setOccupations] = useState<Occupation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    const API_URL = 'https://taskfolio-au-api.hello-bb8.workers.dev'
    fetch(`${API_URL}/api/occupations`)
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

  const filteredOccupations = useMemo(() => {
    if (!searchQuery.trim()) return []
    const query = searchQuery.toLowerCase()
    return occupations
      .filter(o => 
        o.title.toLowerCase().includes(query) || 
        o.anzsco_code.includes(query)
      )
      .slice(0, 8)
  }, [searchQuery, occupations])

  const handleSelect = (code: string) => {
    setSearchQuery('')
    setShowDropdown(false)
    router.push(`/occupations/${code}`)
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg p-4" role="status" aria-live="polite">
        <div className="card-brutal p-6 brutal-hover">
          <span className="sr-only">Loading</span>
          <p className="font-bold text-lg">Loading occupations...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg p-4" role="alert">
        <div className="card-brutal p-6 bg-danger">
          <p className="font-bold">Error: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-bg">
      <div className="mx-auto max-w-7xl px-3 py-4 sm:px-6 sm:py-8 lg:px-8">
        {/* Hero Header */}
        <header className="mb-4 sm:mb-8 card-brutal p-4 sm:p-6 bg-main">
          <div className="flex justify-between items-start">
            <h1 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-black">
              TASKFOLIO
            </h1>
            <ThemeToggle />
          </div>
          <p className="mt-2 sm:mt-3 text-sm sm:text-lg font-medium text-black">
            See exactly which parts of your job AI will affect — task by task, with timeframes.
          </p>
          
          {/* Search */}
          <div className="mt-4 relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setShowDropdown(true)
              }}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              placeholder="Search occupations... (e.g. Software Developer, Nurse)"
              className="w-full sm:w-96 px-4 py-2 text-sm sm:text-base border-2 border-black bg-white rounded-none focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              aria-label="Search occupations"
              aria-expanded={showDropdown && filteredOccupations.length > 0}
              aria-controls="search-results"
            />
            {showDropdown && filteredOccupations.length > 0 && (
              <ul 
                id="search-results"
                className="absolute z-50 w-full sm:w-96 mt-1 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] max-h-80 overflow-auto"
                role="listbox"
              >
                {filteredOccupations.map((o) => (
                  <li key={o.anzsco_code}>
                    <button
                      onClick={() => handleSelect(o.anzsco_code)}
                      className="w-full px-4 py-3 text-left hover:bg-main/30 focus:bg-main/30 focus:outline-none border-b border-black/10 last:border-b-0"
                      role="option"
                    >
                      <div className="font-bold text-sm">{o.title}</div>
                      <div className="text-xs text-black/60 flex gap-2 mt-1">
                        <span>{o.anzsco_code}</span>
                        <span>•</span>
                        <span className={o.ai_exposure > 0.6 ? 'text-red-600' : o.ai_exposure > 0.3 ? 'text-yellow-600' : 'text-green-600'}>
                          {Math.round(o.ai_exposure * 100)}% AI exposure
                        </span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="mt-3 sm:mt-4 flex flex-wrap gap-2" aria-live="polite">
            <span className="badge-brutal bg-white text-[10px] sm:text-xs">
              {occupations.length} occupations
            </span>
            <span className="badge-brutal bg-white text-[10px] sm:text-xs">
              6,690 tasks
            </span>
            <span className="badge-brutal bg-white text-[10px] sm:text-xs hidden sm:inline-flex">
              Click to explore
            </span>
            <span className="badge-brutal bg-white text-[10px] sm:text-xs sm:hidden">
              Tap to explore
            </span>
          </div>
        </header>

        {/* Disclaimer */}
        <details className="mb-4 sm:mb-6 card-brutal p-3 sm:p-4 bg-gray-50">
          <summary className="cursor-pointer font-bold text-sm sm:text-base text-black/80 hover:text-black">
            ⚠️ About this data & methodology
          </summary>
          <div className="mt-3 space-y-3 text-xs sm:text-sm text-black/70">
            <p>
              <strong>This is a research tool, not a prediction.</strong> TaskFolio visualizes 361 Australian occupations 
              and 6,690 tasks to explore how AI might reshape work. It is not a report, a paper, or career advice — 
              it is a development tool for exploring AI exposure visually.
            </p>
            <p>
              <strong>AI Exposure scores are LLM estimates.</strong> We use data from the{' '}
              <a href="https://www.anthropic.com/research/anthropic-economic-index-january-2026-report" target="_blank" rel="noopener noreferrer" className="link-brutal">
                Anthropic Economic Index
              </a>{' '}
              (1M real AI conversations) combined with{' '}
              <a href="https://www.onetonline.org/" target="_blank" rel="noopener noreferrer" className="link-brutal">
                O*NET
              </a>{' '}
              task descriptions, mapped to Australian ANZSCO occupations. For unmapped occupations, 
              tasks were generated by Claude with Australian regulatory context.
            </p>
            <p>
              <strong>High exposure ≠ job disappears.</strong> Software developers score high because AI is 
              transforming their work — but demand for software could grow as each developer becomes more productive. 
              Scores don't account for demand elasticity, latent demand, regulatory barriers, or social preferences 
              for human workers. Many high-exposure jobs will be <em>reshaped</em>, not replaced.
            </p>
            <p>
              <strong>Employment projections from JSA.</strong> The "Employment Outlook" section uses official 
              10-year projections from{' '}
              <a href="https://www.jobsandskills.gov.au/data/employment-projections" target="_blank" rel="noopener noreferrer" className="link-brutal">
                Jobs and Skills Australia
              </a>{' '}
              (May 2025 → May 2035). These are trend-based projections, not forecasts — they don't yet reflect 
              generative AI's labour market implications.
            </p>
            <p className="text-black/50">
              Full methodology and data sources:{' '}
              <a href="/legal/attribution" className="link-brutal">Attribution</a>
              {' • '}
              <a href="https://github.com/suryast/task-folio/blob/main/docs/METHODOLOGY.md" target="_blank" rel="noopener noreferrer" className="link-brutal">
                METHODOLOGY.md
              </a>
            </p>
          </div>
        </details>

        {/* Treemap Section */}
        <section aria-label="Occupation treemap visualization">
          <TreemapVisualization occupations={occupations} />
        </section>

        {/* Changelog Section */}
        <section className="mt-8 mb-8">
          <div className="card-brutal p-5 sm:p-6">
            <h2 className="text-base sm:text-lg font-black uppercase tracking-wide mb-4 flex items-center gap-2" style={{ color: 'var(--black)' }}>
              <span>🔧</span> Latest Updates
            </h2>
            <div className="space-y-2.5">
              {[
                { date: '2026-03-24', text: 'Added Data Confidence grouping to treemap — see how mapping quality varies across occupations', tag: 'feature' },
                { date: '2026-03-24', text: 'Fixed Data Confidence counts and backfilled scores for 1,362 O*NET tasks', tag: 'fix' },
                { date: '2026-03-24', text: 'Normalized data source labels across D1, frontend, and pipeline', tag: 'fix' },
                { date: '2026-03-21', text: 'Regenerated AU-specific tasks for 62 mis-mapped occupations using O*NET crosswalk', tag: 'data' },
                { date: '2026-03-20', text: 'Added ISCO Triangulation mapping — 92 occupations at high confidence', tag: 'feature' },
              ].map((entry, i) => (
                <div key={i} className="flex gap-2 sm:gap-3 items-start">
                  <span className="font-mono text-[10px] sm:text-xs whitespace-nowrap mt-0.5" style={{ color: 'var(--black)', opacity: 0.45 }}>{entry.date}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 font-bold uppercase rounded-sm border border-current whitespace-nowrap mt-0.5 ${
                    entry.tag === 'fix' ? 'badge-danger' : entry.tag === 'data' ? 'badge-main' : 'badge-success'
                  }`}>{entry.tag}</span>
                  <span className="text-xs sm:text-sm" style={{ color: 'var(--black)', opacity: 0.8 }}>{entry.text}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <Footer />
      </div>
    </main>
  )
}
