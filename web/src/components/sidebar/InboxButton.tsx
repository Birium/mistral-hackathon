import { Inbox } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface InboxButtonProps {
  count: number
  onClick: () => void
}

export function InboxButton({ count, onClick }: InboxButtonProps) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground transition-colors text-left"
    >
      <Inbox className="h-4 w-4 shrink-0" />
      <span className="flex-1">Inbox</span>
      {count > 0 && (
        <Badge variant="destructive" className="text-xs px-1.5 py-0">
          {count}
        </Badge>
      )}
    </button>
  )
}
