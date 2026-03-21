import type { KVNamespace } from '@cloudflare/workers-types'

const RATE_LIMIT_WINDOW = 3600 // 1 hour in seconds
const MAX_REQUESTS = 10 // 10 requests per hour per IP

export async function checkRateLimit(
  kv: KVNamespace,
  ip: string
): Promise<{ allowed: boolean; remaining: number; resetAt: number }> {
  const key = `ratelimit:${ip}`
  const now = Math.floor(Date.now() / 1000)
  
  const data = await kv.get(key)
  let count = 0
  let windowStart = now
  
  if (data) {
    const parsed = JSON.parse(data)
    // Check if window has expired
    if (now - parsed.windowStart < RATE_LIMIT_WINDOW) {
      count = parsed.count
      windowStart = parsed.windowStart
    }
  }
  
  const resetAt = windowStart + RATE_LIMIT_WINDOW
  
  if (count >= MAX_REQUESTS) {
    return { allowed: false, remaining: 0, resetAt }
  }
  
  // Increment counter
  await kv.put(key, JSON.stringify({ count: count + 1, windowStart }), {
    expirationTtl: RATE_LIMIT_WINDOW,
  })
  
  return { allowed: true, remaining: MAX_REQUESTS - count - 1, resetAt }
}
