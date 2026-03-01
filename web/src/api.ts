import type { TreeNode, InboxDetail } from './types'

async function throwIfNotOk(res: Response): Promise<Response> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res
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

export async function sendUpdate(
  query: string,
  inboxRef?: string,
): Promise<{ status: string; result: string }> {
  const res = await throwIfNotOk(
    await fetch('/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query, inbox_ref: inboxRef ?? null }),
    }),
  )
  return res.json()
}

export async function sendSearch(query: string): Promise<{ queries: string[]; answer: string }> {
  const res = await throwIfNotOk(
    await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_query: query }),
    }),
  )
  return res.json()
}
