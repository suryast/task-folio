import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { secureHeaders } from 'hono/secure-headers'
import type { Bindings } from './types'
import { occupationsRouter } from './routes/occupations'
import { tasksRouter } from './routes/tasks'
import { analyzeRouter } from './routes/analyze'

const app = new Hono<{ Bindings: Bindings }>()

// Security headers
app.use('/*', secureHeaders())

// CORS - restrict to allowed origins
app.use('/*', cors({
  origin: [
    'https://ai-job-exposure.setiyaputra.me',
    'https://taskfolio-au.pages.dev',
    'http://localhost:3000', // dev
  ],
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: ['Content-Type'],
}))

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
