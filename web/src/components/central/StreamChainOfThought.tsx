import { useEffect, useMemo, useRef, useState } from 'react'
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

/** Delay (ms) before auto-collapsing once the stream ends */
const COLLAPSE_DELAY = 600

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
      <div
        className={[
          'text-xs text-muted-foreground leading-relaxed',
          '[&_h1]:text-sm [&_h1]:font-semibold [&_h1]:mt-2 [&_h1]:mb-1',
          '[&_h2]:text-xs [&_h2]:font-semibold [&_h2]:mt-2 [&_h2]:mb-1',
          '[&_h3]:text-xs [&_h3]:font-semibold [&_h3]:mt-1.5 [&_h3]:mb-0.5',
          '[&_p]:mb-1.5 [&_p]:leading-relaxed',
          '[&_ul]:mb-1.5 [&_ul]:pl-4 [&_li]:leading-relaxed',
          '[&_ol]:mb-1.5 [&_ol]:pl-4',
          '[&_code]:text-xs [&_code]:py-0',
          '[&_pre]:text-xs [&_pre]:p-2',
        ].join(' ')}
      >
        <MarkdownRenderer content={item.content} />
      </div>
    </ChainOfThoughtStep>
  )
}

function ToolStep({ item, isActive }: { item: ToolItem; isActive: boolean }) {
  const icon = getToolIcon(item.name)
  const label = getToolLabel(item.name)
  const filePaths = item.result ? extractFilePaths(item.result) : []

  return (
    <ChainOfThoughtStep
      icon={icon}
      label={label}
      status={isActive ? 'active' : 'complete'}
    >
      <ToolArgsDisplay args={item.args} />

      {item.status === 'done' && filePaths.length > 0 && (
        <ChainOfThoughtSearchResults className="mt-2">
          {filePaths.map((path) => (
            <FileLink key={path} path={path} />
          ))}
        </ChainOfThoughtSearchResults>
      )}

      {item.status === 'error' && item.result && (
        <div className="mt-1 text-xs text-destructive font-mono break-all">
          {item.result}
        </div>
      )}
    </ChainOfThoughtStep>
  )
}

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
  // The active step = last meaningful item while stream is running.
  const isActive = isStreamActive && isLastItem

  switch (item.kind) {
    case 'think':
      return <ThinkStep item={item} isActive={isActive} />
    case 'tool':
      return <ToolStep item={item} isActive={isActive} />
    case 'usage':
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
  // ── Controlled open/close state ──────────────────────────────────────────
  const [isOpen, setIsOpen] = useState(true)
  const prevLoadingRef = useRef(isLoading)

  useEffect(() => {
    const wasLoading = prevLoadingRef.current
    prevLoadingRef.current = isLoading

    // New stream started → open
    if (isLoading && !wasLoading) {
      setIsOpen(true)
      return
    }

    // Stream ended → auto-collapse after a short pause
    if (!isLoading && wasLoading) {
      const timer = setTimeout(() => setIsOpen(false), COLLAPSE_DELAY)
      return () => clearTimeout(timer)
    }
  }, [isLoading])

  // ── Header icon follows the last meaningful step ─────────────────────────
  const currentIcon = useMemo((): LucideIcon => {
    if (!isLoading) return Brain
    const last = [...items].reverse().find((i) => i.kind !== 'usage')
    if (!last) return Brain
    return getItemIcon(last)
  }, [items, isLoading])

  if (items.length === 0) return null

  return (
    <ChainOfThought open={isOpen} onOpenChange={setIsOpen}>
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