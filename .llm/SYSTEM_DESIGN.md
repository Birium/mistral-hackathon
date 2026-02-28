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

There is no Node.js layer. The entire backend runs in Python.

---

## Installation and CLI

### Install

```bash
curl -fsSL https://raw.githubusercontent.com/you/knower/main/install.sh | bash
```

The install script does three things:

- Clones the repo into `~/.knower`
- Creates a symlink from `~/.knower/knower` to `/usr/local/bin/knower`
- Checks that Docker is installed

No pip install, no npm global, no environment setup. Docker handles all dependencies.

### CLI commands

The `knower` script is a thin bash wrapper around `docker compose`.

| Command            | Effect                                       |
| ------------------ | -------------------------------------------- |
| `knower start`     | Starts core service + Qdrant (profile: core) |
| `knower stop`      | Stops all running containers                 |
| `knower visualize` | Starts the web app dev server (profile: web) |
| `knower status`    | Shows which containers are running           |
| `knower vault`     | Opens the vault folder in Finder             |

Internally:

```bash
knower start      → docker compose --profile core up -d
knower visualize  → docker compose --profile web up -d
knower stop       → docker compose down
```

---

## Docker Compose services

Three services total. No Node.

```yaml
services:
  core:
    build: ./core
    profiles: [core]
    ports: ["8000:8000"]
    volumes: ["./vault:/vault"]
    depends_on: [vectordb]

  vectordb:
    image: qdrant/qdrant
    profiles: [core]
    ports: ["6333:6333"]

  web:
    build: ./web
    profiles: [web]
    ports: ["5173:5173"]
```

In production (or after `knower start`), the `core` service also serves the React static build via FastAPI's `StaticFiles`. The `web` profile is only needed in development when Vite's hot reload is useful.

---

## Core service — Python / FastAPI

The single backend service. Runs on `localhost:8000`. Does everything:

- Exposes the MCP server (two routes: `/update` and `/search`)
- Manages the asyncio sequential queue for update processing
- Runs the file watcher (watchdog) on the vault
- Pushes SSE events to the frontend when vault files change
- Runs both AI agents (update and search)
- Runs the background job after each vault write
- Serves the React static build

**Route `POST /update`**

Accepts: text content, images, optional `inbox_ref` field.

Behavior:

1. Returns immediately with `{ "status": "accepted", "id": "update-xyz" }` — the caller never blocks.
2. Passes the payload through the processing pipeline (text as-is, images as-is).
3. Places the processed payload into the asyncio sequential queue.
4. When dequeued, the update agent runs.

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

- `file_changed` with the path of the modified file — frontend re-renders file tree and open file if it matches
- `inbox_updated` with the current count of inbox folders — frontend updates inbox badge

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
- Implementation: maintain a `set` of paths currently being written by the background job. Ignore watchdog events on paths present in this set. Clear the path from the set after the background job write completes.

---

## Update agent

Mental model: _"Where does this information belong?"_

Triggered by: items dequeued from the sequential queue.

Startup sequence (every session):

1. Load `vault/overview.md` into context
2. Load `vault/tree.md` into context
3. Load `vault/profile.md` into context

Then: navigate the vault using tools, decide routing, write files, log to `changelog.md` global.

When routing ambiguity is too high: create an inbox folder with `review.md` exposing full reasoning. The file watcher picks up the new inbox folder and pushes an `inbox_updated` SSE event to the frontend.

If the payload contains `inbox_ref`, the agent reads that inbox folder first, processes the user's answer, routes the files to their destinations, deletes the inbox folder, logs to global changelog.

The update agent has access to all tools (read and write).

---

## Search agent

Mental model: _"What does the user need to know?"_

Triggered by: `POST /search`.

Startup sequence (every session):

1. Load `vault/overview.md` into context
2. Load `vault/tree.md` into context
3. Load `vault/profile.md` into context

Then: use the search tool to identify relevant chunks, read necessary files, pass the result list to the concat engine, return structured markdown.

The search agent is **read-only**. It has no access to write tools.
It runs outside the queue — concurrent with any ongoing update processing.

---

## Background job

Triggered by: the file watcher, after each write/delete/move event on the vault.

Deterministic — no LLM, no AI, no decisions. Same input always produces same output.

Steps (in order):

1. Calculate token count: `math.ceil(len(text) / 4)`
2. Update the file's YAML frontmatter: write `tokens` and `updated` fields
3. Regenerate `vault/tree.md` from the full vault
4. Re-index the modified file in Qdrant (not a full re-scan, only the changed file)

The background job marks its own writes with an internal flag before writing.
The file watcher ignores events flagged as background job writes.
The agent never manages frontmatter. It is plumbing, not reasoning.

---

## Vector DB — Qdrant

Used for the `search` tool called by both agents.

The search tool supports two modes:

- `mode: "fast"` — BM25 exact match, milliseconds, for terms, names, dates, tags
- `mode: "deep"` — full vector + re-ranking pipeline, semantic search

The search tool supports an optional scope:

- `scope: "project:[name]"` — restricts search to a specific project
- No scope — searches the full indexed vault

Qdrant runs in its own container on port 6333. The Python core writes to it and queries it directly.

---

## Web app — React

Stack: React + Vite + Shadcn/UI + Tailwind CSS.

In development: served by Vite on port 5173, API calls proxied to core on port 8000.
In production: static build served by FastAPI's StaticFiles on port 8000.

The web app calls the same `/update` and `/search` routes as Claude Code.

**Layout**

Fixed left sidebar + central zone. No navbar.

**Left sidebar**

