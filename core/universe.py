"""Curated ticker universes for IDX and US markets.

Lists are intentionally hand-maintained snapshots of the most liquid names so the app
works fully offline (no scraping at runtime). Update them as needed; the screener is
agnostic to list size.
"""

from __future__ import annotations

# --- IDX (Indonesia Stock Exchange) ----------------------------------------------------
# Yahoo Finance suffix: ".JK"

IDX30: list[str] = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK",
    "ASII.JK", "GOTO.JK", "ANTM.JK", "ADRO.JK", "PGAS.JK",
    "UNTR.JK", "SMGR.JK", "INDF.JK", "ICBP.JK", "KLBF.JK",
    "UNVR.JK", "INKP.JK", "MEDC.JK", "ITMG.JK", "PTBA.JK",
    "MNCN.JK", "EXCL.JK", "ISAT.JK", "CPIN.JK", "AMRT.JK",
    "ARTO.JK", "BRIS.JK", "MDKA.JK", "INCO.JK", "TPIA.JK",
]

LQ45: list[str] = sorted(set(IDX30 + [
    "BUKA.JK", "EMTK.JK", "ESSA.JK", "AKRA.JK", "BNGA.JK",
    "BTPS.JK", "HRUM.JK", "BSDE.JK", "CTRA.JK", "PWON.JK",
    "SMRA.JK", "ASRI.JK", "JPFA.JK", "TKIM.JK", "BRMS.JK",
]))

IDX80: list[str] = sorted(set(LQ45 + [
    "ADHI.JK", "ADMR.JK", "AGII.JK", "AMMN.JK", "ARCI.JK",
    "AUTO.JK", "AVIA.JK", "BBKP.JK", "BBTN.JK", "BFIN.JK",
    "BIRD.JK", "BJBR.JK", "BJTM.JK", "BNII.JK", "BRPT.JK",
    "CITA.JK", "DEWA.JK", "DOID.JK", "DSNG.JK", "ELSA.JK",
    "ENRG.JK", "ERAA.JK", "FILM.JK", "GGRM.JK", "HMSP.JK",
    "HRTA.JK", "IMAS.JK", "INDY.JK", "INTP.JK", "JSMR.JK",
    "LSIP.JK", "MAPI.JK", "MIKA.JK", "MTEL.JK", "NCKL.JK",
    "PANI.JK", "PNLF.JK", "RAJA.JK", "SCMA.JK", "SIDO.JK",
    "TBIG.JK", "TINS.JK", "TOWR.JK", "WIIM.JK", "WSKT.JK",
]))


# --- US ------------------------------------------------------------------------------
# Top names from S&P 500 + NASDAQ 100 (most liquid / actively traded subset).

US_LARGE_CAP: list[str] = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    "BRK-B", "JPM", "V", "MA", "UNH", "XOM", "JNJ", "PG", "HD", "CVX",
    "LLY", "ABBV", "PEP", "KO", "AVGO", "MRK", "COST", "WMT", "ORCL",
    "CRM", "ADBE", "MCD", "ACN", "BAC", "WFC", "TMO", "ABT", "DIS",
    "CSCO", "PFE", "NFLX", "INTC", "AMD", "QCOM", "TXN", "IBM", "NKE",
    "GE", "BA", "CAT", "GS", "MS", "AXP", "BLK", "C", "PM", "RTX",
    "HON", "LIN", "AMAT", "BKNG", "PYPL", "INTU", "AMGN", "DE", "GILD",
    "ISRG", "VRTX", "REGN", "ADP", "MDT", "SCHW", "T", "VZ", "CMCSA",
    "TMUS", "F", "GM", "UPS", "FDX", "LMT", "NOC", "MO", "SBUX",
    "TGT", "LOW", "CVS", "ELV", "BMY", "DHR", "ANET", "NOW", "PANW",
    "SHOP", "UBER", "ABNB", "PLTR", "COIN", "SNOW", "MU", "MELI", "MARA",
    "DDOG", "CRWD", "NET", "ZS", "SQ", "SOFI",
]

NASDAQ100: list[str] = sorted(set([
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    "AVGO", "COST", "PEP", "ADBE", "NFLX", "AMD", "INTC", "CSCO", "QCOM",
    "TXN", "AMAT", "INTU", "AMGN", "ISRG", "BKNG", "VRTX", "REGN", "ADP",
    "MU", "PANW", "SBUX", "ANET", "MELI", "ABNB", "CDNS", "SNPS", "LRCX",
    "KLAC", "ASML", "MAR", "MRVL", "ORLY", "FTNT", "MDLZ", "PYPL", "CHTR",
    "GILD", "CSX", "NXPI", "ADI", "MNST", "AEP", "KDP", "CTAS", "ROST",
    "PCAR", "PAYX", "DXCM", "TEAM", "FAST", "ODFL", "DDOG", "CRWD", "EXC",
    "BIIB", "WBD", "EBAY", "GEHC", "MCHP", "VRSK", "IDXX", "CPRT", "WBA",
]))


def market_universes() -> dict[str, dict[str, list[str]]]:
    """Return {market: {label: tickers}} mapping."""
    return {
        "IDX": {
            "IDX30": IDX30,
            "LQ45": LQ45,
            "IDX80": IDX80,
        },
        "US": {
            "Large Cap (top ~100)": US_LARGE_CAP,
            "NASDAQ 100 (subset)": NASDAQ100,
        },
    }


def list_markets() -> list[str]:
    return list(market_universes().keys())


def list_universes(market: str) -> list[str]:
    return list(market_universes().get(market, {}).keys())


def get_universe(market: str, name: str) -> list[str]:
    return market_universes().get(market, {}).get(name, [])


def is_idx(symbol: str) -> bool:
    return symbol.upper().endswith(".JK")


def market_of(symbol: str) -> str:
    return "IDX" if is_idx(symbol) else "US"


def currency_of(symbol: str) -> str:
    return "IDR" if is_idx(symbol) else "USD"
