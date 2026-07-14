from zoneinfo import ZoneInfo
from datetime import datetime

TZ = ZoneInfo("America/Caracas")


def is_dnd() -> bool:
    now = datetime.now(TZ)
    return now.hour >= 22 or now.hour < 7


def time_str() -> str:
    return datetime.now(TZ).strftime("%H:%M")
