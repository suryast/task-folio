import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockCreate = vi.fn().mockResolvedValue({
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        tasks: [
          {
            name: 'Write and review code',
            description: 'Design, write, and review software code to build product features.',
            category: 'cognitive',
            frequency: 'daily',
          },
          {
            name: 'Collaborate in code reviews',
            description: "Review teammates' code and provide constructive feedback.",
            category: 'interpersonal',
            frequency: 'daily',
          },
          {
            name: 'Write technical documentation',
            description: 'Document systems, APIs, and decisions for team knowledge sharing.',
            category: 'cognitive',
            frequency: 'weekly',
          },
          {
            name: 'Attend planning meetings',
            description: 'Participate in sprint planning and estimation.',
            category: 'interpersonal',
            frequency: 'weekly',
          },
        ],
      }),
    },
  ],
})

vi.mock('@anthropic-ai/sdk', () => {
  return {
    default: class MockAnthropic {
      messages = {
        create: mockCreate,
      }
    },
  }
})

import { decomposeJob } from '@/lib/decompose'

describe('Task decomposition', () => {
  beforeEach(() => {
    process.env.ANTHROPIC_API_KEY = 'test-key'
    mockCreate.mockClear()
  })

  it('returns valid structure for a job title', async () => {
    const result = await decomposeJob({ jobTitle: 'Software Engineer' })

    expect(result).toHaveProperty('tasks')
    expect(result).toHaveProperty('onetMatch')
    expect(Array.isArray(result.tasks)).toBe(true)
    expect(result.tasks.length).toBeGreaterThan(0)
  })

  it('each task has required fields', async () => {
    const result = await decomposeJob({ jobTitle: 'Software Engineer v2' })

    for (const task of result.tasks) {
      expect(task).toHaveProperty('name')
      expect(task).toHaveProperty('description')
      expect(task).toHaveProperty('category')
      expect(task).toHaveProperty('frequency')
      expect(typeof task.name).toBe('string')
      expect(typeof task.description).toBe('string')
    }
  })

  it('all task categories are valid', async () => {
    const result = await decomposeJob({ jobTitle: 'Software Engineer v3' })
    const validCategories = ['cognitive', 'interpersonal', 'physical', 'administrative']

    for (const task of result.tasks) {
      expect(validCategories).toContain(task.category)
    }
  })

  it('all task frequencies are valid', async () => {
    const result = await decomposeJob({ jobTitle: 'Software Engineer v4' })
    const validFrequencies = ['daily', 'weekly', 'monthly', 'quarterly']

    for (const task of result.tasks) {
      expect(validFrequencies).toContain(task.frequency)
    }
  })

  it('returns onetMatch for known job titles', async () => {
    const result = await decomposeJob({ jobTitle: 'Software Developer match test' })
    expect(result).toHaveProperty('onetMatch')
  })

  it('throws if neither jobTitle nor jobDescription provided', async () => {
    await expect(decomposeJob({})).rejects.toThrow()
  })

  it('uses cache for repeated requests with same title', async () => {
    const cacheTitle = 'Unique Cache Test Engineer'
    mockCreate.mockClear()
    
    await decomposeJob({ jobTitle: cacheTitle })
    await decomposeJob({ jobTitle: cacheTitle })

    expect(mockCreate).toHaveBeenCalledTimes(1)
  })
})
