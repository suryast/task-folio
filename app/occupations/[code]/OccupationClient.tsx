'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Footer } from '@/components/Footer'

interface Task {
  description: string
  automation_pct: number | null
  augmentation_pct: number | null
  speedup_factor: number | null
  timeframe: string
  source: string
}

interface Occupation {
  title: string
  employment: number
  median_pay_aud: number
  ai_exposure_weighted: number
  outlook: string
}

interface JSAProjection {
  baseline_2025: number
  projected_2030: number
  projected_2035: number
  growth_5yr_pct: number
  growth_10yr_pct: number
}

// Calculate composite index (0-100): combines exposure risk with opportunity factors
// Formula: 100 - (AI_exposure × 40) - pay_risk - outlook_risk
// - AI exposure (40 pts max): higher exposure = more risk
// - Pay risk (30 pts max): lower pay = more vulnerable to displacement
// - Outlook risk (30 pts max): negative growth = more risk
function calculateCompositeIndex(
  occ: Occupation, 
  projection: JSAProjection | null
): { score: number; label: string; badgeClass: string } {
  // AI exposure risk: 0-40 points (higher exposure = higher risk)
  const exposureRisk = (occ.ai_exposure_weighted || 0) * 40
  
  // Pay risk: 0-30 points (lower pay = higher risk of displacement)
  // $40K = 30 pts risk, $200K+ = 0 pts risk
  const payNormalized = Math.min(30, Math.max(0, ((occ.median_pay_aud || 60000) - 40000) / 160000 * 30))
  const payRisk = 30 - payNormalized

  // Outlook risk: 0-30 points based on JSA 10-year growth projection
  // +20% growth = 0 pts, 0% = 15 pts, -10% = 30 pts
  let outlookRisk = 15 // default if no data
  if (projection) {
    const growth = projection.growth_10yr_pct
    // Map: +20% → 0, 0% → 15, -10% → 30
    outlookRisk = Math.max(0, Math.min(30, 15 - (growth * 0.75)))
  }

  const totalRisk = Math.round(exposureRisk + payRisk + outlookRisk)
  const score = Math.max(0, Math.min(100, 100 - totalRisk))
  
  const label = score >= 70 ? 'FUTURE-PROOF' : score >= 50 ? 'ADAPTABLE' : score >= 30 ? 'AT RISK' : 'VULNERABLE'
  const badgeClass = score >= 70 ? 'badge-success' : score >= 50 ? 'badge-warning' : score >= 30 ? 'badge-warning' : 'badge-danger'
  
  return { score, label, badgeClass }
}

const API_URL = 'https://taskfolio-au-api.hello-bb8.workers.dev'

