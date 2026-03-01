/**
 * Sandbox AI Toolkit Page — /sandbox/ai-toolkit
 *
 * Static showcase of Vercel AI Elements components,
 * aligned with the Evatt design system.
 *
 * Sections:
 * 01 — Shimmer
 * 02 — Chain of Thought
 * 03 — Attachments
 * 04 — Messages
 * 05 — Prompt Input
 */
import { AIToolkitShowcase } from '../_components/ai-toolkit';

export default function SandboxAIToolkitPage() {
  return (
    <main className="max-w-5xl mx-auto w-full px-6 py-12 space-y-20">
      <AIToolkitShowcase />
    </main>
  );
}