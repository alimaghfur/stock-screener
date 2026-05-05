"""Unit tests for the TradingView integration helpers."""

from __future__ import annotations

import json

import pytest

from core.db import (
    add_tv_alert,
    delete_tv_alert,
    init_db,
    list_tv_alerts,
    update_tv_alert_status,
)
from core.tradingview import (
    TradingViewAlert,
    WidgetConfig,
    advanced_chart_html,
    from_tradingview_symbol,
    parse_alert_payload,
    technical_analysis_html,
    to_tradingview_symbol,
    top_stories_html,
)

# ---------------------------------------------------------------------------
# Symbol mapping
# ---------------------------------------------------------------------------

class TestSymbolMapping:
    def test_idx_symbol_maps_to_idx_prefix(self):
        assert to_tradingview_symbol("BBCA.JK") == "IDX:BBCA"
        assert to_tradingview_symbol("bbca.jk") == "IDX:BBCA"
        assert to_tradingview_symbol("TLKM.JK") == "IDX:TLKM"

    def test_us_nasdaq_known_ticker(self):
        assert to_tradingview_symbol("AAPL") == "NASDAQ:AAPL"
        assert to_tradingview_symbol("nvda") == "NASDAQ:NVDA"
        assert to_tradingview_symbol("MSFT") == "NASDAQ:MSFT"

    def test_us_non_nasdaq_falls_back_to_nyse(self):
        # JPM / WMT are NYSE-listed, not in the curated NASDAQ set.
        assert to_tradingview_symbol("JPM") == "NYSE:JPM"
        assert to_tradingview_symbol("WMT") == "NYSE:WMT"

    def test_brk_class_b_dot_normalization(self):
        # Yahoo uses ``BRK-B``; TradingView uses ``BRK.B``.
        assert to_tradingview_symbol("BRK-B") == "NYSE:BRK.B"
        assert to_tradingview_symbol("brk-b") == "NYSE:BRK.B"

    def test_pre_mapped_symbol_passes_through(self):
        assert to_tradingview_symbol("IDX:BBCA") == "IDX:BBCA"
        assert to_tradingview_symbol("nasdaq:aapl") == "NASDAQ:AAPL"

    def test_empty_input_returns_empty(self):
        assert to_tradingview_symbol("") == ""
        assert to_tradingview_symbol("   ") == ""

    def test_inverse_mapping(self):
        assert from_tradingview_symbol("IDX:BBCA") == "BBCA.JK"
        assert from_tradingview_symbol("NASDAQ:AAPL") == "AAPL"
        assert from_tradingview_symbol("NYSE:BRK.B") == "BRK-B"
        assert from_tradingview_symbol("AAPL") == "AAPL"
        assert from_tradingview_symbol("") == ""


# ---------------------------------------------------------------------------
# Widget HTML generation
# ---------------------------------------------------------------------------

class TestWidgetHtml:
    def test_advanced_chart_contains_mapped_symbol_and_script(self):
        html = advanced_chart_html("BBCA.JK")
        assert "IDX:BBCA" in html
        assert "embed-widget-advanced-chart.js" in html
        assert "tradingview-widget-container" in html

    def test_technical_analysis_contains_mapped_symbol(self):
        html = technical_analysis_html("AAPL")
        assert "NASDAQ:AAPL" in html
        assert "embed-widget-technical-analysis.js" in html

    def test_top_stories_global_feed(self):
        html = top_stories_html()
        # Default feed mode should be global
        assert '"feedMode":"all_symbols"' in html
        assert "embed-widget-timeline.js" in html

    def test_top_stories_with_symbol_focus(self):
        html = top_stories_html("BBCA.JK")
        assert '"feedMode":"symbol"' in html
        assert "IDX:BBCA" in html

    def test_widget_config_height_propagates(self):
        cfg = WidgetConfig(theme="dark", height=800)
        html = advanced_chart_html("AAPL", cfg)
        assert "height:800px" in html
        assert '"theme":"dark"' in html

    def test_widget_config_dataclass_is_immutable(self):
        cfg = WidgetConfig()
        with pytest.raises((AttributeError, TypeError)):
            cfg.theme = "dark"  # type: ignore[misc]

    def test_advanced_chart_payload_is_valid_json(self):
        # Extract JSON between the script tags and ensure it parses.
        html = advanced_chart_html("AAPL")
        start = html.index("{")
        # Find the matching closing brace (last one before </script>)
        end = html.rindex("}") + 1
        payload = json.loads(html[start:end])
        assert payload["symbol"] == "NASDAQ:AAPL"
        assert payload["interval"] == "D"


