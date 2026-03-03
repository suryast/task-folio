import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { DecomposedTask } from '@/lib/decompose'

const mockCreate = vi.fn().mockResolvedValue({
  choices: [
    {
      message: {
        content: JSON.stringify({
          scores: [
            {
              taskName: 'Write and review code',
              exposureScore: 55,
              reasoning: 'AI can assist with code generation but human review is critical.',
              timeframe: '1-2y',
            },
            {
              taskName: 'Collaborate in code reviews',
              exposureScore: 30,
              reasoning: 'Code review requires contextual understanding and team dynamics.',
              timeframe: '3-5y',
            },
            {
              taskName: 'Write technical documentation',
              exposureScore: 75,
              reasoning: 'AI tools excel at drafting structured technical documentation.',
              timeframe: 'now',
            },
          ],
        }),
      },
    },
  ],
})

vi.mock('openai', () => {
  return {
    default: class MockOpenAI {
      chat = {
        completions: {
          create: mockCreate,
        },
      }
    },
  }
})

import { scoreTaskExposure } from '@/lib/ai-exposure'

const sampleTasks: DecomposedTask[] = [
  {
    name: 'Write and review code',
    description: 'Design, write, and review software code.',
    category: 'cognitive',
    frequency: 'daily',
  },
  {
    name: 'Collaborate in code reviews',
    description: 'Review teammates\' code and provide feedback.',
    category: 'interpersonal',
    frequency: 'daily',
  },
  {
    name: 'Write technical documentation',
    description: 'Document systems for knowledge sharing.',
    category: 'cognitive',
    frequency: 'weekly',
  },
]

describe('AI exposure scoring', () => {
  beforeEach(() => {
    process.env.OPENAI_API_KEY = 'test-key'
    mockCreate.mockClear()
  })

  it('returns scores for all tasks', async () => {
    const result = await scoreTaskExposure(sampleTasks)

    expect(result).toHaveProperty('taskScores')
    expect(result).toHaveProperty('jobExposureScore')
    expect(result).toHaveProperty('summary')
    expect(result.taskScores.length).toBe(sampleTasks.length)
  })

  it('all task scores are in range 0-100', async () => {
    const result = await scoreTaskExposure(sampleTasks)

    for (const score of result.taskScores) {
      expect(score.exposureScore).toBeGreaterThanOrEqual(0)
      expect(score.exposureScore).toBeLessThanOrEqual(100)
    }
  })

  it('job-level score is in range 0-100', async () => {
    const result = await scoreTaskExposure(sampleTasks)
    expect(result.jobExposureScore).toBeGreaterThanOrEqual(0)
    expect(result.jobExposureScore).toBeLessThanOrEqual(100)
  })

  it('all timeframes are valid', async () => {
    const result = await scoreTaskExposure(sampleTasks)
    const validTimeframes = ['now', '1-2y', '3-5y', 'unlikely']

    for (const score of result.taskScores) {
      expect(validTimeframes).toContain(score.timeframe)
    }
  })

  it('each score has reasoning', async () => {
    const result = await scoreTaskExposure(sampleTasks)

    for (const score of result.taskScores) {
      expect(typeof score.reasoning).toBe('string')
      expect(score.reasoning.length).toBeGreaterThan(0)
    }
  })

  it('handles empty task list gracefully', async () => {
    const result = await scoreTaskExposure([])
    expect(result.taskScores).toHaveLength(0)
    expect(result.jobExposureScore).toBe(0)
  })

  it('summary is a non-empty string', async () => {
    const result = await scoreTaskExposure(sampleTasks)
    expect(typeof result.summary).toBe('string')
    expect(result.summary.length).toBeGreaterThan(0)
  })
})
