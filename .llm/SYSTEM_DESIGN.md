# Knower — System Design

## What it is

Knower is a personal memory system. The user sends information to it; an AI agent structures it into a local vault. The user queries the vault through a second AI agent.

The vault is a folder of plain Markdown files on the host filesystem. No database, no proprietary format — readable directly in VS Code, terminal, or Finder.

---

## Repository structure

```
knower/
├── web/           # React + Vite + Shadcn/Tailwind
├── core/          # Python — all backend logic
├── vault/         # dev vault (gitignored)
├── install.sh
└── knower         # bash CLI
```

---

## Installation & config

`install.sh` checks system deps, installs QMD globally, creates `core/.venv`, writes `KNOWER_HOME` to config, and symlinks the CLI.

Config lives at `~/.config/knower/config`:
```
KNOWER_HOME=/path/to/repo
VAULT_PATH=/path/to/vault
CORE_PORT=8000
```

Two runtime modes:

| Mode | Vault | Logs | Process |
|------|-------|------|---------|
| `--dev` | `<repo>/vault/` | stdout | foreground, hot reload |
| prod | `VAULT_PATH` from config | `~/.local/share/knower/logs/` | nohup + PID file |

---

## Core service — FastAPI on :8000

Single Python process. Responsibilities:

- HTTP routes (`/update`, `/search`, `/sse`, `/tree`)
- MCP server (`/mcp`)
- Asyncio sequential queue for vault writes
- File watcher (watchdog) on the vault
- SSE stream to the frontend
- Both AI agents (update + search)
- Background job after each vault write

### Startup sequence (`core/start.sh`)

1. Init QMD collection pointing at vault (idempotent)
2. `qmd update` — BM25 index (fast, always runs)
3. `qmd embed` — vectors (slow, skipped if flag file exists)
4. Start uvicorn

### Routes

| Route | Behaviour |
|-------|-----------|
| `POST /update` | Enqueues payload, returns `{status, id}` immediately |
| `POST /search` | Synchronous, read-only, bypasses queue |
| `GET /sse` | Long-lived SSE stream for frontend events |
| `GET /tree` | Returns vault file tree |

---

## Vault

```
vault/
├── overview.md      # always loaded first by agents
├── tree.md          # auto-generated file tree
├── profile.md       # user identity and preferences
├── tasks.md
├── changelog.md
├── inbox/           # items waiting for user input
├── bucket/          # unsorted input files
└── projects/        # one subfolder per project
```

Every file has YAML frontmatter with `created`, `updated`, and `tokens`. The `updated` and `tokens` fields are managed exclusively by the background job — never by agents.

---

## Agents

**Update agent** — routes incoming information into the vault. Reads `overview.md`, `tree.md`, `profile.md` on startup. Navigates the vault with tools, writes files, logs to `changelog.md`. When routing is ambiguous, creates an inbox folder with full reasoning and waits for user input.

**Search agent** — read-only. Same startup context. Uses the search tool to find relevant chunks, reads files, returns structured Markdown.

### Tools

| Tool | Description |
|------|-------------|
| `tree(path, depth)` | Directory listing |
| `read(path)` | Read a file |
| `search(query, mode, scope)` | BM25 or semantic search |
| `write(path, content)` | Create or overwrite |
| `edit(path, old, new)` | Search-replace (first occurrence) |
| `append(path, content, position)` | Insert at top or bottom |
| `delete(path)` | Delete file or folder |
| `move(from, to)` | Move a file |

Search agent has access to `tree`, `read`, `search` only.

---

## Search — QMD

Local search engine, runs inside the core process via subprocess. SQLite index for BM25, GGUF models for semantic search. No external service.

| Mode | How | Speed |
|------|-----|-------|
| `fast` | BM25 keyword match | Instant |
| `deep` | Semantic + rerank | Slow on CPU |

Models (~2GB total) are cached in `~/.cache/qmd`. First boot downloads them; subsequent boots skip this.

BM25 index updates after every vault write. Vectors update on a timer (not per-file) — up to ~5 minutes of latency for new content in `deep` mode.

---

## Web app — React on :5173 (dev)

React + Vite + Shadcn/UI + Tailwind.

- **Left sidebar**: vault file tree (updated via SSE) + inbox badge
- **Central zone**: file view, activity view (search/update results), inbox view
- **Chat input**: three modes — update (default), search, answering (inbox reply)

In production, the React build is served statically by FastAPI on :8000.

---

## Out of scope (MVP)

Authentication, streaming, PDF/audio, git sync, cloud storage, Windows, file editing from UI.