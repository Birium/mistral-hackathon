export interface TreeNode {
  name: string
  path: string
  type: 'file' | 'directory'
  tokens: number
  updated_at: string | null
  children?: TreeNode[] | null
}

export interface InboxDetail {
  name: string
  review: string
  input_files: string[]
}

export type ChatMode = 'update' | 'search' | 'answering'

export type ViewType = 'home' | 'file' | 'activity' | 'inbox-list' | 'inbox-detail'

export interface ActivityResult {
  type: 'update' | 'search' | 'answering'
  content: string
  touched_files?: string[]
  query?: string
}

export interface SSEEvent {
  type: string
  path?: string
}
