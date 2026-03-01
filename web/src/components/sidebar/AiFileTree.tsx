import { useMemo } from 'react'
import type { TreeNode } from '@/types'
import {
  FileTree,
  FileTreeFile,
  FileTreeFolder,
} from '@/components/ai-elements/file-tree'

interface AiFileTreeProps {
  nodes: TreeNode[]
  selectedPath: string | null
  onSelectFile: (path: string) => void
}

function collectDirectoryPaths(
  nodes: TreeNode[],
  result: Set<string> = new Set(),
): Set<string> {
  for (const node of nodes) {
    if (node.type === 'directory') {
      result.add(node.path)
      if (node.children) collectDirectoryPaths(node.children, result)
    }
  }
  return result
}

function renderNodes(nodes: TreeNode[]): React.ReactNode {
  return nodes.map((node) => {
    if (node.type === 'directory') {
      return (
        <FileTreeFolder key={node.path} path={node.path} name={node.name}>
          {renderNodes(node.children ?? [])}
        </FileTreeFolder>
      )
    }
    return <FileTreeFile key={node.path} path={node.path} name={node.name} />
  })
}

export function AiFileTree({
  nodes,
  selectedPath,
  onSelectFile,
}: AiFileTreeProps) {
  const defaultExpanded = new Set(
    nodes.filter((n) => n.type === 'directory').map((n) => n.path),
  )

  const directoryPaths = useMemo(() => collectDirectoryPaths(nodes), [nodes])

  const handleSelect = (path: string) => {
    // Only navigate for files — folders just expand/collapse via the tree component
    if (!directoryPaths.has(path)) {
      onSelectFile(path)
    }
  }

  return (
    <FileTree
      defaultExpanded={defaultExpanded}
      selectedPath={selectedPath ?? undefined}
      onSelect={handleSelect}
      className="border-none rounded-none bg-transparent p-0 font-sans text-sm"
    >
      {renderNodes(nodes)}
    </FileTree>
  )
}
