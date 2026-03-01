SEARCH_TOOL_PROMPT = """\
<search-tool>
Search is your discovery tool for cases where you don't know exactly which file contains
the information, or where reading everything that could be relevant would cost too many tokens.

**When to use search vs read.**
If you already know which file holds the answer — because the overview named it,
or the vault-structure confirmed it exists — read directly. Search is for uncertainty:
when the project is unclear, when the information could be spread across multiple files,
when you're looking for a specific decision or event buried in a large changelog,
or when the bucket is too large to read whole.

**Mode: fast vs deep.**
Use `mode: "fast"` as your default. BM25 matches on exact terms — names, identifiers,
dates, tags, status values. It is instant and precise. A rare term that appears in
2 chunks out of 200 gets massive weight. Use fast whenever you know the specific terms
that should appear in the result: a person's name, a project term, a date, a tag like
`[décision]` or `status: bloqué`.

Use `mode: "deep"` when the query is semantic or conceptual — when you don't know
the exact terms that appear in the vault but you know what you're looking for. Deep runs
a full pipeline: query expansion, BM25, vector search, RRF fusion, re-ranking. It is
slower than fast but catches what exact term matching misses. Examples: "that decision
about payment architecture", "why did we drop the external provider", "everything about
the main client friction point". Use deep when fast would likely miss the target because
the relevant content doesn't share exact vocabulary with your query.

**Scopes.**
Use scopes aggressively. If the question is about one project, scope to that project.
If you're looking for blocked tasks across all projects, scope to all tasks files.
Scoped searches are faster and return cleaner, more relevant results.

Common scope patterns:
- One project, all files: `["vault/projects/[name]/*"]`
- All project states: `["vault/projects/*/state.md"]`
- All changelogs: `["vault/projects/*/changelog.md", "vault/changelog.md"]`
- All tasks: `["vault/projects/*/tasks.md", "vault/tasks.md"]`
- All buckets: `["vault/projects/*/bucket/*", "vault/bucket/*"]`
- All descriptions: `["vault/projects/*/description.md"]`

**Multiple queries in one call.**
Pass multiple queries in a single call for broad coverage:
`queries: ["comptable", "TVA", "bilan"]`. Results are merged, deduplicated, and ranked
globally. This is more efficient than three separate search calls and works well when
you're exploring a topic from multiple angles or are unsure which exact term appears.

**Reading from search results.**
Search results include surrounding context lines, scores, and source paths. Read the
chunks carefully before reaching for read — often the chunk itself contains enough
to answer the question, or it precisely identifies the file and section you need.
A high-scoring chunk from a changelog entry may already give you everything. Do not
reflexively read every file that appears in search results.

**Iterating when results are poor.**
If the first search didn't find what you need: try different terms, switch modes,
narrow or broaden scope. Two or three passes with different angles is normal. What is
not acceptable is giving up after one empty search and returning a thin answer.
</search-tool>"""