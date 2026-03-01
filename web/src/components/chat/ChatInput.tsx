import { useRef, useEffect, useState } from 'react'
import { ArrowUp, Loader2, Mic, Paperclip, Square } from 'lucide-react'
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
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)

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

  async function toggleRecording() {
    if (isRecording) {
      mediaRecorderRef.current?.stop()
      streamRef.current?.getTracks().forEach((t) => t.stop())
      setIsRecording(false)
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      chunksRef.current = []

      const mr = new MediaRecorder(stream)
      mediaRecorderRef.current = mr

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setIsTranscribing(true)
        try {
          const form = new FormData()
          form.append('audio', blob, 'audio.webm')
          const resp = await fetch('/transcribe', { method: 'POST', body: form })
          if (!resp.ok) throw new Error(await resp.text())
          const { text } = await resp.json()
          if (text) onChange(value ? value + ' ' + text : text)
        } catch (err) {
          console.error('Transcription failed:', err)
        } finally {
          setIsTranscribing(false)
        }
      }

      mr.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Microphone access denied:', err)
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
          onClick={toggleRecording}
          disabled={isTranscribing || disabled}
          className={cn(
            'shrink-0 rounded-full h-8 w-8 flex items-center justify-center transition-colors',
            isRecording
              ? 'bg-destructive text-destructive-foreground animate-pulse'
              : isTranscribing
              ? 'bg-muted text-muted-foreground cursor-wait'
              : 'bg-muted text-muted-foreground hover:bg-accent',
          )}
          title={isRecording ? 'Stop recording' : 'Voice input'}
        >
          {isTranscribing
            ? <Loader2 className="h-4 w-4 animate-spin" />
            : isRecording
            ? <Square className="h-3 w-3 fill-current" />
            : <Mic className="h-4 w-4" />}
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
