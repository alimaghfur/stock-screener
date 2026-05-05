"""Curated ticker universes for IDX and US markets.

Lists are intentionally hand-maintained snapshots of the most liquid index members
so the app works fully offline (no scraping at runtime). Update them as needed; the
screener is agnostic to list size.

Sources of truth (refresh periodically):
- IDX30 / LQ45 / IDX80 / Kompas100 — idx.co.id quarterly evaluation announcements.
- S&P 500 / NASDAQ-100 / Dow 30 — en.wikipedia.org constituent tables (auto-maintained).
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

# Kompas100 — broader IDX index of 100 most liquid + sizeable stocks. Snapshot below
# is sourced from id.wikipedia.org (Indeks_Kompas100) plus the Aug-Oct 2024 reshuffle
# announced by BEI; a few clearly delisted names from the Wikipedia snapshot have been
# removed (AISA, BUMI, BRAU, BTEL, BWPT, FAST, KBLV, MSKY, BHIT, STAR, TRAM).
KOMPAS100: list[str] = sorted(set([
    "AALI.JK", "ADMG.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "ANTM.JK", "APIC.JK", "APLN.JK",
    "ASII.JK", "ASRI.JK", "AUTO.JK", "AVIA.JK", "BABP.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK",
    "BBTN.JK", "BBYB.JK", "BDMN.JK", "BIRD.JK", "BISI.JK", "BJBR.JK", "BKSL.JK", "BMRI.JK",
    "BMTR.JK", "BNBR.JK", "BNGA.JK", "BRPT.JK", "BSDE.JK", "BULL.JK", "BYAN.JK", "CLPI.JK",
    "CMNP.JK", "CMRY.JK", "CPIN.JK", "CTRA.JK", "DEWA.JK", "DILD.JK", "ECII.JK", "ELSA.JK",
    "EMTK.JK", "EXCL.JK", "GIAA.JK", "GJTL.JK", "GOOD.JK", "HERO.JK", "HMSP.JK", "ICBP.JK",
    "IMAS.JK", "INCO.JK", "INDF.JK", "INDY.JK", "INKP.JK", "INTA.JK", "INTP.JK", "IPTV.JK",
    "ISAT.JK", "ITMG.JK", "JPFA.JK", "JPRS.JK", "JSMR.JK", "KIJA.JK", "KLBF.JK", "LPCK.JK",
    "LPKR.JK", "LPPF.JK", "LSIP.JK", "MAHA.JK", "MAPA.JK", "MAPB.JK", "MAPI.JK", "MLPL.JK",
    "MNCN.JK", "MPPA.JK", "MSIN.JK", "MYOR.JK", "NCKL.JK", "NETV.JK", "PANI.JK", "PJAA.JK",
    "PNBN.JK", "PNLF.JK", "PTBA.JK", "PTPP.JK", "PWON.JK", "ROTI.JK", "SCMA.JK", "SIDO.JK",
    "SIPD.JK", "SMCB.JK", "SMGR.JK", "SMRA.JK", "SSIA.JK", "TBIG.JK", "TINS.JK", "TLKM.JK",
    "ULTJ.JK", "UNSP.JK", "UNTR.JK", "UNVR.JK", "VKTR.JK",
]))


# --- US ------------------------------------------------------------------------------
# Yahoo Finance dual-class convention: dot replaced with dash (BRK.B -> BRK-B).

# Curated quick-scan list of the most active large-caps (faster than the full S&P 500).
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

# Dow Jones Industrial Average — 30 mega-caps (also subset of S&P 500).
DOW30: list[str] = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO",
    "CVX", "DIS", "GS", "HD", "HON", "IBM", "JNJ", "JPM",
    "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG",
    "SHW", "TRV", "UNH", "V", "VZ", "WMT",
]

# NASDAQ-100 — full index (101 tickers due to dual-class shares).
NASDAQ100: list[str] = sorted(set([
    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "ALNY",
    "AMAT", "AMD", "AMGN", "AMZN", "APP", "ARM", "ASML", "AVGO",
    "AXON", "BKNG", "BKR", "CCEP", "CDNS", "CEG", "CHTR", "CMCSA",
    "COST", "CPRT", "CRWD", "CSCO", "CSGP", "CSX", "CTAS", "CTSH",
    "DASH", "DDOG", "DXCM", "EA", "EXC", "FANG", "FAST", "FER",
    "FTNT", "GEHC", "GILD", "GOOG", "GOOGL", "HON", "IDXX", "INSM",
    "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN", "LRCX",
    "MAR", "MCHP", "MDLZ", "MELI", "META", "MNST", "MPWR", "MRVL",
    "MSFT", "MSTR", "MU", "NFLX", "NVDA", "NXPI", "ODFL", "ORLY",
    "PANW", "PAYX", "PCAR", "PDD", "PEP", "PLTR", "PYPL", "QCOM",
    "REGN", "ROP", "ROST", "SBUX", "SHOP", "SNDK", "SNPS", "STX",
    "TMUS", "TRI", "TSLA", "TTWO", "TXN", "VRSK", "VRTX", "WBD",
    "WDAY", "WDC", "WMT", "XEL", "ZS",
]))

# S&P 500 — full index (503 tickers due to dual-class shares).
SP500: list[str] = sorted(set([
    "A", "AAPL", "ABBV", "ABNB", "ABT", "ACGL", "ACN", "ADBE",
    "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL",
    "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALL", "ALLE",
    "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN",
    "ANET", "AON", "AOS", "APA", "APD", "APH", "APO", "APP",
    "APTV", "ARE", "ARES", "ATO", "AVB", "AVGO", "AVY", "AWK",
    "AXON", "AXP", "AZO", "BA", "BAC", "BALL", "BAX", "BBY",
    "BDX", "BEN", "BF-B", "BG", "BIIB", "BK", "BKNG", "BKR",
    "BLDR", "BLK", "BMY", "BR", "BRK-B", "BRO", "BSX", "BX",
    "BXP", "C", "CAG", "CAH", "CARR", "CASY", "CAT", "CB",
    "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CEG", "CF",
    "CFG", "CHD", "CHRW", "CHTR", "CI", "CIEN", "CINF", "CL",
    "CLX", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP",
    "COF", "COHR", "COIN", "COO", "COP", "COR", "COST", "CPAY",
    "CPB", "CPRT", "CPT", "CRH", "CRL", "CRM", "CRWD", "CSCO",
    "CSGP", "CSX", "CTAS", "CTRA", "CTSH", "CTVA", "CVNA", "CVS",
    "CVX", "D", "DAL", "DASH", "DD", "DDOG", "DE", "DECK",
    "DELL", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR",
    "DOC", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA",
    "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EG",
    "EIX", "EL", "ELV", "EME", "EMR", "EOG", "EPAM", "EQIX",
    "EQR", "EQT", "ERIE", "ES", "ESS", "ETN", "ETR", "EVRG",
    "EW", "EXC", "EXE", "EXPD", "EXPE", "EXR", "F", "FANG",
    "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FICO", "FIS",
    "FISV", "FITB", "FIX", "FOX", "FOXA", "FRT", "FSLR", "FTNT",
    "FTV", "GD", "GDDY", "GE", "GEHC", "GEN", "GEV", "GILD",
    "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC",
    "GPN", "GRMN", "GS", "GWW", "HAL", "HAS", "HBAN", "HCA",
    "HD", "HIG", "HII", "HLT", "HON", "HOOD", "HPE", "HPQ",
    "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM", "IBKR",
    "IBM", "ICE", "IDXX", "IEX", "IFF", "INCY", "INTC", "INTU",
    "INVH", "IP", "IQV", "IR", "IRM", "ISRG", "IT", "ITW",
    "IVZ", "J", "JBHT", "JBL", "JCI", "JKHY", "JNJ", "JPM",
    "KDP", "KEY", "KEYS", "KHC", "KIM", "KKR", "KLAC", "KMB",
    "KMI", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH",
    "LHX", "LII", "LIN", "LITE", "LLY", "LMT", "LNT", "LOW",
    "LRCX", "LULU", "LUV", "LVS", "LYB", "LYV", "MA", "MAA",
    "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT",
    "MET", "META", "MGM", "MKC", "MLM", "MMM", "MNST", "MO",
    "MOS", "MPC", "MPWR", "MRK", "MRNA", "MRSH", "MS", "MSCI",
    "MSFT", "MSI", "MTB", "MTD", "MU", "NCLH", "NDAQ", "NDSN",
    "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG",
    "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA",
    "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORCL", "ORLY",
    "OTIS", "OXY", "PANW", "PAYX", "PCAR", "PCG", "PEG", "PEP",
    "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD",
    "PLTR", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG",
    "PPL", "PRU", "PSA", "PSKY", "PSX", "PTC", "PWR", "PYPL",
    "Q", "QCOM", "RCL", "REG", "REGN", "RF", "RJF", "RL",
    "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY",
    "SATS", "SBAC", "SBUX", "SCHW", "SHW", "SJM", "SLB", "SMCI",
    "SNA", "SNDK", "SNPS", "SO", "SOLV", "SPG", "SPGI", "SRE",
    "STE", "STLD", "STT", "STX", "STZ", "SW", "SWK", "SWKS",
    "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH",
    "TEL", "TER", "TFC", "TGT", "TJX", "TKO", "TMO", "TMUS",
    "TPL", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA",
    "TSN", "TT", "TTD", "TTWO", "TXN", "TXT", "TYL", "UAL",
    "UBER", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI",
    "USB", "V", "VICI", "VLO", "VLTO", "VMC", "VRSK", "VRSN",
    "VRT", "VRTX", "VST", "VTR", "VTRS", "VZ", "WAB", "WAT",
    "WBD", "WDAY", "WDC", "WEC", "WELL", "WFC", "WM", "WMB",
    "WMT", "WRB", "WSM", "WST", "WTW", "WY", "WYNN", "XEL",
    "XOM", "XYL", "XYZ", "YUM", "ZBH", "ZBRA", "ZTS",
]))


def market_universes() -> dict[str, dict[str, list[str]]]:
    """Return {market: {label: tickers}} mapping."""
    return {
        "IDX": {
            "IDX30": IDX30,
            "LQ45": LQ45,
            "IDX80": IDX80,
            "Kompas100": KOMPAS100,
        },
        "US": {
            "Dow 30": DOW30,
            "Large Cap (top ~100)": US_LARGE_CAP,
            "NASDAQ 100": NASDAQ100,
            "S&P 500": SP500,
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
