import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'edge'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

export interface AnalyzeRequest {
  jobTitle?: string
  jobDescription?: string
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    const data = await res.json()
    
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status })
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('API analyze error:', error)
    return NextResponse.json(
      { error: 'Failed to analyze job' },
      { status: 500 }
    )
  }
}
