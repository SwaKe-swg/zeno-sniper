# app.py — entry point compatibile Railway.
# Railway tenta sempre "python app.py"; questo file delega a main.py
# così il deploy parte comunque qualunque sia il comando. Avvia il bot.
import asyncio

import main

if __name__ == "__main__":
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
