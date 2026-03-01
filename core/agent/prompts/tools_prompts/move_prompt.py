MOVE_TOOL_PROMPT = """\
<move-tool>
Move relocates a file or directory from one path to another. The content is untouched —
only the position in the vault changes. Parent directories at the destination are
created automatically if they do not exist.

Use move when routing files from an inbox folder to their final destination after
the user confirms resolution. Use it when correcting an initial routing mistake,
or when a bucket item's project ownership becomes clear after further context.
Move works on entire directories too — useful for relocating inbox folders wholesale.

Always verify the source path exists before calling move. Use the vault-structure
or a tree call to confirm the path — a move to a wrong destination is harder to
fix than a read that returns nothing.
</move-tool>"""