import logging
from datetime import datetime

from telegram import InputFile, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

from config import (
    BOT_TOKEN,
    ENLACE_1_NOMBRE, ENLACE_1_WEB_URL,
    ENLACE_2_NOMBRE, ENLACE_2_WEB_URL,
    IMAGE_SELECTOR,
    CANTV_TELEFONO, CANTV_INFO,
    NETUNO_TELEFONO,
)
from capture import capture_image
from state import StateManager

logger = logging.getLogger(__name__)

MENU = [
    [KeyboardButton("/status"), KeyboardButton("/subscribe")],
    [KeyboardButton("/unsubscribe"), KeyboardButton("/reporte")],
]


class BotHandler:
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.application: Application | None = None

    async def start(self, update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 *Bienvenido al Bot de Monitoreo de Enlaces*\n\n"
            "Comandos disponibles:\n"
            "• `/status` - Estado actual y graficas\n"
            "• `/subscribe` - Suscribirse a alertas\n"
            "• `/unsubscribe` - Darse de baja\n"
            "• `/reporte` - Contactos de soporte\n"
            "• `/help` - Mostrar esta ayuda",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True),
        )

    async def subscribe(self, update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.state.add_subscriber(chat_id)
        await update.message.reply_text(
            "✅ *¡Suscrito exitosamente!*\n\n"
            "Recibiras alertas de caida y reportes periodicos de los enlaces.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True),
        )

    async def unsubscribe(self, update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.state.remove_subscriber(chat_id)
        await update.message.reply_text(
            "✅ *Dado de baja.*\n\nYa no recibiras notificaciones.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True),
        )

    async def reporte(self, update, context: ContextTypes.DEFAULT_TYPE):
        text = (
            "*Contactos de Soporte*\n\n"
            f"*CANTV*\n"
            f"Telefono: {CANTV_TELEFONO}\n"
            f"{CANTV_INFO}\n\n"
            f"*NetUno*\n"
            f"Telefono: {NETUNO_TELEFONO}"
        )
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True),
        )

    async def status(self, update, context: ContextTypes.DEFAULT_TYPE):
        if not self.state.monitors:
            status_text = "📡 *No hay datos de monitoreo todavia.*"
        else:
            lines = ["📡 *Estado de Enlaces*\n"]
            for ip, mon in self.state.monitors.items():
                status_emoji = "🟢" if not mon.is_alerting else "🔴"
                if mon.last_success:
                    last_ok = datetime.fromtimestamp(mon.last_success).strftime("%H:%M:%S")
                else:
                    last_ok = "Nunca"
                pct = (
                    (mon.successful_pings / mon.total_pings * 100)
                    if mon.total_pings > 0
                    else 0
                )
                lines.append(
                    f"{status_emoji} *{mon.name}* (`{ip}`)\n"
                    f"   Ultimo exito: {last_ok}\n"
                    f"   Fallos consecutivos: {mon.consecutive_failures}\n"
                    f"   Total historico: {mon.successful_pings}/{mon.total_pings} ({pct:.0f}%)"
                )
            status_text = "\n\n".join(lines)

        await update.message.reply_text(
            status_text, parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True),
        )

        web_enlaces = [
            (ENLACE_1_NOMBRE, ENLACE_1_WEB_URL),
            (ENLACE_2_NOMBRE, ENLACE_2_WEB_URL),
        ]
        for nombre, web_url in web_enlaces:
            if not web_url:
                continue
            try:
                img_bytes = await capture_image(web_url, IMAGE_SELECTOR)
            except Exception as e:
                logger.warning("Error capturando imagen de %s: %s", nombre, e)
                img_bytes = None
            if img_bytes:
                await update.message.reply_photo(
                    photo=InputFile(img_bytes, filename=f"{nombre}.jpg"),
                    caption=f"📸 *{nombre}*",
                    parse_mode="Markdown",
                )

    async def alert_all(self, message: str):
        if not self.application:
            return
        bot = self.application.bot
        for chat_id in self.state.subscribers:
            try:
                await bot.send_message(
                    chat_id=chat_id, text=message, parse_mode="Markdown"
                )
            except Exception as e:
                logger.error("Error enviando alerta a chat %s: %s", chat_id, e)

    async def broadcast_image(self, image_bytes: bytes, caption: str = "", filename: str = "enlace.jpg"):
        if not self.application:
            return
        bot = self.application.bot
        for chat_id in self.state.subscribers:
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=InputFile(image_bytes, filename=filename),
                    caption=caption,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("Error enviando imagen a chat %s: %s", chat_id, e)

    def build_app(self) -> Application:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("subscribe", self.subscribe))
        app.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("reporte", self.reporte))
        app.add_handler(CommandHandler("help", self.start))
        self.application = app
        return app
