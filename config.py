# zeno-sniper/config.py
import os


class Config:
    # --- Telegram ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- Sorgente dati ---
    PUMPPORTAL_WS_URL = os.getenv(
        "PUMPPORTAL_WS_URL", "wss://pumpportal.fun/api/data"
    )

    # --- Filtri (in USD, come richiesto) ---
    MIN_LIQUIDITY_USD = float(os.getenv("MIN_LIQUIDITY_USD", "2500"))
    MAX_MARKET_CAP_USD = float(os.getenv("MAX_MARKET_CAP_USD", "50000"))
    MIN_HOLDERS = int(os.getenv("MIN_HOLDERS", "10"))

    # --- Riferimenti runtime (settati in main) ---
    BOT = None
