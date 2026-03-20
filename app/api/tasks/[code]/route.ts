import { NextResponse } from 'next/server'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

export async function GET(
  request: Request,
  { params }: { params: { code: string } }
) {
  try {
    const res = await fetch(`${API_BASE}/tasks/${params.code}`)
    const data = await res.json()
    
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status })
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('API fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch tasks' },
      { status: 500 }
    )
  }
}
