"""
anti_cheat.py — Anti-cheat mechanics for LevelUp CLI v2.0

Prevents XP farming via:
- 10-minute cooldown between manual task completions
- 500 XP daily cap from manual tasks (Pomodoros bypass this)
"""

from datetime import datetime

COOLDOWN_SECONDS = 600       # 10 minutes
DAILY_TASK_XP_CAP = 500      # Max XP from manual tasks per day


def check_cooldown(data: dict) -> tuple[bool, int]:
    """
    Check if the user can complete a task (10-min cooldown).
    Returns (allowed, wait_seconds_remaining).
    """
    last_time_str = data["user"].get("last_task_complete_time")
    if last_time_str is None:
        return True, 0

    last_time = datetime.fromisoformat(last_time_str)
    elapsed = (datetime.now() - last_time).total_seconds()
    remaining = COOLDOWN_SECONDS - elapsed

    if remaining <= 0:
        return True, 0
    return False, int(remaining)


def check_daily_cap(data: dict) -> tuple[bool, int]:
    """
    Check if the daily XP cap for manual tasks has been reached.
    Returns (within_cap, remaining_xp_budget).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if data["user"].get("xp_today_date") != today:
        # New day, full budget
        return True, DAILY_TASK_XP_CAP

    used = data["user"].get("xp_today", 0)
    remaining = DAILY_TASK_XP_CAP - used

    if remaining <= 0:
        return False, 0
    return True, remaining


def record_task_complete(data: dict) -> None:
    """Stamp the last task completion time for cooldown tracking."""
    data["user"]["last_task_complete_time"] = datetime.now().isoformat()
