import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import (
    PING_INTERVAL, REPORT_INTERVAL, IMAGE_SELECTOR,
    ENLACE_1_IP, ENLACE_2_IP, ENLACE_1_NOMBRE, ENLACE_2_NOMBRE,
    ENLACE_1_WEB_URL, ENLACE_2_WEB_URL,
)
from dnd import is_dnd, time_str
from monitor import check_enlace
from capture import capture_image
from state import StateManager
from bot import BotHandler

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, state: StateManager, bot_handler: BotHandler):
        self.state = state
        self.bot = bot_handler
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.add_job(
            self._ping_job,
            trigger=IntervalTrigger(seconds=PING_INTERVAL),
            id="ping_job",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self._report_job,
            trigger=IntervalTrigger(seconds=REPORT_INTERVAL),
            id="report_job",
            replace_existing=True,
        )

        self.scheduler.start()

    def _enlaces_ping(self):
        return [
            (ENLACE_1_IP, ENLACE_1_NOMBRE),
            (ENLACE_2_IP, ENLACE_2_NOMBRE),
        ]

    def _enlaces_web(self):
        return [
            (ENLACE_1_NOMBRE, ENLACE_1_WEB_URL),
            (ENLACE_2_NOMBRE, ENLACE_2_WEB_URL),
        ]

    async def run_first_ping(self):
        await self._ping_job()

    async def _ping_job(self):
        for ip, nombre in self._enlaces_ping():
            if not ip:
                continue
            mon = self.state.get_monitor(ip)
            mon.name = nombre
            alert_msg = await check_enlace(ip, mon, self.state)
            if alert_msg:
                await self.bot.alert_all(alert_msg)

    async def _report_job(self):
        dnd_now = is_dnd()
        prev_dnd = self.state.dnd_active

        if dnd_now and not prev_dnd:
            self.state.dnd_active = True
            self.state.save()
            await self.bot.alert_all(
                f"🌙 *Modo No Molestar activado* ({time_str()} VE)\n\n"
                "No se enviaran reportes horarios hasta las 7:00 AM.\n"
                "Las alertas de falla continuan activas."
            )
            logger.info("DND activado")
            return

        if not dnd_now and prev_dnd:
            self.state.dnd_active = False
            self.state.save()
            await self.bot.alert_all(
                f"☀️ *Modo Normal restaurado* ({time_str()} VE)\n\n"
                "Los reportes horarios se reanudan."
            )
            logger.info("DND desactivado")

        if dnd_now:
            logger.info("DND activo - reporte omitido")
            return

        for nombre, web_url in self._enlaces_web():
            if not web_url:
                continue

            try:
                img_bytes = await capture_image(web_url, IMAGE_SELECTOR)
            except Exception:
                img_bytes = None

            ip = next(
                (ip for ip, n in self._enlaces_ping() if n == nombre), None
            )
            mon = self.state.get_monitor(ip) if ip else None

            if mon:
                pct = (
                    (mon.hourly_success / mon.hourly_total * 100)
                    if mon.hourly_total > 0
                    else 0
                )
                status_emoji = "🟢" if pct >= 90 else "🟡" if pct >= 50 else "🔴"
                caption = (
                    f"📊 *{nombre}*\n"
                    f"{status_emoji} {mon.hourly_success}/{mon.hourly_total} "
                    f"exitosos ({pct:.0f}%)"
                )
            else:
                caption = f"📊 *{nombre}*"

            if img_bytes:
                await self.bot.broadcast_image(
                    img_bytes, caption=caption, filename=f"{nombre}.jpg"
                )
            else:
                await self.bot.alert_all(caption)

        self.state.reset_hourly_stats()
