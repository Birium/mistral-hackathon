"""
dev.py — developer exercise script for the frontmatter and tree packages.

Subcommands
-----------
tree <src> [--depth N]
    Scan a directory and print a formatted ASCII tree with token counts
    and last-modified timestamps.

frontmatter <file>
    Update the `updated` and `tokens` fields of a vault Markdown file,
    then print all three frontmatter values and the full file content.
    Useful for manually verifying frontmatter read/write behaviour.

Usage (run from core/)
----------------------
    python functions/frontmatter/dev.py tree ../../vault/
    python functions/frontmatter/dev.py tree ../../vault/ --depth 2
    python functions/frontmatter/dev.py frontmatter ../../vault/notes/foo.md
"""

import sys
from pathlib import Path

# Ensure `core/` is on the path so sibling packages resolve correctly
# regardless of where this script is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse

from functions.tree import tree
from functions.frontmatter import (
    FM, read_created,
    update_updated, read_updated,
    read_tokens, update_tokens, format_tokens,
)


def cmd_tree(args) -> None:
    print(tree(args.src, args.depth))


def cmd_frontmatter(args) -> None:
    path = Path(args.file)

    if not path.exists():
        print(f"[error] file not found: {path}")
        return

    update_updated(path)
    update_tokens(path)

    print(f"created:  {read_created(path)}")
    print(f"updated:  {read_updated(path)}")
    tokens = read_tokens(path)
    print(f"tokens:   {tokens} ({format_tokens(tokens)})")
    print(f"\n--- file content ---\n{path.read_text()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="y-knot dev tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_tree = sub.add_parser("tree", help="Scan and display a file tree.")
    p_tree.add_argument("src", help="Source directory to scan")
    p_tree.add_argument("--depth", type=int, default=None, help="Max depth to traverse")
    p_tree.set_defaults(func=cmd_tree)

    p_fm = sub.add_parser("frontmatter", help="Exercise all frontmatter interactions on a file.")
    p_fm.add_argument("file", help="Markdown file to operate on")
    p_fm.set_defaults(func=cmd_frontmatter)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