# ---------------------------------------------------------------------------
# Webhook payload parsing
# ---------------------------------------------------------------------------

class TestWebhookParsing:
    def test_dict_payload_with_idx_symbol(self):
        alert = parse_alert_payload(
            {"symbol": "IDX:BBCA", "action": "above", "price": 9000}
        )
        assert isinstance(alert, TradingViewAlert)
        assert alert.symbol == "BBCA.JK"
        assert alert.condition == "above"
        assert alert.value == 9000.0

    def test_dict_payload_with_nasdaq_symbol_and_value_field(self):
        alert = parse_alert_payload(
            {"ticker": "NASDAQ:AAPL", "condition": "below", "value": "175.5"}
        )
        assert alert.symbol == "AAPL"
        assert alert.condition == "below"
        assert alert.value == 175.5

    def test_json_string_payload(self):
        body = json.dumps(
            {"symbol": "IDX:TLKM", "action": "cross", "close": 3200}
        )
        alert = parse_alert_payload(body)
        assert alert.symbol == "TLKM.JK"
        assert alert.condition == "cross"
        assert alert.value == 3200.0

    def test_bytes_payload(self):
        body = json.dumps(
            {"symbol": "AAPL", "action": "above", "price": 200}
        ).encode("utf-8")
        alert = parse_alert_payload(body)
        assert alert.symbol == "AAPL"
        assert alert.value == 200.0

    def test_plain_text_payload_extracts_symbol_and_value(self):
        text = "AAPL crossed above 175.50"
        alert = parse_alert_payload(text)
        assert alert.symbol == "AAPL"
        assert alert.condition in ("above", "cross")
        assert alert.value == 175.5
        assert alert.note == text

    def test_empty_payload_yields_empty_symbol(self):
        alert = parse_alert_payload({})
        assert alert.symbol == ""

    def test_payload_keeps_raw_dict(self):
        payload = {"symbol": "AAPL", "price": 100}
        alert = parse_alert_payload(payload)
        assert alert.raw == payload


# ---------------------------------------------------------------------------
# DB schema & CRUD
# ---------------------------------------------------------------------------

