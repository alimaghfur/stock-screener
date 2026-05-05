"""Tests for ``core.news`` — parsing, aggregation, and humanize_age."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from core import news as news_mod
from core.news import (
    NewsArticle,
    _parse_article,
    _pick_thumbnail,
    fetch_news_for_symbol,
    fetch_news_for_universe,
    humanize_age,
)


def _modern_item(
    *,
    title: str = "Sample headline",
    pub: str = "2026-05-04T10:00:00Z",
    publisher: str = "Reuters",
    url: str = "https://finance.yahoo.com/news/sample-001",
    summary: str = "A short summary.",
    thumb_url: str | None = "https://img.example/large.jpg",
    related: tuple[str, ...] = ("AAPL", "MSFT"),
) -> dict:
    """Build a yfinance-style ``news`` item with the modern nested ``content`` shape."""
    item: dict = {
        "id": "abc",
        "content": {
            "title": title,
            "summary": summary,
            "pubDate": pub,
            "displayTime": pub,
            "provider": {"displayName": publisher},
            "canonicalUrl": {"url": url, "lang": "en-US"},
            "clickThroughUrl": {"url": url},
        },
        "relatedTickers": list(related),
    }
    if thumb_url is not None:
        item["content"]["thumbnail"] = {
            "originalUrl": thumb_url,
            "resolutions": [
                {"url": thumb_url, "tag": "original", "width": 1000, "height": 1000},
                {"url": thumb_url + "?small", "tag": "170x128", "width": 170, "height": 128},
            ],
        }
    return item


# ---------------------------------------------------------------------------
# _parse_article
# ---------------------------------------------------------------------------

def test_parse_modern_yfinance_item_extracts_all_fields():
    art = _parse_article(_modern_item(), fallback_symbol="AAPL")
    assert art is not None
    assert art.title == "Sample headline"
    assert art.summary == "A short summary."
    assert art.publisher == "Reuters"
    assert art.url == "https://finance.yahoo.com/news/sample-001"
    assert art.published_at == datetime(2026, 5, 4, 10, 0, tzinfo=timezone.utc)
    # Thumbnail picker prefers a non-original resolution.
    assert art.thumbnail_url == "https://img.example/large.jpg?small"
    assert art.lang == "en-US"
    assert art.related_tickers[0] == "AAPL"
    assert "MSFT" in art.related_tickers


def test_parse_legacy_flat_item_falls_back_to_top_level_fields():
    legacy = {
        "title": "Legacy headline",
        "publisher": "Yahoo Finance",
        "link": "https://finance.yahoo.com/news/legacy",
        "providerPublishTime": int(
            datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc).timestamp()
        ),
        "relatedTickers": ["AAPL"],
    }
    art = _parse_article(legacy, fallback_symbol="AAPL")
    assert art is not None
    assert art.title == "Legacy headline"
    assert art.publisher == "Yahoo Finance"
    assert art.url == "https://finance.yahoo.com/news/legacy"
    assert art.published_at == datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert art.thumbnail_url is None
    assert art.related_tickers == ["AAPL"]


def test_parse_returns_none_when_title_missing():
    item = {"content": {"summary": "no title here"}}
    assert _parse_article(item, fallback_symbol="AAPL") is None


def test_parse_handles_invalid_pubdate_gracefully():
    item = _modern_item(pub="not a real date")
    art = _parse_article(item, fallback_symbol="AAPL")
    assert art is not None
    # Falls back to "now" — just assert it's a recent UTC timestamp.
    assert art.published_at.tzinfo is not None
    assert (datetime.now(tz=timezone.utc) - art.published_at).total_seconds() < 5


def test_pick_thumbnail_prefers_smaller_resolution_then_original():
    assert _pick_thumbnail(None) is None
    assert _pick_thumbnail({}) is None

    only_original = {
        "originalUrl": "https://img.example/orig.jpg",
        "resolutions": [
            {"url": "https://img.example/orig.jpg", "tag": "original"},
        ],
    }
    assert _pick_thumbnail(only_original) == "https://img.example/orig.jpg"

    with_small = {
        "originalUrl": "https://img.example/orig.jpg",
        "resolutions": [
            {"url": "https://img.example/orig.jpg", "tag": "original"},
            {"url": "https://img.example/small.jpg", "tag": "170x128"},
        ],
    }
    assert _pick_thumbnail(with_small) == "https://img.example/small.jpg"


# ---------------------------------------------------------------------------
# fetch_news_for_symbol / fetch_news_for_universe
# ---------------------------------------------------------------------------

class _FakeTicker:
    def __init__(self, news: list[dict]):
        self.news = news


def _patch_yfinance(news_by_symbol: dict[str, list[dict]]):
    """Return a ``patch`` context manager that stubs ``yf.Ticker``."""
    class _FakeYF:
        def Ticker(self, symbol: str) -> _FakeTicker:  # noqa: N802 (yfinance API name)
            return _FakeTicker(news_by_symbol.get(symbol, []))

    return patch.object(news_mod, "_yfinance", return_value=_FakeYF())


@pytest.fixture(autouse=True)
def _no_streamlit_cache():
    """Bypass streamlit's cache between tests so each call hits the stub."""
    if hasattr(fetch_news_for_symbol, "clear"):
        fetch_news_for_symbol.clear()
    yield
    if hasattr(fetch_news_for_symbol, "clear"):
        fetch_news_for_symbol.clear()


