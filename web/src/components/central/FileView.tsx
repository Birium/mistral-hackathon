import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { LoadingState } from '@/components/shared/LoadingState'
import { fetchFile } from '@/api'
import { useTree } from '@/hooks/useTree'

export function FileView() {
  const location = useLocation()
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
  if (error)
    return (
      <div className="text-destructive text-sm whitespace-pre-wrap">
        {error}
      </div>
    )
  if (content === null) return <LoadingState message="Loading file…" />

  return (
    <div ref={scrollRef} className="h-full overflow-y-auto">
      <div className="max-w-4xl">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  )
}
