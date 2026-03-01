import { Loader2 } from 'lucide-react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { ErrorState } from '@/components/shared/ErrorState'
import { EventStream } from '@/components/central/EventStream'
import type { ActivityResult, AgentEvent, ChatMode } from '@/types'

interface ActivityViewProps {
  isLoading: boolean
  error: string | null
  result: ActivityResult | null
  chatMode: ChatMode
  streamEvents: AgentEvent[]
  pendingMessage?: string | null
  onSelectFile?: (path: string) => void
  onRetry?: () => void
}

const LOADING_LABELS: Record<ChatMode, string> = {
  update: 'Updating...',
  search: 'Searching...',
  answering: 'Processing reply...',
}

export function ActivityView({
  isLoading,
  error,
  result,
  chatMode,
  streamEvents,
  pendingMessage,
  onSelectFile,
  onRetry,
}: ActivityViewProps) {
  // ── Loading state ─────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="max-w-2xl space-y-4">
        {/* User message bubble */}
        {pendingMessage && (
          <div className="px-4 py-3 bg-muted rounded-lg text-sm text-foreground ml-auto w-fit max-w-xl">
            {pendingMessage}
          </div>
        )}

        {streamEvents.length > 0 ? (
          <>
            <EventStream events={streamEvents} />
            <div className="flex items-center gap-2 text-xs text-muted-foreground px-2 pl-3">
              <Loader2 className="h-3 w-3 animate-spin shrink-0" />
              <span>{LOADING_LABELS[chatMode]}</span>
            </div>
          </>
        ) : (

          <div className="flex flex-col items-center justify-center gap-3 py-8 text-muted-foreground">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="text-sm">{LOADING_LABELS[chatMode]}</span>
          </div>
        )}
      </div>
    )
  }

  // ── Error state ───────────────────────────────────────────────────────────
  if (error) {
    return <ErrorState message={error} onRetry={onRetry} />
  }

  if (!result) return null

  // ── Search result ─────────────────────────────────────────────────────────
  if (result.type === 'search') {
    return (
      <div className="max-w-2xl space-y-6">

        {streamEvents.length > 0 && <EventStream events={streamEvents} />}

        {result.content.trim() ? (
          <MarkdownRenderer content={result.content} />
        ) : (
          <p className="text-muted-foreground text-sm">
            No results found for &ldquo;{result.query}&rdquo;
          </p>
        )}
      </div>
    )
  }

  // ── Update / answering result ─────────────────────────────────────────────
  return (
    <div className="max-w-2xl space-y-6">

      {streamEvents.length > 0 && <EventStream events={streamEvents} />}
      {result.content && <MarkdownRenderer content={result.content} />}
      {result.touched_files && result.touched_files.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
            Modified files
          </p>
          {result.touched_files.map((f) => (
            <button
              key={f}
              onClick={() => onSelectFile?.(f)}
              className="block text-sm text-primary hover:underline"
            >
              {f}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}