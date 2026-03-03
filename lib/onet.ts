import occupationsData from '@/data/onet/occupations.json'

export type TaskCategory = 'cognitive' | 'interpersonal' | 'physical' | 'administrative'

export interface OnetTask {
  id: string
  name: string
  category: TaskCategory
}

export interface OnetOccupation {
  socCode: string
  title: string
  anzscoCode?: string
  anzscoTitle?: string
  description: string
  tasks: OnetTask[]
  technologySkills: string[]
}

const occupations: OnetOccupation[] = occupationsData as OnetOccupation[]

// Normalize a string for comparison
function normalize(str: string): string {
  return str.toLowerCase().trim().replace(/[^a-z0-9\s]/g, '')
}

export function getOccupation(socCode: string): OnetOccupation | null {
  return occupations.find((o) => o.socCode === socCode) ?? null
}

export function searchOccupations(query: string): OnetOccupation[] {
  if (!query || query.trim().length === 0) return occupations.slice(0, 20)

  const q = normalize(query)
  const terms = q.split(/\s+/).filter(Boolean)

  return occupations.filter((o) => {
    const haystack = normalize(
      [o.title, o.anzscoTitle ?? '', o.description].join(' ')
    )
    return terms.every((term) => haystack.includes(term))
  })
}

export function getTasksForOccupation(socCode: string): OnetTask[] {
  const occupation = getOccupation(socCode)
  return occupation?.tasks ?? []
}

export function findBestMatch(jobTitle: string): OnetOccupation | null {
  const q = normalize(jobTitle)
  const terms = q.split(/\s+/).filter(Boolean)

  let bestMatch: OnetOccupation | null = null
  let bestScore = 0

  for (const o of occupations) {
    const titleText = normalize(o.title + ' ' + (o.anzscoTitle ?? ''))
    const matchedTerms = terms.filter((t) => titleText.includes(t))
    const score = matchedTerms.length / Math.max(terms.length, 1)

    if (score > bestScore) {
      bestScore = score
      bestMatch = o
    }
  }

  // Only return if there's a meaningful match
  return bestScore >= 0.5 ? bestMatch : null
}

export function getAllOccupations(): OnetOccupation[] {
  return occupations
}
