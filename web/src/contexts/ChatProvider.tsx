import { useState, useCallback, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import type { ChatMode, ActivityResult, AgentEvent, AgentAnswerEvent } from '@/types'
import { streamSearch, streamUpdate } from '@/api'
import { ChatContext } from './ChatContext'

export function ChatProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()

  const [chatValue, setChatValue] = useState('')
  const [chatMode, setChatMode] = useState<ChatMode>('update')
  const [answeringRef, setAnsweringRef] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activityResult, setActivityResult] = useState<ActivityResult | null>(null)
  const [pendingMessage, setPendingMessage] = useState<string | null>(null)
  const [streamEvents, setStreamEvents] = useState<AgentEvent[]>([])
  const [focusTrigger, setFocusTrigger] = useState(0)

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
    navigate('/activity')
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
  }, [chatValue, chatMode, answeringRef, navigate])

  return (
    <ChatContext.Provider
      value={{
        chatValue,
        setChatValue,
        chatMode,
        answeringRef,
        isLoading,
        error,
        activityResult,
        pendingMessage,
        streamEvents,
        focusTrigger,
        handleSendMessage,
        onReply,
        onCancelReply,
        onModeChange,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}
