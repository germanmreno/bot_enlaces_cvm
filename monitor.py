import asyncio
import subprocess
import platform
import time

from config import PING_TIMEOUT, ALERT_THRESHOLD
from state import StateManager, MonitorState


async def ping(ip: str, timeout: int = PING_TIMEOUT) -> bool:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout), ip]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return_code = await proc.wait()
        return return_code == 0
    except (FileNotFoundError, asyncio.TimeoutError):
        return False


async def check_enlace(
    ip: str, state: MonitorState, state_manager: StateManager
) -> str | None:
    ok = await ping(ip)
    now = time.time()

    state.total_pings += 1
    state.hourly_total += 1

    if ok:
        state.successful_pings += 1
        state.hourly_success += 1
        state.consecutive_failures = 0
        state.last_success = now

        if state.is_alerting:
            state.is_alerting = False
            state_manager.save()
            return (
                f"✅ *{state.name}* RECUPERADO\n"
                f"IP: `{ip}`\n"
                f"El enlace vuelve a responder."
            )
    else:
        state.consecutive_failures += 1
        state.last_failure = now

        if state.consecutive_failures >= ALERT_THRESHOLD and not state.is_alerting:
            state.is_alerting = True
            state_manager.save()
            return (
                f"🚨 *CAÍDA DETECTADA* 🚨\n"
                f"Enlace: *{state.name}*\n"
                f"IP: `{ip}`\n"
                f"Fallos consecutivos: {state.consecutive_failures}\n"
                f"¡Posible corte de fibra!"
            )

    state_manager.save()
    return None
