import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ENLACE_1_IP = os.getenv("ENLACE_1_IP", "")
ENLACE_1_NOMBRE = os.getenv("ENLACE_1_NOMBRE", "Enlace 1")
ENLACE_1_WEB_URL = os.getenv("ENLACE_1_WEB_URL", "")
ENLACE_2_IP = os.getenv("ENLACE_2_IP", "")
ENLACE_2_NOMBRE = os.getenv("ENLACE_2_NOMBRE", "Enlace 2")
ENLACE_2_WEB_URL = os.getenv("ENLACE_2_WEB_URL", "")
IMAGE_SELECTOR = os.getenv("IMAGE_SELECTOR", "img[alt='Daily Graph']")
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "60"))
PING_TIMEOUT = int(os.getenv("PING_TIMEOUT", "5"))
RETRY_DELAY = 10
REPORT_INTERVAL = int(os.getenv("REPORT_INTERVAL", "3600"))

CANTV_TELEFONO = "0800-4378466"
CANTV_INFO = (
    "Corporacion Venezolana de Mineria RIF: G200124725\n"
    "GPON CANTV ABA ULTRA DEDICADO 200 MBPS.\n"
    "Circuito: 2319-0175535. VLAN 2720."
)
NETUNO_TELEFONO = "0212-7720010"
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))
