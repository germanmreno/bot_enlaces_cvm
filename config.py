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
ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", "2"))
REPORT_INTERVAL = int(os.getenv("REPORT_INTERVAL", "3600"))
