"""
visuals.py — All Rich display functions and ASCII art for LevelUp CLI v2.0

Centralized visual output: panels, animations, tables, and art constants.
"""

import os
import random
from datetime import datetime, timedelta

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

# ── Color Palette ────────────────────────────────────────

C_PRIMARY = "bold cyan"
C_SECONDARY = "bold magenta"
C_SUCCESS = "bold green"
C_WARNING = "bold yellow"
C_ACCENT = "bold bright_blue"
C_XP = "bold bright_yellow"
C_LEVEL = "bold bright_magenta"
C_DANGER = "bold bright_red"

# ── ASCII Art ────────────────────────────────────────────

WELCOME_ART = r"""
    ██╗     ███████╗██╗   ██╗███████╗██╗     ██╗   ██╗██████╗ 
    ██║     ██╔════╝██║   ██║██╔════╝██║     ██║   ██║██╔══██╗
    ██║     █████╗  ██║   ██║█████╗  ██║     ██║   ██║██████╔╝
    ██║     ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██╔═══╝ 
    ███████╗███████╗ ╚████╔╝ ███████╗███████╗╚██████╔╝██║     
    ╚══════╝╚══════╝  ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝     
"""

LEVEL_UP_ART = r"""
    ╦  ╔═╗╦  ╦╔═╗╦      ╦ ╦╔═╗ ╦
    ║  ║╣ ╚╗╔╝║╣ ║      ║ ║╠═╝ ║
    ╩═╝╚═╝ ╚╝ ╚═╝╩═╝    ╚═╝╩   o
"""

LEVEL_DOWN_ART = r"""
    ╦  ╔═╗╦  ╦╔═╗╦      ╔╦╗╔═╗╦ ╦╔╗╔
    ║  ║╣ ╚╗╔╝║╣ ║       ║║║ ║║║║║║║
    ╩═╝╚═╝ ╚╝ ╚═╝╩═╝    ═╩╝╚═╝╚╩╝╝╚╝
"""

SESSION_COMPLETE_ART = r"""
    ╔═╗╔═╗╔═╗╔═╗╦╔═╗╔╗╔
    ╚═╗║╣ ╚═╗╚═╗║║ ║║║║
    ╚═╝╚═╝╚═╝╚═╝╩╚═╝╝╚╝
     ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╔╦╗╔═╗
     ║  ║ ║║║║╠═╝║  ║╣  ║ ║╣ 
     ╚═╝╚═╝╩ ╩╩  ╩═╝╚═╝ ╩ ╚═╝
"""

COFFEE_ART = r"""
        ( (
         ) )
      ._______.
      |       |]
      \       /
       `-----'
    ☕ Fresh brew!
"""

LOOT_BOX_ART = r"""
     ╔═══════════╗
     ║  🎁 LOOT  ║
     ║    BOX    ║
     ║   ????    ║
     ╚═══════════╝
"""


# ── Display Functions ────────────────────────────────────

