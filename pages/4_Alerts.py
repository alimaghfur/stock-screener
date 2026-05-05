"""Alerts page — manage and evaluate price alerts."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.data import fetch_quote, normalize_symbol
from core.db import (
    add_alert,
    cancel_alert,
    delete_alert,
    delete_tv_alert,
    evaluate_alerts,
    init_db,
    list_alerts,
    list_tv_alerts,
    update_tv_alert_status,
)

st.set_page_config(page_title="Alerts", page_icon="🔔", layout="wide")
st.title("🔔 Price Alerts")

init_db()

# --- Add alert ----------------------------------------------------------------------

st.subheader("Create alert")

with st.form("add_alert"):
    col1, col2, col3 = st.columns(3)
    symbol = col1.text_input("Symbol", placeholder="BBCA.JK / AAPL")
    condition = col2.selectbox("Trigger when price goes…", ["above", "below"])
    value = col3.number_input("Price level", min_value=0.0, value=0.0, step=0.01, format="%.4f")
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Save alert", type="primary")
    if submitted:
        sym = normalize_symbol(symbol)
        if not sym or value <= 0:
            st.error("Symbol and a positive price level are required.")
        else:
            aid = add_alert(symbol=sym, condition=condition, value=float(value), note=note or None)
            st.success(f"Alert #{aid} saved: {sym} {condition} {value}.")

# --- Evaluate alerts ----------------------------------------------------------------

st.divider()
col_check, col_clean = st.columns([1, 3])
if col_check.button("Check alerts now"):
    def _quote(sym: str) -> float | None:
        q = fetch_quote(sym)
        return float(q["price"]) if q else None

    triggered = evaluate_alerts(_quote)
    if not triggered:
        st.info("No alerts triggered.")
    else:
        for t in triggered:
            st.success(
                f"🚨 {t['symbol']} crossed {t['condition']} {t['value']} "
                f"(last: {t.get('last_price', '?')})."
            )

# --- Active alerts ------------------------------------------------------------------

st.subheader("Active alerts")
active = list_alerts(status="active")
if not active:
    st.write("—")
else:
    rows = []
    for a in active:
        q = fetch_quote(a["symbol"])
        last = float(q["price"]) if q else None
        rows.append({
            "ID": a["id"],
            "Symbol": a["symbol"],
            "Condition": f"{a['condition']} {a['value']}",
            "Last": last if last is not None else "—",
            "Created": a["created_at"],
            "Note": a.get("note") or "",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    target = st.selectbox(
        "Pick an alert",
        options=[(a["id"], f"#{a['id']} {a['symbol']} {a['condition']} {a['value']}") for a in active],
        format_func=lambda x: x[1],
        key="alert_pick_active",
    )
    aid = target[0]
    col_a, col_b = st.columns(2)
    if col_a.button("Cancel alert"):
        cancel_alert(aid)
        st.success(f"Alert #{aid} cancelled.")
        st.rerun()
    if col_b.button("Delete alert", type="secondary"):
        delete_alert(aid)
        st.warning(f"Alert #{aid} deleted.")
        st.rerun()

# --- History (triggered / cancelled) -----------------------------------------------

st.divider()
st.subheader("History")

history = [a for a in list_alerts() if a["status"] != "active"]
if not history:
    st.write("—")
else:
    rows = []
    for a in history:
        rows.append({
            "ID": a["id"],
            "Symbol": a["symbol"],
            "Condition": f"{a['condition']} {a['value']}",
            "Status": a["status"],
            "Created": a["created_at"],
            "Triggered": a.get("triggered_at") or "",
            "Note": a.get("note") or "",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# --- TradingView webhook alerts -----------------------------------------------------

st.divider()
st.subheader("📡 TradingView webhook alerts")
st.caption(
    "Alerts pushed in by `tools/tradingview_webhook.py`. Run that FastAPI server "
    "and point your TradingView alert webhook URL at it (use ngrok or similar to "
    "expose it publicly). See README for setup."
)

show_dismissed = st.checkbox(
    "Show acknowledged / dismissed", value=False, key="tv_show_all"
)
tv_status_filter = None if show_dismissed else "new"
tv_alerts = list_tv_alerts(status=tv_status_filter)

if not tv_alerts:
    st.write("— No TradingView alerts received yet.")
else:
    rows = []
    for a in tv_alerts:
        rows.append({
            "ID": a["id"],
            "Symbol": a["symbol"],
            "Condition": a["condition"],
            "Value": a.get("value") if a.get("value") is not None else "—",
            "Status": a["status"],
            "Received": a["received_at"],
            "Note": a.get("note") or "",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    target = st.selectbox(
        "Pick an alert",
        options=[
            (
                a["id"],
                f"#{a['id']} {a['symbol']} {a['condition']} "
                f"{a.get('value') if a.get('value') is not None else ''}".strip(),
            )
            for a in tv_alerts
        ],
        format_func=lambda x: x[1],
        key="tv_alert_pick",
    )
    tv_aid = target[0]
    col_x, col_y, col_z = st.columns(3)
    if col_x.button("Acknowledge", key="tv_ack"):
        update_tv_alert_status(tv_aid, "acknowledged")
        st.success(f"TradingView alert #{tv_aid} acknowledged.")
        st.rerun()
    if col_y.button("Dismiss", key="tv_dismiss"):
        update_tv_alert_status(tv_aid, "dismissed")
        st.warning(f"TradingView alert #{tv_aid} dismissed.")
        st.rerun()
    if col_z.button("Delete", key="tv_delete"):
        delete_tv_alert(tv_aid)
        st.warning(f"TradingView alert #{tv_aid} deleted.")
        st.rerun()
