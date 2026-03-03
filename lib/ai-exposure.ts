import OpenAI from 'openai'
import type { DecomposedTask, TaskFrequency } from '@/lib/decompose'

export type AITimeframe = 'now' | '1-2y' | '3-5y' | 'unlikely'

export interface TaskExposureScore {
  taskName: string
  exposureScore: number // 0-100
  reasoning: string
  timeframe: AITimeframe
}

export interface JobExposureResult {
  taskScores: TaskExposureScore[]
  jobExposureScore: number // weighted average 0-100
  summary: string
}

const FREQUENCY_WEIGHT: Record<TaskFrequency, number> = {
  daily: 4,
  weekly: 3,
  monthly: 2,
  quarterly: 1,
}

function getClient(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) throw new Error('OPENAI_API_KEY environment variable is not set')
  return new OpenAI({ apiKey })
}

function buildScoringPrompt(tasks: DecomposedTask[]): string {
  const taskList = tasks
    .map((t, i) => `${i + 1}. "${t.name}": ${t.description} [${t.category}]`)
    .join('\n')

  return `You are an AI automation analyst. Score each task for AI automation potential based on current AI capabilities (GPT-4, Claude, AI agents, robotic process automation).

Tasks to score:
${taskList}

For each task, return a JSON object with this exact structure:
{
  "scores": [
    {
      "taskName": "exact task name from input",
      "exposureScore": 75,
      "reasoning": "Why this score — what AI can and cannot do here (1-2 sentences)",
      "timeframe": "now|1-2y|3-5y|unlikely"
    }
  ]
}

Scoring guide:
- 90-100: AI can fully automate this task today (data entry, simple text generation, rule-based decisions)
- 70-89: AI can do most of this task with minimal human oversight
- 50-69: AI can significantly assist but human judgment is still required
- 30-49: AI provides tools/assistance but human remains central
- 10-29: AI has limited applicability; task is highly contextual or relational
- 0-9: AI cannot meaningfully assist (requires physical presence, deep empathy, or novel judgment)

Timeframe guide:
- "now": AI can do this today
- "1-2y": Will be automatable within 2 years with current trajectory
- "3-5y": Requires AI advances but plausible within 5 years
- "unlikely": Requires AGI-level capabilities; not plausible near-term

Return only valid JSON, no explanation. Return scores in the same order as input tasks.`
}

export async function scoreTaskExposure(
  tasks: DecomposedTask[]
): Promise<JobExposureResult> {
  if (tasks.length === 0) {
    return { taskScores: [], jobExposureScore: 0, summary: 'No tasks to score.' }
  }

  const client = getClient()

  const response = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'user',
        content: buildScoringPrompt(tasks),
      },
    ],
    response_format: { type: 'json_object' },
    temperature: 0.2,
  })

  const content = response.choices[0]?.message?.content
  if (!content) throw new Error('Empty response from LLM')

  const parsed = JSON.parse(content) as { scores: TaskExposureScore[] }

  if (!Array.isArray(parsed.scores)) {
    throw new Error('Invalid response: missing scores array')
  }

  // Validate scores are in range
  const taskScores = parsed.scores.map((s) => ({
    ...s,
    exposureScore: Math.max(0, Math.min(100, Math.round(s.exposureScore))),
  }))

  // Weighted average by task frequency
  const jobExposureScore = computeJobScore(tasks, taskScores)

  const summary = generateSummary(jobExposureScore)

  return { taskScores, jobExposureScore, summary }
}

function computeJobScore(
  tasks: DecomposedTask[],
  scores: TaskExposureScore[]
): number {
  let totalWeight = 0
  let weightedSum = 0

  for (let i = 0; i < tasks.length; i++) {
    const task = tasks[i]
    const score = scores.find((s) => s.taskName === task.name) ?? scores[i]
    if (!score) continue

    const weight = FREQUENCY_WEIGHT[task.frequency] ?? 1
    weightedSum += score.exposureScore * weight
    totalWeight += weight
  }

  if (totalWeight === 0) return 0
  return Math.round(weightedSum / totalWeight)
}

function generateSummary(score: number): string {
  if (score >= 80) {
    return 'High AI exposure — a significant portion of this role can be automated by current AI tools.'
  } else if (score >= 60) {
    return 'Moderate-high AI exposure — AI can handle many tasks, but human oversight and judgment remain important.'
  } else if (score >= 40) {
    return 'Moderate AI exposure — AI can assist substantially, but core tasks require human expertise.'
  } else if (score >= 20) {
    return 'Low-moderate AI exposure — AI plays a supporting role, with most value driven by human skills.'
  } else {
    return 'Low AI exposure — this role relies heavily on human judgment, relationships, and physical presence.'
  }
}
