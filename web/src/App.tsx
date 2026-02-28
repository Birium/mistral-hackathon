import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

type SearchResponse = {
  queries: string[]
  answer: string
}

type UpdateResponse = {
  status: string
  result: string
}

export default function App() {
  const [tree, setTree] = useState<string>("")
  const [lastEvent, setLastEvent] = useState<string>("None")

  // Update state
  const [updateContent, setUpdateContent] = useState("")
  const [updateResponse, setUpdateResponse] = useState<UpdateResponse | null>(null)
  const [updateError, setUpdateError] = useState("")
  const [isUpdating, setIsUpdating] = useState(false)

  // Search state
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [searchError, setSearchError] = useState("")
  const [isSearching, setIsSearching] = useState(false)

  const fetchTree = async () => {
    try {
      const res = await fetch("/tree")
      if (res.ok) {
        const data = await res.json()
        setTree(data.tree)
      }
    } catch (err) {
      console.error("Failed to fetch tree", err)
    }
  }

  useEffect(() => {
    fetchTree()

    const eventSource = new EventSource("/sse")

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastEvent(data.type ?? "unknown")
        if (["file_changed", "file_created", "file_deleted"].includes(data.type)) {
          fetchTree()
        }
      } catch (err) {
        console.error("SSE parse error", err)
      }
    }

    eventSource.onerror = (err) => {
      console.error("EventSource failed:", err)
      eventSource.close()
    }

    return () => eventSource.close()
  }, [])

  const handleUpdate = async () => {
    if (!updateContent.trim()) return
    setIsUpdating(true)
    setUpdateResponse(null)
    setUpdateError("")
    try {
      const res = await fetch("/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: updateContent }),
      })
      if (!res.ok) {
        const text = await res.text()
        setUpdateError(`${res.status}: ${text}`)
        return
      }
      const data: UpdateResponse = await res.json()
      setUpdateResponse(data)
      setUpdateContent("")
    } catch {
      setUpdateError("Network error — check console")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setIsSearching(true)
    setSearchError("")
    setSearchResponse(null)

    try {
      const res = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: searchQuery }),
      })
      if (!res.ok) {
        const text = await res.text()
        setSearchError(`${res.status}: ${text}`)
        return
      }
      const data: SearchResponse = await res.json()
      setSearchResponse(data)
    } catch {
      setSearchError("Network error — check console")
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyDown =
    (callback: () => void) => (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        callback()
      }
    }

  return (
    <div className="flex h-screen w-screen bg-background text-foreground overflow-hidden">
      {/* Left: File Tree */}
      <div className="w-1/3 border-r p-4 flex flex-col h-full overflow-hidden">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Vault Tree</h2>
          <Badge variant="outline">SSE: {lastEvent}</Badge>
        </div>
        <Separator className="mb-4" />
        <pre className="flex-1 overflow-auto text-sm p-2 bg-muted/50 rounded-md">
          {tree || "Loading tree…"}
        </pre>
      </div>

      {/* Right: Interaction */}
      <div className="flex-1 p-6 h-full overflow-y-auto">
        <h1 className="text-2xl font-bold mb-6">Knower Shell</h1>

        <Tabs defaultValue="update" className="w-full max-w-2xl">
          <TabsList className="mb-4">
            <TabsTrigger value="update">Update</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
          </TabsList>

          {/* ── Update Tab ── */}
          <TabsContent value="update" className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">New Content</label>
              <Textarea
                placeholder="Enter content to write…"
                className="min-h-[150px]"
                value={updateContent}
                onChange={(e) => setUpdateContent(e.target.value)}
              />
            </div>
            <Button onClick={handleUpdate} disabled={isUpdating}>
              {isUpdating ? "Processing…" : "Send Update"}
            </Button>

            {updateError && (
              <p className="text-sm text-destructive">{updateError}</p>
            )}

            {updateResponse && (
              <div className="mt-4 space-y-2">
                <p className="text-xs text-muted-foreground">
                  Status: <span className="font-mono">{updateResponse.status}</span>
                </p>
                {updateResponse.result ? (
                  <pre className="text-sm bg-muted/30 border rounded-md p-4 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                    {updateResponse.result}
                  </pre>
                ) : (
                  <p className="text-sm text-muted-foreground">Agent completed with no summary.</p>
                )}
              </div>
            )}
          </TabsContent>

          {/* ── Search Tab ── */}
          <TabsContent value="search" className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Search the vault…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown(handleSearch)}
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={isSearching}>
                {isSearching ? "Searching…" : "Search"}
              </Button>
            </div>

            {searchError && (
              <p className="text-sm text-destructive">{searchError}</p>
            )}

            {searchResponse && (
              <div className="mt-4 space-y-2">
                <p className="text-xs text-muted-foreground">
                  Answer for{" "}
                  <span className="font-mono">
                    "{searchResponse.queries.join(", ")}"
                  </span>
                </p>
                {searchResponse.answer ? (
                  <pre className="text-sm bg-muted/30 border rounded-md p-4 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                    {searchResponse.answer}
                  </pre>
                ) : (
                  <p className="text-sm text-muted-foreground">No answer returned.</p>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}