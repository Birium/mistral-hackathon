APPEND_TOOL_PROMPT = """\
<append-tool>
Append inserts a block of markdown at the top or bottom of a file without reading it
first. This is the zero-read insertion tool — its entire value is that it never loads
the existing content into your context.

Use `position: "top"` for changelogs. Changelogs are newest-first, so new entries go
at the top. On a changelog with 300 days of history at 60k tokens, append lets you
add today's entry without loading a single token of past content. This is not an
optimization — it is the intended workflow. Never read a changelog before appending to it.

Use `position: "bottom"` for tasks.md files, where new tasks are added at the end.

If the file has frontmatter, top insertion places content after the closing `---`
of the frontmatter block, not before it.

If the file does not exist, append creates it. In that case, include the full content
including any frontmatter you want — but remember the background job manages
`created`, `updated`, and `tokens`, so omit those fields.

Two identical H1 dates in a changelog are explicitly acceptable. If you append a
`# 2025-07-14` block and one already exists, the file will have two. This marks
two distinct update moments for the same day. Do not try to merge with an existing
H1 date — that would require reading the file, which defeats the purpose of append.
</append-tool>"""