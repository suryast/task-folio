import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'edge'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ code: string }> }
) {
  try {
    const { code } = await params
    const res = await fetch(`${API_BASE}/api/occupations/${code}`)
    const data = await res.json()
    
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status })
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('API fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch occupation' },
      { status: 500 }
    )
  }
}
