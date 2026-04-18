"""
config.py — Configuration system for LevelUp CLI v2.0

Manages user preferences: Pomodoro duration, break times, themes,
blocked sites, pet species, and notification settings.
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".levelup"
CONFIG_FILE = CONFIG_DIR / "config.json"

# ── Theme Presets ────────────────────────────────────────

THEMES = {
    "default": {
        "accent": "bright_cyan",
        "border": "bright_cyan",
        "highlight": "bright_yellow",
        "success": "bright_green",
        "danger": "bright_red",
        "muted": "dim",
        "title": "bold bright_yellow",
    },
    "cyberpunk": {
        "accent": "bright_magenta",
        "border": "bright_magenta",
        "highlight": "bright_cyan",
        "success": "bright_green",
        "danger": "bright_red",
        "muted": "dim magenta",
        "title": "bold bright_magenta",
    },
    "forest": {
        "accent": "green",
        "border": "green",
        "highlight": "bright_yellow",
        "success": "bright_green",
        "danger": "bright_red",
        "muted": "dim green",
        "title": "bold bright_green",
    },
    "ocean": {
        "accent": "blue",
        "border": "bright_blue",
        "highlight": "bright_cyan",
        "success": "bright_green",
        "danger": "bright_red",
        "muted": "dim blue",
        "title": "bold bright_cyan",
    },
}


def _default_config() -> dict:
    """Return the default configuration."""
    return {
        "pomodoro_duration": 25,       # minutes
        "short_break": 5,              # minutes
        "long_break": 15,              # minutes
        "theme": "default",
        "pet_species": "dragon",
        "blocked_sites": [
            "twitter.com", "www.twitter.com",
            "x.com", "www.x.com",
            "youtube.com", "www.youtube.com",
            "facebook.com", "www.facebook.com",
            "reddit.com", "www.reddit.com",
            "instagram.com", "www.instagram.com",
            "tiktok.com", "www.tiktok.com",
        ],
        "notifications": True,
        "sound_enabled": True,
        "git_repos": ["."],
    }


def load_config() -> dict:
    """Load configuration, creating defaults if needed."""
    if not CONFIG_FILE.exists():
        config = _default_config()
        save_config(config)
        return config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # Forward-compatible: merge missing keys
        defaults = _default_config()
        for key, val in defaults.items():
            config.setdefault(key, val)
        return config
    except (json.JSONDecodeError, KeyError):
        config = _default_config()
        save_config(config)
        return config


def save_config(config: dict) -> None:
    """Persist configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_theme() -> dict:
    """Get the current theme colors."""
    config = load_config()
    theme_name = config.get("theme", "default")
    return THEMES.get(theme_name, THEMES["default"])


def reset_config() -> dict:
    """Reset config to defaults."""
    config = _default_config()
    save_config(config)
    return config
