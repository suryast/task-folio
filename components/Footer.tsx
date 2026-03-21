import Link from 'next/link'

export function Footer() {
  return (
    <footer className="mt-8 card-brutal p-2 sm:p-4" role="contentinfo">
      <nav className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1 sm:gap-4 text-[10px] sm:text-sm" aria-label="Footer navigation">
        <Link href="/" className="link-brutal focus-brutal">Home</Link>
        <span aria-hidden="true" className="text-black/30">•</span>
        <Link href="/legal/privacy" className="link-brutal focus-brutal">Privacy</Link>
        <span aria-hidden="true" className="text-black/30">•</span>
        <Link href="/legal/attribution" className="link-brutal focus-brutal">Attribution</Link>
        <span aria-hidden="true" className="text-black/30">•</span>
        <a href="https://github.com/suryast/task-folio" target="_blank" rel="noopener noreferrer" className="link-brutal focus-brutal">
          GitHub<span className="sr-only">(opens in new tab)</span>
        </a>
        <span aria-hidden="true" className="text-black/30">•</span>
        <a href="https://github.com/sponsors/suryast" target="_blank" rel="noopener noreferrer" className="link-brutal focus-brutal">
          💖<span className="hidden sm:inline"> Sponsor</span><span className="sr-only">(opens in new tab)</span>
        </a>
      </nav>
      <p className="mt-2 text-center text-[9px] sm:text-xs text-black/40">
        <span className="hidden sm:inline">Data: ABS + Anthropic + JSA • </span>
        <a href="https://www.neobrutalui.live" target="_blank" rel="noopener noreferrer" className="hover:text-black/60">Neobrutal UI</a>
      </p>
    </footer>
  )
}
