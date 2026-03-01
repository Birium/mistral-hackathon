"""
Shared vault context loader for all agents.

Builds a structured XML context block injected at the top of every agent payload.
Includes today's date, vault overview, vault structure (tree), and user profile.
"""

from datetime import datetime
from agent.tools.tools import read, tree


VAULT_CONTEXT_TEMPLATE = """<date>{date}</date>

<overview>
{overview}
</overview>

<vault-structure>
{vault_structure}
</vault-structure>

<profile>
{profile}
</profile>"""


VAULT_CONTEXT_ERROR_TEMPLATE = """<date>{date}</date>

<vault-context-error>{error}</vault-context-error>"""


def load_vault_context() -> str:
    """
    Load and format vault context as structured XML.

    Returns a single string with four XML sections:
      - <date>            : today's date in YYYY-MM-DD format
      - <overview>        : contents of overview.md
      - <vault-structure> : output of tree(depth=1), no file label
      - <profile>         : contents of profile.md

    On failure, returns a minimal XML block with the error message.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        overview_content = read("overview.md")
        vault_tree_content = tree(depth=1)
        profile_content = read("profile.md")

        return VAULT_CONTEXT_TEMPLATE.format(
            date=today,
            overview=overview_content,
            vault_structure=vault_tree_content,
            profile=profile_content,
        )

    except Exception as e:
        return VAULT_CONTEXT_ERROR_TEMPLATE.format(
            date=today,
            error=e,
        )