import { describe, it, expect } from 'vitest'
import {
  searchOccupations,
  getOccupation,
  getTasksForOccupation,
  getAllOccupations,
} from '@/lib/onet'

describe('O*NET integration', () => {
  it('should load 100+ occupations', () => {
    const all = getAllOccupations()
    expect(all.length).toBeGreaterThanOrEqual(100)
  })

  it('searchOccupations returns results for "software"', () => {
    const results = searchOccupations('software')
    expect(results.length).toBeGreaterThan(0)
    const titles = results.map((r) => r.title.toLowerCase())
    const hasSoftware = titles.some((t) => t.includes('software'))
    expect(hasSoftware).toBe(true)
  })

  it('searchOccupations returns results for "manager"', () => {
    const results = searchOccupations('manager')
    expect(results.length).toBeGreaterThan(0)
  })

  it('searchOccupations returns results for "accountant"', () => {
    const results = searchOccupations('accountant')
    expect(results.length).toBeGreaterThan(0)
  })

  it('searchOccupations with empty query returns occupations', () => {
    const results = searchOccupations('')
    expect(results.length).toBeGreaterThan(0)
  })

  it('getOccupation returns correct occupation by SOC code', () => {
    const occ = getOccupation('15-1252.00')
    expect(occ).not.toBeNull()
    expect(occ!.title).toBe('Software Developers')
    expect(occ!.socCode).toBe('15-1252.00')
  })

  it('getOccupation returns null for unknown SOC code', () => {
    const occ = getOccupation('99-9999.99')
    expect(occ).toBeNull()
  })

  it('getTasksForOccupation returns tasks for software developers', () => {
    const tasks = getTasksForOccupation('15-1252.00')
    expect(tasks.length).toBeGreaterThan(0)
    expect(tasks[0]).toHaveProperty('id')
    expect(tasks[0]).toHaveProperty('name')
    expect(tasks[0]).toHaveProperty('category')
  })

  it('all occupations have valid structure', () => {
    const all = getAllOccupations()
    for (const occ of all) {
      expect(occ).toHaveProperty('socCode')
      expect(occ).toHaveProperty('title')
      expect(occ).toHaveProperty('tasks')
      expect(Array.isArray(occ.tasks)).toBe(true)
      expect(occ.tasks.length).toBeGreaterThan(0)
    }
  })

  it('all task categories are valid', () => {
    const validCategories = ['cognitive', 'interpersonal', 'physical', 'administrative']
    const all = getAllOccupations()
    for (const occ of all) {
      for (const task of occ.tasks) {
        expect(validCategories).toContain(task.category)
      }
    }
  })

  it('occupations include ANZSCO data for Australian titles', () => {
    const all = getAllOccupations()
    const withAnzsco = all.filter((o) => o.anzscoCode && o.anzscoTitle)
    expect(withAnzsco.length).toBeGreaterThan(50)
  })
})
