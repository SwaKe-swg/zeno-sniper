# zeno-sniper/dex/ws_client.py
# Client WebSocket PumpPortal — stream in tempo reale dei NUOVI token solana.
# PumpPortal non è dietro Cloudflare (vs il vecchio WS Dexscreener che dà 403).
import asyncio
import json
from datetime import datetime

import websockets


class PumpPortalWSClient:
    """Connette a wss://pumpportal.fun/api/data e cattura i nuovi token."""

    def __init__(self, ws_url: str, on_token=None):
        self.ws_url = ws_url
        self.on_token = on_token          # callback async (token_event: dict)
        self.reconnect_delay = 5
        self._ping_task = None

    async def _ping_loop(self):
        while True:
            try:
                if self.websocket:
                    await self.websocket.send(json.dumps({"type": "ping"}))
            except Exception:
                pass
            await asyncio.sleep(30)

    async def run(self):
        """Loop principale: connette, si sottoscrive, cattura token, si riconnette."""
        while True:
            try:
                print(f"[{datetime.now()}] Connessione PumpPortal WS: {self.ws_url}")
                self.websocket = await websockets.connect(
                    self.ws_url,
                    extra_headers={"Origin": "https://pumpportal.fun"},
                    ping_interval=30,
                    ping_timeout=15,
                )
                # sottoscrizione ai nuovi token
                await self.websocket.send(
                    json.dumps({"method": "subscribeNewToken"})
                )
                print(f"[{datetime.now()}] PumpPortal WS connesso e sottoscritto.")
                if not self._ping_task:
                    self._ping_task = asyncio.create_task(self._ping_loop())

                async for raw in self.websocket:
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(data, dict):
                        continue
                    # evento di conferma subscribe: {"message": "..."}
                    if data.get("message"):
                        continue
                    if data.get("mint") and self.on_token:
                        await self.on_token(data)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[{datetime.now()}] PumpPortal WS chiuso ({e}). Riconnessione tra {self.reconnect_delay}s...")
            except Exception as e:
                print(f"[{datetime.now()}] Errore PumpPortal: {e}. Riprovo tra {self.reconnect_delay}s...")
            finally:
                self.websocket = None
            await asyncio.sleep(self.reconnect_delay)
