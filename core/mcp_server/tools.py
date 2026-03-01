import asyncio

from env import env

VAULT = env.VAULT_PATH
if not VAULT:
    raise RuntimeError("VAULT_PATH env var is not set")


UPDATE_DESCRIPTION = """\
Save information to the user's personal knowledge vault.

Use this tool to persist any valuable content from the current session. The vault
handles all routing and structuring automatically — just send raw text, any length,
any format.

When to call this tool:
- The user explicitly asks to save, store, or remember something ("save this",
  "note that", "log this decision", "remember this for later").
- A significant decision was made during the session — architectural choices,
  technology picks, strategic directions, trade-offs resolved.
- The session produced important outcomes worth preserving — conclusions, findings,
  action items, summaries.
- At the end of a productive session, to capture what was accomplished and what
  comes next.
- Any time information emerges that the user would benefit from having stored
  permanently rather than lost in conversation history.

What to send: raw text describing what happened, what was decided, what was produced,
or what needs to be remembered. Include all relevant context — project names, dates,
reasoning, outcomes. The more context, the better the routing.

Returns a short confirmation of what was saved and where.\
"""

SEARCH_DESCRIPTION = """\
Search the user's personal knowledge vault. Read-only — never modifies anything.

The vault contains the user's entire knowledge base: all projects with their
descriptions, statuses, and histories, all past decisions and their reasoning,
active and completed tasks, meeting notes, emails, documents, and general notes.
Everything the user has ever stored about their work and life is in there.

Use this tool instead of guessing or relying on conversation history whenever you
need to know something about the user's world:
- "What's the status of project X?" or "What am I working on right now?"
- "What did we decide about Y?" or "Why did we choose Z over W?"
- "What are my current blockers?" or "What tasks are pending?"
- "What's the context around this project?" or "What happened last week?"
- The user asks a question about their own projects, decisions, or history.
- You need background context to give a better answer — check the vault first.

Send a natural language question. Returns an overview of what was found with
the relevant source files attached.\
"""


async def update(content: str) -> str:
    """Save information to the user's personal knowledge vault."""
    from agent.agent.update_agent import UpdateAgent
    from agent.utils.logger import RequestLogger

    agent = UpdateAgent()

    def _run() -> str:
        log = RequestLogger("update")
        try:
            parts = []
            for event in agent.process(content):
                log.log(event)
                if event.get("type") == "answer" and not event.get("tool_calls"):
                    parts.append(event.get("content", ""))
            return "".join(parts)
        finally:
            log.save()

    result = await asyncio.to_thread(_run)
    return result or "Update agent processed the content."


async def search(content: str) -> str:
    """Search the user's personal knowledge vault."""
    from agent.agent.search_agent import SearchAgent
    from agent.utils.logger import RequestLogger

    agent = SearchAgent()

    def _run() -> str:
        log = RequestLogger("search")
        try:
            parts = []
            for event in agent.process(content):
                log.log(event)
                if event.get("type") == "answer" and not event.get("tool_calls"):
                    parts.append(event.get("content", ""))
            return "".join(parts)
        finally:
            log.save()

    try:
        result = await asyncio.to_thread(_run)
    except Exception as e:
        return f"[search error] {e}"

    return result or f"No answer returned for: {content}"