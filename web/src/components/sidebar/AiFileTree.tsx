import { useMemo, type MouseEvent, type ReactEventHandler } from 'react'
import { Eye } from 'lucide-react'
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
  onSelectFolder?: (path: string) => void
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

function FolderName({
  name,
  path,
  onNavigate,
}: {
  name: string
  path: string
  onNavigate?: (path: string) => void
}) {
  const handleClick = (e: MouseEvent) => {
    e.stopPropagation()
    onNavigate?.(path)
  }

  return (
    <span className="inline-flex items-center gap-1 group/folder">
      {name}
      {onNavigate && (
        <button
          onClick={handleClick}
          className="opacity-0 group-hover/folder:opacity-100 transition-opacity p-0.5 rounded hover:bg-muted"
          title="Open folder view"
        >
          <Eye className="h-3 w-3 text-muted-foreground" />
        </button>
      )}
    </span>
  )
}

function renderNodes(
  nodes: TreeNode[],
  onSelectFolder?: (path: string) => void,
): React.ReactNode {
  return nodes.map((node) => {
    if (node.type === 'directory') {
      return (
        <FileTreeFolder
          key={node.path}
          path={node.path}
          name={
            <FolderName
              name={node.name.replace(/\/$/, '')}
              path={node.path}
              onNavigate={onSelectFolder}
            />
          }
        >
          {renderNodes(node.children ?? [], onSelectFolder)}
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
  onSelectFolder,
}: AiFileTreeProps) {
  const defaultExpanded = new Set(
    nodes.filter((n) => n.type === 'directory').map((n) => n.path),
  )

  const directoryPaths = useMemo(() => collectDirectoryPaths(nodes), [nodes])

  const handleSelect: ReactEventHandler<HTMLDivElement> & ((path: string) => void) = (path: string) => {
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
      {renderNodes(nodes, onSelectFolder)}
    </FileTree>
  )
}
