import { ArrowLeft, File } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import type { InboxDetail } from '@/types'

interface InboxDetailViewProps {
  detail: InboxDetail | null
  loading: boolean
  error: string | null
  onBack: () => void
  onReply: (name: string) => void
  onSelectFile: (path: string) => void
}

export function InboxDetailView({
  detail,
  loading,
  error,
  onBack,
  onReply,
  onSelectFile,
}: InboxDetailViewProps) {
  if (loading) return <LoadingState message="Loading inbox..." />
  if (error) return <ErrorState message={error} onRetry={onBack} />
  if (!detail) return null

  return (
    <div className="max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={onBack} className="gap-1.5">
          <ArrowLeft className="h-4 w-4" />
          Inbox
        </Button>
        <h2 className="text-lg font-semibold flex-1 truncate">{detail.name}</h2>
        <Button size="sm" onClick={() => onReply(detail.name)}>
          Reply
        </Button>
      </div>

      {detail.review && <MarkdownRenderer content={detail.review} />}

      {detail.input_files.length > 0 && (
        <>
          <Separator />
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-2">
              Source files
            </p>
            {detail.input_files.map((f) => (
              <button
                key={f}
                onClick={() => onSelectFile(`inbox/${detail.name}/${f}`)}
                className="flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <File className="h-3.5 w-3.5" />
                {f}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
