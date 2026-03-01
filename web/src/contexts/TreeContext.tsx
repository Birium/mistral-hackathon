import { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from 'react'
import type { TreeNode } from '@/types'
import { fetchTree } from '@/api'
import { useSSE } from '@/hooks/useSSE'

interface TreeContextValue {
  treeData: TreeNode | null
  inboxItems: TreeNode[]
  inboxCount: number
  refetchTree: () => Promise<void>
  /** Path of the last file-change SSE event — watchers can react to this */
  lastFileChangePath: string | null
  lastFileChangeAt: number
}

const TreeContext = createContext<TreeContextValue | null>(null)

export function TreeProvider({ children }: { children: ReactNode }) {
  const [treeData, setTreeData] = useState<TreeNode | null>(null)
  const [lastFileChangePath, setLastFileChangePath] = useState<string | null>(null)
  const [lastFileChangeAt, setLastFileChangeAt] = useState(0)

  const refetchTree = useCallback(async () => {
    try {
      const tree = await fetchTree()
      setTreeData(tree)
    } catch {
      // silently ignore
    }
  }, [])

  useEffect(() => {
    refetchTree()
  }, [refetchTree])

  useSSE({
    onTreeChange: refetchTree,
    onFileChange: (path: string) => {
      setLastFileChangePath(path)
      setLastFileChangeAt(Date.now())
    },
  })

  const inboxItems =
    treeData?.children?.find((n) => n.name === 'inbox/' || n.name === 'inbox')?.children ?? []
  const inboxCount = inboxItems.length

  return (
    <TreeContext.Provider
      value={{ treeData, inboxItems, inboxCount, refetchTree, lastFileChangePath, lastFileChangeAt }}
    >
      {children}
    </TreeContext.Provider>
  )
}

export function useTree(): TreeContextValue {
  const ctx = useContext(TreeContext)
  if (!ctx) throw new Error('useTree must be used within <TreeProvider>')
  return ctx
}
