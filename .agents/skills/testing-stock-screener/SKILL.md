---
name: testing-stock-screener
description: Setup and end-to-end testing playbook for the Streamlit stock-screener app (Screener, Top Movers, Positions, Alerts, News). Use when verifying any UI flow, screener strategy, trade-plan math, or news rendering.
---

# Testing the stock-screener app

Streamlit multipage app, Python only, no build step. Live data via `yfinance` (Yahoo Finance, delayed ~15 min). Pages live under `pages/`, each prefixed with a number that controls sidebar order. The home page is `app.py`.

## Setup

From repo root:

```bash
uv sync                            # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/streamlit run app.py --server.port 8765 --server.headless true
```

App is at `http://localhost:8765`. Lint + tests:

```bash
.venv/bin/ruff check .
.venv/bin/pytest -q
```

### Streamlit hot-reload caveat (important)

If you add a new file to `pages/` while the Streamlit server is already running, the new page **does not appear in the sidebar** until you restart the process. Symptom: `curl http://localhost:8765/<NewPage>` returns 200, but the sidebar's nav list is missing the entry. Fix:

```bash
pkill -f 'streamlit run app.py' && \
  nohup .venv/bin/streamlit run app.py --server.port 8765 --server.headless true > /tmp/streamlit.log 2>&1 &
```

Then wait ~5 s and re-check the sidebar.

## What's on each page

- **Screener** — pick Market / Universe / Strategy → `Run scan`, then drill down by typing a Symbol in the `Trade plan (TP / SL)` input. The drill-down also renders a `Latest news` section (up to 5 bullets) below position-sizing metrics.
- **Top Movers** — IDX or US gainers/losers. Currency footer flips IDR ↔ USD on market change; one-time refresh required after switching.
- **Positions** — read-only batch recommendations: pick Market/Universe/Strategy → `Generate recommendations` → table with Entry / SL / TP1/2/3 / sizing. Strategies BPJS/BSJP only show when Market = IDX.
- **Alerts** — create price-based alerts; `Check alerts now` evaluates against latest quote.
- **News** — pick Market / Universe (or paste custom tickers) → list of articles aggregated, deduped by URL, sorted newest first. Each card: thumbnail (when available), title (markdown link), publisher, humanized age, summary, ticker chip.

## Strategies (radio in Screener / Positions)

| Strategy | Universe gating | Logic |
|---|---|---|
| `scalping` | both IDX & US | VWAP break + RSI momentum + 20-bar breakout |
| `swing` | both IDX & US | MA20 > MA50 + volume spike + RSI 40–60 reversal |
| `BPJS` (Beli Pagi Jual Sore) | **IDX only** | 20-day avg intraday (Open→Close) edge ≥ 0.30 % AND ≥ 12/20 green days |
| `BSJP` (Beli Sore Jual Pagi) | **IDX only** | 20-day avg overnight gap (Open vs prevClose) ≥ 0.20 % AND ≥ 11/20 gap-up days |

### BPJS/BSJP threshold tip
Default BPJS thresholds (`_BPJS_MIN_EDGE = 0.003`, `_BPJS_MIN_GREEN = 0.60` in `core/screener.py`) can produce **0 candidates** in low-volatility market conditions. Pipeline still works (info message shows, no crash) — but if you need to demo the BPJS branch live, temporarily lower the thresholds, run the scan, then `git checkout core/screener.py` to revert before exiting test mode.

## TP/SL math (regression invariants — use as adversarial assertions)

For any strategy, every recommendation row must satisfy:

- `|(Entry − SL) − sl_mult × ATR(14)| < 0.01 × ATR(14)` (default `sl_mult = 1.5`)
- `TP1 = Entry + 1R`, `TP2 = Entry + rrR`, `TP3 = Entry + (rr+1)R` where `R = sl_mult × ATR(14)` and `rr` is the Risk:Reward slider (default 2.0)
- `Risk amount = equity × risk_per_trade %`, `Suggested qty = floor(Risk amount / R)`

If the slider for SL multiplier or R:R is broken, this invariant fails — making them very useful sanity checks.

## News feature testing

- Source: `yfinance.Ticker(symbol).news`, cached 10 minutes per ticker (`@st.cache_data(ttl=600)` on `fetch_news_for_symbol`).
- The parser handles **both** the modern nested `content` payload and the legacy flat shape — a single bad payload returning `[]` shouldn't break the page.

### Ticker fixtures (validated live)

| Ticker | Articles | Use for |
|---|---|---|
| `AAPL`, `NVDA`, `TSLA` | ~10 each | Well-covered US — full card rendering, dedupe, newest-first |
| `TLKM.JK` | ~8 | Well-covered IDX — same as above |
| `GOTO.JK` | ~3 | Sparse IDX — confirms aggregation across thin tickers |
| `BBRI.JK` | ~1 | Edge case — single article |
| `BBCA.JK` | **0** | **Empty state assertion** — drill-down should show fallback caption, not crash |

### News page assertions

1. Header strip text: `<N> ticker(s) · cached 10 min per ticker · market: <IDX|US>` — N changes when filter changes (proves filter is wired).
2. Banner: `<M> article(s) — newest first.` — M honors `max_total` slider cap.
3. Each card chip: `<Publisher> · <age> · <Market>/<Currency> · <TICKER>`.
4. Sort order: parsed ages are non-decreasing top-to-bottom.
5. Dedupe: no two cards share the same title (or URL).

### Screener drill-down assertions

1. Section heading **`Latest news`** appears below position-sizing metrics.
2. Up to 5 bullets, each first line is a markdown link `[title](url)`, second line italic `_<Publisher> · <age>_`.
3. **Empty case** (`BBCA.JK`): the heading still appears and a caption reads exactly `No recent headlines on Yahoo Finance for this ticker. Cross-check sentiment elsewhere before entering.` (use this string as a fail-fast assertion).

## Streamlit form gotchas

- `st.form` + `st.number_input`: pressing Enter inside the number_input may submit the form **before** the value is committed. Workaround when testing: type the value, click another field to commit, then click the form's Save button. Don't press Enter.
- The Top Movers footer reads currency from the universe selector and is sticky after switching markets — click `Refresh` after changing market for the footer to flip.

## Recording tips

- Maximize the Chrome window before recording: `wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz`. Do **not** use `xdotool key super+Up` (tiles to half-screen on this WM).
- Annotate `setup` / `test_start` / `assertion` with consolidated single-sentence assertions — avoid micro-assertions per UI element.

## Devin Secrets needed

None — all data flows through public Yahoo Finance endpoints via `yfinance`. No login required for read-only testing.