def show_level_up(level: int) -> None:
    """Display a flashy LEVEL UP animation."""
    os.system("cls" if os.name == "nt" else "clear")
    confetti = "🎉 🎊 ✨ 🌟 💫 🎆 🎇 🥳 🎯 ⭐"
    confetti_line = " ".join(random.choices(confetti.split(), k=12))

    content = Text()
    content.append(f"\n{confetti_line}\n", style="bright_yellow")
    content.append(LEVEL_UP_ART, style="bold bright_yellow")
    content.append(f"\n⚡ You are now LEVEL {level} ⚡\n", style="bold bright_magenta")
    content.append(f"{confetti_line}\n", style="bright_cyan")

    panel = Panel(
        Align.center(content),
        title="[bold bright_yellow]🏆 CONGRATULATIONS 🏆[/]",
        subtitle="[bold bright_cyan]Keep grinding, champion![/]",
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


def show_level_down(level: int) -> None:
    """Display a LEVEL DOWN warning."""
    content = Text()
    content.append(LEVEL_DOWN_ART, style="bold bright_red")
    content.append(f"\n💀 You dropped to LEVEL {level} 💀\n", style="bold bright_red")
    content.append("Complete your pending tasks to recover HP!\n", style="dim")

    panel = Panel(
        Align.center(content),
        title="[bold bright_red]⚠️  LEVEL DOWN ⚠️[/]",
        border_style="bright_red",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


def show_new_badges(badges: list[str]) -> None:
    """Display newly unlocked badges."""
    if not badges:
        return
    badge_text = "\n".join(f"  {b}" for b in badges)
    panel = Panel(
        f"[bold bright_cyan]New Badge{'s' if len(badges) > 1 else ''} Unlocked![/]\n\n{badge_text}",
        title="[bold bright_yellow]🎖️  ACHIEVEMENT UNLOCKED  🎖️[/]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 3),
    )
    console.print(panel)
    console.print()


def show_xp_gain(amount: int, reason: str, multiplier_info: str = "") -> None:
    """Display an XP gain notification."""
    extra = f"  [dim]({multiplier_info})[/]" if multiplier_info else ""
    panel = Panel(
        f"[{C_XP}]+{amount} XP[/]  ·  [dim]{reason}[/]{extra}",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)


def show_streak(streak: int, burned: bool) -> None:
    """Show streak info."""
    if burned:
        console.print(
            f"  [bold bright_red]🔥 Streak burned![/] [dim]You missed a day. Streak reset to 1.[/]"
        )
    elif streak >= 7:
        console.print(
            f"  [bold bright_yellow]🔥 {streak}-day streak![/] [bright_green]1.5x XP multiplier active![/]"
        )
    elif streak > 1:
        console.print(
            f"  [bold bright_yellow]🔥 {streak}-day streak![/] [dim]Reach 7 for 1.5x XP![/]"
        )


def show_hp_warning(hp: int, hp_lost: int, max_hp: int) -> None:
    """Show HP deduction warning."""
    bar_width = 20
    filled = int((hp / max_hp) * bar_width)
    empty = bar_width - filled
    color = "bright_green" if hp > 50 else "bright_yellow" if hp > 25 else "bright_red"
    hp_bar = f"[{color}]{'█' * filled}[/][bright_black]{'░' * empty}[/]"

    panel = Panel(
        f"[bold bright_red]❤️ -{hp_lost} HP[/]  [dim]Stale tasks detected![/]\n\n"
        f"  {hp_bar}  [dim]{hp}/{max_hp} HP[/]\n\n"
        f"  [dim]Complete or remove old tasks to protect your HP![/]",
        title="[bold bright_red]⚠️  HEALTH WARNING ⚠️[/]",
        border_style="bright_red",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_cooldown_error(wait_seconds: int) -> None:
    """Show cooldown rejection message."""
    mins, secs = divmod(wait_seconds, 60)
    panel = Panel(
        f"[bold bright_red]⏳ Anti-Cheat Cooldown Active[/]\n\n"
        f"  Wait [bold bright_yellow]{mins}m {secs}s[/] before completing another task.\n\n"
        f"  [dim]Use a Pomodoro session for bigger, cooldown-free XP![/]",
        title="[bold bright_red]🛑 COOLDOWN[/]",
        border_style="bright_red",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_daily_cap_reached() -> None:
    """Show daily XP cap reached message."""
    panel = Panel(
        f"[bold bright_yellow]📊 Daily Task XP Cap Reached![/]\n\n"
        f"  You've earned the maximum 500 XP from tasks today.\n"
        f"  Task marked as done but no XP awarded.\n\n"
        f"  [dim]Pomodoro sessions bypass this cap. Try:[/]\n"
        f"  [cyan]python levelup.py start[/]",
        title="[bold bright_yellow]⏳ DAILY LIMIT[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_loot_drop(loot: dict) -> None:
    """Display a loot drop event."""
    loot_text = Text()
    loot_text.append(LOOT_BOX_ART, style="bold bright_yellow")

    if loot["type"] == "boost":
        loot_text.append(
            f"\n  You found: {loot['name']}\n"
            f"  2x XP for {loot['duration_minutes']} minutes!\n",
            style="bright_green"
        )
    elif loot["type"] == "badge":
        loot_text.append(
            f"\n  You found: {loot['name']}\n"
            f"  Rarity: {loot['rarity']}\n",
            style="bright_magenta"
        )

    panel = Panel(
        Align.center(loot_text),
        title="[bold bright_yellow]🎁 LOOT DROP! 🎁[/]",
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    console.print()


def show_coffee_easter_egg() -> None:
    """Display the coffee easter egg."""
    coffee_text = Text()
    coffee_text.append(COFFEE_ART, style="bold bright_yellow")
    coffee_text.append("\n  A secret brew for a secret dev.\n", style="dim italic")
    coffee_text.append("  +5 hidden XP added. Shh... 🤫\n", style="bright_green")

    panel = Panel(
        Align.center(coffee_text),
        title="[bold bright_yellow]☕ SECRET COFFEE ☕[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    console.print()


def show_git_sync_results(commits: list[str], xp_earned: int) -> None:
    """Display git sync results in a table."""
    if not commits:
        panel = Panel(
            "[dim]No commits found today.[/]\n\n"
            "  [dim]Make some commits and run this again![/]",
            title="[bold bright_cyan]💻 GIT SYNC[/]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
        return

    table = Table(
        title="💻 Today's Commits",
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_magenta",
        title_style="bold bright_yellow",
        padding=(0, 1),
    )
    table.add_column("#", style="bold bright_yellow", justify="center", width=4)
    table.add_column("Commit", style="bright_white")

    for i, commit in enumerate(commits, 1):
        table.add_row(str(i), commit)

    console.print()
    console.print(table)
    console.print()

    panel = Panel(
        f"[{C_XP}]+{xp_earned} XP[/]  ·  [dim]{len(commits)} commit{'s' if len(commits) != 1 else ''} × 10 XP[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)
    console.print()


def show_leaderboard(entries: list[dict], player_name: str) -> None:
    """Display the global leaderboard."""
    table = Table(
        title="🌍 Global Leaderboard",
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_magenta",
        title_style="bold bright_yellow",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Rank", style="bold bright_yellow", justify="center", width=6)
    table.add_column("Player", style="bright_white", min_width=20)
    table.add_column("Level", style="bright_magenta", justify="center", width=8)
    table.add_column("XP", style="bright_yellow", justify="right", width=10)
    table.add_column("Guild", style="bright_cyan", justify="center", width=15)

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, entry in enumerate(entries, 1):
        rank = medals.get(i, f"#{i}")
        name = entry["name"]
        if name == player_name:
            name = f"[bold bright_green]► {name}[/]"
        guild = entry.get("guild") or "[dim]—[/]"
        table.add_row(str(rank), name, str(entry.get("level", 1)), f"{entry.get('xp', 0):,}", guild)

    console.print()
    console.print(table)
    console.print()


def show_guild_info(guild_name: str, members: list[dict], total_xp: int) -> None:
    """Display guild info panel."""
    table = Table(
        box=box.SIMPLE,
        border_style="bright_cyan",
        header_style="bold bright_magenta",
        padding=(0, 1),
    )
    table.add_column("Member", style="bright_white")
    table.add_column("Level", style="bright_magenta", justify="center")
    table.add_column("XP", style="bright_yellow", justify="right")

    for m in members:
        table.add_row(m["name"], str(m.get("level", 1)), f"{m.get('xp', 0):,}")

    header = (
        f"[bold bright_cyan]🛡️ {guild_name}[/]\n"
        f"[dim]Members:[/] [bright_white]{len(members)}[/]  "
        f"[dim]|[/]  [dim]Pooled XP:[/] [bright_yellow]{total_xp:,}[/]\n"
    )

    panel = Panel(
        Group(Text.from_markup(header), table),
        title="[bold bright_cyan]🛡️  GUILD HQ  🛡️[/]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_strict_mode_status(message: str, success: bool) -> None:
    """Show strict mode status."""
    style = "bright_green" if success else "bright_red"
    panel = Panel(
        f"[{style}]{message}[/]",
        title="[bold bright_red]🛑 STRICT MODE[/]",
        border_style=style,
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)
