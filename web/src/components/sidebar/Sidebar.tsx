import { useLocation, useNavigate } from 'react-router-dom'
import { Separator } from '@/components/ui/separator'
import { useTheme } from '@/hooks/useTheme'
import { useFileNavigation } from '@/hooks/useFileNavigation'
import { AiFileTree } from './AiFileTree'
import { InboxButton } from './InboxButton'
import { ThemeToggle } from './ThemeToggle'
import { useTree } from '@/hooks/useTree'

export function Sidebar() {
  const { treeData, inboxCount } = useTree()
  const { theme, toggleTheme } = useTheme()
  const navigateToFile = useFileNavigation()
  const navigate = useNavigate()
  const location = useLocation()

  const children = treeData?.children ?? []

  const selectedPath = location.pathname.startsWith('/file/')
    ? location.pathname.replace(/^\/file\//, '')
    : null

  const handleSelectFolder = (path: string) => {
    navigate(`/folder/${path.replace(/\/$/, '')}`)
  }

  return (
    <div className="w-72 h-full border-r flex flex-col shrink-0">
      <div className="flex-1 overflow-y-auto py-3 px-2">
        <div className="flex items-center justify-between px-2 mb-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Vault
          </p>
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
        <AiFileTree
          nodes={children}
          selectedPath={selectedPath}
          onSelectFile={navigateToFile}
          onSelectFolder={handleSelectFolder}
        />
      </div>
      <Separator />
      <div className="px-2 py-2">
        <InboxButton count={inboxCount} onClick={() => navigate('/inbox')} />
      </div>
    </div>
  )
}
