# zeno-sniper/virality.py
# Piano A — "virality check" on-chain.
# Soglie numeriche basate su ricerca virality (moonhydra/flashift/bydfi) e
# pre-buy checklist dal video jakegetrich (social gates, holder sanity,
# bubble map, deep proof, narrative, conviction). Parametri Trojan-style
# riferimento: amount 0.1 SOL, slippage 30%, fee 0.02 SOL, tip 0.08 SOL,
# virality mcap+15% in 25s, buy/sell >=2.0 (default 1.2 per flex),
# anti-rug mint/freeze revoked.
import asyncio
from datetime import datetime

import requests

from config import Config

DEX_REST = "https://api.dexscreener.com/latest/dex/tokens/{mint}"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "zeno-sniper/1.0"})

MIN_BACKOFF_S = 5   # attesa iniziale per lasciar propagare il listino


def _get_token_metrics(mint: str) -> dict | None:
    """Mcap/volume/txns live via Dexscreener REST. None se non ancora listato."""
    try:
        r = SESSION.get(DEX_REST.format(mint=mint), timeout=10)
        r.raise_for_status()
        pairs = r.json().get("pairs") or []
        if not pairs:
            return None
        p = pairs[0]
        return {
            "mcap": float(p.get("marketCap") or p.get("fdv") or 0),
            "volume24": float(p.get("volume", {}).get("h24", 0) or 0),
            "txns": (p.get("txns", {}) or {}).get("h24", {}),
            "liquidity": float((p.get("liquidity") or {}).get("usd", 0) or 0),
            "pair_age_s": _pair_age(p),
        }
    except Exception:
        return None


def _pair_age(p) -> float:
    """Età del pair in secondi (dal timestamp di creazione)."""
    try:
        created = p.get("pairCreatedAt") or 0
        if created <= 0:
            return -1
        import time as _t
        return max(0, (_t.time() * 1000 - created) / 1000)
    except Exception:
        return -1


async def check_virality(mint: str, initial_mcap_sol: float, sol_price: float,
                          min_growth: float = None) -> dict:
    """Verifica trazione reale dopo la finestra. ok=True se il mcap cresce.

    Legge finestra e soglia da Config (VIRALITY_WINDOW_S / VIRALITY_MIN_GROWTH).
    """
    window = getattr(Config, "VIRALITY_WINDOW_S", 45)
    min_growth = min_growth if min_growth is not None else getattr(Config, "VIRALITY_MIN_GROWTH", 0.30)
    initial_mcap_usd = initial_mcap_sol * sol_price

    await asyncio.sleep(MIN_BACKOFF_S)
    base = _get_token_metrics(mint)
    if base is None or base["mcap"] <= 0:
        # Non ancora listato su Dexscreener dopo la prima attesa: NON scartare
        # subito (fake-negative: Dexscreener è solo lento a indicizzare i fresh).
        # Riprova una seconda volta dopo ALTRO attesa prima di rinunciare.
        await asyncio.sleep(window)
        base = _get_token_metrics(mint)
        if base is None or base["mcap"] <= 0:
            return {"ok": False,
                    "detail": "non listato su Dexscreener anche dopo 2 attese",
                    "mcap_now": initial_mcap_usd}

    await asyncio.sleep(window)
    now = _get_token_metrics(mint)
    if now is None or now["mcap"] <= 0:
        return {"ok": False, "detail": "mcap non rilevato al re-check",
                "mcap_now": base["mcap"]}

    growth = (now["mcap"] - base["mcap"]) / base["mcap"] if base["mcap"] else 0

    # Trazione reale: oltre alla crescita mcap, se Dexscreener fornisce i txns
    # h24 valutiamo il buy/sell ratio (>= 1.5 = compratori in vantaggio).
    txns = now.get("txns") or {}
    buys = int(txns.get("buys") or 0)
    sells = int(txns.get("sells") or 0)
    bs_ratio = (buys / sells) if sells > 0 else (buys if buys > 0 else 0)

    # Se fornito, la soglia di crescita viene sovrascritta
    # (per il caso virale da profilo social emergente: soglia ridotta).
    actual_min_growth = min_growth

    growth_ok = growth >= actual_min_growth
    bs_ok = True  # buy ratio è vincolante
    if buys > 0 and sells > 0:
        min_bs = getattr(Config, "VIRALITY_BUY_SELL_RATIO", 2.0)
        bs_ok = bs_ratio >= min_bs

    # Trazione: sui mcap più alti pretendiamo del volume reale (30k+),
    # altrimenti è un pump finto che alza il mcap senza mercato.
    vol_ok = now["volume24"] >= 30000 if now["mcap"] >= 100000 else True

    # Holders sanity: se disponibile, controlla che ci siano almeno MIN_HOLDERS.
    # Se il dato non c'è (fresh pump), non scarta per assenza — il filtro
    # MIN_HOLDERS nel main scarta prima di arrivare qui.
    holders_ok = True
    if "holders" in now:
        holders_ok = int(now.get("holders") or 0) >= getattr(Config, "MIN_HOLDERS", 10)

    if growth_ok and bs_ok and vol_ok and holders_ok:
        return {"ok": True,
                "detail": f"mcap {growth*100:+.0f}% (${base['mcap']:,.0f} -> ${now['mcap']:,.0f}), "
                          f"buy/sell {bs_ratio:.1f}, vol24 ${now['volume24']:,.0f}",
                "mcap_now": now["mcap"], "mcap_base": base["mcap"], "growth": growth,
                "bs_ratio": bs_ratio, "age_min": _age_min(now)}
    reason = []
    if not growth_ok:
        reason.append(f"mcap {growth*100:+.0f}% < {actual_min_growth*100:.0f}%")
    if not bs_ok:
        reason.append(f"buy/sell {bs_ratio:.1f} < {getattr(Config, 'VIRALITY_BUY_SELL_RATIO', 2.0)}")
    if not vol_ok:
        reason.append(f"vol ${now['volume24']:,.0f} < $30k (mcap alto)")
    if not holders_ok:
        reason.append(f"holders {now.get('holders', '?')} < {getattr(Config, 'MIN_HOLDERS', 10)}")
    return {"ok": False,
            "detail": ", ".join(reason) + " — niente trazione",
            "mcap_now": now["mcap"], "mcap_base": base["mcap"], "growth": growth,
            "bs_ratio": bs_ratio, "age_min": _age_min(now)}


def _age_min(metrics: dict) -> float:
    """Età in minuti dal pair_age_s (0 se ignoto)."""
    s = (metrics or {}).get("pair_age_s") or 0
    return s / 60.0 if s and s > 0 else 0
