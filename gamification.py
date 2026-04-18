"""
gamification.py — XP, Levels, Streaks, HP, Badges, Loot, and Challenges for LevelUp CLI v2.1

Core game mechanics engine: streak multipliers, daily XP caps,
health points with decay, badge awards, random loot drops,
daily/weekly challenges, and achievement progress tracking.
"""

import random
from datetime import datetime, timedelta


# ── Badge Definitions ────────────────────────────────────

BADGE_DEFS = [
    ("First Steps",      "🐣", "Complete your first task",          1,
     lambda d: sum(1 for t in d["tasks"] if t["status"] == "done") >= 1),
    ("Focused Mind",     "🧠", "Complete your first Pomodoro",      1,
     lambda d: d["user"].get("pomodoros", 0) >= 1),
    ("Task Slayer",      "⚔️", "Complete 5 tasks",                  5,
     lambda d: sum(1 for t in d["tasks"] if t["status"] == "done") >= 5),
    ("Deep Worker",      "🔥", "Complete 5 Pomodoros",              5,
     lambda d: d["user"].get("pomodoros", 0) >= 5),
    ("Level 5 Hero",     "🦸", "Reach Level 5",                     5,
     lambda d: d["user"]["level"] >= 5),
    ("Centurion",        "💯", "Earn 1000 XP total",                1000,
     lambda d: d["user"].get("total_xp", 0) >= 1000),
    ("Task Master",      "👑", "Complete 20 tasks",                 20,
     lambda d: sum(1 for t in d["tasks"] if t["status"] == "done") >= 20),
    ("Level 10 Legend",  "🏆", "Reach Level 10",                    10,
     lambda d: d["user"]["level"] >= 10),
    ("Marathon Runner",  "🏃", "Complete 25 Pomodoros",             25,
     lambda d: d["user"].get("pomodoros", 0) >= 25),
    ("Unstoppable",      "⚡", "Reach Level 20",                    20,
     lambda d: d["user"]["level"] >= 20),
    # v2.0 badges
    ("Streak Warrior",   "🔥", "Maintain a 7-day streak",          7,
     lambda d: d["user"].get("streak", 0) >= 7),
    ("Pet Parent",       "🐾", "Evolve your pet to stage 2",       2,
     lambda d: d["user"].get("pet_stage", 0) >= 2),
    ("Iron Will",        "🛡️", "Survive an HP warning",             1,
     lambda d: d["user"].get("hp", 100) < 100),
    ("Lucky Drop",       "🎁", "Receive your first loot drop",     1,
     lambda d: "Lucky Drop" in d["user"].get("badges", [])),  # awarded manually
]


def get_badge_progress(data: dict) -> list[dict]:
    """
    Return progress for each badge: {name, emoji, desc, current, target, unlocked}.
    Feature #9: Achievement progress bar.
    """
    existing = set(data["user"]["badges"])
    progress = []

    tasks_done = sum(1 for t in data["tasks"] if t["status"] == "done")
    pomodoros = data["user"].get("pomodoros", 0)
    level = data["user"]["level"]
    total_xp = data["user"].get("total_xp", 0)
    streak = data["user"].get("streak", 0)
    pet_stage = data["user"].get("pet_stage", 0)

    # Map badges to their current progress values
    progress_map = {
        "First Steps": tasks_done,
        "Task Slayer": tasks_done,
        "Task Master": tasks_done,
        "Focused Mind": pomodoros,
        "Deep Worker": pomodoros,
        "Marathon Runner": pomodoros,
        "Level 5 Hero": level,
        "Level 10 Legend": level,
        "Unstoppable": level,
        "Centurion": total_xp,
        "Streak Warrior": streak,
        "Pet Parent": pet_stage,
        "Iron Will": 1 if data["user"].get("hp", 100) < 100 else 0,
        "Lucky Drop": 1 if "Lucky Drop" in existing else 0,
    }

    for name, emoji, desc, target, condition in BADGE_DEFS:
        current = min(progress_map.get(name, 0), target)
        progress.append({
            "name": name,
            "emoji": emoji,
            "desc": desc,
            "current": current,
            "target": target,
            "unlocked": name in existing,
        })

    return progress


# ── XP & Leveling ────────────────────────────────────────

def xp_for_next_level(level: int) -> int:
    """XP required to reach the next level."""
    return level * 100


def get_streak_multiplier(data: dict) -> float:
    """Return XP multiplier based on streak. 1.5x at 7+ days."""
    streak = data["user"].get("streak", 0)
    return 1.5 if streak >= 7 else 1.0


def get_boost_multiplier(data: dict) -> float:
    """Return multiplier from active boosts (2x loot boost)."""
    boosts = data["user"].get("active_boosts", [])
    now = datetime.now()
    active = []
    multiplier = 1.0
    for boost in boosts:
        expires = datetime.fromisoformat(boost["expires_at"])
        if now < expires:
            active.append(boost)
            multiplier = max(multiplier, boost.get("multiplier", 1.0))
    data["user"]["active_boosts"] = active  # prune expired
    return multiplier


