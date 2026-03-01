import { useChat } from '@/contexts/ChatContext'
import { useFileNavigation } from '@/hooks/useFileNavigation'
import { LoadingState } from '@/components/shared/LoadingState'
// adjust these imports to whatever your ActivityView currently renders
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import type { AgentEvent } from '@/types'

export function ActivityView() {
  const { isLoading, error, activityResult, chatMode, pendingMessage, streamEvents } = useChat()
  const navigateToFile = useFileNavigation()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {pendingMessage && (
          <div className="text-sm text-muted-foreground italic">"{pendingMessage}"</div>
        )}
        <LoadingState message="Agent is working…" />
        {streamEvents.length > 0 && (
          <div className="space-y-2 text-sm">
            {streamEvents.map((event, i) => (
              <StreamEventLine key={i} event={event} />
            ))}
          </div>
        )}
      </div>
    )
  }

  if (error) {
    return <div className="text-destructive text-sm">{error}</div>
  }

  if (!activityResult) {
    return (
      <div className="text-muted-foreground text-sm">
        Send a message to get started.
      </div>
    )
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="text-xs text-muted-foreground uppercase tracking-wider">
        {activityResult.type === 'search' ? 'Search' : chatMode === 'answering' ? 'Reply' : 'Update'} result
      </div>
      <MarkdownRenderer content={activityResult.content} />
    </div>
  )
}

/** Render a single streaming event — adjust to match your actual event shapes */
function StreamEventLine({ event }: { event: AgentEvent }) {
  if (event.type === 'answer') {
    return <div className="text-foreground">{event.content}</div>
  }
  return (
    <div className="text-muted-foreground text-xs">
      [{event.type}] {JSON.stringify(event).slice(0, 120)}
    </div>
  )
}
