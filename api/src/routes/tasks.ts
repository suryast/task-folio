import { Hono } from 'hono'
import type { Bindings } from '../types'
import { getTasksForOccupation } from '../lib/db'
import { getCached, setCache, TTL } from '../lib/cache'

export const tasksRouter = new Hono<{ Bindings: Bindings }>()

// GET /:code — Get tasks for an occupation
tasksRouter.get('/:code', async (c) => {
  const code = c.req.param('code')
  const cacheKey = `tasks:${code}`

  const cached = await getCached(c.env.CACHE, cacheKey)
  if (cached) return c.json(cached)

  const result = await getTasksForOccupation(c.env.DB, code)
  if (!result) return c.json({ error: 'Occupation not found' }, 404)

  await setCache(c.env.CACHE, cacheKey, result, TTL.TASKS)
  return c.json(result)
})
