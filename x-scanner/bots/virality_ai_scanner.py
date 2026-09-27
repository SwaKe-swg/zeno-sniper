# x-scanner/bots/virality_ai_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "virality_ai token solana",
    "virality_ai coin pump fun",
    "virality_ai crypto solana",
    "AI memecoin",
]
WATCH_TICKERS = ["AI", "virality_ai"]
PROFILE_LABEL = "VIP-virality_ai"
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
