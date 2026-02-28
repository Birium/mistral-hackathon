# Implementation Plan — Vault Web Interface

## Context

Building a read-only web interface for a vault-based knowledge management system. The user interacts exclusively via a floating chat input. The UI reflects the vault in real-time via SSE. No direct file editing — the sole interaction is through chat (Update / Search / Answering modes).

**Layout**: Fixed sidebar (file tree + inbox button) | scrollable central zone | floating chat input anchored at bottom of central zone.

---

## Checklist

### Step 1 — Types (`src/types.ts`)
- [ ] `TreeNode` (name, path, type, tokens, created_at, updated_at, children?)
- [ ] `InboxDetail` (name, review, input_files)
- [ ] `ChatMode` union: `'update' | 'search' | 'answering'`
- [ ] `ViewType` union: `'home' | 'file' | 'activity' | 'inbox-list' | 'inbox-detail'`
- [ ] `ActivityResult` (type, content, touched_files?, query?)
- [ ] `SSEEvent` (type, path?)

---

### Step 2 — API Layer (`src/api.ts`)
- [ ] `fetchTree()` → GET /tree → `response.tree`
- [ ] `fetchFile(path)` → GET /file?path=...
- [ ] `fetchInboxDetail(name)` → GET /inbox/{name}
- [ ] `sendUpdate(query, inboxRef?)` → POST /update
- [ ] `sendSearch(query)` → POST /search
- [ ] All functions throw on non-OK responses

---

### Step 3 — Backend Enhancements (`routes.py`)
- [ ] **Enhance `GET /tree`**: walk vault dir recursively, return structured JSON (name/path/type/tokens/created_at/updated_at/children). Exclude hidden files.
- [ ] **Add `GET /file`**: query param `?path=`, validate no `..` traversal, strip YAML frontmatter, return `{ path, content }`
- [ ] **Add `GET /inbox/{name}`**: read `vault/inbox/{name}/review.md` (strip frontmatter), list other input files, return `{ name, review, input_files }`
- [ ] **Enhance `POST /update`**: add optional `inbox_ref: Optional[str] = None` to payload, pass to agent when present

---

### Step 4 — `MarkdownRenderer.tsx`
- [ ] Install: `npm install react-markdown remark-gfm`
- [ ] `ReactMarkdown` + `remarkGfm` with Tailwind `components` overrides for h1-h3, p, ul/ol/li, code (inline + block), pre, blockquote, hr, a, table/th/td

---

### Step 5 — SSE Hook (`src/hooks/useSSE.ts`)
- [ ] `useSSE({ onTreeChange, onFileChange })` hook
- [ ] On mount: `new EventSource('/sse')`
- [ ] `onmessage`: parse JSON, call `onTreeChange()` + `onFileChange(path)` for any file event
- [ ] `onerror`: close, retry after 3s
- [ ] Cleanup on unmount: `eventSource.close()`

---

### Step 6 — Sidebar (`src/components/sidebar/`)

**`FileTreeNode.tsx`**
- [ ] File: button with File icon, name, token count, highlight when selected
- [ ] Dir: ChevronRight (rotates when expanded) + Folder icon + token count, expand/collapse local state
- [ ] Default expanded for top-level, collapsed for `projects/` children at depth ≥ 2
- [ ] Recursive `<FileTree>` for children; indent `paddingLeft: depth * 16 + 8`

**`FileTree.tsx`**
- [ ] Map `TreeNode[]` → `<FileTreeNode>`, pass depth and selectedPath

**`InboxButton.tsx`**
- [ ] Inbox icon + label + `<Badge variant="destructive">` when count > 0

**`Sidebar.tsx`**
- [ ] `w-72 h-full border-r flex flex-col`
- [ ] Top: scrollable with vault label + `<FileTree>`
- [ ] Bottom: `<Separator>` + `<InboxButton>`

---

### Step 7 — Chat Input (`src/components/chat/`)
- [ ] Install shadcn: `npx shadcn@latest add button badge separator card dropdown-menu`

**`ModeToggle.tsx`**
- [ ] shadcn `<DropdownMenu>` with Update / Search options; disabled when `chatMode === 'answering'`

**`AnsweringBanner.tsx`**
- [ ] Shown only when `chatMode === 'answering'`; CornerDownLeft icon + "Réponse à: {answeringRef}" + X cancel button

