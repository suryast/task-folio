import type { Metadata } from 'next'
import OccupationClient from './OccupationClient'

const API_URL = 'https://taskfolio-au-api.hello-bb8.workers.dev'
const BASE_URL = 'https://ai-job-exposure.setiyaputra.me'

type OccupationSummary = {
  anzsco_code: string
}

type OccupationDetail = {
  anzsco_code: string
  title: string
  ai_exposure_weighted: number | null
  employment: number | null
}

async function fetchOccupation(code: string): Promise<OccupationDetail | null> {
  try {
    const res = await fetch(`${API_URL}/api/occupations/${code}`, {
      next: { revalidate: 86400 },
    })

    if (!res.ok) return null

    return (await res.json()) as OccupationDetail
  } catch {
    return null
  }
}

// Generate static params for all 361 occupations
export async function generateStaticParams() {
  const res = await fetch(`${API_URL}/api/occupations`, {
    next: { revalidate: 86400 },
  })
  const occupations = (await res.json()) as OccupationSummary[]
  return occupations.map((occ) => ({
    code: occ.anzsco_code,
  }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ code: string }>
}): Promise<Metadata> {
  const { code } = await params
  const occupation = await fetchOccupation(code)
  const canonical = `${BASE_URL}/occupations/${code}`

  if (!occupation) {
    return {
      title: 'Occupation not found | TaskFolio',
      description: 'Task-level AI exposure analysis for Australian occupations.',
      alternates: {
        canonical,
      },
    }
  }

  const exposurePercent = occupation.ai_exposure_weighted === null
    ? null
    : Math.round(occupation.ai_exposure_weighted * 100)
  const employment = occupation.employment
    ? `${occupation.employment.toLocaleString('en-AU')} employed`
    : null

  const descriptionParts = [
    `See how AI may affect ${occupation.title} in Australia.`,
    exposurePercent === null ? null : `${exposurePercent}% AI task exposure.`,
    employment,
    'Task-by-task breakdown, timelines, and methodology.',
  ].filter(Boolean)

  const description = descriptionParts.join(' ')
  const title = `${occupation.title} AI Exposure Analysis | TaskFolio`

  return {
    title,
    description,
    alternates: {
      canonical,
    },
    openGraph: {
      title,
      description,
      url: canonical,
      type: 'article',
      images: [
        {
          url: '/preview.png',
          width: 1200,
          height: 630,
          alt: `TaskFolio analysis for ${occupation.title}`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: ['/preview.png'],
    },
  }
}

export default function OccupationPage() {
  return <OccupationClient />
}
