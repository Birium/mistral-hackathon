# Knower

Personal memory system. Send information to it, query it back. Everything lives in a local folder of plain Markdown files.

## Requirements

- macOS
- Python 3.12+
- Node.js 22+
- [uv](https://github.com/astral-sh/uv)

## Install

```bash
./install.sh
```

## First run

```bash
knower config vault ~/my-vault
knower start --dev
```

## Commands

| Command                     | Description                          |
| --------------------------- | ------------------------------------ |
| `knower start`              | Start core in background (prod)      |
| `knower start --dev`        | Start core in foreground (hot reload)|
| `knower dev`                | Start core + web in dev mode         |
| `knower stop`               | Stop core                            |
| `knower status`             | Show running state + config          |
| `knower logs`               | Tail prod log                        |
| `knower visualize`          | Start Vite dev server on :5173       |
| `knower visualize --bg`     | Same, in background                  |
| `knower vault`              | Open vault in Finder                 |
| `knower config vault <path>`| Set vault path                       |
| `knower config show`        | Print current config                 |
| `knower shell`              | Open shell with Python venv activated|

## Services

| Service | URL                    |
| ------- | ---------------------- |
| Core    | `http://localhost:8000`|
| Web     | `http://localhost:5173`|

## Connect to Claude Code

```bash
knower start
claude mcp add knower --transport sse http://localhost:8000/mcp/sse
claude mcp list  # verify: ✓ Connected
```

## Connect to Mistral Vibe

```toml
[[mcp_servers]]
name = "knower"
transport = "streamable-http"
url = "http://localhost:8000/mcp"
```

## Uninstall MCP

**For Claude Code:**

```bash
claude mcp remove knower
```

**For Mistral Vibe:**
Simply remove or modify the `mistral_vibe_config.toml` file to update your MCP configuration.