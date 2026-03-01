import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { LoadingState } from '@/components/shared/LoadingState'
import { useTree } from '@/contexts/TreeContext'
import { useFileNavigation } from '@/hooks/useFileNavigation'
import { fetchFile } from '@/api'

export function FileView() {
  const location = useLocation()
  const navigateToFile = useFileNavigation()
  const { lastFileChangePath, lastFileChangeAt } = useTree()

  // Derive the relative path from the URL: /file/some/path.md → some/path.md
  const path = location.pathname.replace(/^\/file\//, '')

  const [content, setContent] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Fetch file content whenever the path changes
  useEffect(() => {
    if (!path) return

    let cancelled = false
    setContent(null)
    setError(null)

    fetchFile(path)
      .then((data) => {
        if (!cancelled) setContent(data.content)
      })
      .catch((e) => {
        if (!cancelled) setError(`Error: could not load file.\n${e}`)
      })

    return () => {
      cancelled = true
    }
  }, [path])

  // Re-fetch when SSE signals that this file changed
  useEffect(() => {
    if (!lastFileChangePath || !path) return
    if (lastFileChangePath.endsWith(path)) {
      fetchFile(path)
        .then((data) => setContent(data.content))
        .catch(() => {})
    }
  }, [lastFileChangePath, lastFileChangeAt, path])

  // Scroll to top on path change
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = 0
  }, [path])

  if (!path) return null
  if (error) return <div className="text-destructive text-sm whitespace-pre-wrap">{error}</div>
  if (content === null) return <LoadingState message="Loading file…" />

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
                  onClick={() => navigateToFile(segPath)}
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
