import { useNavigate } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BreadcrumbProps {
  segments: string[]
  className?: string
}

export function Breadcrumb({ segments, className }: BreadcrumbProps) {
  const navigate = useNavigate()

  return (
    <nav className={cn('flex items-center gap-1 text-sm text-muted-foreground flex-wrap', className)}>
      {segments.map((seg, i) => {
        const isLast = i === segments.length - 1
        const segPath = segments.slice(0, i + 1).join('/')
        return (
          <span key={segPath} className="flex items-center gap-1">
            {i > 0 && <ChevronRight className="h-3.5 w-3.5" />}
            {isLast ? (
              <span className="text-foreground font-medium">{seg}</span>
            ) : (
              <button
                onClick={() => navigate(`/folder/${segPath}`)}
                className="hover:text-foreground transition-colors"
              >
                {seg}
              </button>
            )}
          </span>
        )
      })}
    </nav>
  )
}
