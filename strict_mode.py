"""
strict_mode.py — Distraction blocker for LevelUp CLI v2.1

Blocks distracting sites using the system hosts file.
Now reads blocked sites from config.json (custom sites support).
"""

import os
import ctypes
from pathlib import Path

from config import load_config, save_config

BLOCK_MARKER = "# === LEVELUP STRICT MODE ==="

if os.name == "nt":
    HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
else:
    HOSTS_PATH = Path("/etc/hosts")


def is_admin() -> bool:
    """Check if running with admin/root privileges."""
    try:
        if os.name == "nt":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except (AttributeError, OSError):
        return False


def get_blocked_sites() -> list[str]:
    """Get blocked sites from config."""
    config = load_config()
    return config.get("blocked_sites", [])


def add_blocked_site(site: str) -> str:
    """Add a site to the blocked list. Returns message."""
    config = load_config()
    sites = config.get("blocked_sites", [])
    # Add both www and non-www
    base = site.replace("www.", "")
    new_sites = [base, f"www.{base}"]
    added = []
    for s in new_sites:
        if s not in sites:
            sites.append(s)
            added.append(s)
    config["blocked_sites"] = sites
    save_config(config)
    if added:
        return f"Added: {', '.join(added)}"
    return f"{site} is already blocked."


def remove_blocked_site(site: str) -> str:
    """Remove a site from the blocked list. Returns message."""
    config = load_config()
    sites = config.get("blocked_sites", [])
    base = site.replace("www.", "")
    to_remove = [base, f"www.{base}"]
    removed = []
    for s in to_remove:
        if s in sites:
            sites.remove(s)
            removed.append(s)
    config["blocked_sites"] = sites
    save_config(config)
    if removed:
        return f"Removed: {', '.join(removed)}"
    return f"{site} was not in the block list."


def block_sites() -> tuple[bool, str]:
    """Block distracting sites by modifying the hosts file."""
    if not is_admin():
        return False, "⚠  Strict Mode requires admin privileges. Run as Administrator."

    sites = get_blocked_sites()
    if not sites:
        return False, "No sites configured to block. Use: python levelup.py strict add <site>"

    try:
        content = HOSTS_PATH.read_text(encoding="utf-8")
        if BLOCK_MARKER in content:
            return True, "Strict Mode already active."

        block_lines = [f"\n{BLOCK_MARKER}"]
        for site in sites:
            block_lines.append(f"127.0.0.1  {site}")
        block_lines.append(f"{BLOCK_MARKER}\n")

        with open(HOSTS_PATH, "a", encoding="utf-8") as f:
            f.write("\n".join(block_lines))

        return True, f"🛑 Strict Mode ON — {len(sites)} sites blocked!"
    except PermissionError:
        return False, "⚠  Permission denied. Run as Administrator."
    except Exception as e:
        return False, f"⚠  Error: {e}"


def unblock_sites() -> tuple[bool, str]:
    """Remove the blocked sites from the hosts file."""
    if not is_admin():
        return False, "⚠  Cannot unblock without admin privileges."

    try:
        content = HOSTS_PATH.read_text(encoding="utf-8")
        if BLOCK_MARKER not in content:
            return True, "No blocks to remove."

        lines = content.split("\n")
        new_lines = []
        inside_block = False
        for line in lines:
            if BLOCK_MARKER in line:
                inside_block = not inside_block
                continue
            if not inside_block:
                new_lines.append(line)

        HOSTS_PATH.write_text("\n".join(new_lines), encoding="utf-8")
        return True, "✅ Strict Mode OFF — Sites unblocked."
    except PermissionError:
        return False, "⚠  Permission denied. Run as Administrator."
    except Exception as e:
        return False, f"⚠  Error: {e}"
