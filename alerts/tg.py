# zeno-sniper/alerts/tg.py
# Formatta e invia la call di un nuovo token su Telegram.
# Stile: pulito, compatto, ottimizzato per telefono (mobile).
from datetime import datetime


def _link_pumpfun(mint: str) -> str:
    return f"https://pump.fun/coin/{mint}"


def _link_axiom(mint: str) -> str:
    # Axiom non espone un deep-link documentato; best-effort: apre il token.
    # Se non dovesse caricare, l'utente ha comunque il mint copiabile (sotto).
    return f"https://axiom.trade/token/{mint}"


def _link_dex(chart_url: str) -> str:
    return chart_url  # già dexscreener.com/solana/{mint}


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
    """Invia la call di un nuovo token (stile bro, compatto per mobile)."""
    header = f"🎯 *{symbol}* — {coin_name}"
    stats = (
        f"💵 Mcap: `${mcap_usd:,.0f}`\n"
        f"💧 Liq: `${liq_usd:,.0f}`\n"
        f"🛒 Buy: `{initial_buy_sol:,.2f} SOL`\n"
        f"🔁 Scambiati: `{sol_traded:,.2f} SOL`\n"
    )
    links = (
        f"⚡ [Pump.fun]({_link_pumpfun(mint)})\n"
        f"⚡ [Dexscreener]({_link_dex(chart_url)})\n"
        f"⚡ [Axiom]({_link_axiom(mint)})\n"
        f"`{mint}`\n"
    )
    footer = "_Wild west bro. DYOR prima di qualsiasi centesimo._"
    message = (
        f"{header}\n\n"
        f"{stats}\n"
        f"🛡️ *Anti-rug pass:* mint + freeze rinunciate\n\n"
        f"{links}\n"
        f"{footer}"
    )
    send_kwargs = dict(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        read_timeout=30,
        connect_timeout=20,
    )
    # Invio con 1 retry
    for attempt in (0, 1):
        try:
            await bot.send_message(**send_kwargs)
            print(f"[{datetime.now()}] Call inviata {symbol} → {chat_id}")
            return
        except Exception as e:
            if attempt == 0:
                print(f"[{datetime.now()}] Errore invio {symbol}: {e} (retry...)")
    print(f"[{datetime.now()}] Retry fallito anche per {symbol}")
