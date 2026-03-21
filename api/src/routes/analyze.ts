import { Hono } from 'hono'
import { z } from 'zod'
import type { Bindings } from '../types'
import { decomposeJob, scoreExposure } from '../lib/anthropic'
import { getCached, setCache, TTL } from '../lib/cache'
import { checkRateLimit } from '../lib/ratelimit'

export const analyzeRouter = new Hono<{ Bindings: Bindings }>()

const JobInputSchema = z.object({
  job_title: z.string().min(2).max(200),
  job_description: z.string().max(5000).optional(),
})

// POST / — Custom job decomposition + scoring
analyzeRouter.post('/', async (c) => {
  // Rate limiting
  const ip = c.req.header('cf-connecting-ip') ?? c.req.header('x-forwarded-for') ?? 'unknown'
  const { allowed, remaining, resetAt } = await checkRateLimit(c.env.CACHE, ip)
  
  c.header('X-RateLimit-Remaining', remaining.toString())
  c.header('X-RateLimit-Reset', resetAt.toString())
  
  if (!allowed) {
    return c.json({ 
      error: 'Rate limit exceeded', 
      message: 'Maximum 10 analyses per hour. Please try again later.',
      resetAt: new Date(resetAt * 1000).toISOString()
    }, 429)
  }

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

    // Cache result (don't store job_description to avoid PII storage)
    await setCache(c.env.CACHE, cacheKey, result, TTL.CUSTOM_ANALYSIS)

    return c.json(result)
  } catch (error) {
    console.error('[/api/analyze]', error)
    // Sanitize error message - don't leak SDK details
    return c.json({ error: 'Analysis failed. Please try again.' }, 500)
  }
})
