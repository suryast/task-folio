export async function getCached<T>(kv: KVNamespace, key: string): Promise<T | null> {
  const cached = await kv.get(key)
  if (!cached) return null
  return JSON.parse(cached) as T
}

export async function setCache(kv: KVNamespace, key: string, data: unknown, ttlSeconds: number) {
  await kv.put(key, JSON.stringify(data), { expirationTtl: ttlSeconds })
}

export const TTL = {
  OCCUPATIONS_LIST: 3600,      // 1 hour
  OCCUPATION_DETAIL: 86400,    // 24 hours
  TASKS: 86400,                // 24 hours
  CUSTOM_ANALYSIS: 604800,     // 7 days
  STATS: 3600,                 // 1 hour
} as const
