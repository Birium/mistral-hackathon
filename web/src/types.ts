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

export interface AgentThinkEvent {
  type: 'think'
  id: string
  content: string
}

export interface AgentAnswerEvent {
  type: 'answer'
  id: string
  content: string
  tool_calls?: Array<{ id: string; type: string; function: { name: string; arguments: string } }>
}

export interface AgentToolEvent {
  type: 'tool'
  id: string
  tool_id: string
  name: string
  arguments: string
  status: 'start' | 'end' | 'error'
  result?: string
}

export interface AgentUsageEvent {
  type: 'usage'
  id: string
  usage_type: string
  prompt_tokens: number
  completion_tokens: number
  input_cost: number
  output_cost: number
  total_cost: number
}

export interface AgentErrorEvent {
  type: 'error'
  id: string
  content: string
}

export interface AgentDoneEvent {
  type: 'done'
}

export type AgentEvent =
  | AgentThinkEvent
  | AgentAnswerEvent
  | AgentToolEvent
  | AgentUsageEvent
  | AgentErrorEvent
  | AgentDoneEvent