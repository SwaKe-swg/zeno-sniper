# x-scanner/bots/openai_scanner.py — bot 2/10: profilo VIP OpenAI / tech AI
PROFILE_KEYWORDS = [
    "openai token solana",
    "openai coin pump fun",
    "openai crypto memecoin",
    "chatgpt token solana",
]
WATCH_TICKERS = ["OPENAI", "GPT", "GPTCOIN", "CHAT"]
PROFILE_LABEL = "VIP-OpenAI"
EXPECTED_PROFILE = "OpenAI"

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