class TestTvAlertsTable:
    def test_init_db_creates_tv_alerts(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        # Sanity: insert/list round-trip works (raises if table missing)
        rows = list_tv_alerts(db_path=db_path)
        assert rows == []

    def test_add_and_list_tv_alert(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        aid = add_tv_alert(
            symbol="BBCA.JK",
            condition="above",
            value=9000.0,
            note="test alert",
            raw='{"symbol":"IDX:BBCA","price":9000}',
            db_path=db_path,
        )
        assert aid > 0
        rows = list_tv_alerts(db_path=db_path)
        assert len(rows) == 1
        assert rows[0]["symbol"] == "BBCA.JK"
        assert rows[0]["condition"] == "above"
        assert rows[0]["value"] == 9000.0
        assert rows[0]["status"] == "new"
        assert rows[0]["note"] == "test alert"

    def test_filter_by_status(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        a1 = add_tv_alert(
            symbol="AAPL", condition="above", value=200.0, db_path=db_path
        )
        a2 = add_tv_alert(
            symbol="MSFT", condition="below", value=400.0, db_path=db_path
        )
        update_tv_alert_status(a1, "acknowledged", db_path=db_path)

        new_only = list_tv_alerts(status="new", db_path=db_path)
        ack_only = list_tv_alerts(status="acknowledged", db_path=db_path)
        assert {r["id"] for r in new_only} == {a2}
        assert {r["id"] for r in ack_only} == {a1}

    def test_invalid_status_rejected(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        aid = add_tv_alert(
            symbol="AAPL", condition="above", value=200.0, db_path=db_path
        )
        with pytest.raises(ValueError):
            update_tv_alert_status(aid, "bogus", db_path=db_path)

    def test_value_can_be_null(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        aid = add_tv_alert(
            symbol="AAPL", condition="custom", value=None, db_path=db_path
        )
        rows = list_tv_alerts(db_path=db_path)
        assert len(rows) == 1
        assert rows[0]["value"] is None
        assert rows[0]["id"] == aid

    def test_delete_tv_alert(self, tmp_path):
        db_path = tmp_path / "test.db"
        init_db(db_path)
        aid = add_tv_alert(
            symbol="AAPL", condition="above", value=200.0, db_path=db_path
        )
        delete_tv_alert(aid, db_path=db_path)
        assert list_tv_alerts(db_path=db_path) == []


# ---------------------------------------------------------------------------
# End-to-end webhook handler (FastAPI TestClient)
# ---------------------------------------------------------------------------

class TestWebhookEndpoint:
    def _client(self, tmp_path, monkeypatch):
        from fastapi.testclient import TestClient

        db_path = tmp_path / "wh.db"
        # Redirect the global DB_PATH that the webhook handler uses.
        monkeypatch.setattr("core.db.DB_PATH", db_path)

        from tools import tradingview_webhook

        return TestClient(tradingview_webhook.app), db_path

    def test_health_endpoint(self, tmp_path, monkeypatch):
        client, _ = self._client(tmp_path, monkeypatch)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_post_json_alert_persists(self, tmp_path, monkeypatch):
        client, db_path = self._client(tmp_path, monkeypatch)
        resp = client.post(
            "/webhook/tradingview",
            json={"symbol": "IDX:BBCA", "action": "above", "price": 9000},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["symbol"] == "BBCA.JK"
        assert body["value"] == 9000.0

        rows = list_tv_alerts(db_path=db_path)
        assert len(rows) == 1
        assert rows[0]["symbol"] == "BBCA.JK"

    def test_post_text_alert_persists(self, tmp_path, monkeypatch):
        client, db_path = self._client(tmp_path, monkeypatch)
        resp = client.post(
            "/webhook/tradingview",
            content="AAPL crossed above 175.50",
            headers={"Content-Type": "text/plain"},
        )
        assert resp.status_code == 200
        rows = list_tv_alerts(db_path=db_path)
        assert len(rows) == 1
        assert rows[0]["symbol"] == "AAPL"

    def test_missing_symbol_rejected(self, tmp_path, monkeypatch):
        client, _ = self._client(tmp_path, monkeypatch)
        resp = client.post(
            "/webhook/tradingview",
            json={"price": 100},
        )
        assert resp.status_code == 422

    def test_token_required_when_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TRADINGVIEW_WEBHOOK_TOKEN", "secret-123")
        client, _ = self._client(tmp_path, monkeypatch)
        # No header -> 401
        resp = client.post(
            "/webhook/tradingview",
            json={"symbol": "AAPL", "price": 100},
        )
        assert resp.status_code == 401
        # Wrong token -> 401
        resp = client.post(
            "/webhook/tradingview",
            json={"symbol": "AAPL", "price": 100},
            headers={"Authorization": "Bearer wrong"},
        )
        assert resp.status_code == 401
        # Correct token -> 200
        resp = client.post(
            "/webhook/tradingview",
            json={"symbol": "AAPL", "price": 100},
            headers={"Authorization": "Bearer secret-123"},
        )
        assert resp.status_code == 200
