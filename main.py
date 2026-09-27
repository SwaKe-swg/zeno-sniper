# zeno-sniper/main.py
# ZENO — sniper meme coin Solana (solo alert, no trading).
# Sorgente: PumpPortal WebSocket (nuovi token in tempo reale, no Cloudflare).
# Prezzo SOL via Dexscreener REST per convertire i valori on-chain in USD.
# Anti-rug: verifica on-chain mint/freeze authority (fail-closed) in background.
import asyncio
import os
import time
import traceback
from datetime import datetime

import requests
from telegram import Bot

from config import Config
from dex.ws_client import PumpPortalWSClient
from alerts.tg import send_alert, update_status
from rug import check_rug
from virality import check_virality
from scanner_multi import scan_profiles_and_find_coin

# Set globale di ticker/profili emergenti sui social (web search parallelo)
# Aggiornato dal task scanner_multi.
social_hot_tickers = set()

# mcap base rilevato al momento dell'alert (per confrontare su/giu dopo)
token_state = {}   # mint -> {"ev": dict, "message_id": int, "base_mcap": float}

# Session HTTP condivisa con pool adeguato (evita "pool occupied" sotto carico)
HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "zeno-sniper/1.0"})
adapter = requests.adapters.HTTPAdapter(pool_connections=8, pool_maxsize=8)
HTTP.mount("https://", adapter)
HTTP.mount("http://", adapter)

# Cache anti-duplicati (mint già visti, verificati o in coda)
alerted_mints = set()
# Mint già in verifica (per non duplicare il task se arriva lo stesso evento)
in_flight = set()

# Semaforo: max 4 check rug on-chain in parallelo (niente pool saturato)
RUG_SEM = asyncio.Semaphore(4)

# Rate-limit anti-flood Telegram
_send_lock = asyncio.Lock()
_last_send = 0.0
RATE_LIMIT_SEC = Config.RATE_LIMIT_SEC

# Prezzo SOL in USD (cache ~30s, non a ogni token)
SOL_SOL_USD = 121.0
_SOL_FETCHED_AT = 0.0


def get_sol_usd() -> float:
    """Prezzo SOL con cache di 30s (evita chiamate REST per ogni token)."""
    global SOL_SOL_USD, _SOL_FETCHED_AT
    if time.time() - _SOL_FETCHED_AT < 30:
        return SOL_SOL_USD
    url = "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"
    try:
        r = HTTP.get(url, timeout=8)
        pairs = r.json().get("pairs") or []
        if pairs:
            p = float(pairs[0].get("priceUsd") or 0)
            if p > 0:
                SOL_SOL_USD = p
                _SOL_FETCHED_AT = time.time()
    except Exception as e:
        print(f"[{datetime.now()}] errore prezzo SOL: {e}")
    return SOL_SOL_USD


def get_token_chart_url(mint: str) -> str:
    return f"https://dexscreener.com/solana/{mint}"


async def _health_server():
    """Mini HTTP server per gli healthcheck di Railway (porta PORT o 8080).
    Il bot non ha un web server, ma Railway con healthcheckPath '/' lo richiede."""
    import http.server
    import socketserver
    import threading

    port = int(os.getenv("PORT", "8080"))

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, *a):
            pass

    httpd = socketserver.ThreadingTCPServer(("0.0.0.0", port), H)
    print(f"[{datetime.now()}] Health server su :{port}")
    # esegue in un thread per non bloccare l'event loop
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        httpd.shutdown()


async def _check_and_update_status(mint: str):
    """Dopo la finestra di osservazione, verifica se il mcap è salito o sceso
    e aggiorna il colore del messaggio (🟢 salito / 🔴 sceso)."""
    try:
        import asyncio
        from virality import _get_token_metrics
        st = token_state.get(mint)
        if not st:
            return
        # attesa osservazione (90s da quando è stato alertato)
        await asyncio.sleep(getattr(Config, "STATUS_WINDOW_S", 90))

        now = _get_token_metrics(mint)
        if now is None or now["mcap"] <= 0:
            return  # non leggibile, lascia arancione
        base = st.get("base_mcap") or 0
        if base <= 0:
            base = now["mcap"]
        state = "up" if now["mcap"] >= base else "rug"
        ev = st["ev"]
        sol_price = get_sol_usd()
        await update_status(
            Config.BOT, Config.TELEGRAM_CHAT_ID, st["message_id"],
            ev.get("symbol") or "?", ev.get("name") or "?",
            mint, get_token_chart_url(mint),
            now["mcap"], (ev.get("vSolInBondingCurve") or 0) * sol_price,
            ev.get("initialBuy") or 0, ev.get("solAmount") or 0, state,
        )
        token_state.pop(mint, None)
    except Exception as e:
        print(f"[{datetime.now()}] errore update status {mint}: {e}\n{traceback.format_exc()}")


