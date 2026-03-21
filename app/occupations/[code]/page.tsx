import OccupationClient from './OccupationClient'

// Generate static params for all 361 occupations
export async function generateStaticParams() {
  const res = await fetch('https://taskfolio-au-api.hello-bb8.workers.dev/api/occupations')
  const occupations = await res.json()
  return occupations.map((occ: { anzsco_code: string }) => ({
    code: occ.anzsco_code,
  }))
}

export default function OccupationPage() {
  return <OccupationClient />
}
