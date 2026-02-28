import { useState, useEffect, FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function App() {
  const [tree, setTree] = useState<string>("")
  const [lastEvent, setLastEvent] = useState<string>("None")
  
  // Update state
  const [updateContent, setUpdateContent] = useState("")
  const [updateStatus, setUpdateStatus] = useState("")

  // Search state
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResult, setSearchResult] = useState("")

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
        setLastEvent(data.type || "Unknown event")
        if (data.type === "file_changed" || data.type === "file_created" || data.type === "file_deleted") {
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

    return () => {
      eventSource.close()
    }
  }, [])

  const handleUpdate = async (e: FormEvent) => {
    e.preventDefault()
    setUpdateStatus("Sending...")
    try {
      const res = await fetch("/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: updateContent })
      })
      const data = await res.json()
      setUpdateStatus(`Accepted (ID: ${data.id})`)
      setUpdateContent("")
    } catch (err) {
      setUpdateStatus("Error updating")
    }
  }

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault()
    setSearchResult("Searching...")
    try {
      const res = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery })
      })
      const data = await res.json()
      setSearchResult(data.result)
    } catch (err) {
      setSearchResult("Error searching")
    }
  }

  return (
    <div className="flex h-screen w-screen bg-background text-foreground overflow-hidden">
      {/* Left Column: File Tree */}
      <div className="w-1/3 border-r p-4 flex flex-col h-full overflow-hidden">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Vault Tree</h2>
          <Badge variant="outline">SSE: {lastEvent}</Badge>
        </div>
        <Separator className="mb-4" />
        <pre className="flex-1 overflow-auto text-sm p-2 bg-muted/50 rounded-md">
          {tree || "Loading tree..."}
        </pre>
      </div>

      {/* Right Column: Interaction */}
      <div className="flex-1 p-6 h-full overflow-y-auto">
        <h1 className="text-2xl font-bold mb-6">Knower Shell</h1>
        
        <Tabs defaultValue="update" className="w-full max-w-2xl">
          <TabsList className="mb-4">
            <TabsTrigger value="update">Update</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
          </TabsList>

          <TabsContent value="update" className="space-y-4">
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">New Content</label>
                <Textarea 
                  placeholder="Enter content to write to a dummy file..."
                  className="min-h-[150px]"
                  value={updateContent}
                  onChange={(e) => setUpdateContent(e.target.value)}
                  required
                />
              </div>
              <div className="flex items-center gap-4">
                <Button type="submit">Send Update</Button>
                <span className="text-sm text-muted-foreground">{updateStatus}</span>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="search" className="space-y-4">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Search Query</label>
                <div className="flex gap-2">
                  <Input 
                    placeholder="Enter search term..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    required
                  />
                  <Button type="submit">Search</Button>
                </div>
              </div>
            </form>
            
            {searchResult && (
              <div className="mt-6 border rounded-md p-4 bg-muted/30">
                <h3 className="text-sm font-medium mb-2">Result:</h3>
                <pre className="whitespace-pre-wrap text-sm">{searchResult}</pre>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
