import { useEffect, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { useStreamParser } from '@/hooks/useStreamParser'
import { StreamChainOfThought } from '@/components/central/StreamChainOfThought'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'

export function ActivityView() {
  const { isLoading, error, activityResult, pendingMessage } = useChat()
  const { items, headerText } = useStreamParser()
  const [displayedMessage, setDisplayedMessage] = useState<string | null>(null)

  useEffect(() => {
    if (pendingMessage) {
      setDisplayedMessage(pendingMessage)
    }
  }, [pendingMessage])

  // ── Empty state ────────────────────────────────────────────────────────────
  if (!isLoading && !activityResult && items.length === 0 && !error && !displayedMessage) {
    return (
      <div className="text-muted-foreground text-sm">
        Send a message to get started.
      </div>
    )
  }

  return (
    <div className="space-y-4 min-w-2xl max-w-2xl py-5">
      {/* User message bubble — persists for the full activity session */}
      {displayedMessage && (
        <div className="inline-block max-w-[85%] px-4 py-2.5 rounded-2xl rounded-tl-sm bg-muted text-sm text-foreground">
          {displayedMessage}
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
