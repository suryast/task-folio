import Link from 'next/link'
import { Footer } from '@/components/Footer'

export const metadata = {
  title: 'Data Attribution - TaskFolio',
  description: 'Data sources and attribution for TaskFolio',
}

export default function AttributionPage() {
  return (
    <main className="min-h-screen bg-bg py-12">
      <div className="mx-auto max-w-3xl px-4">
        <Link 
          href="/"
          className="btn-brutal-neutral text-sm mb-8 inline-block"
        >
          ← Back to home
        </Link>

        <div className="card-brutal p-8">
          <h1 className="text-4xl font-extrabold text-black mb-2">DATA ATTRIBUTION</h1>
          <p className="text-sm font-medium text-black/60 mb-8">
            TaskFolio combines multiple data sources for task-level AI exposure analysis.
          </p>
          
          <div className="space-y-6">
            {/* Anthropic */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(182, 172, 228, 0.2)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-purple shrink-0">PRIMARY</span>
                <div>
                  <h2 className="text-xl font-bold text-black">Anthropic Economic Index</h2>
                  <p className="text-black/70 mt-2">
                    Task automation/augmentation data from{' '}
                    <a 
                      href="https://www.anthropic.com/research/anthropic-economic-index-january-2026-report" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="link-brutal"
                    >
                      1M real AI conversations
                    </a>
                  </p>
                  <div className="mt-3 flex gap-2">
                    <span className="badge-brutal bg-white shadow-none text-xs">CC-BY 4.0</span>
                    <span className="badge-brutal bg-white shadow-none text-xs">January 2026</span>
                  </div>
                </div>
              </div>
            </section>

            {/* O*NET */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(136, 212, 238, 0.2)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-main shrink-0">TASKS</span>
                <div>
                  <h2 className="text-xl font-bold text-black">O*NET Database</h2>
                  <p className="text-black/70 mt-2">
                    Occupational task descriptions from{' '}
                    <a 
                      href="https://www.onetonline.org/" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="link-brutal"
                    >
                      O*NET OnLine
                    </a>
                  </p>
                  <p className="text-xs text-black/50 mt-2">
                    Developed by U.S. Department of Labor/Employment and Training Administration (USDOL/ETA). O*NET® is a trademark of USDOL/ETA.
                  </p>
                </div>
              </div>
            </section>

            {/* JSA */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(151, 238, 136, 0.2)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-success shrink-0">AU DATA</span>
                <div>
                  <h2 className="text-xl font-bold text-black">Jobs and Skills Australia</h2>
                  <p className="text-black/70 mt-2">
                    ANZSCO taxonomy, employment data, and wage information from{' '}
                    <a 
                      href="https://www.jobsandskills.gov.au/" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="link-brutal"
                    >
                      jobsandskills.gov.au
                    </a>
                  </p>
                </div>
              </div>
            </section>

            {/* JSA Projections */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(151, 238, 136, 0.2)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-success shrink-0">OUTLOOK</span>
                <div>
                  <h2 className="text-xl font-bold text-black">JSA Employment Projections</h2>
                  <p className="text-black/70 mt-2">
                    10-year employment growth projections (May 2025 → May 2035) for 358 occupations from{' '}
                    <a 
                      href="https://www.jobsandskills.gov.au/data/employment-projections" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="link-brutal"
                    >
                      JSA Employment Projections
                    </a>
                  </p>
                  <p className="text-xs text-black/50 mt-2">
                    Used in Future-Proof Index calculation and Employment Outlook section.
                  </p>
                  <div className="mt-3 flex gap-2">
                    <span className="badge-brutal bg-white shadow-none text-xs">AU Gov CC</span>
                    <span className="badge-brutal bg-white shadow-none text-xs">November 2025</span>
                  </div>
                </div>
              </div>
            </section>

            {/* AI Generated */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(254, 209, 112, 0.2)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-warning shrink-0">AI GEN</span>
                <div>
                  <h2 className="text-xl font-bold text-black">Claude Sonnet 4.5</h2>
                  <p className="text-black/70 mt-2">
                    For 214 Australian occupations not matched to O*NET, tasks generated with AU context:
                  </p>
                  <ul className="mt-3 space-y-1">
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-black rounded-full" aria-hidden="true"></span>
                      <span className="text-black/70 text-sm">Regulatory (ACCC, ASIC, TGA, APRA)</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-black rounded-full" aria-hidden="true"></span>
                      <span className="text-black/70 text-sm">SME adoption rates</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-black rounded-full" aria-hidden="true"></span>
                      <span className="text-black/70 text-sm">Geographic constraints (rural internet)</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-black rounded-full" aria-hidden="true"></span>
                      <span className="text-black/70 text-sm">Privacy culture & market structure</span>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Inspiration */}
            <section className="card-brutal p-5" style={{ backgroundColor: 'rgba(182, 172, 228, 0.15)' }}>
              <div className="flex items-start gap-3">
                <span className="badge-brutal shrink-0">INSPIRED BY</span>
                <div>
                  <h2 className="text-xl font-bold text-black">Prior Art</h2>
                  <ul className="mt-3 space-y-2">
                    <li className="text-black/70 text-sm">
                      <a 
                        href="https://karpathy.ai/jobs" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="link-brutal"
                      >
                        Andrej Karpathy&apos;s US Job Market Visualizer
                      </a>
                      {' '}— Original treemap visualization concept
                    </li>
                    <li className="text-black/70 text-sm">
                      <a 
                        href="https://ychua.github.io/jobs/" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="link-brutal"
                      >
                        ychua&apos;s Australian adaptation
                      </a>
                      {' '}— Australian ANZSCO version with LLM-powered AI exposure scoring
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Methodology */}
            <section className="card-brutal p-5">
              <h2 className="text-xl font-bold text-black mb-3">METHODOLOGY</h2>
              <p className="text-black/70">
                Built on the "jobs as bundles of tasks" framework (David Autor et al). 
                Full pipeline documentation on{' '}
                <a 
                  href="https://github.com/suryast/task-folio" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="link-brutal"
                >
                  GitHub
                </a>
              </p>
            </section>

            {/* License */}
            <section className="card-brutal p-5 bg-[#e8f4fa]">
              <h2 className="text-xl font-bold text-black mb-3">LICENSE</h2>
              <div className="flex flex-wrap gap-2">
                <span className="badge-brutal bg-white">Code: MIT</span>
                <span className="badge-brutal bg-white">Data: Per source terms</span>
              </div>
            </section>
          </div>
        </div>

        <Footer />
      </div>
    </main>
  )
}
