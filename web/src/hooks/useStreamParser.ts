import { useMemo } from 'react'
import { useChat } from '@/hooks/useChat'
import {
  parseStreamEvents,
  deriveHeaderText,
  getToolIcon,
  type DisplayItem,
  type ToolItem,
} from '@/lib/parseStreamEvents'
import type { LucideIcon } from 'lucide-react'

interface StreamParserResult {
  /** Parsed display items derived from raw stream events. */
  items: DisplayItem[]
  /** Dynamic header text reflecting the current activity. */
  headerText: string
  /** Icon of the currently running tool, if any. */
  activeToolIcon: LucideIcon | null
  /** Total number of tool calls (running + done + error). */
  toolCount: number
}

/**
 * Reactive hook that transforms raw `streamEvents` from ChatContext
 * into structured display items for the ChainOfThought UI.
 *
 * All derived values are memoised — recomputed only when
 * `streamEvents` or `isLoading` change.
 */
export function useStreamParser(): StreamParserResult {
  const { streamEvents, isLoading } = useChat()

  const items = useMemo(
    () => parseStreamEvents(streamEvents),
    [streamEvents],
  )

  const headerText = useMemo(
    () => deriveHeaderText(items, isLoading),
    [items, isLoading],
  )

  const activeToolIcon = useMemo<LucideIcon | null>(() => {
    const runningTool = [...items]
      .reverse()
      .find((i): i is ToolItem => i.kind === 'tool' && i.status === 'running')
    return runningTool ? getToolIcon(runningTool.name) : null
  }, [items])

  const toolCount = useMemo(
    () => items.filter((i) => i.kind === 'tool').length,
    [items],
  )

  return { items, headerText, activeToolIcon, toolCount }
}