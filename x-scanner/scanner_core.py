# x-scanner/scanner_core.py
# Core: avvia 10 bot scanner in parallelo, raccoglie ticker emergenti,
# verifica se corrispondono a token PumpPortal esistenti, e passa a Zeno.
# Nessun video/browser pesante — solo web search testo (reddit/xurl se disponibile).
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, "/opt/data/x-scanner")

from scanner_multi import scan_profiles_and_find_coin


def main_loop():
    print(f"[{datetime.now()}] 🟢 X-SCANNER: avvio scan parallelo 10 profili/vip (ogni 30 min). Nessun video pesante.")
    # Avvia il loop asincrono per la ricerca parallela
    async def run():
        while True:
            found = await scan_profiles_and_find_coin()
            # Se trovati ticker, li passiamo a un webhook / variabile per Zeno.
            # Nel setup Railway, questa funzione può anche scrivere su un file
            # condiviso o chiamare una variabile globale del servizio Zeno.
            # Per ora: registriamo nel log e passiamo al virality se corrispondono.
            if found:
                for item in found:
                    print(f"[{datetime.now()}] ⚡ TICKER EMERGENTE: {item.get('ticker')} (fonte: {item.get('source')}) | {item.get('url')}")
            await asyncio.sleep(30)
    # Proviamo a usare asyncio nel thread principale
    import time
    print("[SCANNER] Avviato. Sarà attivo in background. Per fermare: kill process o variabile.")
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("[SCANNER] Spento manualmente.")


if __name__ == "__main__":
    main_loop()
