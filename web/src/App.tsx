import { useState, useEffect, useCallback, useRef } from 'react'
import { toast } from 'sonner'
import type { ViewType, ChatMode, TreeNode, ActivityResult, InboxDetail, AgentEvent, AgentAnswerEvent } from './types'
import { fetchTree, fetchFile, fetchInboxDetail, streamSearch, streamUpdate } from './api'
import { useSSE } from './hooks/useSSE'
import { useTheme } from './hooks/useTheme'
import { Sidebar } from './components/sidebar/Sidebar'
import { CentralZone } from './components/central/CentralZone'
import { ChatInput } from './components/chat/ChatInput'

export default function App() {
  const { theme, toggleTheme } = useTheme()

  // ── Global state ──────────────────────────────────────────────────────────
  const [currentView, setCurrentView] = useState<ViewType>('home')
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const [chatMode, setChatMode] = useState<ChatMode>('update')
  const [answeringRef, setAnsweringRef] = useState<string | null>(null)
  const [treeData, setTreeData] = useState<TreeNode | null>(null)
  const [activityResult, setActivityResult] = useState<ActivityResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [inboxDetail, setInboxDetail] = useState<InboxDetail | null>(null)
  const [inboxDetailLoading, setInboxDetailLoading] = useState(false)
  const [inboxDetailError, setInboxDetailError] = useState<string | null>(null)
  const [chatValue, setChatValue] = useState('')
  const [focusTrigger, setFocusTrigger] = useState(0)
  const [pendingMessage, setPendingMessage] = useState<string | null>(null)
  const [streamEvents, setStreamEvents] = useState<AgentEvent[]>([])

  // ── Derived ───────────────────────────────────────────────────────────────
  const inboxItems =
    treeData?.children?.find((n) => n.name === 'inbox/' || n.name === 'inbox')?.children ?? []
  const inboxCount = inboxItems.length

  // ── Tree fetching ─────────────────────────────────────────────────────────
  const refetchTree = useCallback(async () => {
    try {
      const tree = await fetchTree()
      setTreeData(tree)
    } catch {
      // silently ignore tree fetch errors
    }
  }, [])

  // Fetch tree on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { refetchTree() }, [])

  // ── SSE ───────────────────────────────────────────────────────────────────
  const currentFileRef = useRef(selectedFilePath)
  currentFileRef.current = selectedFilePath

  useSSE({
    onTreeChange: refetchTree,
    onFileChange: (path) => {
      if (currentFileRef.current && path.endsWith(currentFileRef.current)) {
        fetchFile(currentFileRef.current)
          .then((data) => setFileContent(data.content))
          .catch(() => {})
      }
    },
  })

  // ── Callbacks ─────────────────────────────────────────────────────────────
  const onSelectFile = useCallback(async (rawPath: string) => {
    const vaultMarker = '/vault/'
    const idx = rawPath.indexOf(vaultMarker)
    const relPath = idx !== -1 ? rawPath.slice(idx + vaultMarker.length) : rawPath

    setSelectedFilePath(relPath)
    setFileContent(null)
    setCurrentView('file')
    try {
      const data = await fetchFile(relPath)
      setFileContent(data.content)
    } catch (e) {
      setFileContent(`Error: could not load file.\n${e}`)
    }
  }, [])

  const onOpenInbox = useCallback(() => {
    setCurrentView('inbox-list')
  }, [])

  const onOpenInboxDetail = useCallback(async (name: string) => {
    setCurrentView('inbox-detail')
    setInboxDetail(null)
    setInboxDetailError(null)
    setInboxDetailLoading(true)
    try {
      const detail = await fetchInboxDetail(name)
      setInboxDetail(detail)
    } catch (e: unknown) {
      setInboxDetailError(e instanceof Error ? e.message : String(e))
    } finally {
      setInboxDetailLoading(false)
    }
  }, [])

  const onBackToInboxList = useCallback(() => {
    setCurrentView('inbox-list')
  }, [])

  const onReply = useCallback((name: string) => {
    setChatMode('answering')
    setAnsweringRef(name)
    setFocusTrigger((t) => t + 1)
  }, [])

  const onCancelReply = useCallback(() => {
    setChatMode('update')
    setAnsweringRef(null)
  }, [])

  const onModeChange = useCallback((mode: 'update' | 'search') => {
    setChatMode(mode)
    setAnsweringRef(null)
  }, [])

  const handleSendMessage = useCallback(async () => {
    const query = chatValue.trim()
    if (!query) return

    setChatValue('')
    setCurrentView('activity')
    setIsLoading(true)
    setError(null)
    setActivityResult(null)
    setStreamEvents([])
    setPendingMessage(query)

    const collected: AgentEvent[] = []

    const onEvent = (event: AgentEvent) => {
      if (event.type === 'done') return
      collected.push(event)
      setStreamEvents((prev) => [...prev, event])
    }

    try {
      if (chatMode === 'search') {
        await streamSearch(query, onEvent)

        const finalEvent = collected
          .filter((e): e is AgentAnswerEvent => e.type === 'answer')
          .find((e) => e.id === 'final')

        setActivityResult({
          type: 'search',
          content: finalEvent?.content ?? '',
          query,
        })
      } else {
        const ref = chatMode === 'answering' ? answeringRef ?? undefined : undefined
        await streamUpdate(query, onEvent, ref)

        const content = collected
          .filter((e): e is AgentAnswerEvent => e.type === 'answer' && !e.tool_calls?.length)
          .map((e) => e.content)
          .join('')

        setActivityResult({
          type: chatMode === 'answering' ? 'answering' : 'update',
          content,
          query,
        })

        toast.success(chatMode === 'answering' ? 'Reply sent' : 'Update complete')

        if (chatMode === 'answering') {
          setChatMode('update')
          setAnsweringRef(null)
        }
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
      toast.error(msg)
    } finally {
      setIsLoading(false)
      setPendingMessage(null)
    }
  }, [chatValue, chatMode, answeringRef])

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen w-screen bg-background text-foreground overflow-hidden">
      <Sidebar
        treeData={treeData}
        inboxCount={inboxCount}
        selectedPath={selectedFilePath}
        onSelectFile={onSelectFile}
        onOpenInbox={onOpenInbox}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <div className="flex-1 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto pb-40">
          <CentralZone
            currentView={currentView}
            selectedFilePath={selectedFilePath}
            fileContent={fileContent}
            isLoading={isLoading}
            error={error}
            activityResult={activityResult}
            chatMode={chatMode}
            pendingMessage={pendingMessage}
            streamEvents={streamEvents}
            inboxItems={inboxItems}
            inboxDetail={inboxDetail}
            inboxDetailLoading={inboxDetailLoading}
            inboxDetailError={inboxDetailError}
            onSelectFile={onSelectFile}
            onOpenInboxDetail={onOpenInboxDetail}
            onBackToInboxList={onBackToInboxList}
            onReply={onReply}
          />
        </div>

        <ChatInput
          value={chatValue}
          onChange={setChatValue}
          onSend={handleSendMessage}
          chatMode={chatMode}
          onModeChange={onModeChange}
          answeringRef={answeringRef}
          onCancelReply={onCancelReply}
          disabled={isLoading}
          focusTrigger={focusTrigger}
        />
      </div>
    </div>
  )
}