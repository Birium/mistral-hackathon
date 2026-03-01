import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, File } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useFileNavigation } from '@/hooks/useFileNavigation'
import { fetchInboxDetail } from '@/api'
import type { InboxDetail } from '@/types'
import { useChat } from '@/hooks/useChat'

export function InboxDetailView() {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  const navigateToFile = useFileNavigation()
  const { onReply } = useChat()

  const [detail, setDetail] = useState<InboxDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!name) return

    let cancelled = false
    setDetail(null)
    setError(null)
    setLoading(true)

    fetchInboxDetail(name)
      .then((data) => {
        if (!cancelled) setDetail(data)
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [name])

  const handleBack = () => navigate('/inbox')

  if (loading) return <LoadingState message="Loading inbox…" />
  if (error) return <ErrorState message={error} onRetry={handleBack} />
  if (!detail) return null

  return (
    <div className="max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={handleBack} className="gap-1.5">
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
                onClick={() => navigateToFile(`inbox/${detail.name}/${f}`)}
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