def add_xp(data: dict, base_amount: int, source: str = "task") -> tuple[int, bool]:
    """
    Add XP with multipliers applied. Returns (actual_xp_gained, leveled_up).
    source: 'task' (subject to daily cap) or 'pomodoro' (bypasses cap).
    """
    streak_mult = get_streak_multiplier(data)
    boost_mult = get_boost_multiplier(data)
    amount = int(base_amount * streak_mult * boost_mult)

    data["user"]["xp"] += amount
    data["user"]["total_xp"] += amount

    # Track daily XP for cap enforcement
    today = datetime.now().strftime("%Y-%m-%d")
    if data["user"].get("xp_today_date") != today:
        data["user"]["xp_today"] = 0
        data["user"]["xp_today_date"] = today
    if source == "task":
        data["user"]["xp_today"] += amount

    leveled_up = False
    while data["user"]["xp"] >= xp_for_next_level(data["user"]["level"]):
        data["user"]["xp"] -= xp_for_next_level(data["user"]["level"])
        data["user"]["level"] += 1
        leveled_up = True
        _update_pet_stage(data)

    return amount, leveled_up


def _update_pet_stage(data: dict) -> None:
    """Evolve the pet based on level thresholds."""
    level = data["user"]["level"]
    if level >= 20:
        data["user"]["pet_stage"] = 4
    elif level >= 10:
        data["user"]["pet_stage"] = 3
    elif level >= 5:
        data["user"]["pet_stage"] = 2
    elif level >= 2:
        data["user"]["pet_stage"] = 1
    else:
        data["user"]["pet_stage"] = 0


# ── Streaks ──────────────────────────────────────────────

def update_streak(data: dict) -> tuple[int, bool]:
    """Update the daily streak. Returns (current_streak, streak_just_burned)."""
    today = datetime.now().strftime("%Y-%m-%d")
    last = data["user"].get("last_active_date")

    burned = False
    if last is None:
        data["user"]["streak"] = 1
    elif last == today:
        pass
    else:
        last_date = datetime.strptime(last, "%Y-%m-%d").date()
        today_date = datetime.now().date()
        diff = (today_date - last_date).days
        if diff == 1:
            data["user"]["streak"] += 1
        elif diff > 1:
            burned = True
            data["user"]["streak"] = 1

    data["user"]["last_active_date"] = today
    return data["user"]["streak"], burned


# ── Health Points ────────────────────────────────────────

def check_hp(data: dict) -> tuple[int, bool]:
    """Check for stale tasks (pending > 3 days) and deduct HP."""
    now = datetime.now()
    hp_lost = 0
    for task in data["tasks"]:
        if task["status"] == "pending":
            created = datetime.fromisoformat(task["created_at"])
            days_old = (now - created).days
            if days_old > 3:
                hp_lost += 5

    if hp_lost > 0:
        data["user"]["hp"] = max(0, data["user"]["hp"] - hp_lost)

    leveled_down = False
    if data["user"]["hp"] <= 0 and data["user"]["level"] > 1:
        data["user"]["level"] -= 1
        data["user"]["hp"] = data["user"]["max_hp"]
        _update_pet_stage(data)
        leveled_down = True

    return hp_lost, leveled_down


# ── Badges ───────────────────────────────────────────────

def check_and_award_badges(data: dict) -> list[str]:
    """Check badge conditions and award new badges. Returns list of newly awarded."""
    new_badges = []
    existing = set(data["user"]["badges"])
    for name, emoji, desc, target, condition in BADGE_DEFS:
        if name == "Lucky Drop":
            continue
        if name not in existing and condition(data):
            data["user"]["badges"].append(name)
            new_badges.append(f"{emoji} {name}")
    return new_badges


# ── Loot Drops ───────────────────────────────────────────

LOOT_TABLE = [
    {"type": "boost", "name": "⚡ Double XP", "multiplier": 2.0, "duration_minutes": 60},
    {"type": "badge", "name": "🌈 Rainbow Coder", "rarity": "Rare"},
    {"type": "badge", "name": "💎 Diamond Focus", "rarity": "Epic"},
    {"type": "boost", "name": "🚀 Turbo Mode", "multiplier": 2.0, "duration_minutes": 30},
]

# Feature #16: Boss-specific loot table
BOSS_LOOT_TABLE = [
    {"type": "badge", "name": "🐉 Dragon Slayer", "rarity": "Legendary"},
    {"type": "badge", "name": "⚔️ Boss Crusher", "rarity": "Epic"},
    {"type": "badge", "name": "🏰 Dungeon Master", "rarity": "Legendary"},
    {"type": "boost", "name": "🔮 Boss Power", "multiplier": 3.0, "duration_minutes": 120},
    {"type": "badge", "name": "💀 Death Defier", "rarity": "Epic"},
    {"type": "boost", "name": "👑 Royal Decree", "multiplier": 2.0, "duration_minutes": 180},
]


