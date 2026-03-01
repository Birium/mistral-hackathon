import { CheckCircle, Loader2 } from 'lucide-react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { ErrorState } from '@/components/shared/ErrorState'
import type { ActivityResult, ChatMode } from '@/types'

interface ActivityViewProps {
  isLoading: boolean
  error: string | null
  result: ActivityResult | null
  chatMode: ChatMode
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
  pendingMessage,
  onSelectFile,
  onRetry,
}: ActivityViewProps) {
  if (isLoading) {
    return (
      <div className="max-w-2xl space-y-6">
        {pendingMessage && (
          <div className="px-4 py-3 bg-muted rounded-lg text-sm text-foreground ml-auto w-fit max-w-xl">
            {pendingMessage}
          </div>
        )}
        <div className="flex flex-col items-center justify-center gap-3 py-8 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="text-sm">{LOADING_LABELS[chatMode]}</span>
        </div>
      </div>
    )
  }

  if (error) {
    return <ErrorState message={error} onRetry={onRetry} />
  }

  if (!result) return null

  if (result.type === 'search') {
    if (!result.content.trim()) {
      return (
        <p className="text-muted-foreground text-sm">
          No results found for &ldquo;{result.query}&rdquo;
        </p>
      )
    }
    return (
      <div className="max-w-2xl">
        <MarkdownRenderer content={result.content} />
      </div>
    )
  }

  // update / answering
  return (
    <div className="max-w-2xl space-y-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <CheckCircle className="h-4 w-4 text-green-500" />
        <span>
          {result.type === 'answering' ? 'Reply sent' : 'Update complete'}
        </span>
      </div>

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
