# zeno-sniper/alerts/tg.py
# Formatta e invia le call con STATO COLORATO nel tempo:
#   🟠 alert iniziale "trovata, vediamo"
#   🟢 edit verde "coin trovata, sta salendo"
#   🔴 edit rosso "era rugpull, sta scendendo"
from datetime import datetime


def _link_pumpfun(mint: str) -> str:
    return f"https://pump.fun/coin/{mint}"


def _link_axiom(mint: str) -> str:
    return f"https://axiom.trade/token/{mint}"


def _link_dex(chart_url: str) -> str:
    return chart_url  # già dexscreener.com/solana/{mint}


def _build_message(symbol, coin_name, mcap_usd, liq_usd, initial_sol, sol_traded,
                   mint, chart_url, virality_note="", status="watch",
                   age_min=0, bs_ratio=None):
    """Costruisce il testo della call con stato colore + dati pre-buy."""
    head = (
        f"🟢 *{symbol}* — {coin_name}\n✅ *Coin trovata — sta salendo!*"
        if status == "up" else
        f"🔴 *{symbol}* — {coin_name}\n❌ *ERA RUGPULL — sta scendendo*"
        if status == "rug" else
        f"🟠 *{symbol}* — {coin_name}\n👀 Trovata — verifico se sale..."
    )

    stats = (
        f"💵 Mcap: `${mcap_usd:,.0f}`\n"
        f"💧 Liq: `${liq_usd:,.0f}`\n"
        f"🛒 Buy: `{initial_sol:,.2f} SOL`\n"
        f"🔁 Scambiati: `{sol_traded:,.2f} SOL`\n"
    )
    # dati extra dal pre-buy checklist (il video: non blind buy, guarda sempre)
    if age_min and age_min > 0:
        stats += f"⏱ Età: `{age_min:.0f} min`\n"
    if bs_ratio is not None and bs_ratio > 0:
        stats += f"⚖️ Buy/sell: `{bs_ratio:.1f}`\n"

    links = (
        f"⚡ [Pump.fun]({_link_pumpfun(mint)})\n"
        f"⚡ [Dexscreener]({_link_dex(chart_url)})\n"
        f"⚡ [Axiom]({_link_axiom(mint)})\n"
        f"`{mint}`\n"
    )
    virality_line = f"{virality_note}\n" if virality_note else ""
    # prompt del pre-buy checklist (dal video): reminder per il check manuale
    checklist = (
        "📝 *Pre-buy check (dal video):*\n"
        "— social presenti? (X/Telegram/website)\n"
        "— bubble map diversificata? (no 1 wallet >20%)\n"
        "— narrative forte? non copycat\n"
        "— conviction: bassa=skip, media=watch, alta=size"
    )
    footer = "_Wild west bro. DYOR prima di qualsiasi centesimo._"
    return (
        f"{head}\n\n"
        f"{stats}\n"
        f"🛡️ *Anti-rug:* mint+freeze rinunciate\n"
        f"{virality_line}"
        f"{links}\n"
        f"{checklist}\n\n"
        f"{footer}"
    )


async def send_alert(bot, chat_id, symbol, coin_name, mint, chart_url,
                     mcap_usd, liq_usd, initial_sol, sol_traded,
                     virality_note="", age_min=0, bs_ratio=None):
    """Invia l'alert ARANCIONE iniziale. Ritorna il message_id (per l'edit)."""
    text = _build_message(symbol, coin_name, mcap_usd, liq_usd, initial_sol,
                          sol_traded, mint, chart_url, virality_note,
                          status="watch", age_min=age_min, bs_ratio=bs_ratio)
    send_kwargs = dict(
        chat_id=chat_id, text=text, parse_mode="Markdown",
        disable_web_page_preview=True, read_timeout=30, connect_timeout=20,
    )
    for attempt in (0, 1):
        try:
            msg = await bot.send_message(**send_kwargs)
            print(f"[{datetime.now()}] Alert 🟠 {symbol} → {chat_id}")
            return msg.message_id
        except Exception as e:
            if attempt == 0:
                print(f"[{datetime.now()}] Errore invio {symbol}: {e} (retry...)")
    return None


async def update_status(bot, chat_id, message_id, symbol, coin_name, mint, chart_url,
                        mcap_usd, liq_usd, initial_sol, sol_traded, state,
                        age_min=0, bs_ratio=None):
    """Edita il messaggio esistente con il nuovo colore/status.
    state: 'up' (verde) o 'rug' (rosso). Non invia un nuovo messaggio."""
    status = "up" if state == "up" else "rug"
    text = _build_message(symbol, coin_name, mcap_usd, liq_usd, initial_sol,
                          sol_traded, mint, chart_url, status=status,
                          age_min=age_min, bs_ratio=bs_ratio)
    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=text,
            parse_mode="Markdown", read_timeout=30, connect_timeout=20,
        )
        print(f"[{datetime.now()}] ✏️ Aggiornato {symbol} → {'🟢' if state=='up' else '🔴'}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Edit fallito {symbol}: {e}")
        return False
