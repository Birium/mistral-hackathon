import { useEffect } from 'react'
import type { SSEEvent } from '../types'

interface UseSSEOptions {
  onTreeChange: () => void
  onFileChange: (path: string) => void
}

export function useSSE({ onTreeChange, onFileChange }: UseSSEOptions) {
  useEffect(() => {
    let es: EventSource
    let retryTimer: ReturnType<typeof setTimeout>

    function connect() {
      es = new EventSource('/sse')

      es.onmessage = (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data)
          const fileEvents = ['file_changed', 'file_created', 'file_deleted']
          if (fileEvents.includes(data.type)) {
            onTreeChange()
            if (data.path) {
              onFileChange(data.path)
            }
          }
        } catch {
          // ignore parse errors
        }
      }

      es.onerror = () => {
        es.close()
        retryTimer = setTimeout(connect, 3000)
      }
    }

    connect()

    return () => {
      es?.close()
      clearTimeout(retryTimer)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
