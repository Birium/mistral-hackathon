import type { TreeNode } from '@/types'
import { FileTreeNode } from './FileTreeNode'

interface FileTreeProps {
  nodes: TreeNode[]
  depth: number
  selectedPath: string | null
  onSelectFile: (path: string) => void
}

export function FileTree({ nodes, depth, selectedPath, onSelectFile }: FileTreeProps) {
  return (
    <div>
      {nodes.map((node) => (
        <FileTreeNode
          key={node.path}
          node={node}
          depth={depth}
          selectedPath={selectedPath}
          onSelectFile={onSelectFile}
        />
      ))}
    </div>
  )
}
