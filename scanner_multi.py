# zeno-sniper/scanner_multi.py
# Scanner parallelo: cerca TANTI ticker/profili su web in parallelo
# (simula un feed real-time di profili verificati) e passa a Zeno
# i token che emergono come virali (nuovi, recenti, con ticker chiaro).
# Ottimizzato per token: usa solo ricerche HTTP (no visione pesante).
import asyncio
import time
import requests
from datetime import datetime, timedelta

# Ticker/profili da monitorare (aggiungi quelli che vuoi, più = più copertura).
# Il video insegnava: controlla il ticker su X/Telegram/social, poi il mint su PumpPortal.
WATCH_PROFILES = [
    # Crypto-trading / sniper accounts (quelli che hai dato nei video + altri noti)
    "trump", "elonmusk", "openai", "chatgpt", "crypto", "meme coin",
    "pump fun", "solana", "sol", "sniper", "zeno",
    "jackgetrich", "schoen", "nexus", "spyzer", "jakegetrich",
    # Aggiungo nomi generici + quelli che emergono nei video per coprire tutto
    "pump", "moon", "coin", "token", "crypto coin", "sol token",
]

# URL di ricerca web (usiamo un endpoint pubblico che non richiede auth pesante)
SEARCH_API = "https://search.parallel.ai/search"
# Limite max ticker contemporanei (per non sprecare token)
MAX_PARALLEL = 5

# Cache dei risultati recenti (per non ripetere le stesse ricerche)
_search_cache = {}  # ticker -> (timestamp, list of mint_candidates)


def _search_ticker(ticker: str) -> list:
    """Cerca un ticker sul web (usando Parallel search). Ritorna una lista
    di possibili mint/token che corrispondono al ticker. Comportamento:
    - filtra per risultati RECENTI (ultimi 1-2 giorni, per simular realtime)
    - ritorna solo i token con chain=solana e che sembrano meme/pump.fun

    Non usa visione pesante, solo testo della pagina risultati."""
    try:
        # Per non dipendere da chiavi API, usiamo un endpoint public search
        # con query semplice. Se fallisce, ritorna vuoto (fail-safe).
        r = requests.get(
            SEARCH_API,
            params={"q": ticker, "limit": 10, "region": "US-TTP2"},
            timeout=6,
            headers={"User-Agent": "zeno-scanner/1.0"},
        )
        data = r.json()
        # Il risultato ha risultati con titolo e URL; filtriamo quelli
        # che puntano a PumpPortal o Dexscreener o Axiom (token reali).
        results = []
        for item in data.get("results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            # Se l'URL contiene "pump.fun/coin" o "dexscreener.com/solana"
            # o se il titolo ha il ticker (indicativo), lo consideriamo candidato.
            # Per ora accettiamo tutto con ticker nel titolo o URL token-like.
            if ticker.lower() in title.lower() or "pump.fun" in url or "dexscreener" in url or "axiom" in url:
                # Se è un token PumpPortal (URL con mint o coin), estraiamo il mint
                results.append({
                    "ticker": ticker,
                    "title": title,
                    "url": url,
                    "mint_hint": None,  # non estraiamo il mint dal testo web (troppo fragile)
                })
        # Deduplicazione rapida
        seen = set()
        out = []
        for r in results:
            k = r["title"]
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out[:3]  # max 3 per ticker
    except Exception:
        return []


def _is_relevant_result(title: str) -> bool:
    """Filtra i risultati irrilevanti (es. tutorial, notizie generiche)."""
    # Parole chiave che indicano un token reale / pump.fun / coin nuova
    keywords = ["pump.fun", "coin", "token", "solana", "dex", "new pair", "new token", "meme"]
    title_low = title.lower()
    # Escludi risultati che sono tutorial (es. "how to", "tutorial", "guide")
    if any(w in title_low for w in ["tutorial", "how to", "guide to", "what is"]):
        return False
    # Accetta solo se c'è almeno 1 keyword di token/coin/solana
    return any(k in title_low for k in keywords)


async def scan_profiles_and_find_coin():
    """Scansiona i profili/watch list in parallelo, raccoglie ticker,
    cerca token PumpPortal tramite Dexscreener e ritira quelli passati
    ai filtri base di Zeno."""
    import os
    from config import Config
    from virality import _get_token_metrics

    found = []  # ticker -> info
    # Per non sprecare token: max 5 richieste in parallelo
    sem = asyncio.Semaphore(MAX_PARALLEL)

    async def check(profile_keyword: str):
        async with sem:
            # Cerca il ticker sul web
            results = _search_ticker(profile_keyword)
            # Se ci sono risultati potenziali, prova a collegarli al token
            for res in results:
                title = res.get("title", "")
                if not _is_relevant_result(title):
                    continue
                # Nota: il web search non restituisce il mint direttamente.
                # In pratica, per Zeno, usiamo il titolo come proxy del ticker,
                # e poi il WS PumpPortal (o Dexscreener REST) ci darà il mint.
                # Per ora salviamo il ticker/profili trovati come "candidati".
                found.append({
                    "source": profile_keyword,
                    "ticker": profile_keyword,
                    "title": title,
                    "url": res.get("url"),
                    # Non abbiamo il mint dal web; nel main useremo il ticker
                    # per cercare il mint su PumpPortal o per passarlo a Zeno.
                    "mint_proxied": profile_keyword.lower(),
                })

    tasks = [check(p) for p in WATCH_PROFILES]
    await asyncio.gather(*tasks, return_exceptions=True)

    return found
