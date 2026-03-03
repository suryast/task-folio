import OpenAI from 'openai'
import { findBestMatch, type OnetOccupation } from '@/lib/onet'

export type TaskFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly'

export interface DecomposedTask {
  name: string
  description: string
  category: 'cognitive' | 'interpersonal' | 'physical' | 'administrative'
  frequency: TaskFrequency
}

export interface DecompositionResult {
  tasks: DecomposedTask[]
  onetMatch: { socCode: string; title: string } | null
}

// Simple in-memory cache keyed by normalized job title
const cache = new Map<string, DecompositionResult>()

function normalizeTitle(title: string): string {
  return title.toLowerCase().trim().replace(/\s+/g, ' ')
}

function getClient(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) throw new Error('OPENAI_API_KEY environment variable is not set')
  return new OpenAI({ apiKey })
}

function buildPrompt(
  jobTitle: string,
  jobDescription: string | undefined,
  onetMatch: OnetOccupation | null
): string {
  const onetContext = onetMatch
    ? `
O*NET baseline tasks for this role (${onetMatch.title}):
${onetMatch.tasks.map((t) => `- ${t.name} [${t.category}]`).join('\n')}

Use these as a starting point. Refine, merge, or supplement with additional tasks specific to the role.`
    : ''

  const input = jobDescription
    ? `Job description:\n${jobDescription.slice(0, 3000)}`
    : `Job title: ${jobTitle}`

  return `You are a workforce analyst. Decompose the following job into a structured list of tasks.

${input}
${onetContext}

Return a JSON object with this exact structure:
{
  "tasks": [
    {
      "name": "Short task name (max 10 words)",
      "description": "What this task involves and why it matters (1-2 sentences)",
      "category": "cognitive|interpersonal|physical|administrative",
      "frequency": "daily|weekly|monthly|quarterly"
    }
  ]
}

Guidelines:
- Include 8-15 tasks that represent the core of this role
- category must be exactly one of: cognitive, interpersonal, physical, administrative
- frequency must be exactly one of: daily, weekly, monthly, quarterly
- Focus on knowledge work tasks; omit trivial activities
- Be specific and actionable, not vague

Return only valid JSON, no explanation.`
}

export async function decomposeJob(params: {
  jobTitle?: string
  jobDescription?: string
}): Promise<DecompositionResult> {
  const { jobTitle = '', jobDescription } = params

  if (!jobTitle && !jobDescription) {
    throw new Error('Either jobTitle or jobDescription must be provided')
  }

  const cacheKey = normalizeTitle(jobTitle || jobDescription!.slice(0, 100))

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey)!
  }

  const onetMatch = jobTitle ? findBestMatch(jobTitle) : null
  const client = getClient()

  const response = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'user',
        content: buildPrompt(jobTitle, jobDescription, onetMatch),
      },
    ],
    response_format: { type: 'json_object' },
    temperature: 0.3,
  })

  const content = response.choices[0]?.message?.content
  if (!content) throw new Error('Empty response from LLM')

  const parsed = JSON.parse(content) as { tasks: DecomposedTask[] }

  if (!Array.isArray(parsed.tasks)) {
    throw new Error('Invalid response structure: missing tasks array')
  }

  const result: DecompositionResult = {
    tasks: parsed.tasks,
    onetMatch: onetMatch
      ? { socCode: onetMatch.socCode, title: onetMatch.title }
      : null,
  }

  cache.set(cacheKey, result)
  return result
}
