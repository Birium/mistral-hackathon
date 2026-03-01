import { useRef, useEffect } from 'react'
import { ArrowUp, Paperclip } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ChatMode } from '@/types'
import { ModeToggle } from './ModeToggle'
import { AnsweringBanner } from './AnsweringBanner'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  chatMode: ChatMode
  onModeChange: (mode: 'update' | 'search') => void
  answeringRef: string | null
  onCancelReply: () => void
  disabled?: boolean
  focusTrigger?: number
}

export function ChatInput({
  value,
  onChange,
  onSend,
  chatMode,
  onModeChange,
  answeringRef,
  onCancelReply,
  disabled,
  focusTrigger,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const canSend = value.trim().length > 0 && !disabled

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
  }, [value])

  // Focus when focusTrigger changes (e.g. after clicking Reply)
  useEffect(() => {
    if (focusTrigger !== undefined && focusTrigger > 0) {
      textareaRef.current?.focus()
    }
  }, [focusTrigger])

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (canSend) onSend()
    }
  }

  return (
    <div
      className="fixed bottom-6 z-20 max-w-2xl"
      style={{ left: 'calc(18rem + 2rem)', right: '1.5rem' }}
    >
      <div className="max-w-3xl mx-auto bg-background/80 backdrop-blur-md border shadow-lg rounded-xl overflow-hidden">
      {chatMode === 'answering' && answeringRef && (
        <AnsweringBanner answeringRef={answeringRef} onCancel={onCancelReply} />
      )}
      <div className="flex items-end gap-2 px-3 py-2">
        <ModeToggle
          mode={chatMode}
          onChange={onModeChange}
          disabled={chatMode === 'answering'}
        />
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={
            chatMode === 'search'
              ? 'Search the vault...'
              : 'Send an update...'
          }
          className={cn(
            'flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground py-1 max-h-[200px] leading-relaxed',
            disabled && 'opacity-50',
          )}
        />
        <button
          disabled={!canSend}
          onClick={onSend}
          className={cn(
            'shrink-0 rounded-full h-8 w-8 flex items-center justify-center transition-colors',
            canSend ? 'bg-primary text-primary-foreground hover:opacity-90' : 'bg-muted text-muted-foreground cursor-not-allowed',
          )}
        >
          <ArrowUp className="h-4 w-4" />
        </button>
        <button
          disabled
          className="shrink-0 rounded-full h-8 w-8 flex items-center justify-center bg-muted text-muted-foreground cursor-not-allowed opacity-50"
          title="Attachment (unavailable)"
        >
          <Paperclip className="h-4 w-4" />
        </button>
      </div>
      </div>
    </div>
  )
}
