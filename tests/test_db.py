"""Unit tests for the SQLite store (positions & alerts)."""

from __future__ import annotations

import pytest

from core import db as dbm


@pytest.fixture
def tmp_db(tmp_path):
    path = tmp_path / "test.db"
    dbm.init_db(path)
    yield path


def test_add_and_list_positions(tmp_db):
    pid = dbm.add_position(
        symbol="bbca.jk",
        side="long",
        strategy="swing",
        entry=8000.0,
        qty=100.0,
        stop_loss=7800.0,
        take_profit=8400.0,
        note="test",
        db_path=tmp_db,
    )
    assert pid > 0
    rows = dbm.list_positions(status="open", db_path=tmp_db)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "BBCA.JK"
    assert rows[0]["side"] == "long"


def test_close_and_delete_position(tmp_db):
    pid = dbm.add_position(
        symbol="AAPL", side="long", strategy="scalping",
        entry=100.0, qty=10.0, stop_loss=95.0, take_profit=110.0,
        db_path=tmp_db,
    )
    dbm.close_position(pid, exit_price=108.0, db_path=tmp_db)
    closed = dbm.list_positions(status="closed", db_path=tmp_db)
    assert len(closed) == 1
    assert closed[0]["exit_price"] == 108.0
    dbm.delete_position(pid, db_path=tmp_db)
    assert dbm.list_positions(db_path=tmp_db) == []


def test_alerts_lifecycle(tmp_db):
    aid = dbm.add_alert(symbol="AAPL", condition="above", value=200.0, db_path=tmp_db)
    assert aid > 0
    assert len(dbm.list_alerts(status="active", db_path=tmp_db)) == 1

    # Trigger via evaluate.
    triggered = dbm.evaluate_alerts(lambda s: 250.0, db_path=tmp_db)
    assert len(triggered) == 1
    assert triggered[0]["symbol"] == "AAPL"
    assert dbm.list_alerts(status="active", db_path=tmp_db) == []
    assert len(dbm.list_alerts(status="triggered", db_path=tmp_db)) == 1


def test_alerts_below_condition(tmp_db):
    dbm.add_alert(symbol="AAPL", condition="below", value=100.0, db_path=tmp_db)
    triggered = dbm.evaluate_alerts(lambda s: 90.0, db_path=tmp_db)
    assert len(triggered) == 1


def test_alert_invalid_condition(tmp_db):
    with pytest.raises(ValueError):
        dbm.add_alert(symbol="AAPL", condition="weird", value=1.0, db_path=tmp_db)


def test_cancel_alert(tmp_db):
    aid = dbm.add_alert(symbol="AAPL", condition="above", value=100.0, db_path=tmp_db)
    dbm.cancel_alert(aid, db_path=tmp_db)
    assert len(dbm.list_alerts(status="cancelled", db_path=tmp_db)) == 1
    assert len(dbm.list_alerts(status="active", db_path=tmp_db)) == 0
