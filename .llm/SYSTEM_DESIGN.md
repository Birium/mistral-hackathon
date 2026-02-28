# Knower — System Design

## What this document is

This document describes the complete system design for Knower's MVP.
It is written to be consumed by an LLM that will implement part of this system.
Every architectural decision made here is intentional. Do not deviate without explicit instruction.

---

## What Knower is

Knower is a personal memory system. The user sends information (text, images) to it.
An AI agent structures that information into a local filesystem vault.
The user can then query that vault through a second AI agent that returns structured context.

The vault is plain markdown files on the host filesystem — no database, no proprietary format.
Everything is readable directly in VS Code, terminal, or Finder.

---

## Three moments the MVP must demonstrate

1. **Send information → it gets structured automatically in the vault.** The file tree updates in real time. The user sees files change. It is not a black box.
2. **Ask a question → receive real context pulled from memory.** Not generalities. Context built from what the user has deposited.
3. **The system doesn't know where to put something → it says so.** An item appears in inbox with the agent's full reasoning. The user responds. The agent executes. The item disappears.

---

## Repository structure

```
knower/
├── apps/
│   └── web/             # React + Vite + Shadcn/Tailwind — static build
├── core/                # Python — everything backend
├── vault/               # Docker volume, mounted on host filesystem
├── docker-compose.yml
└── knower               # Bash CLI script
```

---

## Installation and CLI

### CLI commands

The `knower` script is a thin bash wrapper around `docker compose`.

| Command            | Effect                                      |
| ------------------ | ------------------------------------------- |
| `knower start`     | Starts the core service (profile: core)     |
| `knower stop`      | Stops all running containers                |
| `knower visualize` | Starts the web app dev server (profile: web)|
| `knower status`    | Shows which containers are running          |
| `knower vault`     | Opens the vault folder in Finder            |

Internally:

```bash
knower start      → docker compose --profile core up -d
knower visualize  → docker compose --profile web up -d
knower stop       → docker compose down
```

---

## Docker Compose services

Two services total.

```yaml
services:
  core:
    build: ./core
    profiles: [core]
    ports: ["8000:8000"]
    volumes:
      - "./vault:/vault"
      - "qmd_cache:/root/.cache/qmd"
    environment:
      - VAULT_PATH=/vault
      - NODE_LLAMA_CPP_GPU=false

  web:
    build: ./web
    profiles: [web]
    ports: ["5173:5173"]

volumes:
  qmd_cache:
```

The `qmd_cache` volume persists QMD's SQLite index and GGUF models (~2GB) across container restarts. First boot is slow; subsequent boots are fast.

In production, the `core` service also serves the React static build via FastAPI's `StaticFiles`. The `web` profile is only needed in development.

---

## Core service — Python / FastAPI

The single backend service. Runs on `localhost:8000`. Does everything:

- Exposes the MCP server and HTTP routes
- Manages the asyncio sequential queue for update processing
- Runs the file watcher (watchdog) on the vault
- Pushes SSE events to the frontend when vault files change
- Runs both AI agents (update and search)
- Runs the background job after each vault write
- Serves the React static build

The core container ships Python 3.12 + Node.js 22 + the `qmd` CLI. Node is an implementation detail — it is not exposed and has no routes. QMD is called exclusively via Python subprocess from within the same container.

### Container startup sequence (`start.sh`)

1. Initialize QMD collection pointing at `/vault` (idempotent)
2. Run `qmd update` — index all vault files (BM25, fast)
3. If no embeddings exist yet, run `qmd embed` (slow on first boot, skipped on warm restart via flag file)
4. Start FastAPI via uvicorn

**Route `POST /update`**

Accepts: text content, images, optional `inbox_ref` field.

Behavior:

1. Returns immediately with `{ "status": "accepted", "id": "update-xyz" }` — the caller never blocks.
2. Places the payload into the asyncio sequential queue.
3. When dequeued, the update agent runs.

**Route `POST /search`**

Accepts: a text query string.

Behavior:

- Synchronous — does not go through the queue.
- Read-only — no risk of write conflicts.
- The search agent runs immediately and returns structured markdown.

**Route `GET /sse`**

Long-lived Server-Sent Events connection.
The frontend connects once on load and keeps the connection open.
The file watcher pushes events on this stream when vault files change.

