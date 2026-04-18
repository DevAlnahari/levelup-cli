"""
git_sync.py — Git integration for LevelUp CLI v2.1

Scans multiple local Git repositories for today's commits and awards XP.
Multi-repo paths configured via config.json.
"""

import subprocess
from datetime import datetime

from config import load_config


def scan_today_commits(repo_path: str = ".") -> list[str]:
    """Scan a Git repo for commits made today. Returns list of commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=midnight", "--oneline", "--no-merges"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        return lines
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def scan_all_repos() -> dict[str, list[str]]:
    """
    Scan all configured repositories for today's commits.
    Returns {repo_path: [commit_messages]}.
    """
    config = load_config()
    repos = config.get("git_repos", ["."])
    results = {}
    for repo in repos:
        commits = scan_today_commits(repo)
        if commits:
            results[repo] = commits
    return results


def get_git_user(repo_path: str = ".") -> str | None:
    """Get the configured Git username."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


XP_PER_COMMIT = 10
