import { createContext } from 'react'
import type { TreeNode } from '@/types'

export interface TreeContextValue {
  treeData: TreeNode | null
  tree: TreeNode[]
  inboxItems: TreeNode[]
  inboxCount: number
  refetchTree: () => Promise<void>
  lastFileChangePath: string | null
  lastFileChangeAt: number
}

export const TreeContext = createContext<TreeContextValue | null>(null)
