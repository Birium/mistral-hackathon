import { Routes, Route } from 'react-router-dom'
import { AIPromptInput } from '@/components/ai-components/ai-prompt-input'
import { HomeView } from './HomeView'
import { ActivityView } from './ActivityView'
import { InboxListView } from './InboxListView'
import { InboxDetailView } from './InboxDetailView'
import { FolderView } from './FolderView'
import { useChat } from '@/hooks/useChat'
import { FileView } from './FileView'
import { BreadCrumbsLayout } from '../shared/BreadCrumbsLayout'

export function CentralZone() {
  const {
    chatValue,
    setChatValue,
    chatMode,
    answeringRef,
    isLoading,
    focusTrigger,
    handleSendMessage,
    onModeChange,
    onCancelReply,
  } = useChat()

  return (
    <>
      <div className="flex-1 overflow-y-auto pb-40">
        <div className="flex flex-col items-center min-h-full">
          <Routes>
            <Route path="/" element={<HomeView />} />
            <Route path="/file/*" element={<BreadCrumbsLayout><FileView /></BreadCrumbsLayout>} />
            <Route path="/folder/*" element={<BreadCrumbsLayout><FolderView /></BreadCrumbsLayout>} />
            <Route path="/activity" element={<ActivityView />} />
            <Route path="/inbox" element={<InboxListView />} />
            <Route path="/inbox/:name" element={<InboxDetailView />} />
          </Routes>
        </div>
      </div>

      <AIPromptInput
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
    </>
  )
}
