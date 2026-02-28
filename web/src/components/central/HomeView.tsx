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

  if (loading) return <LoadingState message="Chargement de l'aperçu..." />

  if (content === null) {
    return (
      <div className="max-w-2xl">
        <h1 className="text-2xl font-bold mb-2">Bienvenue dans le vault</h1>
        <p className="text-muted-foreground">
          Utilisez le chat ci-dessous pour mettre à jour ou rechercher dans votre vault.
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
