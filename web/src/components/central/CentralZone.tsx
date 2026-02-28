import type { ViewType, ActivityResult, InboxDetail, ChatMode, TreeNode } from '@/types'
import { HomeView } from './HomeView'
import { FileView } from './FileView'
import { ActivityView } from './ActivityView'
import { InboxListView } from './InboxListView'
import { InboxDetailView } from './InboxDetailView'

interface CentralZoneProps {
  currentView: ViewType
  // file view
  selectedFilePath: string | null
  fileContent: string | null
  // activity view
  isLoading: boolean
  error: string | null
  activityResult: ActivityResult | null
  chatMode: ChatMode
  // inbox
  inboxItems: TreeNode[]
  inboxDetail: InboxDetail | null
  inboxDetailLoading: boolean
  inboxDetailError: string | null
  // callbacks
  onSelectFile: (path: string) => void
  onOpenInboxDetail: (name: string) => void
  onBackToInboxList: () => void
  onReply: (name: string) => void
}

export function CentralZone({
  currentView,
  selectedFilePath,
  fileContent,
  isLoading,
  error,
  activityResult,
  chatMode,
  inboxItems,
  inboxDetail,
  inboxDetailLoading,
  inboxDetailError,
  onSelectFile,
  onOpenInboxDetail,
  onBackToInboxList,
  onReply,
}: CentralZoneProps) {
  return (
    <div className="px-8 py-6 h-full">
      {currentView === 'home' && <HomeView />}

      {currentView === 'file' && selectedFilePath && fileContent !== null && (
        <FileView
          path={selectedFilePath}
          content={fileContent}
          onNavigate={onSelectFile}
        />
      )}

      {currentView === 'activity' && (
        <ActivityView
          isLoading={isLoading}
          error={error}
          result={activityResult}
          chatMode={chatMode}
          onSelectFile={onSelectFile}
        />
      )}

      {currentView === 'inbox-list' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Inbox</h2>
          <InboxListView items={inboxItems} onOpenDetail={onOpenInboxDetail} />
        </div>
      )}

      {currentView === 'inbox-detail' && (
        <InboxDetailView
          detail={inboxDetail}
          loading={inboxDetailLoading}
          error={inboxDetailError}
          onBack={onBackToInboxList}
          onReply={onReply}
          onSelectFile={onSelectFile}
        />
      )}
    </div>
  )
}