- File tree of the vault. Updated via SSE `file_changed` events.
- Inbox icon at the bottom with a numeric badge. Updated via SSE `inbox_updated` events. The badge count is a file count in `inbox/` — maintained programmatically, not by the agent.

**Central zone — three views**

_File view_: triggered by clicking a file in the tree. Renders the markdown file, read-only.

_Activity view_: triggered by using the chat input. For MVP: sends request, shows loading state, waits for full response — no streaming. On search response: renders agent overview followed by concatenated files. On update response: summary of files touched. On answering response: confirmation that inbox item is closed.

_Inbox view_: triggered by clicking the inbox icon. Lists pending inbox folders with name and date. Click on an item → renders `review.md` + lists input files. A "Reply" button switches the chat input to answering mode and pre-fills `inbox_ref`.

**Chat input — three modes**

Always visible at the bottom. Switched via explicit toggle — no automatic intent detection.

- _Update mode_ (default): user sends information. Free text, optional file attachments.
- _Search mode_: user asks a question or formulates a search.
- _Answering mode_: activated only from inbox view via "Reply" button. A banner recalls which inbox item is being answered. The request goes to `/update` with `inbox_ref: [folder-path]` in the payload.

---

## The vault

A directory of plain markdown files mounted as a Docker volume.
Lives at `./vault` relative to the repo root on the host machine.
Fully readable from the host — in VS Code, terminal, Finder.

### Initial state

Created at first launch. The user never starts with an empty vault.

```
vault/
├── overview.md        # full map of the vault, always loaded first by agents
├── tree.md            # auto-generated file tree with token counts and timestamps
├── profile.md         # durable user identity and preferences
├── tasks.md           # global orphan tasks, live view only
├── changelog.md       # global events and decisions, grows indefinitely
├── inbox/             # items waiting for user disambiguation
├── bucket/            # raw input files not yet attached to a project
└── projects/          # one subfolder per project
```

### YAML frontmatter

Every file in the vault has YAML frontmatter. Minimum fields:

```yaml
---
created: 2025-07-14T16:42:00
updated: 2025-07-14T18:30:00
tokens: 847
---
```

The `updated` and `tokens` fields are managed exclusively by the background job. The agent never touches them.

### Files never indexed in Qdrant

`overview.md`, `tree.md`, `profile.md` — always loaded directly into context at session start.
Content in `inbox/` — temporary, deleted after resolution.

### Files always indexed in Qdrant

Global: `changelog.md`, `tasks.md`.
Per project: `description.md`, `state.md`, `tasks.md`, `changelog.md`.
All bucket files: `bucket/*.md` and `projects/[name]/bucket/*.md`.

---

## Agent tools

Both agents share the read and search tools. Only the update agent has write tools.

| Tool     | Signature                              | Description                                                                                  |
| -------- | -------------------------------------- | -------------------------------------------------------------------------------------------- |
| `tree`   | `tree(path, depth)`                    | File tree from a given path with token counts and timestamps. Depth configurable.            |
| `read`   | `read(path)`                           | Reads a full file including frontmatter.                                                     |
| `search` | `search(query, mode, scope)`           | Searches Qdrant. mode: "fast" or "deep". scope: optional project filter.                     |
| `write`  | `write(path, content)`                 | Creates a new file or fully rewrites an existing one.                                        |
| `edit`   | `edit(path, old_content, new_content)` | Search-replace on a specific section of a file. First occurrence only.                       |
| `append` | `append(path, content, position)`      | Inserts a markdown block at "top" or "bottom" without reading the file. Used for changelogs. |
| `delete` | `delete(path)`                         | Deletes a file or an entire folder and its contents.                                         |
| `move`   | `move(from, to)`                       | Moves a file. Background job handles the rest automatically.                                 |

---

## Data flows

### Update path

```
Client
  → POST /update
  → ack returned immediately { status: "accepted", id: "..." }
  → processing pipeline (text as-is, images as-is)
  → asyncio sequential queue
  → update agent runs
  → writes files to vault/
  → watchdog event fires
  → background job: tokens + updated frontmatter + tree.md + Qdrant re-index
  → SSE file_changed → frontend re-renders
```

### Search path

```
Client
  → POST /search
  → synchronous, bypasses queue
  → search agent runs (read-only)
  → loads overview.md + tree.md + profile.md
  → calls search tool → Qdrant returns ranked chunks
  → agent reads relevant files
  → concat engine: agent overview (2–5 lines) + raw file contents with path headers
  → structured markdown returned to client
```

### Inbox resolution path

```
User sees inbox badge in sidebar
  → opens inbox view, reads review.md
  → clicks "Reply", answering mode activates
  → user sends response
  → POST /update with inbox_ref: [folder-path]
  → update agent reads inbox folder first
  → routes files to their destinations
  → deletes inbox folder
  → logs to global changelog.md
  → watchdog fires → SSE inbox_updated → badge clears
```

---

## What is out of scope for MVP

- MCP server exposed over network or with authentication — local only
- Streaming / WebSocket — full response, no streaming
- Orchestrator / worker model split — one model for both agents
- External notifications (Discord, Telegram, email)
- PDF processing — post-MVP
- Audio processing — handled by external upstream layer, not by this service
- Git sync or cloud storage of vault
- Windows support — macOS only
- File editing from the web interface — read-only for MVP
- Cross-cutting search scopes (`all-states`, `all-changelogs`, etc.) — post-MVP
- Date filtering on search — post-MVP
- Partial file reads (`head`/`tail` on `read` tool) — post-MVP
