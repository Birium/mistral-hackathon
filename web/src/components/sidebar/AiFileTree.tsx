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

function TokenBadge({ tokens }: { tokens: number }) {
  if (tokens <= 0) return null
  return <span className="ml-auto text-xs text-muted-foreground shrink-0">{tokens}</span>
}

function renderNodes(nodes: TreeNode[]): React.ReactNode {
  return nodes.map((node) => {
    if (node.type === 'directory') {
      return (
        <FileTreeFolder
          key={node.path}
          path={node.path}
          name={node.name}
          label={<TokenBadge tokens={node.tokens} />}
        >
          {renderNodes(node.children ?? [])}
        </FileTreeFolder>
      )
    }
    return (
      <FileTreeFile
        key={node.path}
        path={node.path}
        name={node.name}
        label={<TokenBadge tokens={node.tokens} />}
      />
    )
  })
}

export function AiFileTree({ nodes, selectedPath, onSelectFile }: AiFileTreeProps) {
  const defaultExpanded = new Set(
    nodes.filter((n) => n.type === 'directory').map((n) => n.path),
  )

  return (
    <FileTree
      defaultExpanded={defaultExpanded}
      selectedPath={selectedPath ?? undefined}
      onSelect={onSelectFile}
      className="border-none rounded-none bg-transparent p-0 font-sans text-sm"
    >
      {renderNodes(nodes)}
    </FileTree>
  )
}
