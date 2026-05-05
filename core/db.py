"""SQLite persistence for tracked positions and price alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"


def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK (side IN ('long','short')),
                strategy TEXT NOT NULL,
                entry REAL NOT NULL,
                qty REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                opened_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed')),
                closed_at TEXT,
                exit_price REAL,
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                condition TEXT NOT NULL CHECK (condition IN ('above','below')),
                value REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','triggered','cancelled')),
                created_at TEXT NOT NULL,
                triggered_at TEXT,
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS tv_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                condition TEXT NOT NULL,
                value REAL,
                received_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new'
                    CHECK (status IN ('new','acknowledged','dismissed')),
                note TEXT,
                raw TEXT
            );
            """
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- Positions -----------------------------------------------------------------------

def add_position(
    *,
    symbol: str,
    side: str,
    strategy: str,
    entry: float,
    qty: float,
    stop_loss: float,
    take_profit: float,
    note: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO positions
                (symbol, side, strategy, entry, qty, stop_loss, take_profit, opened_at, status, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """,
            (symbol.upper(), side, strategy, entry, qty, stop_loss, take_profit, _now(), note),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_positions(
    status: str | None = None,
    db_path: str | Path | None = None,
) -> list[dict]:
    sql = "SELECT * FROM positions"
    params: tuple = ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    sql += " ORDER BY opened_at DESC"
    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def close_position(
    pos_id: int,
    exit_price: float,
    db_path: str | Path | None = None,
) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE positions SET status='closed', exit_price=?, closed_at=? WHERE id=?",
            (exit_price, _now(), pos_id),
        )
        conn.commit()


def delete_position(pos_id: int, db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM positions WHERE id=?", (pos_id,))
        conn.commit()


# --- Alerts --------------------------------------------------------------------------

def add_alert(
    *,
    symbol: str,
    condition: str,
    value: float,
    note: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    if condition not in ("above", "below"):
        raise ValueError("condition must be 'above' or 'below'")
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO alerts (symbol, condition, value, status, created_at, note)
            VALUES (?, ?, ?, 'active', ?, ?)
            """,
            (symbol.upper(), condition, value, _now(), note),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_alerts(
    status: str | None = None,
    db_path: str | Path | None = None,
) -> list[dict]:
    sql = "SELECT * FROM alerts"
    params: tuple = ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    sql += " ORDER BY created_at DESC"
    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def trigger_alert(alert_id: int, db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE alerts SET status='triggered', triggered_at=? WHERE id=? AND status='active'",
            (_now(), alert_id),
        )
        conn.commit()


def cancel_alert(alert_id: int, db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE alerts SET status='cancelled' WHERE id=? AND status='active'",
            (alert_id,),
        )
        conn.commit()


def delete_alert(alert_id: int, db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
        conn.commit()


# --- TradingView webhook alerts -----------------------------------------------------

def add_tv_alert(
    *,
    symbol: str,
    condition: str,
    value: float | None = None,
    note: str | None = None,
    raw: str | None = None,
    received_at: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """Persist an alert delivered by the TradingView webhook receiver."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO tv_alerts (symbol, condition, value, received_at, status, note, raw)
            VALUES (?, ?, ?, ?, 'new', ?, ?)
            """,
            (
                symbol.upper(),
                condition,
                value,
                received_at or _now(),
                note,
                raw,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_tv_alerts(
    status: str | None = None,
    db_path: str | Path | None = None,
) -> list[dict]:
    sql = "SELECT * FROM tv_alerts"
    params: tuple = ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    sql += " ORDER BY received_at DESC"
    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def update_tv_alert_status(
    alert_id: int,
    status: str,
    db_path: str | Path | None = None,
) -> None:
    if status not in ("new", "acknowledged", "dismissed"):
        raise ValueError(
            "tv_alert status must be 'new', 'acknowledged' or 'dismissed'"
        )
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE tv_alerts SET status=? WHERE id=?",
            (status, alert_id),
        )
        conn.commit()


def delete_tv_alert(alert_id: int, db_path: str | Path | None = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM tv_alerts WHERE id=?", (alert_id,))
        conn.commit()


def evaluate_alerts(
    quote_lookup,
    db_path: str | Path | None = None,
) -> list[dict]:
    """Walk active alerts; for each, call quote_lookup(symbol) -> last_price.
    If condition met, mark triggered. Returns list of newly triggered alert dicts."""
    triggered: list[dict] = []
    for alert in list_alerts(status="active", db_path=db_path):
        try:
            price = quote_lookup(alert["symbol"])
        except Exception:
            continue
        if price is None:
            continue
        hit = (
            (alert["condition"] == "above" and price >= alert["value"])
            or (alert["condition"] == "below" and price <= alert["value"])
        )
        if hit:
            trigger_alert(alert["id"], db_path=db_path)
            alert = dict(alert)
            alert["status"] = "triggered"
            alert["last_price"] = price
            triggered.append(alert)
    return triggered
