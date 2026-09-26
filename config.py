# zeno-sniper/config.py
import os


class Config:
    # --- Telegram ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- Kill-switch (Railway) ---
    # Default ENABLED: assenza della var -> il bot parte.
    # Per spegnerlo: ZENO_ENABLED=false|0|no|off (case-insensitive).
    ZENO_ENABLED = os.getenv("ZENO_ENABLED", "").strip().lower() not in (
        "false", "0", "no", "off"
    )

    # --- Sorgente dati ---
    PUMPPORTAL_WS_URL = os.getenv(
        "PUMPPORTAL_WS_URL", "wss://pumpportal.fun/api/data"
    )

    # --- Filtri (in USD) ---
    # I nuovi token Pump.fun partono con ~$3.5-4k di liquidità: la soglia
    # $2500 lascia passare i fresh launch senza scartare i pitest.
    MIN_LIQUIDITY_USD = float(os.getenv("MIN_LIQUIDITY_USD", "2500"))
    MAX_MARKET_CAP_USD = float(os.getenv("MAX_MARKET_CAP_USD", "50000"))
    MIN_HOLDERS = int(os.getenv("MIN_HOLDERS", "10"))

    # --- Filtro anti-spam (basso = più call, alto = più selettivo) ---
    # Se >0, scarta i token con initial buy sotto questa soglia in SOL.
    # Es. "2" = solo token con un buy iniziale >=2 SOL (più forti, meno spam).
    MIN_INITIAL_BUY_SOL = float(os.getenv("MIN_INITIAL_BUY_SOL", "0"))

    # --- Rate-limit invio ---
    RATE_LIMIT_SEC = float(os.getenv("RATE_LIMIT_SEC", "1.6"))

    # --- Riferimenti runtime (settati in main) ---
    BOT = None
