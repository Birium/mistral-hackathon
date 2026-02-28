"""
Unit tests for functions/search/ — qmd.raw_search is mocked.
Run: pytest tests/test_search.py -v
"""

import pytest
from unittest.mock import AsyncMock, patch

RAW_RESULTS = [
    {
        "docid": "#aaa111",
        "file": "qmd://vault/projects/startup-x/changelog.md",
        "score": 0.89,
        "snippet": "@@ -8,4 @@ (2 before, 0 after)\n\n## [décision] Abandon API\nLe prestataire ne peut pas livrer.\n",
    },
    {
        "docid": "#bbb222",
        "file": "qmd://vault/profile.md",  # excluded
        "score": 0.75,
        "snippet": "@@ -1,3 @@ (0 before, 0 after)\n\n# Profile\nUser: Alice\n",
    },
    {
        "docid": "#ccc333",
        "file": "qmd://vault/inbox/pending.md",  # excluded
        "score": 0.70,
        "snippet": "@@ -1,2 @@ (0 before, 0 after)\n\n# Pending\n",
    },
    {
        "docid": "#ddd444",
        "file": "qmd://vault/projects/appart-search/state.md",
        "score": 0.50,
        "snippet": "@@ -3,2 @@ (1 before, 0 after)\n\nEn avance sur planning.\n",
    },
]


@pytest.mark.asyncio
async def test_exclusions_are_filtered():
    with patch("qmd.raw_search", new=AsyncMock(return_value=RAW_RESULTS)):
        from functions.search import search

        results = await search(["décision"], mode="fast", scopes=None)

    paths = [r.path for r in results]
    assert "profile.md" not in paths
    assert "inbox/pending.md" not in paths
    assert "projects/startup-x/changelog.md" in paths


@pytest.mark.asyncio
async def test_scope_filters_correctly():
    with patch("qmd.raw_search", new=AsyncMock(return_value=RAW_RESULTS)):
        from functions.search import search

        results = await search(
            ["décision"],
            mode="fast",
            scopes=["vault/projects/startup-x/*"],
        )

    paths = [r.path for r in results]
    assert all(p.startswith("projects/startup-x/") for p in paths)
    assert "projects/appart-search/state.md" not in paths


@pytest.mark.asyncio
async def test_deduplication():
    # Same file returned by two queries — should appear only once with highest score
    dup = [
        {
            "docid": "#aaa111",
            "file": "qmd://vault/changelog.md",
            "score": 0.60,
            "snippet": "@@ -1,2 @@ (0 before, 0 after)\n\ncontent\n",
        },
        {
            "docid": "#aaa111",
            "file": "qmd://vault/changelog.md",
            "score": 0.90,
            "snippet": "@@ -1,2 @@ (0 before, 0 after)\n\ncontent\n",
        },
    ]
    with patch("qmd.raw_search", new=AsyncMock(return_value=dup)):
        from functions.search import search

        results = await search(["a", "b"], mode="fast", scopes=None)

    assert len(results) == 1
    assert results[0].score == 0.90


@pytest.mark.asyncio
async def test_empty_queries_raises():
    from functions.search import search

    with pytest.raises(ValueError):
        await search([], mode="fast")


@pytest.mark.asyncio
async def test_invalid_mode_raises():
    from functions.search import search

    with pytest.raises(ValueError):
        await search(["test"], mode="banana")


@pytest.mark.asyncio
async def test_sorted_by_score_descending():
    with patch("qmd.raw_search", new=AsyncMock(return_value=RAW_RESULTS)):
        from functions.search import search

        results = await search(["test"], mode="fast", scopes=None)

    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
