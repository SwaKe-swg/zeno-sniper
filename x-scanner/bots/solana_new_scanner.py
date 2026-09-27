# x-scanner/bots/solana_new_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "solana_new token solana",
    "solana_new coin pump fun",
    "solana_new crypto solana",
    "SOL memecoin",
]
WATCH_TICKERS = ["SOL", "solana_new"]
PROFILE_LABEL = "VIP-solana_new"
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
