import { TreeProvider } from './contexts/TreeContext'
import { ChatProvider } from './contexts/ChatContext'
import { Sidebar } from './components/sidebar/Sidebar'
import { CentralZone } from './components/central/CentralZone'

function AppShell() {
  return (
    <div className="flex h-screen w-screen bg-background text-foreground overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <CentralZone />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <TreeProvider>
      <ChatProvider>
        <AppShell />
      </ChatProvider>
    </TreeProvider>
  )
}
