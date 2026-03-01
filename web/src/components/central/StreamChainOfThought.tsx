import { useMemo } from 'react'
import { Brain, AlertTriangle } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Shimmer } from '@/components/ai-elements/shimmer'
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '@/components/ai-elements/chain-of-thought'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { FileLink } from '@/components/shared/FileLink'
import {
  getToolIcon,
  getItemIcon,
  parseArgs,
  extractFilePaths,
  type DisplayItem,
  type ThinkItem,
  type ToolItem,
  // UsageItem is parsed and kept in the items array for future use,
  // but is intentionally not rendered in the UI at this time.
  // type UsageItem,
  type ErrorItem,
} from '@/lib/parseStreamEvents'

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

const TOOL_LABELS: Record<string, string> = {
  read: 'Reading files',
  tree: 'Exploring vault structure',
  write: 'Writing changes',
  patch: 'Patching file',
  search: 'Searching vault',
  grep: 'Searching for pattern',
  concat: 'Assembling files',
}

function getToolLabel(name: string): string {
  return TOOL_LABELS[name] ?? `Calling ${name}`
}

// ─────────────────────────────────────────────────────────────────────────────
// Tool args — full display, no truncation
// ─────────────────────────────────────────────────────────────────────────────

function ToolArgsDisplay({ args }: { args: string }) {
  const parsed = parseArgs(args)

  if (!parsed) {
    if (!args) return null
    return (
      <span className="font-mono text-xs text-muted-foreground break-all">{args}</span>
    )
  }

  const entries = Object.entries(parsed)
  if (entries.length === 0) return null

  return (
    <div className="space-y-1 mt-1">
      {entries.map(([key, value]) => {
        const display = Array.isArray(value)
          ? value.join(', ')
          : typeof value === 'object'
          ? JSON.stringify(value, null, 0)
          : String(value)

        return (
          <div key={key} className="flex gap-2 text-xs font-mono">
            <span className="text-muted-foreground/60 shrink-0">{key}:</span>
            <span className="text-muted-foreground break-all">{display}</span>
          </div>
        )
      })}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Step sub-components
// ─────────────────────────────────────────────────────────────────────────────

function ThinkStep({ item, isActive }: { item: ThinkItem; isActive: boolean }) {
  return (
    <ChainOfThoughtStep
      icon={Brain}
      label="Reasoning"
      status={isActive ? 'active' : 'complete'}
    >
      {/*
        Render accumulated think content as markdown.
        Override text sizes so inline `code` and headings match the xs context —
        prevents inline code from ballooning to text-sm inside text-xs prose.
      */}
      <div
        className={[
          'text-xs text-muted-foreground leading-relaxed',
          '[&_h1]:text-sm [&_h1]:font-semibold [&_h1]:mt-2 [&_h1]:mb-1',
          '[&_h2]:text-xs [&_h2]:font-semibold [&_h2]:mt-2 [&_h2]:mb-1',
          '[&_h3]:text-xs [&_h3]:font-semibold [&_h3]:mt-1.5 [&_h3]:mb-0.5',
          '[&_p]:mb-1.5 [&_p]:leading-relaxed',
          '[&_ul]:mb-1.5 [&_ul]:pl-4 [&_li]:leading-relaxed',
          '[&_ol]:mb-1.5 [&_ol]:pl-4',
          // Fix: force inline code to inherit the xs size of its context
          '[&_code]:text-xs [&_code]:py-0',
          '[&_pre]:text-xs [&_pre]:p-2',
        ].join(' ')}
      >
        <MarkdownRenderer content={item.content} />
      </div>
    </ChainOfThoughtStep>
  )
}

function ToolStep({ item }: { item: ToolItem }) {
  const icon = getToolIcon(item.name)
  const label = getToolLabel(item.name)
  const filePaths = item.result ? extractFilePaths(item.result) : []
  const status = item.status === 'running' ? 'active' : 'complete'

  return (
    <ChainOfThoughtStep icon={icon} label={label} status={status}>
      {/* Full tool arguments — no truncation */}
      <ToolArgsDisplay args={item.args} />

      {/* Referenced files as clickable chips once the tool completes */}
      {item.status === 'done' && filePaths.length > 0 && (
        <ChainOfThoughtSearchResults className="mt-2">
          {filePaths.map((path) => (
            <FileLink key={path} path={path} />
          ))}
        </ChainOfThoughtSearchResults>
      )}

      {/* Error output */}
      {item.status === 'error' && item.result && (
        <div className="mt-1 text-xs text-destructive font-mono break-all">
          {item.result}
        </div>
      )}
    </ChainOfThoughtStep>
  )
}

// Usage items are parsed and available in `items` for future use.
// Uncomment this component and the case in ActivityStep to enable.
//
// function UsageStep({ item }: { item: UsageItem }) {
//   return (
//     <ChainOfThoughtStep
//       icon={BarChart2}
//       label="Token usage"
//       description={`${item.prompt_tokens} in · ${item.completion_tokens} out · $${item.total_cost.toFixed(5)}`}
//       status="complete"
//     />
//   )
// }

function ErrorStep({ item }: { item: ErrorItem }) {
  return (
    <ChainOfThoughtStep
      icon={AlertTriangle}
      label="Error"
      description={item.content}
      status="complete"
    />
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Step router
// ─────────────────────────────────────────────────────────────────────────────

function ActivityStep({
  item,
  isStreamActive,
  isLastItem,
}: {
  item: DisplayItem
  isStreamActive: boolean
  isLastItem: boolean
}) {
  switch (item.kind) {
    case 'think':
      return (
        <ThinkStep item={item} isActive={isStreamActive && isLastItem} />
      )
    case 'tool':
      return <ToolStep item={item} />
    case 'usage':
      // Parsed and retained — not displayed.
      // Enable UsageStep above to show token stats.
      return null
    case 'error':
      return <ErrorStep item={item} />
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────────────────────────────────────

interface StreamChainOfThoughtProps {
  items: DisplayItem[]
  headerText: string
  isLoading: boolean
}

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────

export function StreamChainOfThought({
  items,
  headerText,
  isLoading,
}: StreamChainOfThoughtProps) {
  /*
   * Icon strategy: follow the LAST item added to the stream.
   *
   * We intentionally avoid filtering for `status === 'running'` because
   * React 18 automatic batching can merge tool `start` + `end` events into
   * a single render cycle — meaning the tool is already `done` by the time
   * we observe it. Tracking the last item is stable and always accurate.
   */
  const currentIcon = useMemo((): LucideIcon => {
    // When the stream is done, always show Brain
    if (!isLoading) return Brain
    // While loading, follow the last meaningful step — skip usage items
    // (usage events are emitted after each LLM call and would pollute the icon)
    const last = [...items].reverse().find((i) => i.kind !== 'usage')
    if (!last) return Brain
    return getItemIcon(last)
  }, [items, isLoading])

  if (items.length === 0) return null

  return (
    // Starts closed — the header icon communicates current activity
    <ChainOfThought defaultOpen={false}>
      <ChainOfThoughtHeader icon={currentIcon}>
        {isLoading ? (
          <Shimmer as="span" duration={1.5}>
            {headerText}
          </Shimmer>
        ) : (
          headerText
        )}
      </ChainOfThoughtHeader>

      <ChainOfThoughtContent>
        {items.map((item, i) => (
          <ActivityStep
            key={i}
            item={item}
            isStreamActive={isLoading}
            isLastItem={i === items.length - 1}
          />
        ))}
      </ChainOfThoughtContent>
    </ChainOfThought>
  )
}