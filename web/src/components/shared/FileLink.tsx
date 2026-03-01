import type { ReactNode } from 'react'
import { FileText } from 'lucide-react'
import { useFileNavigation } from '@/hooks/useFileNavigation'
import { cn } from '@/lib/utils'

interface FileLinkProps {
  /** Vault-relative or absolute path to the file. */
  path: string
  /** Optional custom label — defaults to the filename portion of the path. */
  children?: ReactNode
  /** Additional CSS classes. */
  className?: string
}

/**
 * Clickable chip that navigates to a vault file via the FileView route.
 *
 * Renders as a small inline badge with a file icon.
 * Uses `useFileNavigation()` to normalise the path and navigate to `/file/<relPath>`.
 */
export function FileLink({ path, children, className }: FileLinkProps) {
  const navigateToFile = useFileNavigation()

  // Display the filename if no children provided
  const displayName = children ?? path.split('/').pop() ?? path

  return (
    <button
      type="button"
      onClick={(e) => {
        e.preventDefault()
        e.stopPropagation()
        navigateToFile(path)
      }}
      className={cn(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded',
        'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80',
        'text-xs font-mono transition-colors cursor-pointer',
        'border border-border/50',
        className,
      )}
      title={path}
    >
      <FileText className="size-3 shrink-0" />
      <span className="truncate max-w-[200px]">{displayName}</span>
    </button>
  )
}