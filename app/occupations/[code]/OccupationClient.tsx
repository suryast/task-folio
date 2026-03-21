'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import { Footer } from '@/components/Footer'
import { ThemeToggle } from '@/components/ThemeToggle'

function ShareButton({ title, exposureScore }: { title: string; exposureScore: number }) {
  const [copied, setCopied] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  const shareUrl = typeof window !== 'undefined' ? window.location.href : ''
  const shareText = `${title}: ${exposureScore}% AI exposure. See which tasks AI will affect → `

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(`${shareText}${shareUrl}`)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = `${shareText}${shareUrl}`
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
    setShowMenu(false)
  }, [shareText, shareUrl])

  const handleShare = useCallback(async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${title} - AI Job Exposure`,
          text: shareText,
          url: shareUrl,
        })
      } catch {
        // User cancelled or share failed, show menu instead
        setShowMenu(true)
      }
    } else {
      setShowMenu(!showMenu)
    }
  }, [title, shareText, shareUrl, showMenu])

  const shareToTwitter = () => {
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
      '_blank'
    )
    setShowMenu(false)
  }

  const shareToLinkedIn = () => {
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
      '_blank'
    )
    setShowMenu(false)
  }

  const shareToThreads = () => {
    window.open(
      `https://www.threads.net/intent/post?text=${encodeURIComponent(`${shareText}${shareUrl}`)}`,
      '_blank'
    )
    setShowMenu(false)
  }

  return (
    <div className="relative">
      <button
        onClick={handleShare}
        className="px-4 py-2 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all text-xs sm:text-sm font-bold flex items-center gap-2 shrink-0"
        aria-label="Share this occupation"
      >
        <span aria-hidden="true">📤</span>
        {copied ? 'Copied!' : 'Share'}
      </button>
      
      {showMenu && (
        <div className="absolute right-0 mt-2 w-48 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50">
          <button
            onClick={handleCopy}
            className="w-full px-4 py-3 text-left text-sm hover:bg-main/30 flex items-center gap-2 border-b border-black/10"
          >
            📋 Copy link
          </button>
          <button
            onClick={shareToTwitter}
            className="w-full px-4 py-3 text-left text-sm hover:bg-main/30 flex items-center gap-2 border-b border-black/10"
          >
            𝕏 Share on X
          </button>
          <button
            onClick={shareToLinkedIn}
            className="w-full px-4 py-3 text-left text-sm hover:bg-main/30 flex items-center gap-2 border-b border-black/10"
          >
            💼 Share on LinkedIn
          </button>
          <button
            onClick={shareToThreads}
            className="w-full px-4 py-3 text-left text-sm hover:bg-main/30 flex items-center gap-2"
          >
            🧵 Share on Threads
          </button>
        </div>
      )}
    </div>
  )
}

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

// Calculate displacement vs augmentation (inspired by AI Work Index methodology)
// displacement = exposure × (1 - bottleneck) — AI replaces
// augmentation = exposure × bottleneck — AI amplifies
function calculateImpactType(
  tasks: Task[],
  exposure: number
): { 
  displacement: number
  augmentation: number
  impactType: 'AT_RISK' | 'AUGMENTED' | 'STABLE' | 'MIXED'
  impactLabel: string
  badgeClass: string
} {
  // Calculate bottleneck from task augmentation vs automation ratios
  const totalAug = tasks.reduce((sum, t) => sum + (t.augmentation_pct || 0), 0)
  const totalAuto = tasks.reduce((sum, t) => sum + (t.automation_pct || 0), 0)
  const bottleneck = totalAug + totalAuto > 0 
    ? totalAug / (totalAug + totalAuto) 
    : 0.5 // default to 50% if no data

  const displacement = exposure * (1 - bottleneck)
  const augmentation = exposure * bottleneck

  // 2x2 classification
  const highDisplacement = displacement >= 0.25
  const highAugmentation = augmentation >= 0.12

  let impactType: 'AT_RISK' | 'AUGMENTED' | 'STABLE' | 'MIXED'
  let impactLabel: string
  let badgeClass: string

  if (highDisplacement && highAugmentation) {
    impactType = 'MIXED'
    impactLabel = 'Mixed Signals'
    badgeClass = 'badge-purple'
  } else if (highDisplacement) {
    impactType = 'AT_RISK'
    impactLabel = 'At Risk'
    badgeClass = 'badge-danger'
  } else if (highAugmentation) {
    impactType = 'AUGMENTED'
    impactLabel = 'AI Augmented'
    badgeClass = 'badge-success'
  } else {
    impactType = 'STABLE'
    impactLabel = 'Stable'
    badgeClass = 'badge-main'
  }

  return { displacement, augmentation, impactType, impactLabel, badgeClass }
}

