import { NextRequest, NextResponse } from 'next/server'
import { searchOccupations } from '@/lib/onet'

export async function GET(request: NextRequest): Promise<NextResponse> {
  const q = request.nextUrl.searchParams.get('q') ?? ''

  const results = searchOccupations(q)

  return NextResponse.json({
    query: q,
    count: results.length,
    occupations: results.map((o) => ({
      socCode: o.socCode,
      title: o.title,
      anzscoTitle: o.anzscoTitle ?? null,
      description: o.description,
      taskCount: o.tasks.length,
    })),
  })
}
