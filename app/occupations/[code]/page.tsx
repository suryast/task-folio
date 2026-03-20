'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

interface Task {
  description: string
  automation_pct: number | null
  augmentation_pct: number | null
  success_rate: number | null
  human_time_without_ai: number | null
  human_time_with_ai: number | null
  speedup_factor: number | null
  human_education_years: number | null
  ai_autonomy: number | null
  timeframe: string
  taskfolio_score: number
  frequency: string
  source: string
}

interface Occupation {
  anzsco_code: string
  title: string
  employment: number
  median_pay_aud: number
  outlook: string
  education: string
  ai_exposure_weighted: number
  source: string
}

interface OccupationDetail {
  occupation: Occupation
  tasks: Task[]
  task_count: number
}

export default function OccupationPage() {
  const params = useParams()
  const router = useRouter()
  const code = params.code as string

  const [data, setData] = useState<OccupationDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!code) return

    Promise.all([
      fetch(`/api/occupations/${code}`).then(res => res.json()),
      fetch(`/api/tasks/${code}`).then(res => res.json())
    ])
      .then(([occupation, tasksData]) => {
        setData({
          occupation,
          tasks: tasksData.tasks || [],
          task_count: tasksData.task_count || 0
        })
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [code])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="text-zinc-600 dark:text-zinc-400">Loading...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="text-red-600">Error: {error || 'Occupation not found'}</div>
      </div>
    )
  }

  const { occupation, tasks } = data

  // Group tasks by timeframe
  const tasksByTimeframe = tasks.reduce((acc, task) => {
    const tf = task.timeframe || 'unknown'
    if (!acc[tf]) acc[tf] = []
    acc[tf].push(task)
    return acc
  }, {} as Record<string, Task[]>)

  const timeframeOrder = ['now', '1-2y', '3-5y', '5-10y', '10y+', 'unknown']

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <Link 
          href="/"
          className="inline-flex items-center text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50"
        >
          ← Back to all occupations
        </Link>

        <header className="mt-6">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-4xl">
            {occupation.title}
          </h1>
          <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <div className="text-sm text-zinc-500">Employment</div>
              <div className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                {occupation.employment?.toLocaleString() || 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-zinc-500">Median Pay</div>
              <div className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                ${occupation.median_pay_aud?.toLocaleString() || 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-zinc-500">AI Exposure</div>
              <div className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                {((occupation.ai_exposure_weighted || 0) * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-zinc-500">Tasks</div>
              <div className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                {tasks.length}
              </div>
            </div>
          </div>
        </header>

        <div className="mt-8">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
            Task Breakdown by AI Impact Timeframe
          </h2>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            See which specific tasks AI will affect and when
          </p>
        </div>

        {timeframeOrder.map(timeframe => {
          const tfTasks = tasksByTimeframe[timeframe]
          if (!tfTasks || tfTasks.length === 0) return null

          return (
            <div key={timeframe} className="mt-8">
              <h3 className="mb-4 flex items-center gap-3 text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                <span className={`inline-block h-3 w-3 rounded-full ${getTimeframeDot(timeframe)}`}></span>
                {getTimeframeLabel(timeframe)}
                <span className="text-sm font-normal text-zinc-500">
                  ({tfTasks.length} tasks)
                </span>
              </h3>

              <div className="space-y-4">
                {tfTasks.map((task, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
                  >
                    <p className="text-sm text-zinc-900 dark:text-zinc-50">
                      {task.description}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-3 text-xs text-zinc-600 dark:text-zinc-400">
                      {task.automation_pct !== null && (
                        <span>Automation: {(task.automation_pct * 100).toFixed(0)}%</span>
                      )}
                      {task.augmentation_pct !== null && (
                        <span>Augmentation: {(task.augmentation_pct * 100).toFixed(0)}%</span>
                      )}
                      {task.speedup_factor !== null && (
                        <span>Speedup: {task.speedup_factor.toFixed(1)}x</span>
                      )}
                      <span className="text-zinc-400">•</span>
                      <span className="font-medium">{task.source}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function getTimeframeDot(timeframe: string): string {
  const colors = {
    now: 'bg-red-500',
    '1-2y': 'bg-orange-500',
    '3-5y': 'bg-yellow-500',
    '5-10y': 'bg-blue-500',
    '10y+': 'bg-green-500',
    unknown: 'bg-zinc-400'
  }
  return colors[timeframe as keyof typeof colors] || 'bg-zinc-400'
}

function getTimeframeLabel(timeframe: string): string {
  const labels = {
    now: 'Now — Already happening',
    '1-2y': '1-2 years — Early deployment',
    '3-5y': '3-5 years — Mainstream adoption',
    '5-10y': '5-10 years — Significant barriers',
    '10y+': '10+ years — Fundamental constraints',
    unknown: 'Unknown'
  }
  return labels[timeframe as keyof typeof labels] || timeframe
}
