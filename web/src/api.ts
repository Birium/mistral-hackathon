import type { TreeNode, InboxDetail, AgentEvent } from './types'

async function throwIfNotOk(res: Response): Promise<Response> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res
}

async function consumeStream(
  response: Response,
  onEvent: (event: AgentEvent) => void,
): Promise<void> {
  const body = response.body
  if (!body) return

  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // Split on newlines — the last element might be an incomplete line
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      try {
        const event = JSON.parse(trimmed) as AgentEvent
        onEvent(event)
      } catch {
        console.warn('[stream] failed to parse line:', trimmed)
      }
    }
  }

  // Handle any remaining data in the buffer after stream closes
  if (buffer.trim()) {
    try {
      const event = JSON.parse(buffer.trim()) as AgentEvent
      onEvent(event)
    } catch {
      console.warn('[stream] failed to parse trailing buffer:', buffer)
    }
  }
}

export async function streamSearch(
  query: string,
  onEvent: (event: AgentEvent) => void,
): Promise<void> {
  const response = await throwIfNotOk(
    await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query }),
    }),
  )
  await consumeStream(response, onEvent)
}

export async function streamUpdate(
  query: string,
  onEvent: (event: AgentEvent) => void,
  inboxRef?: string,
): Promise<void> {
  const response = await throwIfNotOk(
    await fetch('/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query, inbox_ref: inboxRef ?? null }),
    }),
  )
  await consumeStream(response, onEvent)
}

export async function fetchTree(): Promise<TreeNode> {
  const res = await throwIfNotOk(await fetch('/tree'))
  const data = await res.json()
  return data.tree
}

export async function fetchFile(path: string): Promise<{ path: string; content: string }> {
  const res = await throwIfNotOk(await fetch(`/file?path=${encodeURIComponent(path)}`))
  return res.json()
}

export async function fetchInboxDetail(name: string): Promise<InboxDetail> {
  const res = await throwIfNotOk(await fetch(`/inbox/${encodeURIComponent(name)}`))
  return res.json()
}