'use client';

/**
 * AI Toolkit — Sandbox Section
 *
 * Static showcase of Vercel AI Elements components
 * rendered against the Evatt design system.
 *
 * 01 — Loaders (Chain of Thought + Shimmer)
 * 02 — Attachments
 * 03 — Messages
 * 04 — Prompt Input
 */

import { SectionHeader } from './section-header';
import { TooltipProvider } from '@/components/ui/tooltip';

// ─── Showcase Components ──────────────────────────────────────────────────────
import { LoaderShowcase } from './ai-loader';
import { AttachmentsShowcase } from './ai-attachments';
import { MessagesShowcase } from './ai-messages';
import { PromptInputShowcase } from './ai-prompt-input';

// ─────────────────────────────────────────────────────────────────────────────
// Main Export
// ─────────────────────────────────────────────────────────────────────────────

export function AIToolkitShowcase() {
  return (
    <TooltipProvider delayDuration={200}>
      <section className="space-y-16">
        <SectionHeader
          tag="04"
          title="AI Toolkit"
          description="Vercel AI Elements — static showcase rendered against the live design system."
        />
        <LoaderShowcase />
        <AttachmentsShowcase />
        <MessagesShowcase />
        <PromptInputShowcase />
      </section>
    </TooltipProvider>
  );
}