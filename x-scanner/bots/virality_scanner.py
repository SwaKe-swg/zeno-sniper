# x-scanner/bots/virality_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "virality token solana",
    "virality coin pump fun",
    "virality crypto solana",
    "VIRAL memecoin",
]
WATCH_TICKERS = ["VIRAL", "virality"]
PROFILE_LABEL = "VIP-virality"
EXPECTED_PROFILE = ""

ZENO_FILTER_REF = {
    "liq_min_usd": 2500,
    "mcap_max_usd": 300000,
    "virality_enabled": True,
    "virality_window_s": 25,
    "virality_growth": 0.15,
    "virality_buy_sell": 1.2,
    "status_window_s": 60,
    "anti_rug_retry_s": 11,
}