Event types pushed:

- `file_changed` with the path of the modified file
- `inbox_updated` with the current count of inbox folders

**Route `GET /static`**

Serves the React build output. Only active when the build is present.

---

## Sequential queue

- asyncio-based, in-memory. No Redis, no external queue system.
- One update is processed at a time. The next one does not start until the previous one completes.
- Rationale: prevents concurrent write conflicts on vault files. Usage is personal, a few updates per hour at most.

---

## File watcher

- Uses `watchdog` watching `./vault`.
- On any file change event, does two things:
  - Pushes an SSE event to all connected frontend clients.
  - Triggers the background job on the changed file path.
- Must ignore writes made by the background job to avoid infinite loops.
- Implementation: maintain a `set` of paths currently being written by the background job. Ignore watchdog events on paths in this set.

---

## Update agent

Mental model: _"Where does this information belong?"_

Triggered by: items dequeued from the sequential queue.

Startup sequence (every session):

1. Load `vault/overview.md` into context
2. Load `vault/tree.md` into context
3. Load `vault/profile.md` into context

Then: navigate the vault using tools, decide routing, write files, log to `changelog.md`.

When routing ambiguity is too high: create an inbox folder with `review.md` exposing full reasoning. The file watcher picks up the new folder and pushes an `inbox_updated` SSE event.

If the payload contains `inbox_ref`, the agent reads that inbox folder first, processes the user's answer, routes files to destinations, deletes the inbox folder, logs to global changelog.

The update agent has access to all tools (read and write).

---

## Search agent

Mental model: _"What does the user need to know?"_

Triggered by: `POST /search`.

Startup sequence (every session):

1. Load `vault/overview.md` into context
2. Load `vault/tree.md` into context
3. Load `vault/profile.md` into context

Then: use the search tool to identify relevant chunks, read necessary files, return structured markdown.

The search agent is **read-only**. It has no access to write tools. It runs outside the queue — concurrent with any ongoing update processing.

---

## Background job

Triggered by: the file watcher, after each write/delete/move event on the vault.

Deterministic — no LLM, no AI, no decisions.

Steps (in order):

1. Calculate token count: `math.ceil(len(text) / 4)`
2. Update the file's YAML frontmatter: write `tokens` and `updated` fields
3. Regenerate `vault/tree.md` from the full vault
4. Call `qmd update` via subprocess to re-index the vault (BM25, fast)

The background job marks its own writes before writing so the file watcher ignores them. The agent never manages frontmatter.

---

## Search — QMD

Search is powered by **QMD**, a local search engine running inside the core container. It uses a SQLite index for BM25 and GGUF models for semantic search. No external service, no network dependency.

The `search` tool supports two modes:

- `mode: "fast"` — BM25 keyword match. Instant. No model required. Covers ~80% of use cases.
- `mode: "deep"` — semantic search with query expansion and reranking. Uses GGUF models. Slower on CPU.

The `search` tool supports an optional scope:

- `scope: "project:[name]"` — restricts results to `projects/[name]/`
- No scope — searches the full vault

Scoping is implemented as post-filter in Python: over-fetch from QMD, filter by path prefix, trim to requested limit.

### QMD models (loaded on first use)

| Model | Size | Purpose |
|---|---|---|
| embeddinggemma-300M | ~300MB | Embeddings |
| Qwen3-Reranker-0.6B | ~640MB | Reranking |
| qmd-query-expansion-1.7B | ~1.1GB | Query expansion |

All models are cached in the `qmd_cache` Docker volume. First boot downloads them; subsequent boots skip this.

### Embed schedule

`qmd embed` (generates vectors) is **not** called on every file change — it is slow. Strategy:

- BM25 (`mode: "fast"`) is always current — runs after every vault write.
- Vectors (`mode: "deep"`) have up to ~5 minutes of latency for newly added content.
- `qmd embed` runs on a timer or explicit action, not per-file.

---

## Web app — React

Stack: React + Vite + Shadcn/UI + Tailwind CSS.

In development: served by Vite on port 5173, API calls proxied to core on port 8000.
In production: static build served by FastAPI's StaticFiles on port 8000.

**Layout**

