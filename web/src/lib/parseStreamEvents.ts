import {
    Brain,
    FileText,
    FolderTree,
    Pencil,
    Search,
    Layers,
    Wrench,
    BarChart2,
    AlertTriangle,
  } from 'lucide-react'
  import type { LucideIcon } from 'lucide-react'
  import type { AgentEvent } from '@/types'
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Display item types
  // ─────────────────────────────────────────────────────────────────────────────
  
  export type ThinkItem = { kind: 'think'; content: string }
  
  export type ToolItem = {
    kind: 'tool'
    name: string
    args: string
    status: 'running' | 'done' | 'error'
    result?: string
  }
  
  export type UsageItem = {
    kind: 'usage'
    prompt_tokens: number
    completion_tokens: number
    total_cost: number
  }
  
  export type ErrorItem = { kind: 'error'; content: string }
  
  export type DisplayItem = ThinkItem | ToolItem | UsageItem | ErrorItem
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Argument helpers
  // ─────────────────────────────────────────────────────────────────────────────
  
  /**
   * Parse a tool's JSON arguments string into an object.
   * Returns null if the string is empty or invalid JSON.
   */
  export function parseArgs(argsStr: string): Record<string, unknown> | null {
    if (!argsStr) return null
    try {
      const parsed = JSON.parse(argsStr)
      return typeof parsed === 'object' && parsed !== null ? parsed : null
    } catch {
      return null
    }
  }
  
  /**
   * Format tool arguments as a compact, human-readable string.
   * Values are shown in full — no truncation.
   */
  export function formatArgs(argsStr: string): string {
    if (!argsStr) return ''
    const args = parseArgs(argsStr)
    if (!args) return argsStr
    const entries = Object.entries(args)
    if (entries.length === 0) return ''
    return entries
      .map(([k, v]) => {
        const val = typeof v === 'object' ? JSON.stringify(v) : String(v)
        return `${k}: ${val}`
      })
      .join(' · ')
  }
  
  /**
   * Extract file paths referenced as code-fence headers in a tool result.
   * Matches patterns like: ```path/to/file.md
   */
  export function extractFilePaths(result: string): string[] {
    if (!result) return []
    const fencePattern = /^```([^\s`]+\.\w+)/gm
    const paths: string[] = []
    let match: RegExpExecArray | null
    while ((match = fencePattern.exec(result)) !== null) {
      paths.push(match[1])
    }
    return paths
  }
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Icon mapping
  // ─────────────────────────────────────────────────────────────────────────────
  
  const TOOL_ICON_MAP: Record<string, LucideIcon> = {
    read: FileText,
    tree: FolderTree,
    write: Pencil,
    patch: Pencil,
    search: Search,
    grep: Search,
    concat: Layers,
  }
  
  export function getToolIcon(toolName: string): LucideIcon {
    return TOOL_ICON_MAP[toolName] ?? Wrench
  }
  
  export function getItemIcon(item: DisplayItem): LucideIcon {
    switch (item.kind) {
      case 'think':   return Brain
      case 'tool':    return getToolIcon(item.name)
      case 'usage':   return BarChart2
      case 'error':   return AlertTriangle
    }
  }
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Core parser — AgentEvent[] → DisplayItem[]
  // ─────────────────────────────────────────────────────────────────────────────
  
  function stripThinkTags(content: string): string {
    return content.replace(/<\/?think>\n?/g, '')
  }
  
  export function parseStreamEvents(events: AgentEvent[]): DisplayItem[] {
    const items: DisplayItem[] = []
  
    for (const event of events) {
      if (event.type === 'done') continue
      if (event.type === 'answer') continue
  
      // ── Think ────────────────────────────────────────────────────────────
      if (event.type === 'think') {
        const stripped = stripThinkTags(event.content)
        if (!stripped) continue
        const last = items[items.length - 1]
        if (last?.kind === 'think') {
          last.content += stripped
        } else {
          items.push({ kind: 'think', content: stripped })
        }
        continue
      }
  
      // ── Tool lifecycle ────────────────────────────────────────────────────
      if (event.type === 'tool') {
        if (event.status === 'start') {
          items.push({ kind: 'tool', name: event.name, args: event.arguments, status: 'running' })
          continue
        }
        if (event.status === 'end' || event.status === 'error') {
          const match = [...items]
            .reverse()
            .find(
              (i): i is ToolItem =>
                i.kind === 'tool' && i.name === event.name && i.status === 'running',
            )
          if (match) {
            match.status = event.status === 'end' ? 'done' : 'error'
            match.result = event.result ?? undefined
          }
          continue
        }
      }
  
      // ── Usage ─────────────────────────────────────────────────────────────
      if (event.type === 'usage') {
        items.push({
          kind: 'usage',
          prompt_tokens: event.prompt_tokens,
          completion_tokens: event.completion_tokens,
          total_cost: event.total_cost,
        })
        continue
      }
  
      // ── Error ─────────────────────────────────────────────────────────────
      if (event.type === 'error') {
        items.push({ kind: 'error', content: event.content })
        continue
      }
    }
  
    return items
  }
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Header text derivation
  // ─────────────────────────────────────────────────────────────────────────────
  
  const TOOL_LABEL_MAP: Record<string, string> = {
    read: 'Reading',
    search: 'Searching',
    concat: 'Assembling files',
    write: 'Writing',
    edit: 'Editing',
    append: 'Appending',
    move: 'Moving',
    delete: 'Deleting',
  }
  
  export function deriveHeaderText(items: DisplayItem[], isLoading: boolean): string {
    if (items.length === 0) {
      return isLoading ? 'Thinking…' : 'Chain of thought'
    }
  
    if (isLoading) {
      // Mirror the icon logic: follow the last meaningful step, skip usage events
      const last = [...items].reverse().find((i) => i.kind !== 'usage')
  
      if (last?.kind === 'tool') {
        const base = TOOL_LABEL_MAP[last.name] ?? `Calling ${last.name}`
  
        // For file operations, append the filename(s) for extra context
        if (['read', 'write', 'patch', 'concat'].includes(last.name)) {
          const args = parseArgs(last.args)
          const paths = args?.paths as string[] | undefined
          const path = args?.path as string | undefined
          const targets = paths ?? (path ? [path] : [])
  
          if (targets.length > 0) {
            const firstName = (targets[0] as string).split('/').pop()
            return targets.length > 1
              ? `${base} · ${firstName} +${targets.length - 1}`
              : `${base} · ${firstName}`
          }
        }
  
        return base
      }
  
      if (last?.kind === 'think') return 'Thinking…'
  
      return 'Working…'
    }
  
    // Done — summary
    const toolCount = items.filter((i) => i.kind === 'tool').length
    if (toolCount === 0) return 'Thought'
    if (toolCount === 1) return 'Thought · 1 tool call'
    return `Thought · ${toolCount} tool calls`
  }