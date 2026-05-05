"""FastAPI webhook receiver for TradingView alerts.

TradingView alert webhooks are simple HTTP POSTs whose body is whatever you put
in the alert "message" field — typically a JSON blob if you template it, or a
plain string. This server normalizes both shapes into a row in the
``tv_alerts`` SQLite table where the Streamlit Alerts page can render them.

Run locally::

    uvicorn tools.tradingview_webhook:app --host 0.0.0.0 --port 8766

Then expose it publicly with ngrok or Cloudflare Tunnel and paste the resulting
URL into your TradingView alert's "Webhook URL" field. Optionally set
``TRADINGVIEW_WEBHOOK_TOKEN`` so callers must include
``Authorization: Bearer <token>`` to be accepted.
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from core.db import add_tv_alert, init_db
from core.tradingview import parse_alert_payload

logger = logging.getLogger("tradingview_webhook")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="TradingView Alert Receiver",
    version="0.1.0",
    docs_url="/docs",
    lifespan=_lifespan,
)


def _ensure_db() -> None:
    """Idempotent fallback — guarantees the schema exists even when the FastAPI
    lifespan ``startup`` hook did not run (e.g. inside ``TestClient`` without
    its context manager)."""
    init_db()


def _check_token(authorization: str | None) -> None:
    expected = os.environ.get("TRADINGVIEW_WEBHOOK_TOKEN")
    if not expected:
        return  # Token not configured — accept all callers (dev mode).
    if not authorization:
        raise HTTPException(status_code=401, detail="missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != expected:
        raise HTTPException(status_code=401, detail="invalid token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/tradingview")
async def receive_alert(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_token(authorization)
    _ensure_db()

    body = await request.body()
    try:
        payload: Any = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = body.decode("utf-8", errors="replace")

    alert = parse_alert_payload(payload)
    if not alert.symbol:
        raise HTTPException(
            status_code=422,
            detail="payload missing symbol/ticker; cannot store alert",
        )

    raw_str = body.decode("utf-8", errors="replace") if body else ""
    alert_id = add_tv_alert(
        symbol=alert.symbol,
        condition=alert.condition,
        value=alert.value,
        note=alert.note,
        raw=raw_str,
        received_at=alert.received_at.isoformat(timespec="seconds"),
    )
    logger.info(
        "TradingView alert stored id=%s symbol=%s condition=%s value=%s",
        alert_id,
        alert.symbol,
        alert.condition,
        alert.value,
    )
    return {
        "ok": True,
        "id": alert_id,
        "symbol": alert.symbol,
        "condition": alert.condition,
        "value": alert.value,
    }


if __name__ == "__main__":  # pragma: no cover - manual entry point
    import uvicorn

    port = int(os.environ.get("TRADINGVIEW_WEBHOOK_PORT", "8766"))
    uvicorn.run(app, host="0.0.0.0", port=port)
