Agent Memory: Letta vs OneContext vs OpenClaw (Claude Code)
Based on our past investigation sessions (all from today's deep dives).
1. Letta (Context Repositories)
How it works: Git-backed filesystem memory. Agents clone a memory repository locally and read/write memory as Markdown files with YAML frontmatter. Git provides versioning automatically.
Architecture:
- Progressive disclosure: filetree (always visible) » frontmatter metadata » system directory (pinned to context) » dynamic loading
- Agents reorganize their own file hierarchies, move files between directories to control what's in context
Multina writes it got a lot bisod seme thou renado testerre outs, targets 15-25 sle hierarchy
Pro
Con
Full filesystem + bash + scripting access
Requires git knowledge/infrastructure
Concurrent multi-agent writes via worktrees
Merge conflicts possible in complex scenarios
Every memory change is auditable (git commits)
File hierarchy can drift over time (needs defrag)
Agents can write custom scripts to analyze their own memory
More complex setup than flat memory
Version history - can roll back memory states
Git overhead for simple use cases
2. OneContext (Aline)
How it works: Distributed, LLM-powered conversation archival system with three background daemons (Watcher, Worker, Search). All memory flows through a SQLite database.
Architecture:
- 4-level hierarchy: Event → Session → Turn → Content
- Watcher daemon monitors session files (Claude, Codex, Gemini), detects new turns
- Worker daemon claims summarization jobs, calls cloud LLM API to generate per-turn summaries, session-level summaries, and agent profiles
- Search uses regex mode (fast, summaries only) or content mode (slow, raw JSONL)
- FTS5 virtual tables for full-text search on events
- Distributed lease locks (10-min TTL) for multi-process safety
- Cloud-proxied LLM calls (no local API keys needed)
- 10-second debounce + content hash dedup to prevent excessive processing

---
OneContext (Aline)
How it works: Distributed, LLM-powered conversation archival system with three background daemons (Watcher, Worker, Search). All memory flows through a SQLite database.
Architecture:
- 4-level hierarchy: Event → Session → Turn → Content
- Watcher daemon monitors session files (Claude, Codex, Gemini), detects new turns
- Worker daemon claims summarization jobs, calls cloud LLM API to generate per-turn summaries, session-level summaries, and agent profiles
- Search uses regex mode (fast, summaries only) or content mode (slow, raw JSONL)
- FTS5 virtual tables for full-text search on events
- Distributed lease locks (10-min TTL) for multi-process safety
- Cloud-proxied LLM calls (no local API keys needed)
- 10-second debounce + content hash dedup to prevent excessive processing
Pro
Con
Fully automatic - zero manual memory management
Search can be slow for deep content queries
Works across multiple Al platforms (Claude, Codex, Gemini)
Depends on cloud LLM proxy for summarization
Rich search (regex, FTS5, hierarchical filtering)
SQLite DB can grow large (~3GB on your machine)
Session/event/agent grouping provides organizational structure
No agent self-modification of memory
Durable job queue with retry/backoff
Memory is read-only archival, not mutable agent state
Share/export with Slack messages, preset questions
Passive observation model - agents don't decide what to remember

---
3. OpenClaw (Claude Code Auto-Memory)
How it works: Simple file-based memory injected into system prompts. MEMORY.md at -/.claude/projects/(project)/memory/ is loaded into every conversation's syste prompt. The agent reads/writes these files directly.
Architecture:
- MEMORY.md - always loaded (200-line cap, truncated beyond that)
- Separate topic files (e.g., debugging.d, patterns.md) linked from MEMORY md
- CLAUDE,md files at global/project level for persistent instructions
- Agent uses standard Read/Write/Edit tools to update memory files
- No background processes, no database, no daemons
Note: Our past Codex investigation of OpenClaw was incomplete (session ran out of quota), so this is supplemented by what we know from using it directly.
Pro
Con
Dead simple - just files in a directory
200-line hard cap on MEMORY.md (system prompt injection)
No infrastructure (no daemons, no DB, no git)
No automatic memory - agent must explicitly decide to save
Agent has full control over what to remember
No search across conversation history
Instant - no processing pipeline or latency
No multi-agent coordination for memory
Easy to inspect/edit manually
No versioning (overwrite = data loss)
Works offline, zero dependencies
Memory doesn't grow organically - stays stale without effort