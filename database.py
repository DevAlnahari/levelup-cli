"""
database.py — Data persistence layer for LevelUp CLI v2.0

Handles loading, saving, migration, and schema defaults for ~/.levelup/data.json.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

DATA_DIR = Path.home() / ".levelup"
DATA_FILE = DATA_DIR / "data.json"


def _default_data() -> dict:
    """Return the default data structure for a fresh user."""
    return {
        "user": {
            "name": "Player",
            "xp": 0,
            "total_xp": 0,
            "level": 1,
            "badges": [],
            "pomodoros": 0,
            "created_at": datetime.now().isoformat(),
            # v2.0 fields
            "hp": 100,
            "max_hp": 100,
            "streak": 0,
            "last_active_date": None,
            "xp_today": 0,
            "xp_today_date": None,
            "last_task_complete_time": None,
            "active_boosts": [],
            "pet_stage": 0,
            "pet_sick": False,
            # v2.1 fields
            "pet_name": None,
            "pet_species": "dragon",
            "pet_hunger": 100,
            "daily_challenge": None,
            "daily_challenge_date": None,
            "weekly_challenge": None,
            "weekly_challenge_date": None,
            "xp_history": [],  # [{"date": "2026-04-18", "xp": 150}, ...]
            "pomodoro_history": [],  # [{"date": "2026-04-18", "count": 3}, ...]
        },
        "tasks": [],
        "active_boss": {
            "name": None,
            "max_hp": 1000,
            "current_hp": 1000,
            "is_active": False,
        },
    }


def load_data() -> dict:
    """Load user data from disk, creating defaults if needed."""
    if not DATA_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = _default_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Forward-compatible migration: ensure all keys exist
        defaults = _default_data()
        for key, val in defaults["user"].items():
            data["user"].setdefault(key, val)
        if "tasks" not in data:
            data["tasks"] = []
        if "active_boss" not in data:
            data["active_boss"] = defaults["active_boss"]
        return data
    except (json.JSONDecodeError, KeyError):
        data = _default_data()
        save_data(data)
        return data


def save_data(data: dict) -> None:
    """Persist user data to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_data(export_path: str) -> str:
    """Export data.json to a backup file. Returns the path."""
    if not DATA_FILE.exists():
        return ""
    dest = Path(export_path)
    shutil.copy2(DATA_FILE, dest)
    return str(dest.resolve())


def import_data(import_path: str) -> bool:
    """Import a data.json backup. Returns True if successful."""
    src = Path(import_path)
    if not src.exists():
        return False
    try:
        with open(src, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate it's a LevelUp data file
        if "user" not in data or "tasks" not in data:
            return False
        save_data(data)
        return True
    except (json.JSONDecodeError, KeyError):
        return False


def record_xp_history(data: dict, xp_earned: int) -> None:
    """Record daily XP for statistics tracking."""
    today = datetime.now().strftime("%Y-%m-%d")
    history = data["user"].get("xp_history", [])
    if history and history[-1]["date"] == today:
        history[-1]["xp"] += xp_earned
    else:
        history.append({"date": today, "xp": xp_earned})
    # Keep last 90 days
    data["user"]["xp_history"] = history[-90:]


def record_pomodoro_history(data: dict) -> None:
    """Record daily Pomodoro count for statistics."""
    today = datetime.now().strftime("%Y-%m-%d")
    history = data["user"].get("pomodoro_history", [])
    if history and history[-1]["date"] == today:
        history[-1]["count"] += 1
    else:
        history.append({"date": today, "count": 1})
    data["user"]["pomodoro_history"] = history[-90:]
