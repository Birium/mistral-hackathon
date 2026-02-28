import { Mail } from 'lucide-react'
import type { TreeNode } from '@/types'

interface InboxListViewProps {
  items: TreeNode[]
  onOpenDetail: (name: string) => void
}

function formatRelativeTime(updatedAt: string | null): string {
  if (!updatedAt) return '—'
  const diff = Date.now() - new Date(updatedAt).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return "à l'instant"
  if (minutes < 60) return `il y a ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `il y a ${hours} h`
  const days = Math.floor(hours / 24)
  return `il y a ${days} j`
}

export function InboxListView({ items, onOpenDetail }: InboxListViewProps) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">Aucun item en attente.</p>
    )
  }

  return (
    <div className="space-y-2 max-w-xl">
      {items.map((item) => (
        <button
          key={item.path}
          onClick={() => onOpenDetail(item.name.replace(/\/$/, ''))}
          className="w-full flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent transition-colors text-left"
        >
          <Mail className="h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="flex-1 text-sm font-medium truncate">
            {item.name.replace(/\/$/, '')}
          </span>
          <span className="text-xs text-muted-foreground shrink-0">
            {formatRelativeTime(item.updated_at)}
          </span>
        </button>
      ))}
    </div>
  )
}
