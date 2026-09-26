# zeno-sniper/alerts/tg.py
# Formatta e invia l'alert di nuovo token su Telegram.
from datetime import datetime


async def send_pump_alert(
    bot,
    chat_id: str,
    coin_name: str,
    symbol: str,
    mint: str,
    chart_url: str,
    mcap_usd: float,
    liq_usd: float,
    initial_buy_sol: float,
    sol_traded: float,
    sol_price: float,
):
    """Invia l'alert di un nuovo token SOLANO verificato anti-rug on-chain."""
    axiom_pulse = "https://axiom.trade/pulse"
    message = (
        f"🚨 *ZENO — NUOVO TOKEN SOLANA (on-chain puliti)* 🚨\n\n"
        f"*Nome:* {coin_name} (`{symbol}`)\n"
        f"*Market Cap:* `${mcap_usd:,.0f}`\n"
        f"*Liquidità:* `${liq_usd:,.0f}`\n"
        f"*Initial Buy:* `{initial_buy_sol:,.2f}` SOL\n"
        f"*SOL scambiati:* `{sol_traded:,.2f}` SOL\n\n"
        f"🛡️ *Anti-rug PASS:* mint + freeze authority rinunciate (on-chain)\n\n"
        f"📊 *Chart:* [Dexscreener]({chart_url})\n"
        f"📡 *Axiom Pulse:* [lista nuovi token]({axiom_pulse})\n"
        f"`{mint}`  ← incolla mint in Axiom per tradare\n\n"
        f"🔥 *DYOR bro. Wild west.*\n"
    )
    kwargs = dict(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        read_timeout=30,
        connect_timeout=20,
    )
    try:
        await bot.send_message(**kwargs)
        print(f"[{datetime.now()}] Alert inviato per {symbol} → {chat_id}")
        return
    except Exception as e:
        print(f"[{datetime.now()}] Errore invio alert {symbol}: {e} (retry...)")
    try:
        await bot.send_message(**kwargs)
        print(f"[{datetime.now()}] Retry riuscito per {symbol} → {chat_id}")
    except Exception as e2:
        print(f"[{datetime.now()}] Retry fallito per {symbol}: {e2}")