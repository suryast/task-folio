import Anthropic from '@anthropic-ai/sdk'
import type { DecomposedTask, TaskExposureScore, TaskFrequency } from '../types'

const FREQUENCY_WEIGHT: Record<TaskFrequency, number> = {
  daily: 4,
  weekly: 3,
  monthly: 2,
  quarterly: 1,
}

export async function decomposeJob(
  apiKey: string,
  jobTitle: string,
  jobDescription?: string
): Promise<DecomposedTask[]> {
  const client = new Anthropic({ apiKey })

  const input = jobDescription
    ? `Job description:\n${jobDescription.slice(0, 3000)}`
    : `Job title: ${jobTitle}`

  const response = await client.messages.create({
    model: 'claude-haiku-4-5-20250514',
    max_tokens: 2048,
    temperature: 0.3,
    messages: [{
      role: 'user',
      content: `You are a workforce analyst. Decompose the following job into a structured list of tasks.

${input}

Return a JSON object with this exact structure:
{
  "tasks": [
    {
      "name": "Short task name (max 10 words)",
      "description": "What this task involves (1-2 sentences)",
      "category": "cognitive|interpersonal|physical|administrative",
      "frequency": "daily|weekly|monthly|quarterly"
    }
  ]
}

Guidelines:
- Include 8-15 tasks that represent the core of this role
- Focus on concrete, observable tasks
- Be specific and actionable

Return only valid JSON, no explanation.`
    }]
  })

  const text = response.content.find(b => b.type === 'text')
  if (!text || text.type !== 'text') throw new Error('Empty LLM response')

  const jsonMatch = text.text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) throw new Error('No JSON in LLM response')

  const parsed = JSON.parse(jsonMatch[0]) as { tasks: DecomposedTask[] }
  if (!Array.isArray(parsed.tasks)) throw new Error('Invalid response: missing tasks array')

  return parsed.tasks
}

export async function scoreExposure(
  apiKey: string,
  tasks: DecomposedTask[]
): Promise<{ taskScores: TaskExposureScore[]; jobExposureScore: number; summary: string }> {
  if (tasks.length === 0) {
    return { taskScores: [], jobExposureScore: 0, summary: 'No tasks to score.' }
  }

  const client = new Anthropic({ apiKey })

  const taskList = tasks
    .map((t, i) => `${i + 1}. "${t.name}": ${t.description} [${t.category}]`)
    .join('\n')

  const response = await client.messages.create({
    model: 'claude-haiku-4-5-20250514',
    max_tokens: 2048,
    temperature: 0.2,
    messages: [{
      role: 'user',
      content: `You are an AI automation analyst. Score each task for AI automation potential.

Tasks to score:
${taskList}

Return JSON:
{
  "scores": [
    {
      "taskName": "exact task name",
      "exposureScore": 75,
      "reasoning": "Why this score (1-2 sentences)",
      "timeframe": "now|1-2y|3-5y|unlikely"
    }
  ]
}

Scoring: 90-100=fully automatable, 70-89=mostly AI, 50-69=AI assists, 30-49=human-led, 10-29=limited AI, 0-9=no AI.
Timeframe: "now"=today, "1-2y"=within 2y, "3-5y"=within 5y, "unlikely"=requires AGI.

Return only valid JSON.`
    }]
  })

  const text = response.content.find(b => b.type === 'text')
  if (!text || text.type !== 'text') throw new Error('Empty LLM response')

  const jsonMatch = text.text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) throw new Error('No JSON in LLM response')

  const parsed = JSON.parse(jsonMatch[0]) as { scores: TaskExposureScore[] }
  if (!Array.isArray(parsed.scores)) throw new Error('Invalid response: missing scores array')

  const taskScores = parsed.scores.map(s => ({
    ...s,
    exposureScore: Math.max(0, Math.min(100, Math.round(s.exposureScore))),
  }))

  // Compute weighted job score
  let totalWeight = 0
  let weightedSum = 0
  for (let i = 0; i < tasks.length; i++) {
    const score = taskScores.find(s => s.taskName === tasks[i].name) ?? taskScores[i]
    if (!score) continue
    const weight = FREQUENCY_WEIGHT[tasks[i].frequency] ?? 1
    weightedSum += score.exposureScore * weight
    totalWeight += weight
  }
  const jobExposureScore = totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0

  let summary: string
  if (jobExposureScore >= 80) summary = 'High AI exposure — significant automation potential with current AI.'
  else if (jobExposureScore >= 60) summary = 'Moderate-high — AI handles many tasks, human oversight still needed.'
  else if (jobExposureScore >= 40) summary = 'Moderate — AI assists substantially but core tasks need human expertise.'
  else if (jobExposureScore >= 20) summary = 'Low-moderate — AI plays a supporting role.'
  else summary = 'Low exposure — relies heavily on human judgment and relationships.'

  return { taskScores, jobExposureScore, summary }
}
