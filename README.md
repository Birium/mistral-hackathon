# Knower

Personal knowledge system with an MCP server for Claude Code.

## Install

```bash
chmod +x install.sh && ./install.sh
```

This creates a `knower` command available system-wide via symlink at `/usr/local/bin/knower`.

## Usage

```bash
knower start       # start all services
knower status      # check running containers
knower visualize   # open web UI
```

## Services

| Service    | URL              | What it does                        |
| ---------- | ---------------- | ----------------------------------- |
| `core`     | `localhost:8000` | FastAPI + MCP server + file watcher |
| `vectordb` | `localhost:6333` | Qdrant — semantic search storage    |
| `web`      | `localhost:5173` | Visual vault explorer               |

Your vault lives in `./vault/` — a plain folder of Markdown files, bind-mounted into the container.

## Connect to Claude Code

**1. Start the stack**

```bash
knower start
```

**2. Register the MCP server**

```bash
claude mcp add knower --transport sse http://localhost:8000/mcp/sse
```

**3. Verify**

```bash
claude mcp list
```

You should see:

```bash
knower: http://localhost:8000/mcp/sse (SSE) - ✓ Connected
```

**4. Test in a Claude Code session**

Start a Claude Code session and ask:

```
List all files in my vault.
```

Claude should call the `tree` tool and return your vault structure.

## Connect to Mistral Vibe

**1. Start the stack**

```bash
knower start
```

**2. Configure MCP tools**

(One is already existing, feel free to edit it)
Create a configuration file (e.g., `mistral_vibe_config.toml`) with your MCP server details:

```toml
[[mcp_servers]]
name = "knower"
transport = "streamable-http"
url = "http://localhost:8000/mcp"

# Set tool permissions
[tools.knower_tree]
permission = "always"

[tools.knower_read]
permission = "always"

[tools.knower_search]
permission = "always"
```

**3. Test with Mistral Vibe**

Start a Mistral Vibe session and ask:

```
List all files in my vault.
```

Mistral Vibe will use the configured MCP tools to access your vault structure.

## Uninstall MCP

**For Claude Code:**

```bash
claude mcp remove knower
```

**For Mistral Vibe:**
Simply remove or modify the `mistral_vibe_config.toml` file to update your MCP configuration.