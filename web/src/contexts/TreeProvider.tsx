import { useState, useCallback, type ReactNode } from 'react'
import type { TreeNode } from '@/types'
import { fetchTree } from '@/api'
import { useSSE } from '@/hooks/useSSE'
import { TreeContext } from './TreeContext'

export function TreeProvider({ children }: { children: ReactNode }) {
  const [treeData, setTreeData] = useState<TreeNode | null>(null)
  const [lastFileChangePath, setLastFileChangePath] = useState<string | null>(null)
  const [lastFileChangeAt, setLastFileChangeAt] = useState(0)
  const [initialized, setInitialized] = useState(false)

  const refetchTree = useCallback(async () => {
    try {
      const data = await fetchTree()
      setTreeData(data)
    } catch {
      // silently ignore
    }
  }, [])

  // Initial fetch — avoids useEffect + setState lint issue
  if (!initialized) {
    setInitialized(true)
    refetchTree()
  }

  useSSE({
    onTreeChange: refetchTree,
    onFileChange: (path: string) => {
      setLastFileChangePath(path)
      setLastFileChangeAt(Date.now())
    },
  })

  const tree = treeData?.children ?? []

  const inboxItems =
    tree.find((n) => n.name === 'inbox/' || n.name === 'inbox')?.children ?? []
  const inboxCount = inboxItems.length

  return (
    <TreeContext.Provider
      value={{
        treeData,
        tree,
        inboxItems,
        inboxCount,
        refetchTree,
        lastFileChangePath,
        lastFileChangeAt,
      }}
    >
      {children}
    </TreeContext.Provider>
  )
}
