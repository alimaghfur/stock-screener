"""News layer — fetches headlines from Yahoo Finance via yfinance.

Same caching pattern as ``core.data``: a streamlit-aware cache decorator that
falls back to a no-op when Streamlit is not available (so tests don't need
the runtime).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

try:  # pragma: no cover - exercised at runtime
    import streamlit as st

    def _cache_data(*args: Any, **kwargs: Any):
        return st.cache_data(*args, **kwargs)
except Exception:  # pragma: no cover
    def _cache_data(*args: Any, **kwargs: Any):
        def deco(fn):
            return fn
        return deco


def _yfinance():
    """Lazy-import yfinance so unit tests don't require the library at import time."""
    import yfinance as yf
    return yf


@dataclass
class NewsArticle:
    """One headline with the metadata needed for rendering."""

    title: str
    summary: str
    publisher: str
    url: str
    published_at: datetime  # timezone-aware UTC
    thumbnail_url: str | None = None
    lang: str = "en-US"
    related_tickers: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_pub_date(raw: str | None) -> datetime:
    """Best-effort ISO-8601 parse with UTC fallback to ``now``."""
    if not raw:
        return datetime.now(tz=timezone.utc)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return datetime.now(tz=timezone.utc)


def _pick_thumbnail(thumbnail: dict | None) -> str | None:
    """Prefer a small / medium resolution; fall back to original."""
    if not thumbnail:
        return None
    resolutions = thumbnail.get("resolutions") or []
    for res in resolutions:
        if res.get("tag") and res.get("tag") != "original" and res.get("url"):
            return res["url"]
    return thumbnail.get("originalUrl")


def _parse_article(item: dict, fallback_symbol: str) -> NewsArticle | None:
    """Convert one yfinance ``news`` item into a ``NewsArticle``.

    yfinance currently nests article data under ``content`` and exposes both
    ``canonicalUrl`` and ``clickThroughUrl``; older shapes flatten the same
    fields. Both are handled.
    """
    content = item.get("content") or item
    title = content.get("title") or item.get("title") or ""
    if not title:
        return None

    url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
    url = url_obj.get("url") if isinstance(url_obj, dict) else None
    url = url or item.get("link") or ""

    pub_raw = content.get("pubDate") or content.get("displayTime")
    if pub_raw:
        published_at = _parse_pub_date(pub_raw)
    else:
        ts = item.get("providerPublishTime")
        if isinstance(ts, (int, float)):
            published_at = datetime.fromtimestamp(ts, tz=timezone.utc)
        else:
            published_at = datetime.now(tz=timezone.utc)

    provider = (content.get("provider") or {}).get("displayName") if isinstance(content.get("provider"), dict) else None
    publisher = provider or item.get("publisher") or "Yahoo Finance"

    lang = url_obj.get("lang") if isinstance(url_obj, dict) else None
    related = list(item.get("relatedTickers") or [])
    if fallback_symbol and fallback_symbol not in related:
        related.insert(0, fallback_symbol)

    return NewsArticle(
        title=title,
        summary=(content.get("summary") or content.get("description") or "").strip(),
        publisher=publisher,
        url=url,
        published_at=published_at,
        thumbnail_url=_pick_thumbnail(content.get("thumbnail")),
        lang=lang or "en-US",
        related_tickers=related,
    )


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

@_cache_data(ttl=600, show_spinner=False)
def fetch_news_for_symbol(symbol: str, limit: int = 10) -> list[NewsArticle]:
    """Return up to ``limit`` recent articles for one ticker.

    Returns an empty list on any error; failures are silent so the UI can
    degrade gracefully when a single ticker has no coverage.
    """
    if not symbol:
        return []
    yf = _yfinance()
    try:
        raw = yf.Ticker(symbol).news or []
    except Exception:
        return []
    articles: list[NewsArticle] = []
    for item in raw[:limit]:
        parsed = _parse_article(item, fallback_symbol=symbol)
        if parsed:
            articles.append(parsed)
    return articles


def fetch_news_for_universe(
    symbols: list[str],
    per_symbol: int = 3,
    max_total: int | None = None,
) -> list[NewsArticle]:
    """Aggregate news across many tickers, dedupe by URL, sort newest first."""
    seen: set[str] = set()
    out: list[NewsArticle] = []
    for sym in symbols:
        for art in fetch_news_for_symbol(sym, limit=per_symbol):
            key = art.url or art.title
            if key in seen:
                continue
            seen.add(key)
            out.append(art)
    out.sort(key=lambda a: a.published_at, reverse=True)
    if max_total is not None:
        out = out[:max_total]
    return out


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def humanize_age(dt: datetime, now: datetime | None = None) -> str:
    """Return a human-readable age like ``"3 hours ago"`` (UTC reference)."""
    now = now or datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    seconds = int((now - dt).total_seconds())
    if seconds < 0:
        return "just now"
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"
    return dt.strftime("%Y-%m-%d %H:%M UTC")
