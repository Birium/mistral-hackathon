import { useChat } from '@/hooks/useChat'
import { useStreamParser } from '@/hooks/useStreamParser'
import { StreamChainOfThought } from '@/components/central/StreamChainOfThought'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'

export function ActivityView() {
  const { isLoading, error, activityResult, pendingMessage } = useChat()
  const { items, headerText } = useStreamParser()

  // ── Empty state ────────────────────────────────────────────────────────────
  if (!isLoading && !activityResult && items.length === 0 && !error) {
    return (
      <div className="text-muted-foreground text-sm">
        Send a message to get started.
      </div>
    )
  }

  return (
    <div className="space-y-4 max-w-2xl">
      {/* Query that triggered this activity */}
      {pendingMessage && isLoading && (
        <div className="text-sm text-muted-foreground italic">
          "{pendingMessage}"
        </div>
      )}

      {/* Chain of thought — progressive steps from the live stream */}
      <StreamChainOfThought
        items={items}
        headerText={headerText}
        isLoading={isLoading}
      />

      {/* Error state */}
      {error && (
        <div className="text-destructive text-sm">{error}</div>
      )}

      {/* Final answer — appears once the stream completes */}
      {!isLoading && activityResult?.content && (
        <MarkdownRenderer content={activityResult.content} />
      )}
    </div>
  )
}