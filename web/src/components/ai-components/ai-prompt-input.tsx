import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputTextarea,
  PromptInputTools,
  type PromptInputMessage,
} from '@/components/ai-elements/prompt-input'
import type { ChatMode } from '@/types'
import { ModeToggle } from '@/components/chat/ModeToggle'
import { AnsweringBanner } from '@/components/chat/AnsweringBanner'

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

export function AIPromptInput({
  value,
  onChange,
  onSend,
  chatMode,
  onModeChange,
  answeringRef,
  onCancelReply,
  disabled,
}: ChatInputProps) {

  function handleSubmit(_message: PromptInputMessage) {
    onSend()
  }

  return (
    <div
      className="space-y-6"
    >
      {chatMode === 'answering' && answeringRef && (
        <AnsweringBanner answeringRef={answeringRef} onCancel={onCancelReply} />
      )}
      <PromptInput onSubmit={handleSubmit} className="max-w-2xl">
        <PromptInputBody>
          <PromptInputTextarea
            value={value}
            placeholder={chatMode === 'search' ? 'Search the vault...' : 'Send an update...'}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
          />
        </PromptInputBody>
        <PromptInputFooter>
          <PromptInputTools>
            <ModeToggle
              mode={chatMode}
              onChange={onModeChange}
              disabled={chatMode === 'answering'}
            />
          </PromptInputTools>
        </PromptInputFooter>
      </PromptInput>
    </div>
  )
}
