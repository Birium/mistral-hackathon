"""Search tool — BM25 and semantic search over the indexed vault."""

import asyncio
import logging
from typing import Optional, List

from agent.tools.base_tool import BaseTool
from functions.search import search as _search_impl

logger = logging.getLogger(__name__)


def search(
    queries: List[str],
    mode: str = "fast",
    scopes: Optional[List[str]] = None,
) -> str:
    """Search the indexed vault via QMD (BM25 or full semantic pipeline).

    Args:
        queries: One or more search queries to run simultaneously.
        mode: 'fast' for BM25 term matching, 'deep' for full semantic pipeline.
        scopes: Optional list of glob patterns to restrict the search scope.
    """
    try:
        results = asyncio.run(_search_impl(queries=queries, mode=mode, scopes=scopes))
    except Exception as e:
        return f"[SEARCH ERROR] {e}"

    if not results:
        return f"No results found for: {queries}"

    logger.info(
        f"[search] returning {len(results)} results for queries={queries} with scopes={scopes}"
    )

    lines = [f"## Search results for `{queries}`\n"]
    for r in results:
        lines.append(f"### {r.path} (score: {r.score}, lines: {r.lines})")
        lines.append(f"```\n{r.chunk_with_context}\n```\n")

    return "\n".join(lines)


SearchTool = BaseTool(search)


SEARCH_TOOL_PROMPT = """\
<search-tool>
Search is the scanning tool. It casts a net across the vault using keywords or semantic
meaning and returns scored chunks from wherever they match. Use it when you don't know
where the information lives — to orient yourself before reading.

<modes>
<fast>
BM25 term matching. Instant. Your default mode.
Matches exact terms: names, dates, identifiers, tags, status values. A rare term in
2 chunks out of 200 gets massive weight. Use whenever the relevant content shares
vocabulary with your query.

Examples: a person's name, a project term, `[décision]`, `status: bloqué`, a date.
</fast>

<deep>
Full semantic pipeline: query expansion, BM25, vector search, RRF fusion, re-ranking.
Takes ~10 seconds. Use when you don't know the exact terms that appear in the vault
but you know what you're looking for conceptually.

Examples: "that decision about payment architecture", "why did we drop the external
provider", "the main client friction point".
</deep>

Rule of thumb: if you can name what you're searching for, use fast. If you can only
describe it, use deep.
</modes>

<scopes>
Scope every search. Unscoped searches waste ranking on irrelevant files.

One project, all files:       ["vault/projects/[name]/*"]
All project states:           ["vault/projects/*/state.md"]
All changelogs:               ["vault/projects/*/changelog.md", "vault/changelog.md"]
All tasks:                    ["vault/projects/*/tasks.md", "vault/tasks.md"]
All buckets:                  ["vault/projects/*/bucket/*", "vault/bucket/*"]
All descriptions:             ["vault/projects/*/description.md"]
</scopes>

<multi-query>
Pass multiple queries in one call for broad coverage. Results are merged, deduplicated,
and ranked globally. More efficient than separate calls.

Example: `queries: ["comptable", "TVA", "bilan"]` — explores a topic from three angles.
</multi-query>

<examples>
User asks "where does project X stand?"
→ Don't search. Read `projects/X/state.md` directly — destination is known.

User asks "when did we decide to drop the external API?"
→ `search(queries=["API externe", "décision API"], mode="fast", scopes=["vault/projects/*/changelog.md", "vault/changelog.md"])`

User asks "everything related to Marie"
→ `search(queries=["Marie"], mode="fast")` — no scope, cast wide.

User asks "that discussion about simplifying the onboarding flow"
→ `search(queries=["simplifying onboarding flow"], mode="deep", scopes=["vault/projects/*/changelog.md", "vault/projects/*/bucket/*"])`

User asks "are any projects blocked?"
→ Don't search. `read(["projects/*/state.md"])` — glob covers all states directly.
</examples>

<using-results>
Search results include surrounding context lines. Read the chunks before reaching for
read — often the chunk itself answers the question or pinpoints the exact file and
section. Do not reflexively read every file that appears in results.
</using-results>

<iteration>
If the first search returns nothing useful: try different terms, switch modes, broaden
or narrow scope. Two to three passes is normal. Giving up after one empty result is not.
</iteration>
</search-tool>"""