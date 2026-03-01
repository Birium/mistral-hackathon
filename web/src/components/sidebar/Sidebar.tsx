import { Separator } from '@/components/ui/separator'
import type { TreeNode } from '@/types'
import { AiFileTree } from './AiFileTree'
import { InboxButton } from './InboxButton'
import { ThemeToggle } from './ThemeToggle'

interface SidebarProps {
  treeData: TreeNode | null
  inboxCount: number
  selectedPath: string | null
  onSelectFile: (path: string) => void
  onOpenInbox: () => void
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function Sidebar({
  treeData,
  inboxCount,
  selectedPath,
  onSelectFile,
  onOpenInbox,
  theme,
  onToggleTheme,
}: SidebarProps) {
  const children = treeData?.children ?? []

  return (
    <div className="w-72 h-full border-r flex flex-col shrink-0">
      <div className="flex-1 overflow-y-auto py-3 px-2">
        <div className="flex items-center justify-between px-2 mb-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Vault
          </p>
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </div>
        <AiFileTree
          nodes={children}
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
