import { useRef, useEffect } from 'react'
import { ChevronRight } from 'lucide-react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'

interface FileViewProps {
  path: string
  content: string
  onNavigate: (path: string) => void
}

export function FileView({ path, content, onNavigate }: FileViewProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const savedScrollRef = useRef<number>(0)

  // Save scroll position before path changes
  useEffect(() => {
    return () => {
      savedScrollRef.current = scrollRef.current?.scrollTop ?? 0
    }
  }, [path])

  // Restore scroll position after path changes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [path])

  const segments = path.split('/').filter(Boolean)

  return (
    <div ref={scrollRef} className="h-full overflow-y-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground mb-4 flex-wrap">
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
                  onClick={() => onNavigate(segPath)}
                  className="hover:text-foreground transition-colors"
                >
                  {seg}
                </button>
              )}
            </span>
          )
        })}
      </nav>

      <div className="max-w-2xl">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  )
}
