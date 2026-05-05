"""TradingView integration helpers.

TradingView does not expose a public REST API, so the integration is centered around:

1.  Symbol mapping between Yahoo Finance conventions (used internally) and
    TradingView's `EXCHANGE:TICKER` notation, e.g.:
        BBCA.JK   -> IDX:BBCA
        AAPL      -> NASDAQ:AAPL
        BRK-B     -> NYSE:BRK.B

2.  HTML snippets for the free TradingView embeddable widgets — Advanced Chart,
    Technical Analysis gauge, and Top Stories — that can be rendered via
    ``streamlit.components.v1.html``.

3.  A webhook payload parser for alerts that TradingView sends via Pine Script
    ``alert()`` / ``alertcondition()`` (consumed by ``tools/tradingview_webhook.py``).

Everything here is pure Python with no Streamlit / FastAPI dependency so it stays
unit-testable.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Symbol mapping
# ---------------------------------------------------------------------------

# Hand-maintained NASDAQ-listed subset.  Members of the NASDAQ-100 *index* are
# NOT all NASDAQ-listed (e.g., WMT, KHC, LIN, HON are NYSE-listed but still in
# the index), so we must curate this manually rather than auto-deriving from
# ``core/universe.NASDAQ100``.  Anything not found here defaults to NYSE.
_NASDAQ_TICKERS: frozenset[str] = frozenset({
    # Mega caps + popular tech
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    "AVGO", "COST", "PEP", "ADBE", "NFLX", "AMD", "INTC", "CSCO", "QCOM",
    "TXN", "AMAT", "INTU", "AMGN", "ISRG", "BKNG", "VRTX", "REGN", "ADP",
    "MU", "PANW", "SBUX", "ANET", "MELI", "ABNB", "CDNS", "SNPS", "LRCX",
    "KLAC", "ASML", "MAR", "MRVL", "ORLY", "FTNT", "MDLZ", "PYPL", "CHTR",
    "GILD", "CSX", "NXPI", "ADI", "MNST", "AEP", "KDP", "CTAS", "ROST",
    "PCAR", "PAYX", "DXCM", "TEAM", "FAST", "ODFL", "DDOG", "CRWD", "EXC",
    "BIIB", "WBD", "EBAY", "GEHC", "MCHP", "VRSK", "IDXX", "CPRT", "WBA",
    "PLTR", "COIN", "SNOW", "MARA", "NET", "ZS", "TMUS", "CMCSA", "ORCL",
    "SHOP", "MDB", "OKTA", "ROKU", "ZM", "DOCU", "SQ", "SOFI", "UBER",
    # Additional NASDAQ-listed names from the expanded NASDAQ-100 universe
    "ADSK", "ALNY", "APP", "ARM", "AXON", "CCEP", "CDW", "CEG", "CSGP",
    "CTSH", "DASH", "DLTR", "EA", "FANG", "FER", "INSM", "MPWR", "MRNA",
    "MSTR", "PDD", "PSKY", "SBAC", "SNDK", "STX", "TRI", "TTD", "TTWO",
    "VRSN", "WDAY", "WDC", "XEL",
})


def _looks_like_idx(symbol: str) -> bool:
    return symbol.upper().endswith(".JK")


def to_tradingview_symbol(symbol: str) -> str:
    """Convert a Yahoo Finance symbol into TradingView's ``EXCHANGE:TICKER`` form.

    >>> to_tradingview_symbol("BBCA.JK")
    'IDX:BBCA'
    >>> to_tradingview_symbol("AAPL")
    'NASDAQ:AAPL'
    >>> to_tradingview_symbol("brk-b")
    'NYSE:BRK.B'
    >>> to_tradingview_symbol("")
    ''
    """
    if not symbol:
        return ""
    sym = symbol.strip().upper()
    if not sym:
        return ""

    # Pre-mapped (already has exchange prefix)
    if ":" in sym:
        return sym

    if _looks_like_idx(sym):
        # Strip ``.JK`` suffix.
        return f"IDX:{sym[:-3]}"

    # US: prefer NASDAQ when we know it, otherwise NYSE.
    # Yahoo uses ``BRK-B`` with hyphen, TradingView prefers ``BRK.B``.
    tv_ticker = sym.replace("-", ".")
    if tv_ticker in _NASDAQ_TICKERS or sym in _NASDAQ_TICKERS:
        return f"NASDAQ:{tv_ticker}"
    return f"NYSE:{tv_ticker}"


def from_tradingview_symbol(tv_symbol: str) -> str:
    """Inverse of :func:`to_tradingview_symbol` — best-effort.

    >>> from_tradingview_symbol("IDX:BBCA")
    'BBCA.JK'
    >>> from_tradingview_symbol("NASDAQ:AAPL")
    'AAPL'
    >>> from_tradingview_symbol("NYSE:BRK.B")
    'BRK-B'
    >>> from_tradingview_symbol("AAPL")
    'AAPL'
    """
    if not tv_symbol:
        return ""
    raw = tv_symbol.strip().upper()
    if ":" not in raw:
        return raw
    exchange, _, ticker = raw.partition(":")
    if exchange == "IDX":
        return f"{ticker}.JK"
    # US — restore Yahoo's hyphen convention for share classes.
    return ticker.replace(".", "-")


# ---------------------------------------------------------------------------
# Widget HTML
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WidgetConfig:
    """Configuration shared by all TradingView widget helpers."""

    theme: str = "light"
    locale: str = "en"
    timezone: str = "Asia/Jakarta"
    width: str = "100%"
    height: int = 520


def _safe_json(payload: dict[str, Any]) -> str:
    """Serialize widget config to JSON suitable for inlining into HTML."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def advanced_chart_html(symbol: str, config: WidgetConfig | None = None) -> str:
    """Return HTML embed for TradingView's Advanced Chart widget.

    The widget renders a full TradingView chart with candles, indicators,
    drawing tools, and timeframe controls.
    """
    cfg = config or WidgetConfig()
    tv_symbol = to_tradingview_symbol(symbol) or symbol
    payload = {
        "autosize": True,
        "symbol": tv_symbol,
        "interval": "D",
        "timezone": cfg.timezone,
        "theme": cfg.theme,
        "style": "1",
        "locale": cfg.locale,
        "withdateranges": True,
        "hide_side_toolbar": False,
        "allow_symbol_change": True,
        "details": True,
        "calendar": False,
        "support_host": "https://www.tradingview.com",
    }
    return f"""<div class="tradingview-widget-container" style="height:{cfg.height}px;width:{cfg.width}">
  <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
  <script type="text/javascript"
          src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js"
          async>
  {_safe_json(payload)}
  </script>
</div>"""


