import { Hono } from 'hono'
import { cors } from 'hono/cors'
import type { Bindings } from './types'
import { occupationsRouter } from './routes/occupations'
import { tasksRouter } from './routes/tasks'
import { analyzeRouter } from './routes/analyze'

const app = new Hono<{ Bindings: Bindings }>()

// Middleware
app.use('/*', cors())

// Health check
app.get('/health', (c) =>
  c.json({
    status: 'ok',
    service: 'taskfolio-au-api',
    timestamp: new Date().toISOString(),
  })
)

// Routes
app.route('/api/occupations', occupationsRouter)
app.route('/api/tasks', tasksRouter)
app.route('/api/analyze', analyzeRouter)

// 404
app.notFound((c) => c.json({ error: 'Not found' }, 404))

// Error handler
app.onError((err, c) => {
  console.error('[taskfolio-api]', err)
  return c.json({ error: 'Internal server error' }, 500)
})

export default app