async def _verify_and_alert(ev: dict):
    """Verifica anti-rug on-chain (in background) e, se pulito + virale, alerta."""
    mint = ev.get("mint")
    try:
        # check rug on-chain sotto semaforo (max 4 paralleli)
        async with RUG_SEM:
            rug = check_rug(mint)
        if not rug["ok"]:
            print(f"[{datetime.now()}] 🚫 SCARTATO anti-rug {ev.get('symbol')} -> "
                  f"{rug['reason']} | {rug['detail'][:60]}")
            return

        # anti-spam (opt-in): scarta i buy troppo deboli
        sol_spent = ev.get("solAmount") or 0
        if Config.MIN_INITIAL_BUY_SOL > 0 and sol_spent < Config.MIN_INITIAL_BUY_SOL:
            print(f"[{datetime.now()}] 🚫 SCARTATO anti-spam {ev.get('symbol')} "
                  f"(solo {sol_spent:.2f} SOL < {Config.MIN_INITIAL_BUY_SOL})")
            return

        sol_price = get_sol_usd()
        mcap_sol = ev.get("marketCapSol") or 0

        # Piano A — virality check: trazione reale prima di alertare.
        virality_note = ""
        growth = None
        age_min = 0
        bs_ratio = None
        if Config.VIRALITY_ENABLED:
            v = await check_virality(mint, mcap_sol, sol_price)
            growth = v.get("growth")
            age_min = v.get("age_min", 0) or 0
            bs_ratio = v.get("bs_ratio")
            if not v["ok"]:
                print(f"[{datetime.now()}] 🚫 SCARTATO non-virale {ev.get('symbol')} "
                      f"-> {v['detail'][:80]}")
                return
            virality_note = f"📈 {v['detail']}"

        # segna come alertato PRIMA del send (anti-duplicati/anti-flood)
        alerted_mints.add(mint)

        # send sotto lock: il rate-limit copre anche l'invio effettivo
        global _last_send
        async with _send_lock:
            now = asyncio.get_event_loop().time()
            wait = RATE_LIMIT_SEC - (now - _last_send)
            if wait > 0:
                await asyncio.sleep(wait)
            _last_send = asyncio.get_event_loop().time()
            msg_id = await send_alert(
                Config.BOT,
                Config.TELEGRAM_CHAT_ID,
                ev.get("symbol") or "N/A",
                ev.get("name") or "N/A",
                mint,
                get_token_chart_url(mint),
                mcap_sol * sol_price,                     # mcap usd
                (ev.get("vSolInBondingCurve") or 0) * sol_price,  # liq usd
                ev.get("initialBuy") or 0,                # initial buy SOL
                ev.get("solAmount") or 0,                 # SOL traded
                virality_note,
                age_min=age_min,
                bs_ratio=bs_ratio,
            )

        if msg_id:
            # traccia per il follow-up colorato (verde/rosso)
            token_state[mint] = {
                "ev": ev,
                "message_id": msg_id,
                "base_mcap": mcap_sol * sol_price,
            }
            asyncio.create_task(_check_and_update_status(mint))

        print(f"[{datetime.now()}] ✅ ALERT ZENO → {ev.get('symbol')} ${mcap_sol:.1f} SOL mcap "
              + (f"[{growth*100:+.0f}%]" if growth is not None else ""))
    except Exception as e:
        print(f"[{datetime.now()}] errore in verifica/alert {ev.get('symbol')}: {e}\n"
              f"{traceback.format_exc()}")
    finally:
        in_flight.discard(mint)


async def process_new_token(ev: dict):
    """Filtro rapido + dispatch del task di verifica in background."""
    mint = ev.get("mint")
    if not mint or mint in alerted_mints or mint in in_flight:
        return
    if not ev.get("symbol") or not ev.get("name"):
        return

    # --- filtri rapidi (prima del costoso check on-chain) ---
    sol_price = get_sol_usd()
    mcap_usd = (ev.get("marketCapSol") or 0) * sol_price
    liq_usd = (ev.get("vSolInBondingCurve") or 0) * sol_price
    if liq_usd < Config.MIN_LIQUIDITY_USD:
        return
    if mcap_usd > Config.MAX_MARKET_CAP_USD:
        return

    # superato il filtro -> verifica anti-rug in background
    in_flight.add(mint)
    asyncio.create_task(_verify_and_alert(ev))


# scanner Freecash parallelo (opzionale, testo/web leggero)
async def _freecash_loop():
    from freecash_scanner import scan_freecash
    while True:
        try:
            results = scan_freecash()
            for r in results:
                print(f"[{datetime.now()}] 💰 FREECASH TROVATO: {r['nome']} — €{r['premio_eur']} — {r.get('url', r.get('fonte'))}")
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️ errore freecash scan: {e}")
        await asyncio.sleep(30)


async def main():
    # KILL-SWITCH: se ZENO_ENABLED non è "true", il bot esce subito e
    # NON si connette né manda alert.
    if not Config.ZENO_ENABLED:
        print(f"[{datetime.now()}] 🛑 ZENO DISABILITATO (ZENO_ENABLED != true). Esco senza connettermi.")
        return

    print(f"[{datetime.now()}] 🚀 ZENO Sniper avviato — chat {Config.TELEGRAM_CHAT_ID}")
    print(f"[{datetime.now()}] Filtri: liq>${Config.MIN_LIQUIDITY_USD:.0f} "
          f"mcap<${Config.MAX_MARKET_CAP_USD:.0f} + anti-rug on-chain" 
          + (f" + initialBuy>={Config.MIN_INITIAL_BUY_SOL} SOL" if Config.MIN_INITIAL_BUY_SOL > 0 else ""))

    Config.BOT = Bot(token=Config.TELEGRAM_BOT_TOKEN)

    # health server per Railway
    asyncio.create_task(_health_server())

    # scanner Freecash parallelo (opzionale, testo/web leggero, nessun video pesante)
    if Config.FREECASH_ENABLED:
        from freecash_scanner import scan_freecash
        asyncio.create_task(_freecash_loop())

    ws = PumpPortalWSClient(Config.PUMPPORTAL_WS_URL, on_token=process_new_token)
    await ws.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] ZENO terminato.")
    except Exception as e:
        print(f"[{datetime.now()}] ERRORE CRITICO: {traceback.format_exc()}")
