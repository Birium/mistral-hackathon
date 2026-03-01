WRITE_TOOL_PROMPT = """\
<write-tool>
Write creates a new file or completely replaces an existing one. The entire content
is yours to define. Do not include frontmatter fields (`created`, `updated`, `tokens`) —
the background job handles those automatically after every write.

Use write when creating a file that does not exist yet — a new project's description.md,
a new bucket item, an inbox review.md. Use it when the changes to an existing file are
so extensive that surgical editing would be messier than a clean rewrite — a full
restructuring of state.md, a description.md that needs to be rebuilt from scratch.

Do not use write to add an entry to a changelog — that is what append does.
Do not use write to update a single section of a file — that is what edit does.
Write replaces everything. Be certain that is what you intend.

Parent directories are created automatically if they do not exist.
</write-tool>"""