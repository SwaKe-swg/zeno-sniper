# x-scanner/bots/trump_scanner.py — bot 1/10: profilo VIP Trump
PROFILE_KEYWORDS = [
    "trump crypto token solana",
    "trump coin pump fun",
    "trump memecoin solana",
    "trump twitter crypto",
]
WATCH_TICKERS = ["TRUMP", "TRUMPS", "TRUMPV2", "TRUMPL"]
PROFILE_LABEL = "VIP-Trump"
EXPECTED_PROFILE = "realDonaldTrump"

# Parametri di filtro da passare al bot Zeno (per riferimento, non per esecuzione diretta)
# Passano al core scanner se il ticker corrisponde.
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
