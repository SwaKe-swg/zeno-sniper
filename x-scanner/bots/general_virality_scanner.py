# x-scanner/bots/general_virality_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "general_virality token solana",
    "general_virality coin pump fun",
    "general_virality crypto solana",
    "GENERAL memecoin",
]
WATCH_TICKERS = ["GENERAL", "general_virality"]
PROFILE_LABEL = "VIP-general_virality"
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
