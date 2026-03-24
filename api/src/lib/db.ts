import type { Bindings } from '../types'

export async function listOccupations(db: D1Database, limit = 500) {
  const { results } = await db
    .prepare(`
      SELECT anzsco_code, title, employment, median_pay_aud, outlook,
             COALESCE(ai_exposure_weighted, 0) as ai_exposure, source, mapping_confidence
      FROM occupations
      ORDER BY employment DESC
      LIMIT ?
    `)
    .bind(limit)
    .all()
  return results
}

export async function getOccupation(db: D1Database, code: string) {
  return db
    .prepare('SELECT * FROM occupations WHERE anzsco_code = ?')
    .bind(code)
    .first()
}

export async function searchOccupations(db: D1Database, query: string, limit = 20) {
  const { results } = await db
    .prepare(`
      SELECT anzsco_code, title, employment,
             ai_exposure_weighted as ai_exposure
      FROM occupations
      WHERE title LIKE ?
      ORDER BY employment DESC
      LIMIT ?
    `)
    .bind(`%${query}%`, limit)
    .all()
  return results
}

export async function getTasksForOccupation(db: D1Database, code: string) {
  const occupation = await db
    .prepare('SELECT id FROM occupations WHERE anzsco_code = ?')
    .bind(code)
    .first<{ id: number }>()

  if (!occupation) return null

  const { results } = await db
    .prepare(`
      SELECT description, automation_pct, augmentation_pct, success_rate,
             human_time_without_ai, human_time_with_ai, speedup_factor,
             human_education_years, ai_autonomy, timeframe,
             taskfolio_score, frequency, source
      FROM tasks
      WHERE occupation_id = ?
      ORDER BY taskfolio_score DESC
    `)
    .bind(occupation.id)
    .all()

  return { anzsco_code: code, task_count: results.length, tasks: results }
}

// REMOVED: storeAnalysis - no longer storing user job descriptions to avoid PII concerns
// Custom analyses are cached in KV only (with TTL) instead of permanent D1 storage
