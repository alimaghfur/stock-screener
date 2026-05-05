"""Positions page — log trades, monitor live P/L, close positions."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.data import fetch_quote, normalize_symbol
from core.db import (
    add_position,
    close_position,
    delete_position,
    init_db,
    list_positions,
)
from core.risk import unrealized_pnl
from core.universe import currency_of

st.set_page_config(page_title="Positions", page_icon="💼", layout="wide")
st.title("💼 Positions")

init_db()

# --- Add position ------------------------------------------------------------------

st.subheader("Open new position")

last_plan = st.session_state.get("last_plan")

with st.form("add_position"):
    col1, col2, col3 = st.columns(3)
    symbol = col1.text_input(
        "Symbol",
        value=last_plan.get("symbol", "") if last_plan else "",
        placeholder="BBCA.JK / AAPL",
    )
    side = col2.selectbox("Side", ["long", "short"], index=0 if not last_plan else (0 if last_plan["side"] == "long" else 1))
    strategy = col3.selectbox("Strategy", ["scalping", "swing"], index=0 if not last_plan else (0 if last_plan["strategy"] == "scalping" else 1))

    col4, col5, col6 = st.columns(3)
    entry = col4.number_input("Entry price", min_value=0.0, value=float(last_plan["entry"]) if last_plan else 0.0, step=0.01, format="%.4f")
    qty = col5.number_input("Quantity", min_value=0.0, value=float(last_plan["qty"]) if last_plan else 0.0, step=1.0)
    sl = col6.number_input("Stop-Loss", min_value=0.0, value=float(last_plan["stop_loss"]) if last_plan else 0.0, step=0.01, format="%.4f")

    col7, col8 = st.columns(2)
    tp = col7.number_input("Take-Profit", min_value=0.0, value=float(last_plan["take_profit"]) if last_plan else 0.0, step=0.01, format="%.4f")
    note = col8.text_input("Note (optional)")

    submitted = st.form_submit_button("Save position", type="primary")
    if submitted:
        sym = normalize_symbol(symbol)
        if not sym or entry <= 0 or qty <= 0 or sl <= 0 or tp <= 0:
            st.error("Fill in symbol, entry, qty, SL, and TP (all > 0).")
        else:
            pos_id = add_position(
                symbol=sym, side=side, strategy=strategy,
                entry=float(entry), qty=float(qty),
                stop_loss=float(sl), take_profit=float(tp),
                note=note or None,
            )
            st.success(f"Position #{pos_id} ({sym} {side}) saved.")
            if last_plan and last_plan.get("symbol", "").upper() == sym:
                st.session_state.pop("last_plan", None)

if last_plan:
    st.caption(f"Form pre-filled from last plan: {last_plan['symbol']} {last_plan['side']}.")

# --- Open positions ----------------------------------------------------------------

st.divider()
st.subheader("Open positions")

open_pos = list_positions(status="open")
if not open_pos:
    st.info("No open positions yet.")
else:
    rows = []
    total_pnl = 0.0
    for p in open_pos:
        q = fetch_quote(p["symbol"])
        last = float(q["price"]) if q else float("nan")
        pnl = unrealized_pnl(p["side"], p["entry"], p["qty"], last) if q else {"pnl": 0.0, "pnl_pct": 0.0}
        total_pnl += pnl["pnl"]

        # Status flags vs SL / TP.
        status_flag = "—"
        if q:
            if p["side"] == "long":
                if last <= p["stop_loss"]:
                    status_flag = "⚠️ SL hit"
                elif last >= p["take_profit"]:
                    status_flag = "🎯 TP hit"
            else:
                if last >= p["stop_loss"]:
                    status_flag = "⚠️ SL hit"
                elif last <= p["take_profit"]:
                    status_flag = "🎯 TP hit"

        rows.append({
            "ID": p["id"],
            "Symbol": p["symbol"],
            "Side": p["side"],
            "Strategy": p["strategy"],
            "Entry": p["entry"],
            "Qty": p["qty"],
            "SL": p["stop_loss"],
            "TP": p["take_profit"],
            "Last": last,
            "P/L": pnl["pnl"],
            "P/L %": pnl["pnl_pct"],
            "Flag": status_flag,
            "Opened": p["opened_at"],
            "Note": p.get("note") or "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.format({
            "Entry": "{:,.4f}",
            "Qty": "{:,.0f}",
            "SL": "{:,.4f}",
            "TP": "{:,.4f}",
            "Last": "{:,.4f}",
            "P/L": "{:+,.2f}",
            "P/L %": "{:+.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.metric("Total unrealized P/L", f"{total_pnl:+,.2f}")

    st.markdown("**Manage**")
    target = st.selectbox(
        "Pick a position",
        options=[(p["id"], f"#{p['id']} {p['symbol']} {p['side']} qty={p['qty']}") for p in open_pos],
        format_func=lambda x: x[1],
    )
    pid = target[0]
    pos = next(p for p in open_pos if p["id"] == pid)
    ccy = currency_of(pos["symbol"])
    exit_price = st.number_input(
        f"Exit price ({ccy})",
        min_value=0.0,
        value=float(pos["entry"]),
        step=0.01,
        format="%.4f",
    )
    col_a, col_b = st.columns(2)
    if col_a.button("Close position"):
        close_position(pid, float(exit_price))
        st.success(f"Position #{pid} closed at {exit_price}.")
        st.rerun()
    if col_b.button("Delete position", type="secondary"):
        delete_position(pid)
        st.warning(f"Position #{pid} deleted.")
        st.rerun()

# --- Closed positions --------------------------------------------------------------

st.divider()
st.subheader("Closed positions")

closed_pos = list_positions(status="closed")
if not closed_pos:
    st.write("—")
else:
    rows = []
    total = 0.0
    for p in closed_pos:
        if p["exit_price"] is None:
            continue
        if p["side"] == "long":
            pnl = (p["exit_price"] - p["entry"]) * p["qty"]
        else:
            pnl = (p["entry"] - p["exit_price"]) * p["qty"]
        total += pnl
        cost = p["entry"] * p["qty"]
        pct = pnl / cost * 100.0 if cost else 0.0
        rows.append({
            "ID": p["id"],
            "Symbol": p["symbol"],
            "Side": p["side"],
            "Entry": p["entry"],
            "Exit": p["exit_price"],
            "Qty": p["qty"],
            "P/L": pnl,
            "P/L %": pct,
            "Opened": p["opened_at"],
            "Closed": p["closed_at"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.format({
            "Entry": "{:,.4f}",
            "Exit": "{:,.4f}",
            "Qty": "{:,.0f}",
            "P/L": "{:+,.2f}",
            "P/L %": "{:+.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.metric("Total realized P/L", f"{total:+,.2f}")
