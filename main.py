import asyncio
import logging

from config import (BOT_TOKEN, ENLACE_1_IP, ENLACE_2_IP, ENLACE_1_NOMBRE, ENLACE_2_NOMBRE,
                    ENLACE_1_WEB_URL, ENLACE_2_WEB_URL)
from state import StateManager
from bot import BotHandler
from scheduler import Scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN no configurado. Revisa el archivo .env")
        return

    state = StateManager()
    bot_handler = BotHandler(state)
    app = bot_handler.build_app()

    scheduler = Scheduler(state, bot_handler)
    scheduler.start()

    print("[Bot] Bot de Monitoreo de Enlaces iniciado")
    print(f"  Ping 1: {ENLACE_1_NOMBRE} ({ENLACE_1_IP or 'no configurado'})")
    print(f"  Ping 2: {ENLACE_2_NOMBRE} ({ENLACE_2_IP or 'no configurado'})")
    print(f"  Web 1: {ENLACE_1_NOMBRE} ({ENLACE_1_WEB_URL or 'no configurado'})")
    print(f"  Web 2: {ENLACE_2_NOMBRE} ({ENLACE_2_WEB_URL or 'no configurado'})")
    print(f"  Suscriptores: {len(state.subscribers)}")

    await app.initialize()
    await bot_handler.setup_commands()
    await app.updater.start_polling()
    await app.start()

    print("[Bot] Esperando actualizaciones...")

    asyncio.create_task(scheduler.run_first_ping())

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
