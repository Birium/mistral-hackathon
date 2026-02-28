import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type SearchResult = {
  path: string
  score: number
  lines: string
  chunk_with_context: string
}

type SearchResponse = {
  queries: string[]
  results: SearchResult[]
}

export default function App() {
  const [tree, setTree] = useState<string>("")
  const [lastEvent, setLastEvent] = useState<string>("None")

  // Update state
  const [updateContent, setUpdateContent] = useState("")
  const [updateStatus, setUpdateStatus] = useState("")
  const [isUpdating, setIsUpdating] = useState(false)

  // Search state
  const [searchQuery, setSearchQuery] = useState("")
  const [searchMode, setSearchMode] = useState<"fast" | "deep">("fast")
  const [searchScope, setSearchScope] = useState("")
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
    setUpdateStatus("Sending…")
    try {
      const res = await fetch("/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: updateContent }),
      })
      const data = await res.json()
      setUpdateStatus(`Accepted (ID: ${data.id})`)
      setUpdateContent("")
    } catch {
      setUpdateStatus("Error — check console")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setIsSearching(true)
    setSearchError("")
    setSearchResponse(null)

    const scopeTrimmed = searchScope.trim()

    try {
      const res = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          queries: [searchQuery.trim()],
          mode: searchMode,
          scopes: scopeTrimmed ? [scopeTrimmed] : null,
          limit: 10,
        }),
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

        <Tabs defaultValue="search" className="w-full max-w-2xl">
          <TabsList className="mb-4">
            <TabsTrigger value="search">Search</TabsTrigger>
            <TabsTrigger value="update">Update</TabsTrigger>
          </TabsList>

          {/* ── Search Tab ── */}
          <TabsContent value="search" className="space-y-4">
            <div className="space-y-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Search the vault…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyDown(handleSearch)}
                  className="flex-1"
                />
                <Select
                  value={searchMode}
                  onValueChange={(v) => setSearchMode(v as "fast" | "deep")}
                >
                  <SelectTrigger className="w-28">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fast">Fast</SelectItem>
                    <SelectItem value="deep">Deep</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={handleSearch} disabled={isSearching}>
                  {isSearching ? "Searching…" : "Search"}
                </Button>
              </div>

              <Input
                placeholder="Scope (optional): vault/projects/startup-x/*"
                value={searchScope}
                onChange={(e) => setSearchScope(e.target.value)}
              />
            </div>

            {searchError && (
              <p className="text-sm text-destructive">{searchError}</p>
            )}

            {searchResponse && (
              <div className="space-y-3 mt-4">
                <p className="text-xs text-muted-foreground">
                  {searchResponse.results.length} result(s) for{" "}
                  <span className="font-mono">
                    "{searchResponse.queries.join(", ")}"
                  </span>
                </p>

                {searchResponse.results.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No results found.</p>
                ) : (
                  searchResponse.results.map((r, i) => (
                    <div
                      key={i}
                      className="border rounded-md p-4 bg-muted/30 space-y-2"
                    >
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <span className="text-sm font-mono font-medium">
                          {r.path}
                        </span>
                        <div className="flex gap-2">
                          {r.lines && r.lines !== "?" && (
                            <Badge variant="outline">L{r.lines}</Badge>
                          )}
                          <Badge variant="secondary">
                            {r.score.toFixed(3)}
                          </Badge>
                        </div>
                      </div>
                      {r.chunk_with_context && (
                        <pre className="text-xs text-muted-foreground bg-muted rounded p-2 overflow-x-auto whitespace-pre">
                          {r.chunk_with_context}
                        </pre>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </TabsContent>

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
            <div className="flex items-center gap-4">
              <Button onClick={handleUpdate} disabled={isUpdating}>
                {isUpdating ? "Sending…" : "Send Update"}
              </Button>
              {updateStatus && (
                <span className="text-sm text-muted-foreground">
                  {updateStatus}
                </span>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
