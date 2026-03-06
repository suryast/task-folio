import onetData from '@/data/onet-full.json'

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

interface OnetData {
  occupations: Record<string, OnetOccupation>
  alternateTitles: Record<string, string>
}

const data = onetData as OnetData
const occupationsMap = data.occupations
const alternateTitlesMap = data.alternateTitles

// Lazily built sorted array for enumeration
let _occupationsArray: OnetOccupation[] | null = null
function getArray(): OnetOccupation[] {
  if (!_occupationsArray) {
    _occupationsArray = Object.values(occupationsMap)
  }
  return _occupationsArray
}

// Normalize: lowercase, trim, collapse whitespace, strip punctuation
function normalize(str: string): string {
  return str.toLowerCase().trim().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, ' ')
}

// Collect SOC codes whose alternate titles contain all query terms
function altTitleMatches(terms: string[]): Set<string> {
  const codes = new Set<string>()
  for (const [altTitle, code] of Object.entries(alternateTitlesMap)) {
    const normalized = normalize(altTitle)
    if (terms.every((t) => normalized.includes(t)) && occupationsMap[code]) {
      codes.add(code)
    }
  }
  return codes
}

export function getOccupation(socCode: string): OnetOccupation | null {
  return occupationsMap[socCode] ?? null
}

export function searchOccupations(query: string): OnetOccupation[] {
  if (!query || query.trim().length === 0) return getArray().slice(0, 20)

  const q = normalize(query)
  const terms = q.split(/\s+/).filter(Boolean)

  // Match on title/description
  const titleMatches = getArray().filter((o) => {
    const haystack = normalize(
      [o.title, o.anzscoTitle ?? '', o.description].join(' ')
    )
    return terms.every((term) => haystack.includes(term))
  })

  // Also match via alternate titles (handles "frontend" → "front end developer")
  const altCodes = altTitleMatches(terms)
  const altMatches = [...altCodes]
    .map((code) => occupationsMap[code])
    .filter((o) => o && !titleMatches.find((r) => r.socCode === o.socCode))

  return [...titleMatches, ...altMatches]
}

export function getTasksForOccupation(socCode: string): OnetTask[] {
  return occupationsMap[socCode]?.tasks ?? []
}

export function findBestMatch(jobTitle: string): OnetOccupation | null {
  const normalized = jobTitle.toLowerCase().trim()

  // 1. Exact alternate title match
  const altCode = alternateTitlesMap[normalized]
  if (altCode && occupationsMap[altCode]) {
    return occupationsMap[altCode]
  }

  // 2. Fuzzy: best scoring alternate title containing all terms
  const q = normalize(jobTitle)
  const terms = q.split(/\s+/).filter(Boolean)

  const altCodes = altTitleMatches(terms)
  if (altCodes.size > 0) {
    // Return first (deterministic iteration order)
    return occupationsMap[[...altCodes][0]]
  }

  // 3. Fuzzy match on occupation titles
  let bestMatch: OnetOccupation | null = null
  let bestScore = 0

  for (const o of getArray()) {
    const titleText = normalize(o.title + ' ' + (o.anzscoTitle ?? ''))
    const matchedTerms = terms.filter((t) => titleText.includes(t))
    const score = matchedTerms.length / Math.max(terms.length, 1)

    if (score > bestScore) {
      bestScore = score
      bestMatch = o
    }
  }

  return bestScore >= 0.5 ? bestMatch : null
}

export function getAllOccupations(): OnetOccupation[] {
  return getArray()
}
