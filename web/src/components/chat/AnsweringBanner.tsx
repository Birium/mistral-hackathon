import { CornerDownLeft, X } from 'lucide-react'

interface AnsweringBannerProps {
  answeringRef: string
  onCancel: () => void
}

export function AnsweringBanner({ answeringRef, onCancel }: AnsweringBannerProps) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground border-b">
      <CornerDownLeft className="h-3.5 w-3.5 shrink-0" />
      <span className="flex-1 truncate">
        Réponse à : <span className="font-medium text-foreground">{answeringRef}</span>
      </span>
      <button
        onClick={onCancel}
        className="shrink-0 hover:text-foreground transition-colors"
        aria-label="Annuler"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}
