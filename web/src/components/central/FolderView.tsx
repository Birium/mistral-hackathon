import { useLocation, useNavigate } from 'react-router-dom'
import { ChevronRight, Folder, FileText } from 'lucide-react'
import type { TreeNode } from '@/types'
import { useTree } from '@/contexts/TreeContext'

function normalizePath(p: string): string {
  return p.replace(/\/+$/, '')
}

function pathMatches(absolutePath: string, relativePath: string): boolean {
  const a = normalizePath(absolutePath)
  const r = normalizePath(relativePath)
  return a === r || a.endsWith(`/${r}`)
}

function findNode(nodes: TreeNode[], targetPath: string): TreeNode | null {
  for (const node of nodes) {
    if (pathMatches(node.path, targetPath)) return node
    if (node.type === 'directory' && node.children) {
      const found = findNode(node.children, targetPath)
      if (found) return found
    }
  }
  return null
}

/** Extract the relative portion of an absolute tree path */
function toRelativePath(absolutePath: string, tree: TreeNode[]): string {
  if (tree.length === 0) return normalizePath(absolutePath)
  // Detect the vault root from the first node
  const firstPath = normalizePath(tree[0].path)
  const firstName = tree[0].name.replace(/\/$/, '')
  const root = firstPath.endsWith(firstName)
    ? firstPath.slice(0, -(firstName.length))
    : ''
  const normalized = normalizePath(absolutePath)
  return root && normalized.startsWith(root)
    ? normalized.slice(root.length)
    : normalized
}

export function FolderView() {
  const location = useLocation()
  const navigate = useNavigate()
  const { tree } = useTree()

  const folderPath = location.pathname.replace(/^\/folder\//, '')
  const segments = folderPath.split('/').filter(Boolean)

  const folderNode = tree.length > 0 ? findNode(tree, folderPath) : null

  const handleItemClick = (node: TreeNode) => {
    const rel = toRelativePath(node.path, tree)
    if (node.type === 'directory') {
      navigate(`/folder/${rel}`)
    } else {
      navigate(`/file/${rel}`)
    }
  }

  return (
    <div className="h-full overflow-y-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground mb-6 flex-wrap">
        {segments.map((seg, i) => {
          const isLast = i === segments.length - 1
          const segPath = segments.slice(0, i + 1).join('/')
          return (
            <span key={segPath} className="flex items-center gap-1">
              {i > 0 && <ChevronRight className="h-3.5 w-3.5" />}
              {isLast ? (
                <span className="text-foreground font-medium">{seg}</span>
              ) : (
                <button
                  onClick={() => navigate(`/folder/${segPath}`)}
                  className="hover:text-foreground transition-colors"
                >
                  {seg}
                </button>
              )}
            </span>
          )
        })}
      </nav>

      {!folderNode ? (
        <p className="text-muted-foreground text-sm">Folder not found.</p>
      ) : !folderNode.children?.length ? (
        <p className="text-muted-foreground text-sm">This folder is empty.</p>
      ) : (
        <ul className="space-y-1">
          {folderNode.children
            .slice()
            .sort((a, b) => {
              if (a.type === b.type) return a.name.localeCompare(b.name)
              return a.type === 'directory' ? -1 : 1
            })
            .map((child) => (
              <li key={child.path}>
                <button
                  onClick={() => handleItemClick(child)}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 rounded-md text-sm hover:bg-muted transition-colors"
                >
                  {child.type === 'directory' ? (
                    <Folder className="h-4 w-4 text-muted-foreground shrink-0" />
                  ) : (
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                  )}
                  <span>{child.name}</span>
                </button>
              </li>
            ))}
        </ul>
      )}
    </div>
  )
}