// Calculate confidence based on data sources
function calculateConfidence(
  tasks: Task[]
): { level: 'HIGH' | 'MEDIUM' | 'LOW'; label: string; badgeClass: string } {
  const sources = tasks.map(t => t.source)
  const anthropicCount = sources.filter(s => s === 'anthropic').length
  const onetCount = sources.filter(s => s === 'onet').length
  const syntheticCount = sources.filter(s => s === 'synthetic' || s === 'llm').length
  const total = tasks.length

  // High: >50% from Anthropic/O*NET empirical data
  // Medium: Mixed sources
  // Low: >50% synthetic
  const empiricalRatio = (anthropicCount + onetCount) / Math.max(total, 1)
  const syntheticRatio = syntheticCount / Math.max(total, 1)

  if (empiricalRatio >= 0.5) {
    return { level: 'HIGH', label: 'High', badgeClass: 'badge-success' }
  } else if (syntheticRatio >= 0.5) {
    return { level: 'LOW', label: 'Low', badgeClass: 'badge-warning' }
  } else {
    return { level: 'MEDIUM', label: 'Medium', badgeClass: 'badge-main' }
  }
}

// Risk band (Very Low to Very High) - uses design system colors
function getRiskBand(exposure: number): { band: string; badgeClass: string; position: number } {
  if (exposure < 0.05) return { band: 'Very Low', badgeClass: 'badge-success', position: 0 }
  if (exposure < 0.15) return { band: 'Low', badgeClass: 'badge-success', position: 1 }
  if (exposure < 0.30) return { band: 'Moderate', badgeClass: 'badge-warning', position: 2 }
  if (exposure < 0.50) return { band: 'High', badgeClass: 'badge-warning', position: 3 }
  return { band: 'Very High', badgeClass: 'badge-danger', position: 4 }
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
  const impact = calculateImpactType(tasks, occupation.ai_exposure_weighted || 0)
  const confidence = calculateConfidence(tasks)
  const riskBand = getRiskBand(occupation.ai_exposure_weighted || 0)

  const getExposureBadge = () => {
    if (exposureScore >= 80) return 'badge-danger'
    if (exposureScore >= 50) return 'badge-warning'
    return 'badge-success'
  }

  return (
    <main className="min-h-screen bg-bg">
      <div className="max-w-5xl mx-auto px-3 py-4 sm:px-4 sm:py-8">
        {/* Back navigation + theme toggle */}
        <nav aria-label="Breadcrumb" className="flex justify-between items-center">
          <Link href="/" className="btn-brutal-neutral text-xs sm:text-sm focus-brutal">
            <span aria-hidden="true">←</span> Back
          </Link>
          <ThemeToggle />
        </nav>
        
        {/* Title + Share */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mt-4 sm:mt-6">
          <h1 className="text-xl sm:text-3xl lg:text-4xl font-extrabold text-black tracking-tight leading-tight">
            {occupation.title.toUpperCase()}
          </h1>
          <ShareButton title={occupation.title} exposureScore={exposureScore} />
        </div>
        
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

        {/* Impact Analysis Row - NEW */}
        <section aria-label="Impact analysis" className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mt-3 sm:mt-4">
          {/* Impact Type 2x2 */}
          <article className="card-brutal p-4 sm:p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs sm:text-sm font-bold text-black/70">IMPACT TYPE</span>
              <span className={`${impact.badgeClass} text-[10px] sm:text-xs`}>
                {impact.impactLabel}
              </span>
            </div>
            
            {/* 2x2 Matrix Visual */}
            <div className="grid grid-cols-2 gap-1 mt-2">
              <div 
                className="p-2 text-center text-[10px] font-bold border-2"
                style={{ 
                  backgroundColor: impact.impactType === 'MIXED' ? 'var(--purple)' : 'var(--bg-alt)',
                  borderColor: impact.impactType === 'MIXED' ? 'var(--black)' : 'var(--black)',
                  opacity: impact.impactType === 'MIXED' ? 1 : 0.5
                }}
              >
                Mixed
              </div>
              <div 
                className="p-2 text-center text-[10px] font-bold border-2"
                style={{ 
                  backgroundColor: impact.impactType === 'AUGMENTED' ? 'var(--success)' : 'var(--bg-alt)',
                  borderColor: impact.impactType === 'AUGMENTED' ? 'var(--black)' : 'var(--black)',
                  opacity: impact.impactType === 'AUGMENTED' ? 1 : 0.5
                }}
              >
                Augmented
              </div>
              <div 
                className="p-2 text-center text-[10px] font-bold border-2"
                style={{ 
                  backgroundColor: impact.impactType === 'AT_RISK' ? 'var(--danger)' : 'var(--bg-alt)',
                  borderColor: impact.impactType === 'AT_RISK' ? 'var(--black)' : 'var(--black)',
                  opacity: impact.impactType === 'AT_RISK' ? 1 : 0.5
                }}
              >
                At Risk
              </div>
              <div 
                className="p-2 text-center text-[10px] font-bold border-2"
                style={{ 
                  backgroundColor: impact.impactType === 'STABLE' ? 'var(--main)' : 'var(--bg-alt)',
                  borderColor: impact.impactType === 'STABLE' ? 'var(--black)' : 'var(--black)',
                  opacity: impact.impactType === 'STABLE' ? 1 : 0.5
                }}
              >
                Stable
              </div>
            </div>
            
            {/* Displacement vs Augmentation bar */}
            <div className="mt-3">
              <div className="flex justify-between text-[10px] font-medium text-black/60 mb-1">
                <span>Displacement: {Math.round(impact.displacement * 100)}%</span>
                <span>Augmentation: {Math.round(impact.augmentation * 100)}%</span>
              </div>
              <div className="h-3 rounded-full overflow-hidden flex border-2 border-black" style={{ backgroundColor: 'var(--bg-alt)' }}>
                <div 
                  className="h-full" 
                  style={{ width: `${impact.displacement * 100}%`, backgroundColor: 'var(--danger)' }}
                />
                <div 
                  className="h-full" 
                  style={{ width: `${impact.augmentation * 100}%`, backgroundColor: 'var(--success)' }}
                />
              </div>
            </div>
          </article>

          {/* Confidence & Risk Band */}
          <article className="card-brutal p-4 sm:p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs sm:text-sm font-bold text-black/70">DATA CONFIDENCE</span>
              <span className={`${confidence.badgeClass} text-[10px] sm:text-xs`}>
                {confidence.label}
              </span>
            </div>
            
            {/* Confidence breakdown */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-medium text-black/60">Empirical (Anthropic + O*NET)</span>
                <span className="text-[10px] font-bold">
                  {tasks.filter(t => t.source === 'anthropic' || t.source === 'onet').length}/{tasks.length} tasks
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-medium text-black/60">Synthetic (LLM-generated)</span>
                <span className="text-[10px] font-bold">
                  {tasks.filter(t => t.source === 'synthetic' || t.source === 'llm').length}/{tasks.length} tasks
                </span>
              </div>
            </div>

            {/* Risk Band */}
            <div className="pt-3 border-t border-black/20">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm font-bold text-black/70">RISK BAND</span>
                <span className={`${riskBand.badgeClass} text-[10px] sm:text-xs`}>
                  {riskBand.band}
                </span>
              </div>
              {/* Risk band scale - uses CSS vars */}
              <div className="flex gap-0.5 mt-2">
                {[0, 1, 2, 3, 4].map((i) => (
                  <div 
                    key={i}
                    className={`flex-1 h-2 border border-black ${i === 0 ? 'rounded-l' : ''} ${i === 4 ? 'rounded-r' : ''}`}
                    style={{ 
                      backgroundColor: i < 2 ? 'var(--success)' : i === 2 ? 'var(--warning)' : 'var(--danger)',
                      opacity: riskBand.position === i ? 1 : 0.4,
                      boxShadow: riskBand.position === i ? '0 0 0 2px var(--black)' : 'none'
                    }}
                  />
                ))}
              </div>
              <div className="flex justify-between text-[8px] text-black/40 mt-1">
                <span>Very Low</span>
                <span>Very High</span>
              </div>
            </div>
          </article>
        </section>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 mt-3 sm:mt-4">
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: 'var(--bg-alt)' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">EMPLOYMENT</span>
            <p className="text-sm sm:text-lg font-bold">{occupation.employment?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: 'var(--bg-alt)' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">MEDIAN PAY</span>
            <p className="text-sm sm:text-lg font-bold">${occupation.median_pay_aud?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: 'var(--bg-alt)' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">TASKS</span>
            <p className="text-sm sm:text-lg font-bold">{tasks.length}</p>
          </div>
          <div className="card-brutal p-2 sm:p-3" style={{ backgroundColor: 'var(--bg-alt)' }}>
            <span className="text-[10px] sm:text-xs font-bold text-black/60">CONFIDENCE</span>
            <p className="text-sm sm:text-lg font-bold">{confidence.level}</p>
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