def test_fetch_news_for_symbol_parses_modern_payload():
    items = [_modern_item(title=f"Article {i}", url=f"https://x/{i}") for i in range(3)]
    with _patch_yfinance({"AAPL": items}):
        out = fetch_news_for_symbol("AAPL", limit=10)
    assert len(out) == 3
    assert all(isinstance(a, NewsArticle) for a in out)
    assert out[0].title == "Article 0"


def test_fetch_news_for_symbol_respects_limit():
    items = [_modern_item(title=f"A{i}", url=f"https://x/{i}") for i in range(10)]
    with _patch_yfinance({"AAPL": items}):
        out = fetch_news_for_symbol("AAPL", limit=3)
    assert len(out) == 3


def test_fetch_news_for_symbol_returns_empty_when_yfinance_raises():
    class _Boom:
        def Ticker(self, symbol: str):  # noqa: N802
            raise RuntimeError("network down")

    with patch.object(news_mod, "_yfinance", return_value=_Boom()):
        assert fetch_news_for_symbol("AAPL") == []


def test_fetch_news_for_symbol_returns_empty_for_blank_symbol():
    assert fetch_news_for_symbol("") == []


def test_fetch_news_for_universe_dedupes_and_sorts_newest_first():
    shared_url = "https://finance.yahoo.com/news/shared"
    older = _modern_item(
        title="Older shared", pub="2026-05-01T10:00:00Z", url=shared_url
    )
    newer = _modern_item(
        title="Newer shared", pub="2026-05-04T10:00:00Z", url=shared_url
    )
    aapl_only = _modern_item(
        title="AAPL only", pub="2026-05-03T10:00:00Z", url="https://x/aapl-only"
    )
    msft_only = _modern_item(
        title="MSFT only", pub="2026-05-02T10:00:00Z", url="https://x/msft-only"
    )

    feeds = {"AAPL": [newer, aapl_only], "MSFT": [older, msft_only]}
    with _patch_yfinance(feeds):
        out = fetch_news_for_universe(["AAPL", "MSFT"], per_symbol=5)

    titles = [a.title for a in out]
    # Shared URL appears once (deduped) and uses whichever was parsed first
    # (AAPL fetched first, so the newer copy wins).
    assert titles.count("Newer shared") == 1
    assert "Older shared" not in titles
    # Sorted newest-first.
    assert out[0].published_at >= out[-1].published_at


def test_fetch_news_for_universe_max_total_caps_results():
    items = {sym: [_modern_item(title=f"{sym}-{i}", url=f"https://x/{sym}/{i}") for i in range(5)]
             for sym in ("AAPL", "MSFT", "GOOG")}
    with _patch_yfinance(items):
        out = fetch_news_for_universe(["AAPL", "MSFT", "GOOG"], per_symbol=5, max_total=4)
    assert len(out) == 4


# ---------------------------------------------------------------------------
# humanize_age
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=5), "5s ago"),
        (timedelta(minutes=1), "1 minute ago"),
        (timedelta(minutes=42), "42 minutes ago"),
        (timedelta(hours=1), "1 hour ago"),
        (timedelta(hours=5), "5 hours ago"),
        (timedelta(days=1), "1 day ago"),
        (timedelta(days=3), "3 days ago"),
    ],
)
def test_humanize_age_buckets(delta: timedelta, expected: str):
    now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
    past = now - delta
    assert humanize_age(past, now=now) == expected


def test_humanize_age_falls_back_to_absolute_after_one_week():
    now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
    past = now - timedelta(days=10)
    assert humanize_age(past, now=now) == past.strftime("%Y-%m-%d %H:%M UTC")


def test_humanize_age_handles_naive_input():
    now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
    past_naive = datetime(2026, 5, 4, 11, 0)  # no tzinfo
    assert humanize_age(past_naive, now=now) == "1 hour ago"
