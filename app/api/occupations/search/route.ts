import { NextRequest, NextResponse } from 'next/server'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get('q') ?? ''

  if (!q || q.length < 2) {
    return NextResponse.json({ 
      error: 'Query must be at least 2 characters',
      query: q,
      count: 0,
      occupations: []
    }, { status: 400 })
  }

  try {
    const res = await fetch(`${API_BASE}/api/occupations/search?q=${encodeURIComponent(q)}`)
    const data = await res.json()
    
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status })
    }
    
    return NextResponse.json({
      query: q,
      count: data.length,
      occupations: data
    })
  } catch (error) {
    console.error('API search error:', error)
    return NextResponse.json(
      { error: 'Failed to search occupations' },
      { status: 500 }
    )
  }
}
