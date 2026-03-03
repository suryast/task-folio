import { NextRequest, NextResponse } from 'next/server'
import { getOccupation } from '@/lib/onet'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ socCode: string }> }
): Promise<NextResponse> {
  const { socCode } = await params

  const occupation = getOccupation(socCode)

  if (!occupation) {
    return NextResponse.json(
      { error: `Occupation with SOC code "${socCode}" not found` },
      { status: 404 }
    )
  }

  return NextResponse.json(occupation)
}
