import { NextRequest, NextResponse } from 'next/server'
import { decomposeJob } from '@/lib/decompose'
import { scoreTaskExposure } from '@/lib/ai-exposure'

export interface AnalyzeRequest {
  jobTitle?: string
  jobDescription?: string
}

export interface AnalyzeResponse {
  onetMatch: { socCode: string; title: string } | null
  tasks: Array<{
    name: string
    description: string
    category: string
    frequency: string
    aiExposureScore: number
    aiReasoning: string
    aiTimeframe: string
  }>
  jobExposureScore: number
  summary: string
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const body = (await request.json()) as AnalyzeRequest

    if (!body.jobTitle && !body.jobDescription) {
      return NextResponse.json(
        { error: 'Either jobTitle or jobDescription is required' },
        { status: 400 }
      )
    }

    // Decompose into tasks
    const decomposition = await decomposeJob({
      jobTitle: body.jobTitle,
      jobDescription: body.jobDescription,
    })

    // Score AI exposure
    const exposure = await scoreTaskExposure(decomposition.tasks)

    // Merge tasks with their scores
    const tasks = decomposition.tasks.map((task, i) => {
      const score = exposure.taskScores.find((s) => s.taskName === task.name)
        ?? exposure.taskScores[i]

      return {
        name: task.name,
        description: task.description,
        category: task.category,
        frequency: task.frequency,
        aiExposureScore: score?.exposureScore ?? 0,
        aiReasoning: score?.reasoning ?? '',
        aiTimeframe: score?.timeframe ?? 'unlikely',
      }
    })

    const response: AnalyzeResponse = {
      onetMatch: decomposition.onetMatch,
      tasks,
      jobExposureScore: exposure.jobExposureScore,
      summary: exposure.summary,
    }

    return NextResponse.json(response)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal server error'
    console.error('[/api/analyze]', err)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
