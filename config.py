# zeno-sniper/config.py
import os


class Config:
    # --- Telegram ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- Kill-switch (Railway) ---
    # Se false/off, il bot esce subito e NON connettersi. Default ENABLED.
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
    # Entry precoce: il max mcap non deve essere troppo basso o perdiamo le
    # virali tipo HEISENBERG (esplose da $5k a $324k in 1h). Teniamo $300k;
    # il virality check resta il gate vero (mcap in crescita + vol/txns reali).
    MAX_MARKET_CAP_USD = float(os.getenv("MAX_MARKET_CAP_USD", "300000"))
    MIN_HOLDERS = int(os.getenv("MIN_HOLDERS", "50"))

    # --- Filtro anti-spam (basso = più call, alto = più selettivo) ---
    MIN_INITIAL_BUY_SOL = float(os.getenv("MIN_INITIAL_BUY_SOL", "0"))

    # --- Piano A: virality check on-chain ---
    VIRALITY_ENABLED = os.getenv("VIRALITY_ENABLED", "").strip().lower() not in (
        "false", "0", "no", "off"
    )  # default TRUE
    VIRALITY_WINDOW_S = int(os.getenv("VIRALITY_WINDOW_S", "25"))
    VIRALITY_MIN_GROWTH = float(os.getenv("VIRALITY_MIN_GROWTH", "0.15"))
    # buy/sell ratio soglia (default 1.2 = leggero vantaggio compratori)
    # se >0, il virality check richiede anche questo.
    VIRALITY_BUY_SELL_RATIO = float(os.getenv("VIRALITY_BUY_SELL_RATIO", "2.0"))

    # --- Rate-limit invio ---
    RATE_LIMIT_SEC = float(os.getenv("RATE_LIMIT_SEC", "1.6"))

    # --- Follow-up colore (verde/rosso) ---
    STATUS_WINDOW_S = int(os.getenv("STATUS_WINDOW_S", "60"))

    # --- Riferimenti runtime (settati in main) ---
    BOT = None