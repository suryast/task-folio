import { MetadataRoute } from 'next'
import occupationConfidence from '@/public/data/occupation_confidence.json'

export const dynamic = 'force-static'

const baseUrl = 'https://ai-job-exposure.setiyaputra.me'
const sitemapLastModified = new Date()
const occupationsApiUrl = 'https://taskfolio-au-api.hello-bb8.workers.dev/api/occupations'

async function getOccupationCodes(): Promise<string[]> {
  try {
    const res = await fetch(occupationsApiUrl, { next: { revalidate: 86400 } })
    if (!res.ok) {
      throw new Error(`Failed to fetch occupations: ${res.status}`)
    }

    const occupations = await res.json() as Array<{ anzsco_code: string }>
    return occupations
      .map((occupation) => occupation.anzsco_code)
      .filter(Boolean)
      .sort()
  } catch {
    return Object.keys(occupationConfidence).sort()
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const occupationCodes = await getOccupationCodes()

  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: sitemapLastModified,
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${baseUrl}/legal/privacy`,
      lastModified: sitemapLastModified,
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/legal/attribution`,
      lastModified: sitemapLastModified,
      changeFrequency: 'monthly',
      priority: 0.5,
    },
  ]

  const occupationRoutes: MetadataRoute.Sitemap = occupationCodes.map((code) => ({
    url: `${baseUrl}/occupations/${code}`,
    lastModified: sitemapLastModified,
    changeFrequency: 'monthly',
    priority: 0.8,
  }))

  return [...staticRoutes, ...occupationRoutes]
}
