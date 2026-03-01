<div align="center">

# Knower

### One memory. Every tool.

A personal AI memory service, Local, portable, connected everywhere.

Your context follows you across Mistral, Claude, Gemini, and whatever comes next.

![Knower Schema](docs/knower-as-hub.svg)

</div>

**Quick start** — try it in 60 seconds:

```bash
git clone git@github.com:Birium/mistral-hackathon.git && cd knower
./install.sh                        # ~2 GB model download, one time
knower config vault ~/my-vault
knower start                        # http://localhost:8000
```

---

## The Problem

### You re-explain yourself. Every. Single. Session.

You open Mistral. You need help with your project. So you explain the stack, the constraints, the decisions you made two weeks ago, the thing you tried and abandoned. You do it again in Claude. Again in Gemini. Every session starts from zero because no tool remembers what you already told another one.

It's not a minor annoyance. It's your **daily workflow**: re-building context that already exists somewhere, just not _here_.

### Memory is siloed

This isn't a UX problem. It's an **architecture problem**.

Claude has a memory. Cursor has rules. None of them talk to each other. Switch tools, start over. Use two in parallel, they share nothing.

![The Silo Problem](docs/silo-problem.svg)

> Your memory is locked — in silos that don't belong to you.

### Projects evolve. Memory doesn't.

You write some rules in a file. Ten lines. Clear, helpful. Three sprints later it's 200 lines, half of it outdated, contradicted by decisions made since. Nobody updates it. Nobody knows which half is wrong.

Every developer who works with AI agents knows this: **context rots**. Maintaining it manually is a second job that nobody actually does.

### When the agent searches its own memory, it gets dumber

Here's the part that's less obvious.

When an agent retrieves context using its own tools — `grep`, `read`, `tree` — all that exploration **lives inside its context window**. The context window is the agent's working memory. Fill it with search results and file reads, and there's less room left to _think_.

This isn't theoretical:

| Research                        | Finding                                                                                      |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| **Stanford 2025** (n=136 teams) | AI productivity gain drops sharply on complex brownfield tasks vs. simple greenfield ones    |
| **NoLiMa Benchmark**            | Model performance degrades with context length                                               |
| **Needle-in-Haystack**          | Retrieval accuracy collapses at large context depths — even on models that claim 200K tokens |

![Stanford study](docs/stanford-study.jpeg)

> The smarter the task, the worse this gets. An agent burning context on memory retrieval is an agent that can't reason.

---

## Why Existing Solutions Miss

The problem isn't that memory doesn't exist. It's that every memory lives in a silo owned by someone else.

| Solution                  | What it does       | Why it's not enough                                                         |
| ------------------------- | ------------------ | --------------------------------------------------------------------------- |
| Claude memory             | Stores preferences | Locked inside Claude                                                        |
| Cursor rules              | Project context    | Only for coding, only in Cursor                                             |
| ChatGPT memory            | Recall snippets    | Locked inside ChatGPT                                                       |
| Notion/Drive + chatbot    | File storage       | Agent navigates blind — no structure                                        |
| Knowledge graphs (Neo4j…) | Entity relations   | Too atomic; LLMs can't build coherent understanding from disconnected nodes |

Nobody has built a memory that is **yours**, **local**, and **connected everywhere**.

---

## How Knower Works

Two operations. That's it.

```
SEND anything  →  Knower structures it into your vault
ASK  anything  →  Knower returns relevant Markdown
```

Knower is a **separate service**, not a plugin, not a feature of an existing tool. It sits on the side. You call it when you need it, from wherever you are.

![Knower webapp screenshot](docs/how-it-works.svg)

### Why Markdown files

The vault is a folder of plain `.md` files on your filesystem.

- **Human-readable** — open in VS Code, Obsidian, terminal. No black box.
- **Navigable by structure** — agents know _where_ to look, not just _what_ to search. The structure is predictable; the content evolves.
- **Portable** — no proprietary format. Copy the folder and you have everything.
- **Where the ecosystem is converging** — Claude Code, OpenClaw, and Letta all chose Markdown. It's not a coincidence — it's what works.

### Why a separate process

This is the key architectural insight.

When an agent searches memory with its own tools, the search work fills its context window. A context window saturated with memory retrieval is a context window that **can't think about your actual task**.

Knower separates the concerns. The agent calls Knower, gets a clean Markdown chunk back, and keeps its context window free for reasoning.

---

## Architecture

### The Vault

```
vault/
├── overview.md       # loaded first by every agent — the map
├── profile.md        # who you are, preferences, constraints
├── tasks.md
├── changelog.md      # update agent logs every change here
├── inbox/            # items where routing was ambiguous — waiting for you
├── bucket/           # unsorted input files
└── projects/         # one subfolder per project
```

Every file has YAML frontmatter (`created`, `updated`, `tokens`). The `updated` and `tokens` fields are managed by a **background job** — agents never touch them. After each vault write, the background job updates frontmatter, re-indexes BM25, and re-embeds vectors.

### The Two Agents

Both agents are powered by **Mistral API** with tool-calling in an agentic loop. On startup, each loads `overview.md` + `tree.md` + `profile.md` as base context.

| Agent      | Role                                  | Available tools                                                       |
| ---------- | ------------------------------------- | --------------------------------------------------------------------- |
| **Update** | Routes new information into the vault | `tree`, `read`, `search`, `write`, `edit`, `append`, `move`, `delete` |
| **Search** | Read-only retrieval                   | `tree`, `read`, `search`, `concat`                                    |