def technical_analysis_html(symbol: str, config: WidgetConfig | None = None) -> str:
    """Return HTML embed for TradingView's Technical Analysis (gauge) widget.

    Renders a single gauge with verdict (Strong Buy / Buy / Neutral / Sell /
    Strong Sell) plus a breakdown of oscillators and moving averages — useful as
    a "second opinion" against our scalping/swing/BPJS/BSJP signals.
    """
    cfg = config or WidgetConfig()
    tv_symbol = to_tradingview_symbol(symbol) or symbol
    payload = {
        "interval": "1D",
        "width": cfg.width,
        "isTransparent": False,
        "height": cfg.height,
        "symbol": tv_symbol,
        "showIntervalTabs": True,
        "displayMode": "single",
        "locale": cfg.locale,
        "colorTheme": cfg.theme,
    }
    return f"""<div class="tradingview-widget-container" style="height:{cfg.height}px;width:{cfg.width}">
  <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
  <script type="text/javascript"
          src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js"
          async>
  {_safe_json(payload)}
  </script>
</div>"""


def top_stories_html(
    symbol: str | None = None, config: WidgetConfig | None = None
) -> str:
    """Return HTML embed for TradingView's Top Stories widget.

    If ``symbol`` is provided, the widget shows news for that single ticker,
    otherwise it shows the global "all symbols" feed.
    """
    cfg = config or WidgetConfig()
    payload: dict[str, Any] = {
        "feedMode": "all_symbols",
        "isTransparent": False,
        "displayMode": "regular",
        "width": cfg.width,
        "height": cfg.height,
        "colorTheme": cfg.theme,
        "locale": cfg.locale,
    }
    if symbol:
        tv_symbol = to_tradingview_symbol(symbol) or symbol
        payload["feedMode"] = "symbol"
        payload["symbol"] = tv_symbol
    return f"""<div class="tradingview-widget-container" style="height:{cfg.height}px;width:{cfg.width}">
  <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
  <script type="text/javascript"
          src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js"
          async>
  {_safe_json(payload)}
  </script>
</div>"""


# ---------------------------------------------------------------------------
# Webhook payload parsing
# ---------------------------------------------------------------------------

@dataclass
class TradingViewAlert:
    """Normalized alert payload received from TradingView's webhook."""

    symbol: str  # Yahoo-style symbol, e.g. ``BBCA.JK``
    condition: str  # Free-form, but typically "above" / "below" / "cross" / etc.
    value: float | None
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = _NUMBER_RE.search(value)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
    return None


def parse_alert_payload(payload: Any) -> TradingViewAlert:
    """Normalize an incoming TradingView webhook body into a :class:`TradingViewAlert`.

    TradingView sends whatever you put in the alert message field — typically a
    JSON blob if you template it, or a free-form string. We accept both.

    >>> a = parse_alert_payload({"symbol": "IDX:BBCA", "action": "above",
    ...                          "price": 9000})
    >>> a.symbol, a.condition, a.value
    ('BBCA.JK', 'above', 9000.0)
    """
    data: dict[str, Any]
    if isinstance(payload, dict):
        data = payload
    elif isinstance(payload, (bytes, bytearray)):
        data = _parse_string_payload(payload.decode("utf-8", errors="replace"))
    elif isinstance(payload, str):
        data = _parse_string_payload(payload)
    else:
        data = {}

    raw_symbol = (
        data.get("ticker")
        or data.get("symbol")
        or data.get("instrument")
        or ""
    )
    sym = from_tradingview_symbol(str(raw_symbol)) if raw_symbol else ""

    condition = (
        data.get("condition")
        or data.get("action")
        or data.get("side")
        or data.get("direction")
        or "alert"
    )

    value = _coerce_float(
        data.get("value")
        if data.get("value") is not None
        else data.get("price") if data.get("price") is not None
        else data.get("close")
    )

    note = data.get("note") or data.get("message") or data.get("text")

    return TradingViewAlert(
        symbol=sym.upper(),
        condition=str(condition).lower(),
        value=value,
        note=note,
        raw=data,
    )


def _parse_string_payload(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    # JSON payload?
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    # Plain text fallback — keep the message and try to extract symbol/value.
    out: dict[str, Any] = {"message": text}
    # crude symbol extraction: first uppercase token with optional ``EXCHANGE:`` prefix
    sym_match = re.search(r"\b([A-Z]{1,12}:)?[A-Z]{2,8}(?:\.[A-Z]{1,4})?\b", text)
    if sym_match:
        out["symbol"] = sym_match.group(0)
    val_match = _NUMBER_RE.search(text)
    if val_match:
        out["value"] = val_match.group(0)
    if "above" in text.lower():
        out["condition"] = "above"
    elif "below" in text.lower():
        out["condition"] = "below"
    elif "cross" in text.lower():
        out["condition"] = "cross"
    return out
