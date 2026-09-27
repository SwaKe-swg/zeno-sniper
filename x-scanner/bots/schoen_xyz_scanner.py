# x-scanner/bots/schoen_xyz_scanner.py — bot per profilo virale
PROFILE_KEYWORDS = [
    "schoen_xyz token solana",
    "schoen_xyz coin pump fun",
    "schoen_xyz crypto solana",
    "schoen_xyz memecoin",
]
WATCH_TICKERS = ["schoen_xyz", "schoen_xyz"]
PROFILE_LABEL = "VIP-schoen_xyz"
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
