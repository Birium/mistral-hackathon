import { Separator } from '@/components/ui/separator'
import type { TreeNode } from '@/types'
import { FileTree } from './FileTree'
import { InboxButton } from './InboxButton'

interface SidebarProps {
  treeData: TreeNode | null
  inboxCount: number
  selectedPath: string | null
  onSelectFile: (path: string) => void
  onOpenInbox: () => void
}

export function Sidebar({
  treeData,
  inboxCount,
  selectedPath,
  onSelectFile,
  onOpenInbox,
}: SidebarProps) {
  const children = treeData?.children ?? []

  return (
    <div className="w-72 h-full border-r flex flex-col shrink-0">
      <div className="flex-1 overflow-y-auto py-3 px-2">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-2">
          Vault
        </p>
        <FileTree
          nodes={children}
          depth={0}
          selectedPath={selectedPath}
          onSelectFile={onSelectFile}
        />
      </div>
      <Separator />
      <div className="px-2 py-2">
        <InboxButton count={inboxCount} onClick={onOpenInbox} />
      </div>
    </div>
  )
}
