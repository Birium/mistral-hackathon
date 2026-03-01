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
    <div className="absolute bottom-0 left-0 right-0 flex flex-col justify-center items-center gap-2 px-4 pb-4 pt-12">
      <div className="w-full max-w-2xl pointer-events-auto flex flex-col gap-2 bg-background">
        {chatMode === 'answering' && answeringRef && (
          <AnsweringBanner answeringRef={answeringRef} onCancel={onCancelReply} />
        )}
        <PromptInput onSubmit={handleSubmit} className="w-full shadow-lg">
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
    </div>
  )
}
