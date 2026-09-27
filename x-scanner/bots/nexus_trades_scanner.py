# x-scanner/bots/nexus_trades_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "nexus_trades token solana",
    "nexus_trades coin pump fun",
    "nexus_trades crypto solana",
    "nexus_trades memecoin",
]
WATCH_TICKERS = ["nexus_trades", "nexus_trades"]
PROFILE_LABEL = "VIP-nexus_trades"
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
