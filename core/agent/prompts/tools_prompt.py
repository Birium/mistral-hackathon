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

WRITE_TOOL_PROMPT = """\
<write-tool>
Creates a new file or completely replaces an existing one. This is full-file writing —
the entire content is yours to define. Do not include frontmatter (created, updated, tokens) —
the background job handles that automatically after every write.

Use write when creating a file that does not exist yet — a new project's description.md,
a new bucket item, an inbox review.md. Use it when the structural changes to an existing
file are so extensive that surgical editing would be messier than a clean rewrite.

Do not use write to add an entry to a changelog — that is what append does. Do not use
write to update a single section of state.md — that is what edit does. Write replaces
everything. Be sure that is what you want.

Parent directories are created automatically if they do not exist.
</write-tool>"""

EDIT_TOOL_PROMPT = """\
<edit-tool>
Modifies a precise section of a file via exact search-and-replace. You provide the old
text and the new text. The tool finds the first occurrence and replaces it. Nothing else
in the file is touched.

You MUST read the file via `read` before calling edit. Without the exact current content,
you cannot construct a valid old_content. This is not a suggestion — it is a hard
precondition.

old_content can include line number prefixes from read output (`7  | ## Statut global`).
The tool strips them automatically before matching. This means you can copy directly from
a read result without cleaning it.

Make old_content unique enough to match exactly one location. If the text you want to
change appears multiple times, include surrounding context to disambiguate. The tool only
replaces the first match — if you target the wrong one, the edit lands in the wrong place.

Use edit for state.md updates, task status changes, overview.md project line modifications —
any case where one section changes and the rest stays identical.
</edit-tool>"""

APPEND_TOOL_PROMPT = """\
<append-tool>
Inserts a block of markdown at the top or bottom of a file without reading it first.
This is the zero-read insertion tool — its entire value is that it never loads the
existing content into your context.

Use `position: "top"` for changelogs. Changelogs are newest-first, so new entries go at
the top. On a changelog with 300 days of history, append lets you add today's entry without
loading 50k tokens of past entries. This is not an optimization — it is the intended
workflow.

Use `position: "bottom"` for adding tasks to tasks.md.

If the file has frontmatter, top insertion places content after the closing `---` of the
frontmatter, not before it.

Two identical H1 dates in a changelog are explicitly acceptable. If you append a
`# 2025-07-14` block and one already exists, the file will contain two. This indicates
two distinct update moments for the same day. Do not try to merge with an existing H1 —
that would require reading the file, which defeats the purpose of append.
</append-tool>"""

MOVE_TOOL_PROMPT = """\
<move-tool>
Relocates a file or directory from one path to another. The content is untouched — only
the position in the vault changes. Parent directories at the destination are created
automatically.

Use move when routing files from inbox to their final destination after the user confirms,
when correcting an initial routing mistake, or when a bucket item's project ownership
becomes clear. Move works on entire directories too — useful for relocating inbox folders.
</move-tool>"""

DELETE_TOOL_PROMPT = """\
<delete-tool>
Removes a file or an entire directory recursively. Deletion is permanent — there is no
trash, no archive. The history of what happened lives in the changelog, not in deleted files.

The primary use case is removing inbox folders after resolution. The sequence is always:
route the files to their destination, log in the changelog, then delete the inbox folder.
</delete-tool>"""
