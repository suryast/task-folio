import { Hono } from 'hono'
import type { Bindings } from '../types'
import { listOccupations, getOccupation, searchOccupations } from '../lib/db'
import { getCached, setCache, TTL } from '../lib/cache'

export const occupationsRouter = new Hono<{ Bindings: Bindings }>()

// GET / — List all occupations
occupationsRouter.get('/', async (c) => {
  const cacheKey = 'occupations:list'
  const cached = await getCached(c.env.CACHE, cacheKey)
  if (cached) return c.json(cached)

  const results = await listOccupations(c.env.DB)
  await setCache(c.env.CACHE, cacheKey, results, TTL.OCCUPATIONS_LIST)
  return c.json(results)
})

// GET /search?q= — Search occupations by title
occupationsRouter.get('/search', async (c) => {
  const query = c.req.query('q')
  if (!query || query.length < 2) {
    return c.json({ error: 'Query must be at least 2 characters' }, 400)
  }
  if (query.length > 100) {
    return c.json({ error: 'Query too long (max 100 characters)' }, 400)
  }

  const results = await searchOccupations(c.env.DB, query)
  return c.json(results)
})

// GET /:code — Get single occupation
occupationsRouter.get('/:code', async (c) => {
  const code = c.req.param('code')
  const cacheKey = `occupation:${code}`

  const cached = await getCached(c.env.CACHE, cacheKey)
  if (cached) return c.json(cached)

  const result = await getOccupation(c.env.DB, code)
  if (!result) return c.json({ error: 'Occupation not found' }, 404)

  await setCache(c.env.CACHE, cacheKey, result, TTL.OCCUPATION_DETAIL)
  return c.json(result)
})
