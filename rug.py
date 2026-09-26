# zeno-sniper/rug.py
# Check anti-rugpull on-chain: legge mint_authority e freeze_authority
# da un RPC pubblico Solana.
#
# Comportamento (deciso per affidabilità):
#   - account_not_found: SOLO latenza di propagazione subito dopo la creazione.
#     NON è un segnale di rug -> si riprova (retry) per dare tempo alla chain.
#     Solo se ancora assente dopo i retry si scarta.
#   - freeze_authority / mint_authority attive: SCARTA subito (rug/honeypot).
#   - errore RPC/network o token-2022 non parlabile: fail-closed -> scarta
#     (più sicuro bloccare che avvisare senza verifica).
import time

import requests
from datetime import datetime

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
TIMEOUT = 6
RETRIES = 22         # ~11s di attesa totale (propagazione RPC pump.fun ~9s)
RETRY_DELAY = 0.5    # secondi tra i retry

# Session condivisa con pool, per non saturare le connessioni sotto carico
_RPC_SESSION = requests.Session()
_RPC_SESSION.headers.update({"User-Agent": "zeno-sniper/1.0"})


def _fetch_mint(mint: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [mint, {"encoding": "jsonParsed"}],
    }
    r = _RPC_SESSION.post(SOLANA_RPC, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("result", {}).get("value")


def check_rug(mint: str) -> dict:
    """Interroga lo stato on-chain del mint (con retry per propagazione).
    Ritorna sempre {'ok': bool, 'reason': str, 'detail': str}."""
    value = None
    last_err = None
    for attempt in range(RETRIES):
        try:
            v = _fetch_mint(mint)
            if v is not None:
                value = v
                break
            last_err = "account_not_found"
        except requests.exceptions.RequestException as e:
            last_err = f"rpc_error: {e}"
            # se è un errore di rete, niente retry stretto: sleep breve
        except Exception as e:
            last_err = f"parse_error: {e}"
        if attempt < RETRIES - 1:
            time.sleep(RETRY_DELAY)

    if value is None:
        # non propagato / errori RPC persistenti -> FAIL-CLOSED (non confermo pulito)
        return {"ok": False, "reason": "not_found_or_rpc",
                "detail": f"mint non leggibile dopo {RETRIES} tentativi: {last_err}"}

    info = (value.get("data") or {}).get("parsed", {}).get("info", {})
    mint_auth = info.get("mintAuthority")
    freeze_auth = info.get("freezeAuthority")

    if freeze_auth is not None:
        return {"ok": False, "reason": "freeze_authority",
                "detail": f"freeze authority ATTIVA: {freeze_auth}. Non puoi vendere -> honeypot/rug."}
    if mint_auth is not None:
        return {"ok": False, "reason": "mint_authority",
                "detail": f"mint authority ATTIVA: {mint_auth}. Dev può coniare all'infinito -> rug."}

    return {"ok": True, "reason": "clean",
            "detail": "mint+freeze authority rinunciate. On-chain pulito."}