export default function OccupationClient() {
  const [occupation, setOccupation] = useState<Occupation | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [projection, setProjection] = useState<JSAProjection | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = typeof window !== 'undefined' 
      ? window.location.pathname.split('/').filter(Boolean).pop() 
      : null

    if (!code) {
      setError('Invalid code')
      setLoading(false)
      return
    }

    Promise.all([
      fetch(`${API_URL}/api/occupations/${code}`),
      fetch(`${API_URL}/api/tasks/${code}`),
      fetch('/data/jsa_projections.json')
    ])
      .then(async ([occRes, tasksRes, projRes]) => {
        if (!occRes.ok || !tasksRes.ok) throw new Error('Load failed')
        const [occ, tasksData] = await Promise.all([occRes.json(), tasksRes.json()])
        setOccupation(occ)
        setTasks(tasksData.tasks || [])
        
        // Load JSA projections
        if (projRes.ok) {
          const projections = await projRes.json()
          setProjection(projections[code] || null)
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex min-h-screen items-center justify-center bg-bg" role="status" aria-live="polite">
      <div className="card-brutal p-6 brutal-hover">
        <span className="sr-only">Loading occupation data</span>
        <p className="font-bold text-lg">Loading...</p>
      </div>
    </div>
  )
  
  if (error || !occupation) return (
    <div className="flex min-h-screen items-center justify-center bg-bg flex-col gap-4" role="alert">
      <div className="card-brutal p-6 bg-danger">
        <p className="font-bold">Occupation not found</p>
      </div>
      <Link href="/" className="btn-brutal focus-brutal">
        ← Back to home
      </Link>
    </div>
  )

  const tasksByTimeframe = tasks.reduce((acc, t) => {
    const tf = t.timeframe || 'unknown'
    if (!acc[tf]) acc[tf] = []
    acc[tf].push(t)
    return acc
  }, {} as Record<string, Task[]>)

  const timeframeBadges: Record<string, string> = {
    'now': 'badge-danger',
    '1-2y': 'badge-danger',
    '3-5y': 'badge-warning',
    '5-10y': 'badge-main',
    '10y+': 'badge-success',
  }

  const timeframeLabels: Record<string, string> = {
    'now': 'NOW — Already happening',
    '1-2y': '1-2 YEARS — Early deployment',
    '3-5y': '3-5 YEARS — Mainstream adoption',
    '5-10y': '5-10 YEARS — Significant barriers',
    '10y+': '10+ YEARS — Fundamental constraints',
  }

  const exposureScore = Math.round((occupation.ai_exposure_weighted || 0) * 100)
  const halfLife = Math.round(2 + (1 - (occupation.ai_exposure_weighted || 0)) * 18)
  const composite = calculateCompositeIndex(occupation, projection)

  const getExposureBadge = () => {
    if (exposureScore >= 80) return 'badge-danger'
    if (exposureScore >= 50) return 'badge-warning'
    return 'badge-success'
  }

  return (
    <main className="min-h-screen bg-bg">
      <div className="max-w-5xl mx-auto px-3 py-4 sm:px-4 sm:py-8">
        {/* Back navigation */}
        <nav aria-label="Breadcrumb">
          <Link href="/" className="btn-brutal-neutral text-xs sm:text-sm focus-brutal">
            <span aria-hidden="true">←</span> Back
          </Link>
        </nav>
        
        {/* Title */}
        <h1 className="text-xl sm:text-3xl lg:text-4xl font-extrabold mt-4 sm:mt-6 text-black tracking-tight leading-tight">
          {occupation.title.toUpperCase()}
        </h1>
        
        {/* Metric Cards Row */}
        <section aria-label="Key metrics" className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-4 sm:mt-6">
          {/* AI Exposure */}
          <article className="card-brutal p-4 sm:p-5" aria-labelledby="exposure-label">
            <div className="flex items-center justify-between">
              <div>
                <span id="exposure-label" className="text-xs sm:text-sm font-bold text-black/70">AI EXPOSURE</span>
                <p className="text-3xl sm:text-5xl font-extrabold text-black mt-1" aria-label={`AI Exposure Score: ${exposureScore} out of 100`}>
                  {exposureScore}
                  <span className="text-base sm:text-xl font-bold text-black/50" aria-hidden="true">/100</span>
                </p>
              </div>
              <span className={`${getExposureBadge()} text-[10px] sm:text-xs`}>
                {exposureScore >= 80 ? 'HIGH' : exposureScore >= 50 ? 'MED' : 'LOW'}
              </span>
            </div>
            <p className="text-[10px] sm:text-xs font-medium text-black/60 mt-2 sm:mt-3">
              Tasks AI can automate or augment.
            </p>
          </article>

          {/* Half-Life */}
          <article className="card-brutal p-4 sm:p-5 bg-main" aria-labelledby="halflife-label">
            <div className="flex items-center justify-between">
              <div>
                <span id="halflife-label" className="text-xs sm:text-sm font-bold text-black/70">HALF-LIFE</span>
                <p className="text-3xl sm:text-5xl font-extrabold text-black mt-1" aria-label={`Estimated Half-Life: ${halfLife} years`}>
                  {halfLife}
                  <span className="text-base sm:text-xl font-bold text-black/50" aria-hidden="true"> yrs</span>
                </p>
              </div>
              <span className="text-2xl sm:text-4xl" aria-hidden="true">⏳</span>
            </div>
            <p className="text-[10px] sm:text-xs font-medium text-black/60 mt-2 sm:mt-3">
              Time until AI can do ~50% of tasks.
            </p>
          </article>

          {/* Future-Proof Index */}
          <article className="card-brutal p-4 sm:p-5" aria-labelledby="futureproof-label">
            <div className="flex items-center justify-between">
              <div>
                <span id="futureproof-label" className="text-xs sm:text-sm font-bold text-black/70">FUTURE-PROOF</span>
                <p className="text-3xl sm:text-5xl font-extrabold text-black mt-1" aria-label={`Future-Proof Index: ${composite.score} out of 100`}>
                  {composite.score}
                  <span className="text-base sm:text-xl font-bold text-black/50" aria-hidden="true">/100</span>
                </p>
              </div>
              <span className={`${composite.badgeClass} text-[10px] sm:text-xs`}>
                {composite.label}
              </span>
            </div>
            <p className="text-[10px] sm:text-xs font-medium text-black/60 mt-2 sm:mt-3">
              Exposure + pay + outlook.
            </p>
          </article>
        </section>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 mt-3 sm:mt-4">
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: '#e8f4fa' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">EMPLOYMENT</span>
            <p className="text-sm sm:text-lg font-bold text-black">{occupation.employment?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: '#e8f4fa' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">MEDIAN PAY</span>
            <p className="text-sm sm:text-lg font-bold text-black">${occupation.median_pay_aud?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: '#e8f4fa' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">TASKS</span>
            <p className="text-sm sm:text-lg font-bold text-black">{tasks.length}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: '#e8f4fa' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">SOURCE</span>
            <p className="text-sm sm:text-lg font-bold text-black">ABS+Anthropic</p>
          </div>
        </div>

        {/* Employment Outlook */}
        {projection && (
          <section aria-label="Employment outlook" className="mt-6 sm:mt-8">
            <h2 className="text-xl sm:text-2xl font-extrabold text-black">EMPLOYMENT OUTLOOK</h2>
            <p className="mt-1 sm:mt-2 text-sm sm:text-base font-medium text-black/70">
              10-year employment projections from Jobs and Skills Australia
            </p>
            
            <div className="card-brutal p-4 sm:p-5 mt-3 sm:mt-4">
              {/* Growth indicator */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-xs sm:text-sm font-bold text-black/70">10-YEAR GROWTH</span>
                  <p className={`text-3xl sm:text-4xl font-extrabold ${
                    projection.growth_10yr_pct >= 15 ? 'text-green-600' :
                    projection.growth_10yr_pct >= 5 ? 'text-yellow-600' :
                    projection.growth_10yr_pct >= 0 ? 'text-black' : 'text-red-600'
                  }`}>
                    {projection.growth_10yr_pct >= 0 ? '+' : ''}{projection.growth_10yr_pct}%
                  </p>
                </div>
                <span className={`badge-brutal text-xs ${
                  projection.growth_10yr_pct >= 15 ? 'bg-green-100' :
                  projection.growth_10yr_pct >= 5 ? 'bg-yellow-100' :
                  projection.growth_10yr_pct >= 0 ? 'bg-gray-100' : 'bg-red-100'
                }`}>
                  {projection.growth_10yr_pct >= 15 ? 'STRONG GROWTH' :
                   projection.growth_10yr_pct >= 5 ? 'MODERATE GROWTH' :
                   projection.growth_10yr_pct >= 0 ? 'STABLE' : 'DECLINING'}
                </span>
              </div>
              
              {/* Timeline */}
              <div className="grid grid-cols-3 gap-2 sm:gap-4 text-center">
                <div className="card-brutal p-2 sm:p-3 bg-gray-50">
                  <span className="text-[10px] sm:text-xs font-bold text-black/60">2025</span>
                  <p className="text-sm sm:text-lg font-bold text-black">
                    {(projection.baseline_2025 / 1000).toFixed(0)}K
                  </p>
                </div>
                <div className="card-brutal p-2 sm:p-3 bg-gray-50">
                  <span className="text-[10px] sm:text-xs font-bold text-black/60">2030</span>
                  <p className="text-sm sm:text-lg font-bold text-black">
                    {(projection.projected_2030 / 1000).toFixed(0)}K
                  </p>
                  <span className="text-[9px] sm:text-xs text-black/50">
                    ({projection.growth_5yr_pct >= 0 ? '+' : ''}{projection.growth_5yr_pct}%)
                  </span>
                </div>
                <div className="card-brutal p-2 sm:p-3 bg-main">
                  <span className="text-[10px] sm:text-xs font-bold text-black/60">2035</span>
                  <p className="text-sm sm:text-lg font-bold text-black">
                    {(projection.projected_2035 / 1000).toFixed(0)}K
                  </p>
                  <span className="text-[9px] sm:text-xs text-black/50">
                    ({projection.growth_10yr_pct >= 0 ? '+' : ''}{projection.growth_10yr_pct}%)
                  </span>
                </div>
              </div>
              
              {/* Growth bar */}
              <div className="mt-4">
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden border-2 border-black">
                  <div 
                    className={`h-full transition-all ${
                      projection.growth_10yr_pct >= 15 ? 'bg-green-500' :
                      projection.growth_10yr_pct >= 5 ? 'bg-yellow-500' :
                      projection.growth_10yr_pct >= 0 ? 'bg-gray-400' : 'bg-red-500'
                    }`}
                    style={{ 
                      width: `${Math.min(100, Math.max(5, 50 + projection.growth_10yr_pct * 2))}%` 
                    }}
                  />
                </div>
              </div>
              
              <p className="text-[10px] sm:text-xs text-black/50 mt-3">
                Source: Jobs and Skills Australia, May 2025 → May 2035 projections
              </p>
            </div>
          </section>
        )}

        {/* Task Breakdown */}
        <section aria-label="Task breakdown by timeframe" className="mt-6 sm:mt-8">
          <h2 className="text-xl sm:text-2xl font-extrabold text-black">TASK BREAKDOWN</h2>
          <p className="mt-1 sm:mt-2 text-sm sm:text-base font-medium text-black/70">Which tasks AI will affect and when</p>

          {['now', '1-2y', '3-5y', '5-10y', '10y+'].map(tf => {
            const tfTasks = tasksByTimeframe[tf]
            if (!tfTasks?.length) return null
            return (
              <div key={tf} className="mt-4 sm:mt-6" role="region" aria-label={`${timeframeLabels[tf]} - ${tfTasks.length} tasks`}>
                {/* Timeframe header */}
                <div className={`card-brutal p-2 sm:p-3 ${timeframeBadges[tf].replace('badge-', 'bg-')}`}>
                  <h3 className="font-bold text-black flex flex-wrap items-center gap-2 sm:gap-3 text-sm sm:text-base">
                    <span className="hidden sm:inline">{timeframeLabels[tf]}</span>
                    <span className="sm:hidden">{tf.toUpperCase()}</span>
                    <span className="badge-brutal bg-white shadow-none text-[10px] sm:text-xs">{tfTasks.length}</span>
                  </h3>
                </div>
                
                {/* Task list */}
                <ul className="space-y-2 sm:space-y-3 mt-2 sm:mt-3" role="list">
                  {tfTasks.map((t, i) => (
                    <li key={i} className="card-brutal p-3 sm:p-4 brutal-hover">
                      <p className="font-medium text-black text-sm sm:text-base">{t.description}</p>
                      <div className="mt-2 sm:mt-3 flex flex-wrap gap-1.5 sm:gap-2">
                        {t.automation_pct !== null && (
                          <span className="badge-brutal bg-white shadow-none text-[10px] sm:text-xs px-2">
                            Auto: {(t.automation_pct*100).toFixed(0)}%
                          </span>
                        )}
                        {t.augmentation_pct !== null && (
                          <span className="badge-brutal bg-white shadow-none text-[10px] sm:text-xs px-2">
                            Aug: {(t.augmentation_pct*100).toFixed(0)}%
                          </span>
                        )}
                        {t.speedup_factor !== null && (
                          <span className="badge-brutal bg-white shadow-none text-[10px] sm:text-xs px-2">
                            {t.speedup_factor.toFixed(1)}x
                          </span>
                        )}
                        <span className="badge-main text-[10px] sm:text-xs px-2">
                          {t.source}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </section>

        {/* Footer */}
        <Footer />
      </div>
    </main>
  )
}
