import Link from 'next/link'
import { Footer } from '@/components/Footer'

export const metadata = {
  title: 'Privacy Policy - TaskFolio',
  description: 'Privacy policy for TaskFolio',
}

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-extrabold text-black mb-2">PRIVACY POLICY</h1>
          <p className="text-sm font-medium text-black/60 mb-8">Last updated: March 20, 2026</p>
          
          <div className="space-y-6">
            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">01</span> Overview
              </h2>
              <p className="text-black/80">
                TaskFolio is a free tool that helps you understand which tasks in your job AI may automate. 
                We collect minimal data and do not sell or share your information.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">02</span> Data We Collect
              </h2>
              <ul className="space-y-2">
                <li className="card-brutal p-3 bg-[rgba(151,238,136,0.2)]">
                  <strong className="text-black">Anonymous Analytics:</strong>
                  <span className="text-black/70"> Cloudflare Web Analytics (no cookies, anonymous)</span>
                </li>
                <li className="card-brutal p-3 bg-[rgba(151,238,136,0.2)]">
                  <strong className="text-black">No Personal Information:</strong>
                  <span className="text-black/70"> No names, emails, or PII collected</span>
                </li>
                <li className="card-brutal p-3 bg-[rgba(151,238,136,0.2)]">
                  <strong className="text-black">No Cookies:</strong>
                  <span className="text-black/70"> No tracking cookies used</span>
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">03</span> Third-Party Services
              </h2>
              <p className="text-black/80">
                TaskFolio uses Cloudflare for hosting and analytics.{' '}
                <a 
                  href="https://www.cloudflare.com/privacypolicy/" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="link-brutal"
                >
                  Cloudflare Privacy Policy →
                </a>
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">04</span> Data Sources
              </h2>
              <div className="grid gap-2">
                <div className="card-brutal p-3 bg-[#e8f4fa]">
                  <span className="badge-purple">Anthropic</span>
                  <span className="ml-2 text-black/80">Economic Index (CC-BY) — 1M AI conversations</span>
                </div>
                <div className="card-brutal p-3 bg-[#e8f4fa]">
                  <span className="badge-main">O*NET</span>
                  <span className="ml-2 text-black/80">US occupational task database</span>
                </div>
                <div className="card-brutal p-3 bg-[#e8f4fa]">
                  <span className="badge-success">JSA</span>
                  <span className="ml-2 text-black/80">Jobs and Skills Australia (ANZSCO)</span>
                </div>
                <div className="card-brutal p-3 bg-[#e8f4fa]">
                  <span className="badge-warning">Claude</span>
                  <span className="ml-2 text-black/80">Sonnet 4.5 for AU-specific tasks</span>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">05</span> Your Rights
              </h2>
              <p className="text-black/80">
                Since we don't collect personal information, there's no data to access, delete, or modify.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-black mb-3 flex items-center gap-2">
                <span className="badge-main">06</span> Contact
              </h2>
              <p className="text-black/80">
                Questions? Open an issue on{' '}
                <a 
                  href="https://github.com/suryast/task-folio" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="link-brutal"
                >
                  GitHub →
                </a>
              </p>
            </section>
          </div>
        </div>

        <Footer />
      </div>
    </main>
  )
}
