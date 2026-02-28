# Knower

Personal memory system. Send information to it, query it back. Everything lives in a local folder of plain Markdown files.

---

## Requirements

- macOS
- Python 3.12+
- Node.js 22+
- [uv](https://github.com/astral-sh/uv)

---

## Install

```bash
./install.sh
```

---

## Quick start

**Development** — core + web, logs in terminal:
```bash
knower dev
```

**Production** — set a vault path, run core in background:
```bash
knower config vault ~/my-vault
knower start
```

---

## Commands

| Command | Description |
|---|---|
| `knower dev` | Dev mode: core (bg, hot-reload, logs in terminal) + web (fg) |
| `knower start` | Prod: start core in background |
| `knower stop` | Stop core |
| `knower status` | Show config and running state |
| `knower logs` | Tail core log (prod) |
| `knower web` | Start Vite dev server on :5173 |
| `knower web --bg` | Same, in background |
| `knower vault` | Open vault in Finder |
| `knower config vault <path>` | Set vault path |
| `knower config show` | Print current config |

---

## Services

| Service | URL |
|---|---|
| Core API | `http://localhost:8000` |
| Web UI | `http://localhost:5173` |

---

## MCP integration

### Claude Code

```bash
knower start
claude mcp add knower --transport sse http://localhost:8000/mcp/sse
claude mcp list   # verify: ✓ Connected
```

To remove:
```bash
claude mcp remove knower
```

### Mistral Le Chat / Vibe

```toml
[[mcp_servers]]
name = "knower"
transport = "streamable-http"
url = "http://localhost:8000/mcp"
```

To remove: delete or comment out the block above from your config file.
