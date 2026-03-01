# Knower — Install & Configuration

Full setup guide, MCP integrations, and CLI reference.
For the product overview and architecture: **[README.md](README.md)**

---

## Prerequisites

| Dependency                 | Version | Notes                           |
| -------------------------- | ------- | ------------------------------- |
| macOS                      | any     | Only supported platform for MVP |
| Python                     | ≥ 3.10  |                                 |
| Node.js                    | ≥ 22    |                                 |
| [uv](https://astral.sh/uv) | any     | Python package manager          |

---

## Install

```bash
git clone git@github.com:Birium/mistral-hackathon.git && cd knower
./install.sh
```

The installer runs the following steps:

1. Checks platform and dependencies
2. Installs QMD globally — `npm install -g @tobilu/qmd`
3. Downloads QMD models (~2 GB, one-time, cached to `~/.cache/qmd/models/`)
4. Creates Python venv in `core/.venv`
5. Writes config to `~/.config/knower/config`
6. Symlinks `knower` CLI to `/usr/local/bin`

Subsequent boots skip step 3 entirely — models are already cached.

---

## Configure

```bash
knower config vault ~/my-vault    # set vault location (created if it doesn't exist)
knower config show                # print current config
```

---

## Run

### Production mode

```bash
knower start           # starts core in background
open http://localhost:8000
```

### Development mode

```bash
knower dev             # core with hot-reload + Vite frontend in parallel
```

---

## MCP Integration

Knower exposes two MCP tools: `update(content)` and `search(content)`.
Available at `http://localhost:8000/mcp` (Streamable HTTP) and `http://localhost:8000/mcp/sse` (SSE).

### Mistral Vibe

Official docs: [Mistral Vibe MCP configuration](https://docs.mistral.ai/mistral-vibe/introduction/configuration#mcp-server-configuration)

```toml
[[mcp_servers]]
name = "knower"
transport = "streamable-http"
url = "http://localhost:8000/mcp"
```

Tools follow the `{server_name}_{tool_name}` pattern. Configure permissions:

```toml
[tools.knower_search]
permission = "always"

[tools.knower_update]
permission = "always"
```

### Claude Code

```bash
claude mcp add knower --transport sse http://localhost:8000/mcp/sse
```

### Open Code

Config file location varies — [see official docs](https://opencode.ai/docs/config/#ordre-de-priorit%C3%A9) for lookup order.

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

---

## REST API

For scripts or custom agents that don't use MCP:

```
POST /update    { "content": "..." }           # returns { status, id }
POST /search    { "query": "..." }             # returns structured Markdown
```

`/update` returns immediately with an acknowledgment — processing is async via the internal queue. `/search` is synchronous and read-only.

---

## CLI Reference

| Command                      | Description                                    |
| ---------------------------- | ---------------------------------------------- |
| `knower start`               | Start core in background (prod)                |
| `knower stop`                | Stop core                                      |
| `knower dev`                 | Dev mode: core (hot-reload) + Vite frontend    |
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

## QMD Models

All models are GGUF files, downloaded once during `./install.sh` and cached to `~/.cache/qmd/models/`.

| Model                    | Size    | Role                                                                    |
| ------------------------ | ------- | ----------------------------------------------------------------------- |
| **Qwen3 1.7B + LoRA**    | ~1.1 GB | Query expansion — HyDE documents, semantic variants, keyword expansions |
| **GGUF embedding model** | ~300 MB | Vector embeddings for semantic search                                   |
| **LLM Reranker (0.6B)**  | ~640 MB | Re-scores fused results for final ranking                               |

To remove models: `knower uninstall --purge`
