import json
import os
import time
from typing import Dict, List

STATE_FILE = "state.json"


class MonitorState:
    def __init__(self, name: str, ip: str):
        self.name = name
        self.ip = ip
        self.consecutive_failures = 0
        self.last_success: float | None = None
        self.last_failure: float | None = None
        self.is_alerting = False
        self.total_pings = 0
        self.successful_pings = 0
        self.hourly_total = 0
        self.hourly_success = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ip": self.ip,
            "consecutive_failures": self.consecutive_failures,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "is_alerting": self.is_alerting,
            "total_pings": self.total_pings,
            "successful_pings": self.successful_pings,
            "hourly_total": self.hourly_total,
            "hourly_success": self.hourly_success,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MonitorState":
        m = cls(data["name"], data["ip"])
        m.consecutive_failures = data.get("consecutive_failures", 0)
        m.last_success = data.get("last_success")
        m.last_failure = data.get("last_failure")
        m.is_alerting = data.get("is_alerting", False)
        m.total_pings = data.get("total_pings", 0)
        m.successful_pings = data.get("successful_pings", 0)
        m.hourly_total = data.get("hourly_total", 0)
        m.hourly_success = data.get("hourly_success", 0)
        return m


class StateManager:
    def __init__(self, filepath: str = STATE_FILE, sync_dnd: bool = True):
        self.filepath = filepath
        self.subscribers: List[int] = []
        self.monitors: Dict[str, MonitorState] = {}
        self.dnd_active: bool = False
        existed = os.path.exists(filepath)
        self._load()
        if sync_dnd and not existed:
            from dnd import is_dnd
            self.dnd_active = is_dnd()
            self.save()

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            self.subscribers = data.get("subscribers", [])
            self.dnd_active = data.get("dnd_active", False)
            for key, val in data.get("monitors", {}).items():
                self.monitors[key] = MonitorState.from_dict(val)
        except (json.JSONDecodeError, KeyError):
            self.subscribers = []
            self.monitors = {}

    def save(self):
        data = {
            "subscribers": self.subscribers,
            "monitors": {k: v.to_dict() for k, v in self.monitors.items()},
            "dnd_active": self.dnd_active,
        }
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add_subscriber(self, chat_id: int):
        if chat_id not in self.subscribers:
            self.subscribers.append(chat_id)
            self.save()

    def remove_subscriber(self, chat_id: int):
        if chat_id in self.subscribers:
            self.subscribers.remove(chat_id)
            self.save()

    def get_monitor(self, ip: str) -> MonitorState:
        if ip not in self.monitors:
            self.monitors[ip] = MonitorState(ip, ip)
        return self.monitors[ip]

    def reset_hourly_stats(self):
        for m in self.monitors.values():
            m.hourly_total = 0
            m.hourly_success = 0
        self.save()