def roll_loot(data: dict) -> dict | None:
    """10% chance to drop loot after a Pomodoro."""
    if random.random() > 0.10:
        return None
    loot = random.choice(LOOT_TABLE)
    _apply_loot(data, loot)
    if "Lucky Drop" not in data["user"]["badges"]:
        data["user"]["badges"].append("Lucky Drop")
    return loot


def roll_boss_loot(data: dict) -> dict:
    """Roll a guaranteed loot drop when a boss is defeated."""
    loot = random.choice(BOSS_LOOT_TABLE)
    _apply_loot(data, loot)
    return loot


def _apply_loot(data: dict, loot: dict) -> None:
    """Apply a loot item to the user's data."""
    if loot["type"] == "boost":
        expires = datetime.now() + timedelta(minutes=loot["duration_minutes"])
        data["user"]["active_boosts"].append({
            "name": loot["name"],
            "multiplier": loot["multiplier"],
            "expires_at": expires.isoformat(),
        })
    elif loot["type"] == "badge":
        if loot["name"] not in data["user"]["badges"]:
            data["user"]["badges"].append(loot["name"])


# ── Daily / Weekly Challenges (Feature #10) ──────────────

DAILY_CHALLENGES = [
    {"id": "pomo3", "desc": "Complete 3 Pomodoros today", "target": 3, "type": "pomodoro", "xp": 50},
    {"id": "task3", "desc": "Complete 3 tasks today", "target": 3, "type": "task", "xp": 30},
    {"id": "pomo5", "desc": "Complete 5 Pomodoros today", "target": 5, "type": "pomodoro", "xp": 100},
    {"id": "task5", "desc": "Complete 5 tasks today", "target": 5, "type": "task", "xp": 75},
    {"id": "pomo1", "desc": "Focus for at least 1 Pomodoro", "target": 1, "type": "pomodoro", "xp": 20},
    {"id": "streak3", "desc": "Maintain a 3-day streak", "target": 3, "type": "streak", "xp": 40},
]

WEEKLY_CHALLENGES = [
    {"id": "pomo15", "desc": "Complete 15 Pomodoros this week", "target": 15, "type": "pomodoro", "xp": 200},
    {"id": "task10", "desc": "Complete 10 tasks this week", "target": 10, "type": "task", "xp": 150},
    {"id": "streak7", "desc": "Reach a 7-day streak", "target": 7, "type": "streak", "xp": 300},
    {"id": "pomo25", "desc": "Complete 25 Pomodoros this week", "target": 25, "type": "pomodoro", "xp": 500},
]


def get_or_assign_challenge(data: dict) -> dict:
    """Get today's daily challenge, assigning a new one if needed."""
    today = datetime.now().strftime("%Y-%m-%d")
    if data["user"].get("daily_challenge_date") != today or not data["user"].get("daily_challenge"):
        challenge = random.choice(DAILY_CHALLENGES).copy()
        challenge["progress"] = 0
        challenge["completed"] = False
        data["user"]["daily_challenge"] = challenge
        data["user"]["daily_challenge_date"] = today
    return data["user"]["daily_challenge"]


def get_or_assign_weekly(data: dict) -> dict:
    """Get the current weekly challenge, assigning if needed."""
    today = datetime.now()
    # Week starts on Monday
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    if data["user"].get("weekly_challenge_date") != week_start or not data["user"].get("weekly_challenge"):
        challenge = random.choice(WEEKLY_CHALLENGES).copy()
        challenge["progress"] = 0
        challenge["completed"] = False
        data["user"]["weekly_challenge"] = challenge
        data["user"]["weekly_challenge_date"] = week_start
    return data["user"]["weekly_challenge"]


def update_challenge_progress(data: dict, event_type: str, count: int = 1) -> list[str]:
    """
    Update challenge progress. event_type: 'pomodoro', 'task', 'streak'.
    Returns list of completion messages.
    """
    messages = []

    daily = get_or_assign_challenge(data)
    if not daily.get("completed") and daily["type"] == event_type:
        daily["progress"] = min(daily["progress"] + count, daily["target"])
        if daily["progress"] >= daily["target"]:
            daily["completed"] = True
            messages.append(f"🎯 Daily Challenge Complete! +{daily['xp']} XP: {daily['desc']}")
            data["user"]["xp"] += daily["xp"]
            data["user"]["total_xp"] += daily["xp"]

    weekly = get_or_assign_weekly(data)
    if not weekly.get("completed") and weekly["type"] == event_type:
        weekly["progress"] = min(weekly["progress"] + count, weekly["target"])
        if weekly["progress"] >= weekly["target"]:
            weekly["completed"] = True
            messages.append(f"🏆 Weekly Challenge Complete! +{weekly['xp']} XP: {weekly['desc']}")
            data["user"]["xp"] += weekly["xp"]
            data["user"]["total_xp"] += weekly["xp"]

    return messages
