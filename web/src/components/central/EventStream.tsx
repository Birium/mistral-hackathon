import type { AgentEvent } from '@/types'
import { cn } from '@/lib/utils'

interface EventStreamProps {
  events: AgentEvent[]
}


function formatArgs(argsStr: string): string {
  if (!argsStr) return ''
  try {
    const args = JSON.parse(argsStr)
    if (!args || typeof args !== 'object') return argsStr
    const entries = Object.entries(args)
    if (entries.length === 0) return ''
    return entries
      .map(([k, v]) => {
        const raw = typeof v === 'object' ? JSON.stringify(v) : String(v)
        const val = raw.length > 50 ? raw.slice(0, 50) + '…' : raw
        return `${k}="${val}"`
      })
      .join(', ')
  } catch {
    return argsStr.slice(0, 80)
  }
}

function stripThinkTags(content: string): string {
  return content.replace(/<\/?think>\n?/g, '')
}

type ThinkItem = { kind: 'think'; content: string }
type ToolItem = {
  kind: 'tool'
  name: string
  args: string
  status: 'running' | 'done' | 'error'
  result?: string
}
type UsageItem = { kind: 'usage'; prompt_tokens: number; completion_tokens: number; total_cost: number }
type ErrorItem = { kind: 'error'; content: string }

type DisplayItem = ThinkItem | ToolItem | UsageItem | ErrorItem


function processEvents(events: AgentEvent[]): DisplayItem[] {
  const items: DisplayItem[] = []

  for (const event of events) {
    if (event.type === 'done') continue
    if (event.type === 'answer') continue

    // --- Think ---
    if (event.type === 'think') {
      const stripped = stripThinkTags(event.content)
      if (!stripped) continue

      const last = items[items.length - 1]
      if (last?.kind === 'think') {
        last.content += stripped
      } else {
        items.push({ kind: 'think', content: stripped })
      }
      continue
    }

    // --- Tool call ---
    if (event.type === 'tool') {
      if (event.status === 'start') {
        items.push({ kind: 'tool', name: event.name, args: event.arguments, status: 'running' })
        continue
      }

      if (event.status === 'end' || event.status === 'error') {
        const match = [...items]
          .reverse()
          .find((i): i is ToolItem => i.kind === 'tool' && i.name === event.name && i.status === 'running')

        if (match) {
          match.status = event.status === 'end' ? 'done' : 'error'
          match.result = event.result ?? undefined
        }
        continue
      }
    }

    // --- Usage ---
    if (event.type === 'usage') {
      items.push({
        kind: 'usage',
        prompt_tokens: event.prompt_tokens,
        completion_tokens: event.completion_tokens,
        total_cost: event.total_cost,
      })
      continue
    }

    // --- Error ---
    if (event.type === 'error') {
      items.push({ kind: 'error', content: event.content })
      continue
    }
  }

  return items
}


function ThinkBlock({ item }: { item: ThinkItem }) {
  const lines = item.content.split('\n').filter((l) => l.trim())
  const preview = lines.slice(-4).join(' ').trim().slice(0, 220)

  return (
    <div className="flex gap-2 items-start px-2 py-1 text-xs text-muted-foreground italic">
      <span className="shrink-0 opacity-40 mt-px">✦</span>
      <span className="opacity-60 leading-relaxed">{preview}{preview.length >= 220 ? '…' : ''}</span>
    </div>
  )
}

function ToolBlock({ item }: { item: ToolItem }) {
  const formattedArgs = formatArgs(item.args)

  return (
    <div className="space-y-0.5">
      {/* Tool call header */}
      <div
        className={cn(
          'flex items-start gap-2 px-2 py-1.5 rounded-md text-xs font-mono',
          item.status === 'running' && 'text-muted-foreground',
          item.status === 'done' && 'text-foreground',
          item.status === 'error' && 'text-destructive',
        )}
      >
        <span className="shrink-0 mt-px w-3 text-center">
          {item.status === 'running' && '→'}
          {item.status === 'done' && '✓'}
          {item.status === 'error' && '✗'}
        </span>
        <span>
          <span className="font-semibold">{item.name}</span>
          {formattedArgs && (
            <span className="text-muted-foreground">({formattedArgs})</span>
          )}
        </span>
      </div>

      {/* Tool result / error — only shown once resolved */}
      {item.status !== 'running' && item.result && (
        <div className="ml-7 px-2 py-1 bg-muted/40 rounded text-xs text-muted-foreground font-mono leading-relaxed">
          {item.result.slice(0, 240)}
          {item.result.length > 240 ? '…' : ''}
        </div>
      )}
    </div>
  )
}

function UsageBlock({ item }: { item: UsageItem }) {
  return (
    <div className="px-2 py-0.5 text-xs text-muted-foreground/50 font-mono">
      {item.prompt_tokens} in / {item.completion_tokens} out · ${item.total_cost.toFixed(5)}
    </div>
  )
}

function ErrorBlock({ item }: { item: ErrorItem }) {
  return (
    <div className="flex items-start gap-2 px-2 py-1.5 text-xs text-destructive">
      <span className="shrink-0">⚠</span>
      <span>{item.content}</span>
    </div>
  )
}

export function EventStream({ events }: EventStreamProps) {
  const items = processEvents(events)

  if (items.length === 0) return null

  return (
    <div className="space-y-0.5 border-l-2 border-border pl-2 ml-1">
      {items.map((item, i) => {
        if (item.kind === 'think') return <ThinkBlock key={i} item={item} />
        if (item.kind === 'tool') return <ToolBlock key={i} item={item} />
        if (item.kind === 'usage') return <UsageBlock key={i} item={item} />
        if (item.kind === 'error') return <ErrorBlock key={i} item={item} />
        return null
      })}
    </div>
  )
}