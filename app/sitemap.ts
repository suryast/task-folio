import { MetadataRoute } from 'next'

export const dynamic = 'force-static'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://ai-job-exposure.setiyaputra.me'
  
  return [
    {
      url: baseUrl,
      lastModified: new Date('2026-03-20'),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${baseUrl}/legal/privacy`,
      lastModified: new Date('2026-03-20'),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/legal/attribution`,
      lastModified: new Date('2026-03-20'),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
  ]
}
