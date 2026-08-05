"""Persistent configuration for Logitech Light Manager."""

from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "logitech-light-manager"
CONFIG_FILE = CONFIG_DIR / "settings.json"
LOCK_FILE = CONFIG_DIR / "hardware.lock"

DEFAULTS = {
    "keyboard": {"enabled": True, "zones": ["#00AEEF"] * 5},
    "headset": {
        "enabled": True,
        "sync": True,
        "bottom": "#00AEEF",
        "top": "#00AEEF",
        "brightness": 100,
    },
}


def load_settings() -> dict:
    if not CONFIG_FILE.exists():
        return json.loads(json.dumps(DEFAULTS))
    try:
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULTS))
    result = json.loads(json.dumps(DEFAULTS))
    for device in ("keyboard", "headset"):
        if isinstance(saved.get(device), dict):
            result[device].update(saved[device])
    return result


def save_settings(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG_FILE)


@contextmanager
def hardware_lock():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
