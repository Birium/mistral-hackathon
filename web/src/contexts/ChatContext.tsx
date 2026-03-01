import { createContext } from 'react'
import type { ChatMode, ActivityResult, AgentEvent } from '@/types'

export interface ChatContextValue {
  chatValue: string
  setChatValue: (v: string) => void
  chatMode: ChatMode
  answeringRef: string | null
  isLoading: boolean
  error: string | null
  activityResult: ActivityResult | null
  pendingMessage: string | null
  streamEvents: AgentEvent[]
  focusTrigger: number
  handleSendMessage: () => Promise<void>
  onReply: (name: string) => void
  onCancelReply: () => void
  onModeChange: (mode: 'update' | 'search') => void
}

export const ChatContext = createContext<ChatContextValue | null>(null)
