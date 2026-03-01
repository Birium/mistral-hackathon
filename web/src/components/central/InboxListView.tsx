import { useTree } from '@/hooks/useTree'
import { Mail } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function formatRelativeTime(updatedAt: string | null): string {
  if (!updatedAt) return '—'
  const diff = Date.now() - new Date(updatedAt).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function InboxListView() {
  const { inboxItems } = useTree()
  const navigate = useNavigate()

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Inbox</h2>

      {inboxItems.length === 0 ? (
        <p className="text-sm text-muted-foreground">No pending items.</p>
      ) : (
        <div className="space-y-2 max-w-xl">
          {inboxItems.map((item) => {
            const name = item.name.replace(/\/$/, '')
            return (
              <button
                key={item.path}
                onClick={() => navigate('/inbox/' + name)}
                className="w-full flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent transition-colors text-left"
              >
                <Mail className="h-4 w-4 shrink-0 text-muted-foreground" />
                <span className="flex-1 text-sm font-medium truncate">{name}</span>
                <span className="text-xs text-muted-foreground shrink-0">
                  {formatRelativeTime(item.updated_at)}
                </span>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
