/**
 * Typography — Sandbox Section
 *
 * Showcases the two font stacks used in the design system:
 * - DM Sans (font-sans)     → UI, body, labels, buttons
 * - Libre Baskerville (font-serif) → headings, document titles
 */
import { SectionHeader } from './section-header';

const SANS_WEIGHTS = [
  { weight: 'font-light', label: '300 Light' },
  { weight: 'font-normal', label: '400 Regular' },
  { weight: 'font-medium', label: '500 Medium' },
  { weight: 'font-semibold', label: '600 Semibold' },
  { weight: 'font-bold', label: '700 Bold' },
] as const;

export function Typography() {
  return (
    <section className="space-y-12">
      <SectionHeader
        tag="02"
        title="Typography"
        description="DM Sans (sans) for UI — Libre Baskerville (serif) for document headings."
      />

      {/* ── DM Sans ───────────────────────────────────────────────────── */}
      <div className="space-y-6">
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
          font-sans — DM Sans
        </p>

        <div className="space-y-6 border-l-2 border-border pl-6">
          {/* Weights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {SANS_WEIGHTS.map(({ weight, label }) => (
              <div key={weight} className="flex items-baseline gap-4">
                <span className="text-[10px] text-muted-foreground font-mono w-24 shrink-0">
                  {label}
                </span>
                <span className={`font-sans ${weight} text-foreground text-base`}>
                  The quick brown fox
                </span>
              </div>
            ))}
          </div>

          {/* Scale */}
          <div className="space-y-2 pt-4 border-t border-border">
            <p className="font-sans text-4xl font-bold text-foreground">
              Display
            </p>
            <p className="font-sans text-2xl font-semibold text-foreground">
              Heading Large
            </p>
            <p className="font-sans text-xl font-medium text-foreground">
              Heading Medium
            </p>
            <p className="font-sans text-base font-normal text-foreground leading-relaxed">
              Body — The law is a profession of words. Evatt AI helps you find
              the right ones precisely when it matters most.
            </p>
            <p className="font-sans text-sm text-muted-foreground">
              Supporting — Used for labels, captions, and secondary content.
            </p>
            <p className="font-sans text-xs text-muted-foreground">
              Caption — metadata, timestamps, footnotes
            </p>
          </div>
        </div>
      </div>

      {/* ── Libre Baskerville ─────────────────────────────────────────── */}
      <div className="space-y-6">
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
          font-serif — Libre Baskerville
        </p>

        <div className="space-y-4 border-l-2 border-border pl-6">
          <p className="font-serif text-4xl font-bold text-foreground">
            Legal Counsel
          </p>
          <p className="font-serif text-2xl font-normal text-foreground">
            The right words, at the right time.
          </p>
          <p className="font-serif text-xl italic text-foreground">
            Evatt AI — Your personal legal intelligence.
          </p>
          <p className="font-serif text-base font-normal text-foreground leading-relaxed max-w-2xl">
            Australian law is complex. Evatt AI cuts through the complexity —
            delivering precise, jurisdiction-aware legal insights in plain
            language. Built for legal professionals who demand accuracy.
          </p>
          <p className="font-serif text-sm text-muted-foreground">
            Supporting serif — footnotes, references, document metadata.
          </p>
        </div>
      </div>
    </section>
  );
}