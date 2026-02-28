import { useState } from 'react'
import { ChevronRight, File, Folder } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { TreeNode } from '@/types'
import { FileTree } from './FileTree'

interface FileTreeNodeProps {
  node: TreeNode
  depth: number
  selectedPath: string | null
  onSelectFile: (path: string) => void
}

export function FileTreeNode({ node, depth, selectedPath, onSelectFile }: FileTreeNodeProps) {
  const isTopLevel = depth === 0
  const isDeepProject = node.name.startsWith('projects') ? false : depth >= 2
  const [expanded, setExpanded] = useState(isTopLevel && !isDeepProject)

  const indent = depth * 16 + 8

  if (node.type === 'file') {
    const isSelected = selectedPath === node.path
    return (
      <button
        onClick={() => onSelectFile(node.path)}
        className={cn(
          'w-full flex items-center gap-1.5 py-0.5 pr-2 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground transition-colors text-left',
          isSelected && 'bg-accent text-accent-foreground font-medium',
        )}
        style={{ paddingLeft: indent }}
      >
        <File className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <span className="flex-1 truncate">{node.name}</span>
        {node.tokens > 0 && (
          <span className="text-xs text-muted-foreground shrink-0">{node.tokens}</span>
        )}
      </button>
    )
  }

  // Directory
  return (
    <div>
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center gap-1.5 py-0.5 pr-2 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground transition-colors text-left"
        style={{ paddingLeft: indent }}
      >
        <ChevronRight
          className={cn(
            'h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform',
            expanded && 'rotate-90',
          )}
        />
        <Folder className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <span className="flex-1 truncate">{node.name}</span>
        {node.tokens > 0 && (
          <span className="text-xs text-muted-foreground shrink-0">{node.tokens}</span>
        )}
      </button>
      {expanded && node.children && (
        <FileTree
          nodes={node.children}
          depth={depth + 1}
          selectedPath={selectedPath}
          onSelectFile={onSelectFile}
        />
      )}
    </div>
  )
}
