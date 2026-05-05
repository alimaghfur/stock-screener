---
name: testing-stock-screener
description: End-to-end test the Streamlit stock screener (IDX & US scalping/swing screener, TP/SL trade plans, position tracking, price alerts). Use when verifying any UI or business-logic change to this app.
---

# Testing the Stock Screener app

## Run it locally

```bash
cd /home/ubuntu/repos/stock-screener
uv venv .venv 2>/dev/null || python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765 --server.headless true --server.address 0.0.0.0 &
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8765/   # expect 200
```

Yahoo Finance (yfinance) is reachable from the Devin VM with **no credentials** for both `.JK` (IDX) and US tickers — no proxy or VPN needed. A quick sanity probe before any UI testing:

```bash
python - <<'PY'
from core.data import fetch_quote
print(fetch_quote('BBCA.JK'), fetch_quote('AAPL'))
PY
```

If this prints two non-`None` quotes the rest of the app will work.

## Primary E2E flows (cover them in this order)

Use the running browser; recording is helpful when changes touch the UI. Maximize the browser window first:

```bash
sudo apt-get install -y wmctrl 2>/dev/null
wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
```

1. **Screener (`/Screener`) → Trade plan**. Pick `Market=IDX, Universe=IDX30, Strategy=swing`, click **Run scan**. Expect ≥ 1 candidate with `Currency=IDR`, populated `Reasons`, and a **Trade plan** block where `Entry − Stop-Loss ≈ SL_mult × ATR(14)` and `TP1/TP2/TP3 = entry + 1R / RR×R / (RR+1)×R`. With default sliders (`SL_mult=1.5, RR=2.0`), `Risk amount = 1 % of 100,000,000 IDR = 1,000,000`.
2. **Top Movers (`/Top_Movers`)**. Click **Refresh**. Adversarial assertions: gainers `Change %` strictly **descending and all ≥ 0**, losers strictly **ascending and all ≤ 0**, footer `Prices in <ccy>` matches the selected market. Switching market to US must flip `IDR → USD` after a Refresh.
3. **Positions (`/Positions`)**. Form is pre-filled when you reach the page from a Trade plan. Save it. Then add an adversarial `AAPL` position with `Entry=200, Qty=1, SL=300, TP=400` to force `Flag = ⚠️ SL hit` (long-side condition `last ≤ stop_loss`); the row's `P/L = (Last − Entry) × Qty` and `Total unrealized P/L` equals the sum of rows. Closing the position at any exit price moves it to **Closed positions** with realized P/L retained.
4. **Alerts (`/Alerts`)**. Create three: `AAPL below 999999`, `AAPL below 999999`, `AAPL above 999999`. Click **Check alerts now** — exactly the two `below` rows must move to **History** with `status=triggered`; the `above` alert must remain Active. If both move or neither does, the evaluate logic is broken.

## Streamlit form gotchas (real, observed)

- `st.number_input` and `st.text_input` inside an `st.form` only commit their value when the form is submitted. **Pressing Enter while focus is in a `number_input` submits the form immediately** — this can save a row with stale defaults if you typed but had not yet committed via blur. The reliable interaction: click field → `ctrl+a` → type → click into a *different* widget (forces blur) → click the **Save** button. Never use Enter to submit forms in this app.
- Pages cache mover results in `st.session_state["movers_cache"]`. The **footer currency** is read from the universe selector, not the cached table — for one render after switching markets you can see the new currency above stale rows. Always click **Refresh** after changing the universe.
- `last_plan` in `st.session_state` is consumed (popped) when a saved Position's symbol matches it — re-run the screener if you need to refill the Positions form.

## What "good" looks like quantitatively

| Page | Min. PASS evidence |
|---|---|
| Screener swing IDX30 | ≥ 1 candidate, `Currency=IDR`, `Reasons` non-empty |
| Trade plan | `\|Entry − SL\| / ATR ≈ SL_mult` within 0.001; `TP2 − Entry ≈ RR × \|Entry − SL\|` |
| Top Movers | Both lists monotone in `Change %`, footer matches selected market currency |
| Positions | `P/L ≈ (Last − Entry) × Qty` (long); SL/TP flag fires on contrived row; close moves to history |
| Alerts | Exactly the alerts whose condition is met flip to `triggered`; others stay Active |

## Devin Secrets Needed

None. The app uses public Yahoo Finance data with no auth.
