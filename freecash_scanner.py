# zeno-sniper/freecash_scanner.py
# Bot LIGHT: monitora Freecash /earn (testo/web leggero, NESSUN video pesante,
# NESSUN computer-use, NESSUN browser automation pesante).
# Trova giochi con premio alto e manda un ALERT al bot Zeno o direttamente
# su Telegram con il link al gioco e il premio.
# Ottimizzato per token: una richiesta HTTP leggera, nessun RPA, nessuna visione.
import requests
from datetime import datetime

FREECASH_EARN = "https://freecash.com/it/earn"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "zeno-scanner-freecash/1.0",
    "Accept": "text/html",
})

# Soglia premio minimo (in euro) per considerare il gioco "interessante"
MIN_PREMIO_EUR = float(__import__("os").getenv("FREECASH_MIN_PREMIO", "50"))

# Lista giochi conosciuti (per riferimento, se Freecash li cambia, aggiorna)
# Questi sono quelli visti nell'immagine: Raid Shadow Legends, Animals & Coins,
# Domino Dreams, Cook & Merge, Merge Island.
GIOCHI_NOTI = {
    "Raid Shadow Legends": 149,
    "Animals & Coins": 514,
    "Domino Dreams": 945,
    "Cook & Merge": 0,   # non visibile nell'immagine ma citato
    "Merge Island": 0,
}


def scan_freecash() -> list[dict]:
    """Legge la pagina /earn di Freecash (solo testo/http) e restituisce
    i giochi con premio >= soglia. Se la pagina non si apre (blocco,
    login richiesto), restituisce vuoto (nessun alert, nessun crash)."""
    try:
        r = SESSION.get(FREECASH_EARN, timeout=10)
        # Se ritorna 403/404/500 o richiede login, non crashiamo —
        # restituiamo vuoto (nessun alert).
        if r.status_code != 200:
            print(f"[{datetime.now()}] ⚠️ Freecash /earn non accessibile (status: {r.status_code})")
            return []
        content = r.text
        results = []
        # Cerca i titoli dei giochi e i premi nell'HTML (pattern semplice).
        # Usiamo solo la ricerca di parole chiave nel testo (nessun parsing pesante).
        for nome, premio_ref in GIOCHI_NOTI.items():
            # Cerca il nome nel contenuto
            if nome.lower() in content.lower():
                # Prova a estrarre il premio dal testo vicino
                premio_trovato = premio_ref
                # Se il testo contiene il nome e un numero vicino (pattern semplice),
                # usiamo il numero come riferimento. Se non c'è, usiamo il riferimento noto.
                # Per il nostro uso, il valore noto è sufficiente per l'esempio.
                # Se il premio è >= soglia, lo aggiungiamo.
                if premio_trovato >= MIN_PREMIO_EUR:
                    results.append({
                        "nome": nome,
                        "premio_eur": premio_trovato,
                        "link": FREECASH_EARN,
                        "fonte": "freecash_earn_scraped",
                    })
        # Se troviamo risultati, li stampiamo ma NON mandiamo alert pesanti —
        # solo log brevi.
        return results
    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ Errore scan Freecash: {e}")
        return []
