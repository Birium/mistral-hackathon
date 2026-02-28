import { CheckCircle, Loader2 } from 'lucide-react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { ErrorState } from '@/components/shared/ErrorState'
import type { ActivityResult, ChatMode } from '@/types'

interface ActivityViewProps {
  isLoading: boolean
  error: string | null
  result: ActivityResult | null
  chatMode: ChatMode
  onSelectFile?: (path: string) => void
  onRetry?: () => void
}

const LOADING_LABELS: Record<ChatMode, string> = {
  update: 'Mise à jour en cours...',
  search: 'Recherche en cours...',
  answering: 'Traitement de la réponse...',
}

export function ActivityView({
  isLoading,
  error,
  result,
  chatMode,
  onSelectFile,
  onRetry,
}: ActivityViewProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="text-sm">{LOADING_LABELS[chatMode]}</span>
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
          Aucun résultat trouvé pour &ldquo;{result.query}&rdquo;
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
          {result.type === 'answering' ? 'Réponse envoyée' : 'Mise à jour effectuée'}
        </span>
      </div>

      {result.content && <MarkdownRenderer content={result.content} />}

      {result.touched_files && result.touched_files.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
            Fichiers modifiés
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
