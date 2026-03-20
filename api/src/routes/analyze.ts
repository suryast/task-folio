import { Hono } from 'hono'
import { z } from 'zod'
import type { Bindings } from '../types'
import { decomposeJob, scoreExposure } from '../lib/anthropic'
import { storeAnalysis } from '../lib/db'
import { getCached, setCache, TTL } from '../lib/cache'

export const analyzeRouter = new Hono<{ Bindings: Bindings }>()

const JobInputSchema = z.object({
  job_title: z.string().min(2).max(200),
  job_description: z.string().max(5000).optional(),
})

// POST / — Custom job decomposition + scoring
analyzeRouter.post('/', async (c) => {
  const body = await c.req.json()
  const validation = JobInputSchema.safeParse(body)
  if (!validation.success) {
    return c.json({ error: 'Invalid input', details: validation.error.issues }, 400)
  }

  const { job_title, job_description } = validation.data
  const cacheKey = `custom:${job_title.toLowerCase().replace(/\s+/g, '-')}`

  // Check cache
  const cached = await getCached(c.env.CACHE, cacheKey)
  if (cached) return c.json(cached)

  try {
    // Decompose into tasks
    const tasks = await decomposeJob(c.env.ANTHROPIC_API_KEY, job_title, job_description)

    // Score AI exposure
    const { taskScores, jobExposureScore, summary } = await scoreExposure(
      c.env.ANTHROPIC_API_KEY,
      tasks
    )

    // Merge tasks with scores
    const mergedTasks = tasks.map((task, i) => {
      const score = taskScores.find(s => s.taskName === task.name) ?? taskScores[i]
      return {
        name: task.name,
        description: task.description,
        category: task.category,
        frequency: task.frequency,
        aiExposureScore: score?.exposureScore ?? 0,
        aiReasoning: score?.reasoning ?? '',
        aiTimeframe: score?.timeframe ?? 'unlikely',
      }
    })

    const result = {
      job_title,
      tasks: mergedTasks,
      jobExposureScore,
      summary,
    }

    // Store + cache
    await storeAnalysis(c.env.DB, job_title, job_description ?? null, JSON.stringify(result))
    await setCache(c.env.CACHE, cacheKey, result, TTL.CUSTOM_ANALYSIS)

    return c.json(result)
  } catch (error) {
    console.error('[/api/analyze]', error)
    const message = error instanceof Error ? error.message : 'Failed to analyze job'
    return c.json({ error: message }, 500)
  }
})
