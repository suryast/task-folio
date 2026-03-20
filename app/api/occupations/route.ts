import { NextResponse } from 'next/server'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787'

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/api/occupations`)
    const data = await res.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('API fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch occupations' },
      { status: 500 }
    )
  }
}