**`ChatInput.tsx`**
- [ ] Fixed: `bottom-6`, `left: calc(18rem + 1.5rem)`, `right: 1.5rem`
- [ ] `bg-background/80 backdrop-blur-md border shadow rounded-xl`
- [ ] Textarea auto-resize (max 200px), `rows={1}`
- [ ] Enter sends, Shift+Enter newlines
- [ ] ArrowUp send button (circular, `bg-primary` active / `bg-muted` disabled)
- [ ] Paperclip attachment button (disabled for MVP)
- [ ] ModeToggle left of textarea; AnsweringBanner above (conditional)

---

### Step 8 — Shared State Components

**`LoadingState.tsx`**: Loader2 spin + message, centered

**`ErrorState.tsx`**: XCircle + "Erreur" + message + "Réessayer" button

---

### Step 9 — Central Zone Views (`src/components/central/`)

**`HomeView.tsx`**
- [ ] On mount: `fetchFile('overview.md')`, render with `<MarkdownRenderer>` in `max-w-2xl`; fallback welcome if fetch fails

**`FileView.tsx`**
- [ ] Breadcrumb: split path by `/`, last segment plain, others buttons
- [ ] `<MarkdownRenderer>` for content
- [ ] Scroll preservation on re-render (save/restore scrollTop via refs)

**`ActivityView.tsx`**
- [ ] Loading: Loader2 + contextual label
- [ ] Error: `<ErrorState>`
- [ ] Update/answering result: CheckCircle + label + markdown + optional touched_files (clickable)
- [ ] Search result: markdown content
- [ ] Empty search: "Aucun résultat trouvé pour..."

**`InboxListView.tsx`**
- [ ] `<Card>` buttons: Mail icon + name + relative time (`formatRelativeTime` helper)
- [ ] Empty state: "Aucun item en attente."

**`InboxDetailView.tsx`**
- [ ] Back button, title, `<MarkdownRenderer>` for review, `<Separator>`, input files list (clickable)
- [ ] "Répondre" button → `chatMode='answering'`, `answeringRef=name`, focus textarea

**`CentralZone.tsx`**
- [ ] Switch on `currentView` → render appropriate view; container `px-8 py-6`

---

### Step 10 — `App.tsx` Wiring

- [ ] Global state: `currentView`, `selectedFilePath`, `fileContent`, `chatMode`, `answeringRef`, `treeData`, `activityResult`, `isLoading`, `error`, `inboxDetailData`
- [ ] Derived: `inboxItems = treeData.find(n => n.name === 'inbox')?.children ?? []`, `inboxCount`
- [ ] On mount: `fetchTree()` → `setTreeData`
- [ ] `useSSE` wired with `refetchTree` and file-change handler
- [ ] Callbacks: `onSelectFile`, `onOpenInbox`, `onOpenInboxDetail`, `onReply`, `onCancelReply`, `onSendMessage`, `onBackToInboxList`
- [ ] `handleSendMessage`: route to `sendSearch` or `sendUpdate`, set `activityResult`, handle errors, reset answering mode after send
- [ ] Layout: `flex h-screen` | `<Sidebar>` fixed width | right: `flex-1 flex flex-col` with `overflow-y-auto pb-40` + fixed `<ChatInput>`

---

### Step 11 — Polish
- [ ] Scroll preservation for FileView
- [ ] Chevron transition (`transition-transform`) on expand/collapse
- [ ] Textarea focus after clicking "Répondre"
- [ ] Verify `pb-40` keeps content above chat input
- [ ] Test SSE reconnection after network drop
- [ ] Test inbox badge real-time updates

---

## Key Design Decisions

- No React Router — view switching via `currentView` state
- No external state management — all state in `App.tsx`
- Inbox derived from tree — no separate inbox list API call
- Attachment button disabled (no upload route for MVP)
- Agent responses rendered as markdown; `touched_files` display ready for when agents provide structured output
- Chat input fixed with `left: calc(18rem + 1.5rem)` to float over central zone only

---

## Verification

1. `GET /tree` returns structured JSON with nested children
2. `GET /file?path=overview.md` returns content with frontmatter stripped
3. `GET /inbox/{name}` returns review + input_files
4. Tree renders with expand/collapse and token counts
5. Clicking a file loads FileView with breadcrumb
6. Update mode → /update → ActivityView shows result
7. Search mode → /search → ActivityView shows answer
8. Inbox badge updates via SSE when inbox changes
9. Répondre activates answering mode with banner visible
10. SSE disconnection triggers reconnect after 3s
