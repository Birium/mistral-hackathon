import { useState, useEffect, useCallback, useRef } from 'react'
import { toast } from 'sonner'
import type { ViewType, ChatMode, TreeNode, ActivityResult, InboxDetail } from './types'
import { fetchTree, fetchFile, fetchInboxDetail, sendUpdate, sendSearch } from './api'
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
    // rawPath may be an absolute path from the tree — derive relative vault path
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
    setPendingMessage(query)

    try {
      if (chatMode === 'search') {
        const res = await sendSearch(query)
        setActivityResult({
          type: 'search',
          content: res.answer,
          query,
        })
      } else {
        const ref = chatMode === 'answering' ? answeringRef ?? undefined : undefined
        const res = await sendUpdate(query, ref)
        setActivityResult({
          type: chatMode === 'answering' ? 'answering' : 'update',
          content: res.result,
          query,
        })
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