Fixed left sidebar + central zone. No navbar.

**Left sidebar**

- File tree of the vault. Updated via SSE `file_changed` events.
- Inbox icon at the bottom with a numeric badge. Updated via SSE `inbox_updated` events.

**Central zone — three views**

_File view_: clicking a file in the tree. Renders the markdown file, read-only.

_Activity view_: triggered by the chat input. For MVP: sends request, shows loading, waits for full response — no streaming.

_Inbox view_: triggered by clicking the inbox icon. Lists pending inbox folders. Click → renders `review.md`. A "Reply" button switches the chat input to answering mode.

**Chat input — three modes**

Always visible at the bottom.

- _Update mode_ (default): user sends information. Free text, optional file attachments.
- _Search mode_: user asks a question.
- _Answering mode_: activated from inbox view via "Reply". Sends to `/update` with `inbox_ref`.

---

## The vault

A directory of plain markdown files mounted as a Docker volume.
Lives at `./vault` on the host machine. Fully readable from VS Code, terminal, Finder.

### Initial state

```
vault/
├── overview.md        # full map of the vault, always loaded first by agents
├── tree.md            # auto-generated file tree with token counts and timestamps
├── profile.md         # durable user identity and preferences
├── tasks.md           # global orphan tasks
├── changelog.md       # global events and decisions
├── inbox/             # items waiting for user disambiguation
├── bucket/            # raw input files not yet attached to a project
└── projects/          # one subfolder per project
```

### YAML frontmatter

Every file has YAML frontmatter. Minimum fields:

```yaml
---
created: 2025-07-14T16:42:00
updated: 2025-07-14T18:30:00
tokens: 847
---
```

`updated` and `tokens` are managed exclusively by the background job.

### Files never indexed in QMD

`overview.md`, `tree.md`, `profile.md` — always loaded directly into agent context.
`inbox/` — temporary, deleted after resolution.

### Files always indexed in QMD

Global: `changelog.md`, `tasks.md`.
Per project: `description.md`, `state.md`, `tasks.md`, `changelog.md`.
All bucket files.

---

## Agent tools

Both agents share read and search tools. Only the update agent has write tools.

| Tool     | Signature                              | Description                                                                                  |
| -------- | -------------------------------------- | -------------------------------------------------------------------------------------------- |
| `tree`   | `tree(path, depth)`                    | File tree from a given path. Depth configurable.                                             |
| `read`   | `read(path)`                           | Reads a full file including frontmatter.                                                     |
| `search` | `search(query, mode, scope)`           | Searches via QMD. mode: "fast" (BM25) or "deep" (semantic). scope: optional project filter. |
| `write`  | `write(path, content)`                 | Creates or fully rewrites a file.                                                            |
| `edit`   | `edit(path, old_content, new_content)` | Search-replace on a specific section. First occurrence only.                                 |
| `append` | `append(path, content, position)`      | Inserts a block at "top" or "bottom". Used for changelogs.                                   |
| `delete` | `delete(path)`                         | Deletes a file or folder.                                                                    |
| `move`   | `move(from, to)`                       | Moves a file.                                                                                |

---

## Data flows

### Update path

```
Client
  → POST /update
  → ack returned immediately
  → asyncio sequential queue
  → update agent runs
  → writes files to vault/
  → watchdog fires
  → background job: tokens + frontmatter + tree.md + qmd update (BM25 reindex)
  → SSE file_changed → frontend re-renders
```

### Search path

```
Client
  → POST /search
  → synchronous, bypasses queue
  → search agent runs (read-only)
  → loads overview.md + tree.md + profile.md
  → calls search tool → qmd subprocess → ranked chunks
  → agent reads relevant files
  → structured markdown returned to client
```

### Inbox resolution path

```
User sees inbox badge
  → reads review.md
  → clicks "Reply", answering mode activates
  → POST /update with inbox_ref
  → update agent routes files, deletes inbox folder, logs to changelog
  → SSE inbox_updated → badge clears
```

---

## What is out of scope for MVP

- Authentication or network exposure of MCP server
- Streaming / WebSocket
- PDF or audio processing
- Git sync or cloud storage
- Windows support
- File editing from the web interface
- Cross-cutting search scopes, date filtering, partial file reads
