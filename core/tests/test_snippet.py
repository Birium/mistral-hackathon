"""
Tests for snippet.py — pure string parsing, no I/O.
Run: pytest tests/test_snippet.py -v
"""

from functions.search.snippet import parse_snippet


def test_basic_parse():
    snippet = (
        "1: @@ -4,4 @@ (3 before, 0 after)\n2: \n3: # Profile\n4: \n5: No profile yet."
    )
    lines_range, ctx = parse_snippet(snippet)

    # match_start = 4 + 3 = 7, match_end = 4 + 4 - 0 - 1 = 7
    assert lines_range == "7-7"
    assert "   4  | " in ctx
    assert "   7  | No profile yet." in ctx


def test_no_context_lines():
    snippet = (
        "1: @@ -10,2 @@ (0 before, 0 after)\n2: First match line\n3: Second match line"
    )
    lines_range, ctx = parse_snippet(snippet)

    # match_start = 10 + 0 = 10, match_end = 10 + 2 - 0 - 1 = 11
    assert lines_range == "10-11"
    assert "  10  | First match line" in ctx
    assert "  11  | Second match line" in ctx


def test_with_after_context():
    snippet = (
        "1: @@ -5,4 @@ (1 before, 2 after)\n"
        "2: context before\n"
        "3: match line\n"
        "4: context after 1\n"
        "5: context after 2"
    )
    lines_range, ctx = parse_snippet(snippet)

    # before=1, after=2, start=5, total=4 (content only)
    # match_start = 5 + 1 = 6, match_end = 5 + 4 - 2 - 1 = 6
    assert lines_range == "6-6"


def test_fallback_on_bad_header():
    snippet = "some text without a header"
    lines_range, ctx = parse_snippet(snippet)
    assert lines_range == "?"
    assert "some text" in ctx


def test_empty_snippet():
    lines_range, ctx = parse_snippet("")
    assert lines_range == "?"
    assert ctx == ""


def test_strips_snippet_relative_numbers():
    snippet = "1: @@ -1,2 @@ (0 before, 0 after)\n2: hello\n3: world"
    _, ctx = parse_snippet(snippet)
    # Should NOT contain "2: hello" (snippet-relative), but "   1  | hello"
    assert "2: hello" not in ctx
    assert "   1  | hello" in ctx
