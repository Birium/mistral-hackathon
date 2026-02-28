SEARCH_TOOL_PROMPT = """\
<search-tool>
Your primary discovery tool. It queries the indexed vault and returns ranked chunks
with surrounding context lines, scores, and source paths.

Use `mode: "fast"` when you are looking for specific, named things.
BM25 matches on exact terms. It is instant and precise when you know what you are after:
names ("Marie", "Dupont"), identifiers ("API Stripe", "TVA Q3"), dates ("2025-07-14"),
tags ("[décision]", "[blocage]"), statuses ("status: bloqué", "prio: haute").
A rare term that appears in 2 chunks out of 200 gets a massive weight.
A common word like "projet" is nearly ignored. That is exactly BM25's strength.

Use `mode: "deep"` when the query is semantic, conceptual, or vaguely worded.
The full pipeline — query expansion, BM25, vector search, RRF fusion, re-ranking —
catches what exact term matching would miss.
"That decision about payment architecture", "why did we drop the external provider",
"everything related to the main client" — these are deep queries.
When you are unsure which mode to use, default to deep. It is slower but more thorough.

Use `scopes` aggressively. If overview.md tells you the answer is in startup-x,
scope your search to `["vault/projects/startup-x/*"]` instead of searching the whole vault.
If you are looking for blocked projects across the system, scope to
`["vault/projects/*/state.md"]`. Scoped searches are faster and produce cleaner results.

Common scope patterns you will use often:
- One project, all files: `["vault/projects/[name]/*"]`
- All project states: `["vault/projects/*/state.md"]`
- All changelogs: `["vault/projects/*/changelog.md", "vault/changelog.md"]`
- All tasks: `["vault/projects/*/tasks.md", "vault/tasks.md"]`
- All buckets: `["vault/projects/*/bucket/*", "vault/bucket/*"]`
- All descriptions: `["vault/projects/*/description.md"]`

Use multiple queries in a single call for broad coverage. Instead of three separate
search calls, pass `queries: ["comptable", "TVA", "bilan"]` in one. Results are merged,
deduplicated, and ranked globally. This is powerful when exploring a topic from
multiple angles or when you are not sure which exact term appears in the vault.
</search-tool>"""

READ_TOOL_PROMPT = """\
<read-tool>
Use read for two purposes: getting full content of a file identified by search,
and exploring the direct contents of a directory.

Be smart about large files. tree.md tells you token counts. A changelog at 8k tokens?
Read it fully, it is fine. A changelog at 45k tokens? Use `head=3000` to get
the most recent entries (changelogs are newest-first), or rely on the search chunks
you already received instead of reading the whole file.

Read a directory to see all files at one level without recursion:
`read("vault/projects/startup-x/")` returns description, state, tasks, changelog —
but not the bucket, which is a subdirectory. To read bucket contents:
`read("vault/projects/startup-x/bucket/")`.

Read multiple files in a single call to batch efficiently:
`read(["vault/projects/startup-x/state.md", "vault/projects/appart-search/state.md"])`.
</read-tool>"""

TREE_TOOL_PROMPT = """\
<tree-tool>
Use tree to zoom into structure when tree.md does not provide enough detail.
tree.md collapses project folders by default. If you need to see the individual files
inside a bucket — their names, sizes, timestamps — call
`tree("vault/projects/startup-x/bucket/", depth=1)`.

You rarely need this tool during a search session. tree.md in your initial context
usually gives you enough structural information. Use it when you encounter
a subdirectory you want to inspect before deciding what to read.
</tree-tool>"""

CONCAT_TOOL_PROMPT = """\
<concat-tool>
Your assembly tool. Always the last tool you call in a session.

After exploring the vault and identifying the relevant files, call concat with
an ordered list of file paths. The tool mechanically assembles them into a structured
markdown document: each file becomes a block prefixed by its path, with line numbers.

Not every file you read during exploration belongs in the final output.
Include what directly answers the user's question — the state.md showing current status,
the changelog entries with the relevant decision, the tasks they asked about.
Leave out files you read only for navigation or orientation.

Order matters. Put the most directly relevant file first.
</concat-tool>"""