The **update agent** reads, navigates, and modifies vault files. When routing is ambiguous, it creates an inbox item with full reasoning and waits for user input. Every change is logged to `changelog.md`.

The **search agent** finds relevant content through hybrid search and file reads, then returns structured Markdown.

Both agents run inside a **base agentic loop** (`BaseAgent`) that handles tool-call cycles with a safety cap (max 25 iterations, then a forced final response with tools disabled).

### Search — QMD

Knower uses [**QMD**](https://github.com/tobilu/qmd) as its local search engine. No external API, no cloud — everything runs on your machine.

![QMD pipeline](docs/qmd-pipeline.png)

#### QMD Models

All models are local GGUF files, cached once at `~/.cache/qmd/models/` (~2 GB total):

| Model                    | Size    | Role                                                                                                      |
| ------------------------ | ------- | --------------------------------------------------------------------------------------------------------- |
| **Qwen3 1.7B + LoRA**    | ~1.1 GB | Query expansion — generates HyDE documents, semantic variants, and keyword expansions from the user query |
| **GGUF embedding model** | ~300 MB | Vector embeddings for semantic search over vault content                                                  |
| **LLM Reranker (0.6B)**  | ~640 MB | Re-scores fused results for final ranking precision                                                       |

Two search modes are exposed to agents:

| Mode   | Pipeline                                                     | Speed              |
| ------ | ------------------------------------------------------------ | ------------------ |
| `fast` | BM25 keyword match only                                      | Instant            |
| `deep` | Full pipeline: expansion → parallel search → fusion → rerank | Slower (CPU-bound) |

First boot downloads all models; subsequent boots skip this entirely.

### Connectivity

Same vault. Three entry points:

```
MCP  →  Claude Code, Cursor, any MCP-compatible client
API  →  any script, any program (POST /update, POST /search)
CLI  →  you, directly, no intermediary
```

In production, the React frontend is served statically by FastAPI — **single process on port 8000**.

Two MCP tools are exposed: `update(content)` and `search(content)`. Any MCP-compatible agent can call them directly.

---

## Getting Started

### Prerequisites

| Dependency                 | Version                            |
| -------------------------- | ---------------------------------- |
| macOS                      | required (only supported platform) |
| Python                     | ≥ 3.x                              |
| Node.js                    | ≥ 22                               |
| [uv](https://astral.sh/uv) | any                                |

### Install

```bash
git clone https://github.com/your-org/knower.git
cd knower
./install.sh
```

The installer:

1. Checks platform and dependencies
2. Installs QMD globally (`npm install -g @tobilu/qmd`)
3. Downloads QMD models (~2 GB, one time)
4. Creates Python venv in `core/.venv`
5. Writes config to `~/.config/knower/config`
6. Symlinks `knower` CLI to `/usr/local/bin`

### Configure and run

```bash
knower config vault ~/my-vault    # set vault location
knower start                      # start in background
open http://localhost:8000        # webapp
```

### MCP Integration

#### Mistral Vibe

Find official docs [here](https://docs.mistral.ai/mistral-vibe/introduction/configuration#mcp-server-configuration).

```toml
[[mcp_servers]]
name = "knower"
transport = "streamable-http"
url = "http://localhost:8000/mcp"
```

MCP tools are named using the pattern `{server_name}_{tool_name}` and can be configured with permissions:

```toml
[tools.knower_search]
permission = "always"
```

#### Claude Code

```bash
claude mcp add knower --transport sse http://localhost:8000/mcp/sse
```

#### Open Code

Find your configuration file, there is different locations. Sources are [listed here](https://opencode.ai/docs/config/#ordre-de-priorit%C3%A9)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "knower": {
      "type": "remote",
      "url": "http://localhost:8000/mcp",
      "enabled": true
    }
  }
}
```

### CLI Reference

| Command                      | Description                                    |
| ---------------------------- | ---------------------------------------------- |
| `knower dev`                 | Dev mode: core (hot-reload) + Vite frontend    |
| `knower start`               | Start core in background (prod)                |
| `knower stop`                | Stop core                                      |
| `knower status`              | Show config + running state                    |
| `knower logs`                | Tail core log                                  |
| `knower config vault <path>` | Set vault path                                 |
| `knower config show`         | Print current config                           |
| `knower vault`               | Open vault in Finder                           |
| `knower web [--bg]`          | Start Vite dev server                          |
| `knower shell`               | Open shell with Python venv activated          |
| `knower uninstall`           | Clean removal (keeps vault + QMD models)       |
| `  --purge`                  | Also remove QMD models (~2 GB) and npm package |
| `  --with-vault`             | Also delete vault (requires path confirmation) |

---

## Stack

| Layer            | Technology                                               |
| ---------------- | -------------------------------------------------------- |
| **Core**         | Python, FastAPI, asyncio queue, watchdog file watcher    |
| **Search**       | QMD — BM25 + vector + LLM reranker, fully local          |
| **Agents**       | Mistral API, agentic tool-calling loop, streaming events |
| **Frontend**     | React + Vite + Shadcn/UI + Tailwind                      |
| **Storage**      | Plain Markdown files with YAML frontmatter               |
| **Connectivity** | MCP server (SSE), REST API, bash CLI                     |

---

## What's Next

**Not in MVP:** git sync, cloud sync, Windows support, UI file editing.

---

<div align="center">

**Your memory. Not theirs.**

Built for the [Mistral × Hackathon 2026](https://worldwide-hackathon.mistral.ai/).

</div>
