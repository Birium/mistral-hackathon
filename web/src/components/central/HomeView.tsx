import { useEffect, useState } from 'react'
import { fetchFile } from '@/api'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'
import { LoadingState } from '@/components/shared/LoadingState'

export function HomeView() {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchFile('overview.md')
      .then((data) => setContent(data.content))
      .catch(() => setContent(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState message="Loading overview..." />

  if (content === null) {
    return (
      <div className="max-w-2xl">
        <h1 className="text-2xl font-bold mb-2">Welcome to the vault</h1>
        <p className="text-muted-foreground">
          Use the chat below to update or search your vault.
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <MarkdownRenderer content={content} />
    </div>
  )
}
