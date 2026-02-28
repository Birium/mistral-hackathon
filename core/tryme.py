import argparse
from pathlib import Path

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
