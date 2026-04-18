#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🎮  LevelUp CLI v2.1 — Gamified Productivity for Devs ║
╠══════════════════════════════════════════════════════════╣
║  Pomodoro + Tasks + XP + Pets + Boss Fights + Challenges ║
╚══════════════════════════════════════════════════════════╝

Dependencies: pip install typer rich
Optional:     pip install playsound (audio) / plyer (notifications)
Usage:        python levelup.py --help
"""

import os
import time
import json
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from rich.progress import (
    Progress, BarColumn, TextColumn, TimeRemainingColumn,
    SpinnerColumn, TaskProgressColumn,
)

# ── Local Modules ────────────────────────────────────────

from database import (
    load_data, save_data, export_data, import_data,
    record_xp_history, record_pomodoro_history,
)
from gamification import (
    xp_for_next_level, add_xp, update_streak, check_hp,
    check_and_award_badges, roll_loot, roll_boss_loot, get_streak_multiplier,
    get_boost_multiplier, get_badge_progress, update_challenge_progress,
    get_or_assign_challenge, get_or_assign_weekly, BADGE_DEFS,
)
from pet import (
    get_pet_art, get_pet_name, check_pet_sickness, cure_pet,
    name_pet, feed_pet, switch_species, ALL_SPECIES, decay_hunger,
)
from anti_cheat import check_cooldown, check_daily_cap, record_task_complete
from git_sync import scan_today_commits, scan_all_repos, XP_PER_COMMIT
from strict_mode import block_sites, unblock_sites, add_blocked_site, remove_blocked_site
from audio import play_sound, generate_sounds
from config import load_config, save_config, reset_config, get_theme, THEMES
from visuals import (
    console, WELCOME_ART, SESSION_COMPLETE_ART,
    show_level_up, show_level_down, show_new_badges, show_xp_gain,
    show_streak, show_hp_warning, show_cooldown_error,
    show_daily_cap_reached, show_loot_drop, show_coffee_easter_egg,
    show_git_sync_results, show_strict_mode_status,
)
from boss import (
    spawn_boss, is_boss_active, animate_attack, animate_victory,
    show_boss_spawn, show_boss_status, ensure_boss_data,
    VICTORY_XP, DRAGON_SLAYER_BADGE,
)

# ── Constants ────────────────────────────────────────────

TASK_XP = 5
POMODORO_XP = 100

# ── Typer App ────────────────────────────────────────────

app = typer.Typer(
    name="levelup",
    help="🎮 LevelUp CLI v2.1 — Gamified Productivity for Developers",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
task_app = typer.Typer(name="task", help="📋 Tasks — add, list, complete, undo", rich_markup_mode="rich", no_args_is_help=True)
boss_app = typer.Typer(name="boss", help="👹 Boss Fights — epic battles", rich_markup_mode="rich", no_args_is_help=True)
pet_app = typer.Typer(name="pet", help="🐾 Pet — name, feed, switch species", rich_markup_mode="rich", no_args_is_help=True)
config_app = typer.Typer(name="config", help="⚙️ Settings — themes, intervals, sites", rich_markup_mode="rich", no_args_is_help=True)
data_app = typer.Typer(name="data", help="💾 Data — export and import backups", rich_markup_mode="rich", no_args_is_help=True)
strict_app = typer.Typer(name="strict", help="🛑 Strict Mode — manage blocked sites", rich_markup_mode="rich", no_args_is_help=True)

app.add_typer(task_app, name="task")
app.add_typer(boss_app, name="boss")
app.add_typer(pet_app, name="pet")
app.add_typer(config_app, name="config")
app.add_typer(data_app, name="data")
app.add_typer(strict_app, name="strict")


# ── Helper ───────────────────────────────────────────────

def _run_passive_checks(data: dict) -> None:
    """Run streak, HP, and pet sickness checks."""
    streak, burned = update_streak(data)
    show_streak(streak, burned)
    check_pet_sickness(data)
    decay_hunger(data)
    hp_lost, leveled_down = check_hp(data)
    if hp_lost > 0:
        show_hp_warning(data["user"]["hp"], hp_lost, data["user"]["max_hp"])
        play_sound("level_down")
    if leveled_down:
        show_level_down(data["user"]["level"])


def _send_notification(title: str, message: str) -> None:
    """Send desktop notification if enabled."""
    config = load_config()
    if not config.get("notifications", True):
        return
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=10)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════
# COMMANDS
# ══════════════════════════════════════════════════════════

@app.command()
def setup(name: str = typer.Argument(..., help="Your player name")):
    """🎮 Initialize your LevelUp profile with a player name."""
    data = load_data()
    data["user"]["name"] = name
    data["user"]["created_at"] = datetime.now().isoformat()
    save_data(data)

    # Generate sounds on first setup
    count = generate_sounds()

    art_text = Text(WELCOME_ART, style="bold cyan")
    welcome_msg = Text()
    welcome_msg.append_text(art_text)
    welcome_msg.append(f"\n  Welcome aboard, ", style="bright_white")
    welcome_msg.append(name, style="bold bright_magenta")
    welcome_msg.append("! 🚀\n\n", style="bright_white")
    welcome_msg.append("  Your quest for productivity begins now.\n", style="dim bright_white")
    welcome_msg.append("  Earn XP by completing tasks and focus sessions.\n", style="dim bright_white")
    welcome_msg.append("  Level up, unlock badges, and become legendary.\n", style="dim bright_white")

    tips = (
        "\n"
        "  [bold cyan]Quick Start:[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py task add \"Your first mission\"[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py start[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py profile[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py boss spawn[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py challenge[/]\n"
        "  [dim]•[/] [bright_white]python levelup.py stats[/]\n"
    )

    panel = Panel(
        Group(Align.center(welcome_msg), Text.from_markup(tips)),
        title="[bold bright_yellow]⚡ LEVELUP CLI v2.1 ⚡[/]",
        subtitle=f"[dim]v2.1 • {datetime.now().strftime('%Y-%m-%d')}[/]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    if count > 0:
        console.print(f"  [dim]🔊 Generated {count} sound effects[/]")
    console.print()


# ── Task Commands ────────────────────────────────────────

@task_app.command("add")
def task_add(title: str = typer.Argument(..., help="Title of the task")):
    """➕ Add a new task to your mission board."""
    data = load_data()
    _run_passive_checks(data)

    existing_ids = [t["id"] for t in data["tasks"]]
    new_id = max(existing_ids, default=0) + 1

    task = {
        "id": new_id,
        "title": title,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    data["tasks"].append(task)
    save_data(data)

    panel = Panel(
        f"[bold green]✅ Task #{new_id} added![/]\n\n"
        f"  [bright_white]{title}[/]\n\n"
        f"  [dim]Complete it with:[/] [cyan]python levelup.py task complete {new_id}[/]",
        title="[bold bright_green]📋 NEW MISSION[/]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


@task_app.command("list")
def task_list():
    """📋 Display all your tasks in a beautiful table."""
    data = load_data()
    _run_passive_checks(data)
    save_data(data)

    tasks = data["tasks"]
    if not tasks:
        panel = Panel(
            "[dim]No tasks yet. Add one with:[/]\n\n"
            "  [cyan]python levelup.py task add \"Your mission\"[/]",
            title="[bold bright_yellow]📋 MISSION BOARD[/]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
        return

    table = Table(
        title="🎯 Mission Board",
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_magenta",
        title_style="bold bright_yellow",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style="bold bright_yellow", justify="center", width=5)
    table.add_column("Mission", style="bright_white", min_width=30)
    table.add_column("Status", justify="center", width=14)
    table.add_column("Age", style="dim", justify="center", width=8)

    for t in tasks:
        task_id = str(t["id"])
        title = t["title"]
        created = datetime.fromisoformat(t.get("created_at", datetime.now().isoformat()))
        age_days = (datetime.now() - created).days
        age_str = f"{age_days}d" if age_days > 0 else "today"

        if t["status"] == "done":
            status = "[bold green]✅ Done[/]"
            title_display = f"[dim strikethrough]{title}[/]"
        else:
            if age_days > 3:
                status = "[bold red]⚠️ Stale[/]"
                title_display = f"[bright_red]{title}[/]"
            else:
                status = "[bold yellow]⏳ Pending[/]"
                title_display = f"[bright_white]{title}[/]"

        table.add_row(task_id, title_display, status, age_str)

    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "done")
    pending = total - done

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"  [dim]Total:[/] [bright_white]{total}[/]  "
        f"[dim]|[/]  [green]Done:[/] [bright_white]{done}[/]  "
        f"[dim]|[/]  [yellow]Pending:[/] [bright_white]{pending}[/]"
    )
    console.print()


@task_app.command("complete")
def task_complete(task_id: int = typer.Argument(..., help="ID of the task to complete")):
    """✅ Mark a task as complete and earn +5 XP (with anti-cheat)."""
    data = load_data()
    _run_passive_checks(data)

    target = None
    for t in data["tasks"]:
        if t["id"] == task_id:
            target = t
            break

    if target is None:
        console.print(f"\n[bold red]❌ Task #{task_id} not found![/]\n")
        raise typer.Exit(code=1)

    if target["status"] == "done":
        console.print(f"\n[bold yellow]⚠  Task #{task_id} is already complete.[/]\n")
        raise typer.Exit()

    allowed, wait = check_cooldown(data)
    if not allowed:
        show_cooldown_error(wait)
        save_data(data)
        raise typer.Exit()

    target["status"] = "done"
    target["completed_at"] = datetime.now().isoformat()
    record_task_complete(data)

    within_cap, _ = check_daily_cap(data)

    panel = Panel(
        f"[bold green]✅ Mission Complete![/]\n\n  [strikethrough dim]{target['title']}[/]\n",
        title=f"[bold bright_green]🎯 TASK #{task_id} CLEARED[/]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)

    if within_cap:
        actual_xp, leveled_up = add_xp(data, TASK_XP, source="task")
        record_xp_history(data, actual_xp)
        mult_info = ""
        if get_streak_multiplier(data) > 1:
            mult_info += "🔥 streak "
        if get_boost_multiplier(data) > 1:
            mult_info += "⚡ boost"
        show_xp_gain(actual_xp, "Task completed", mult_info.strip())
        play_sound("task_complete")
        if leveled_up:
            play_sound("level_up")
            show_level_up(data["user"]["level"])
    else:
        show_daily_cap_reached()

    # Challenge progress
    challenge_msgs = update_challenge_progress(data, "task")
    for msg in challenge_msgs:
        console.print(f"\n  {msg}")
        play_sound("challenge_complete")

    new_badges = check_and_award_badges(data)
    show_new_badges(new_badges)
    if new_badges:
        play_sound("badge")

    save_data(data)


@task_app.command("undo")
def task_undo(task_id: int = typer.Argument(..., help="ID of the task to undo")):
    """↩️ Undo a completed task (mark as pending again)."""
    data = load_data()

    target = None
    for t in data["tasks"]:
        if t["id"] == task_id:
            target = t
            break

    if target is None:
        console.print(f"\n[bold red]❌ Task #{task_id} not found![/]\n")
        raise typer.Exit(code=1)

    if target["status"] != "done":
        console.print(f"\n[bold yellow]⚠  Task #{task_id} is not completed yet.[/]\n")
        raise typer.Exit()

    target["status"] = "pending"
    target.pop("completed_at", None)
    save_data(data)

    panel = Panel(
        f"[bold yellow]↩️ Task #{task_id} reverted to pending[/]\n\n  [bright_white]{target['title']}[/]",
        title="[bold bright_yellow]↩️ TASK UNDONE[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


@task_app.command("remove")
def task_remove(task_id: int = typer.Argument(..., help="ID of the task to remove")):
    """🗑️ Remove a task from the mission board."""
    data = load_data()

    target = None
    for i, t in enumerate(data["tasks"]):
        if t["id"] == task_id:
            target = data["tasks"].pop(i)
            break

    if target is None:
        console.print(f"\n[bold red]❌ Task #{task_id} not found![/]\n")
        raise typer.Exit(code=1)

    save_data(data)

    panel = Panel(
        f"[bold red]🗑️ Task removed[/]\n\n  [dim strikethrough]{target['title']}[/]",
        title="[bold bright_red]🗑️ TASK REMOVED[/]",
        border_style="bright_red",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Pomodoro ─────────────────────────────────────────────

@app.command()
def start(
    duration: int = typer.Option(
        None, "--duration", "-d",
        help="Session duration in seconds (overrides config)",
        hidden=True,
    ),
    strict: bool = typer.Option(
        False, "--strict", "-s",
        help="🛑 Block distracting websites during the session",
    ),
):
    """🍅 Start a Pomodoro focus session (configurable, +100 XP)."""
    config = load_config()
    if duration is None:
        duration = config.get("pomodoro_duration", 25) * 60

    data = load_data()
    _run_passive_checks(data)
    save_data(data)

    player = data["user"]["name"]
    minutes = duration // 60
    seconds = duration % 60
    duration_str = f"{minutes}m {seconds}s" if seconds else f"{minutes}m"

    if strict:
        success, msg = block_sites()
        show_strict_mode_status(msg, success)
        if not success:
            console.print("[dim]Continuing without strict mode...[/]\n")

    mode_label = "[bold red]STRICT[/] " if strict else ""
    launch_text = (
        f"[bold bright_white]Player:[/] [bold bright_magenta]{player}[/]\n"
        f"[bold bright_white]Duration:[/] [bold bright_cyan]{duration_str}[/]\n"
        f"[bold bright_white]Mode:[/] {mode_label}[dim]Deep focus. No distractions.[/]\n\n"
        f"[dim italic]Press Ctrl+C to abort.[/]"
    )
    panel = Panel(
        launch_text,
        title="[bold bright_yellow]🍅 FOCUS SESSION STARTING[/]",
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    console.print()

    try:
        with Progress(
            SpinnerColumn("dots", style="bright_cyan"),
            TextColumn("[bold bright_white]{task.description}[/]"),
            BarColumn(
                bar_width=40, style="bright_black",
                complete_style="bright_cyan", finished_style="bright_green",
                pulse_style="bright_magenta",
            ),
            TaskProgressColumn(),
            TextColumn("[bold bright_yellow]{task.fields[timer]}[/]"),
            TimeRemainingColumn(),
            console=console, transient=False,
        ) as progress:
            task = progress.add_task("🔥 Focusing...", total=duration, timer="")
            for elapsed in range(duration):
                remaining = duration - elapsed
                mins, secs = divmod(remaining, 60)
                timer_str = f"⏱ {mins:02d}:{secs:02d}"
                progress.update(task, advance=1, timer=timer_str)
                pct = (elapsed / duration) * 100
                if pct >= 75:
                    progress.update(task, description="⚡ Almost there!")
                elif pct >= 50:
                    progress.update(task, description="🔥 Halfway through!")
                elif pct >= 25:
                    progress.update(task, description="💪 Keep going!")
                time.sleep(1)
            progress.update(task, description="[bold green]✅ Session Complete!", timer="⏱ 00:00")
    except KeyboardInterrupt:
        if strict:
            unblock_sites()
        console.print("\n[bold yellow]⚠  Session aborted. No XP awarded.[/]\n")
        raise typer.Exit()

    if strict:
        success, msg = unblock_sites()
        show_strict_mode_status(msg, success)

    data = load_data()
    data["user"]["pomodoros"] = data["user"].get("pomodoros", 0) + 1
    pet_cured = cure_pet(data)
    actual_xp, leveled_up = add_xp(data, POMODORO_XP, source="pomodoro")
    record_xp_history(data, actual_xp)
    record_pomodoro_history(data)
    new_badges = check_and_award_badges(data)
    loot = roll_loot(data)
    save_data(data)

    session_text = Text()
    session_text.append(SESSION_COMPLETE_ART, style="bold bright_green")
    session_text.append(f"\n  Great work, {player}! 💪\n", style="bright_white")
    session_text.append(f"  Pomodoro #{data['user']['pomodoros']} in the books.\n", style="dim")
    if pet_cured:
        session_text.append("  🐾 Your pet has been cured!\n", style="bright_green")

    panel = Panel(
        Align.center(session_text),
        title="[bold bright_green]🍅 SESSION COMPLETE 🍅[/]",
        border_style="bright_green",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    play_sound("pomodoro_done")

    mult_info = ""
    if get_streak_multiplier(data) > 1:
        mult_info += "🔥 streak "
    if get_boost_multiplier(data) > 1:
        mult_info += "⚡ boost"
    show_xp_gain(actual_xp, "Pomodoro completed", mult_info.strip())

    if leveled_up:
        play_sound("level_up")
        show_level_up(data["user"]["level"])

    show_new_badges(new_badges)
    if new_badges:
        play_sound("badge")

    if loot:
        play_sound("loot_drop")
        show_loot_drop(loot)

    # Challenge progress
    challenge_msgs = update_challenge_progress(data, "pomodoro")
    for msg in challenge_msgs:
        console.print(f"\n  {msg}")
        play_sound("challenge_complete")
    save_data(data)

    # Notification
    _send_notification("LevelUp CLI 🍅", f"Pomodoro #{data['user']['pomodoros']} complete! +{actual_xp} XP")

    # Break suggestion
    break_min = config.get("short_break", 5)
    if data["user"]["pomodoros"] % 4 == 0:
        break_min = config.get("long_break", 15)
        console.print(f"\n  [bold bright_yellow]☕ Time for a long break! ({break_min} min)[/]\n")
    else:
        console.print(f"\n  [dim]💤 Take a short break ({break_min} min)[/]\n")

    # Boss auto-attack
    data = load_data()
    if is_boss_active(data):
        defeated, dmg = animate_attack(data)
        if defeated:
            boss_name = data["active_boss"]["name"]
            animate_victory(boss_name)
            boss_loot = roll_boss_loot(data)
            victory_xp, victory_leveled = add_xp(data, VICTORY_XP, source="pomodoro")
            show_xp_gain(victory_xp, f"Defeated {boss_name}!")
            console.print(f"  [bold bright_yellow]🎁 Boss Loot: {boss_loot['name']}[/]\n")
            if victory_leveled:
                play_sound("level_up")
                show_level_up(data["user"]["level"])
        save_data(data)


# ── Profile ──────────────────────────────────────────────

@app.command()
def profile():
    """👤 Display your player profile — the bragging command!"""
    data = load_data()
    _run_passive_checks(data)
    save_data(data)

    user = data["user"]
    name = user["name"]
    level = user["level"]
    xp = user["xp"]
    total_xp = user.get("total_xp", 0)
    next_lvl_xp = xp_for_next_level(level)
    pomodoros = user.get("pomodoros", 0)
    badges = user.get("badges", [])
    hp = user.get("hp", 100)
    max_hp = user.get("max_hp", 100)
    streak = user.get("streak", 0)
    tasks_done = sum(1 for t in data["tasks"] if t["status"] == "done")
    tasks_pending = sum(1 for t in data["tasks"] if t["status"] == "pending")

    bar_w = 30
    filled = int((xp / next_lvl_xp) * bar_w) if next_lvl_xp > 0 else 0
    xp_bar = f"[bright_cyan]{'█' * filled}[/][bright_black]{'░' * (bar_w - filled)}[/]"

    hp_filled = int((hp / max_hp) * 20)
    hp_color = "bright_green" if hp > 50 else "bright_yellow" if hp > 25 else "bright_red"
    hp_bar = f"[{hp_color}]{'█' * hp_filled}[/][bright_black]{'░' * (20 - hp_filled)}[/]"

    streak_emoji = "🔥" if streak >= 7 else "📅"
    streak_mult = "1.5x" if streak >= 7 else "1.0x"

    pet_art = get_pet_art(data)
    pet_name = get_pet_name(data)
    pet_species = user.get("pet_species", "dragon").title()
    hunger = user.get("pet_hunger", 100)
    hunger_bar = f"{'🟢' if hunger > 60 else '🟡' if hunger > 30 else '🔴'} {hunger}%"

    lines = []
    lines.append(f"  [bold bright_magenta]🎮 {name}[/]")
    lines.append(f"  [bold bright_yellow]⭐ LEVEL {level}[/]")
    lines.append(f"  {xp_bar}  [dim]{xp}/{next_lvl_xp} XP[/]")
    lines.append("")
    lines.append(f"  [bright_red]❤️ HP[/]  {hp_bar}  [dim]{hp}/{max_hp}[/]")
    lines.append(f"  {streak_emoji} [bright_yellow]Streak:[/] [bright_white]{streak} day{'s' if streak != 1 else ''}[/]  [dim]({streak_mult} mult)[/]")
    lines.append("")
    lines.append(f"  [bright_cyan]📊 Stats[/]")
    lines.append(f"  [dim]Total XP:[/]      [bright_yellow]{total_xp:,}[/]")
    lines.append(f"  [dim]Pomodoros:[/]     [bright_cyan]{pomodoros}[/]")
    lines.append(f"  [dim]Tasks done:[/]   [bright_green]{tasks_done}[/]")
    lines.append(f"  [dim]Tasks pending:[/] [bright_yellow]{tasks_pending}[/]")
    lines.append("")

    lines.append(f"  [bright_cyan]🐾 Pet:[/] [bright_white]{pet_name}[/]  [dim]({pet_species})[/]")
    lines.append(f"  [dim]Hunger:[/] {hunger_bar}")
    lines.append("")

    if badges:
        lines.append(f"  [bright_cyan]🎖️  Badges ({len(badges)})[/]")
        for badge_name in badges:
            emoji = "🏅"
            for bname, bemoji, bdesc, _, _ in BADGE_DEFS:
                if bname == badge_name:
                    emoji = bemoji
                    break
            lines.append(f"  {emoji} [bright_white]{badge_name}[/]")
    else:
        lines.append(f"  [dim]🎖️  No badges yet — keep grinding![/]")

    boosts = user.get("active_boosts", [])
    if boosts:
        lines.append("")
        lines.append(f"  [bright_yellow]⚡ Active Boosts[/]")
        for b in boosts:
            lines.append(f"  {b['name']}  [dim](expires soon)[/]")

    profile_content = "\n".join(lines)

    panel = Panel(
        Group(Text.from_markup(profile_content), pet_art),
        title="[bold bright_yellow]⚡ PLAYER PROFILE ⚡[/]",
        subtitle=f"[dim]Since {user.get('created_at', 'N/A')[:10]}[/]",
        border_style="bright_magenta",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()

    import random
    quotes = [
        "The secret of getting ahead is getting started. — Mark Twain",
        "Focus is the new currency. Spend it wisely.",
        "Every level unlocked is proof you showed up.",
        "One Pomodoro at a time, one task at a time.",
        "Discipline beats motivation. Keep pushing!",
        "Your future self will thank you for this grind.",
    ]
    console.print(f"  [dim italic]💭 \"{random.choice(quotes)}\"[/]\n")


# ── Statistics Dashboard ─────────────────────────────────

@app.command()
def stats():
    """📊 View your productivity statistics and trends."""
    data = load_data()
    user = data["user"]

    xp_hist = user.get("xp_history", [])
    pomo_hist = user.get("pomodoro_history", [])

    # XP chart (last 7 days)
    console.print()
    console.print("  [bold bright_cyan]📈 XP Earned (Last 7 Days)[/]")
    console.print()

    last_7 = xp_hist[-7:] if xp_hist else []
    max_xp = max((h["xp"] for h in last_7), default=1)
    for day in last_7:
        bar_len = int((day["xp"] / max_xp) * 25) if max_xp > 0 else 0
        bar = "█" * bar_len
        label = day["date"][-5:]  # MM-DD
        console.print(f"  [dim]{label}[/]  [bright_cyan]{bar}[/] [bright_white]{day['xp']}[/]")

    if not last_7:
        console.print("  [dim]No XP data yet. Complete tasks or Pomodoros![/]")

    # Pomodoro chart (last 7 days)
    console.print()
    console.print("  [bold bright_green]🍅 Pomodoros (Last 7 Days)[/]")
    console.print()

    last_7p = pomo_hist[-7:] if pomo_hist else []
    max_p = max((h["count"] for h in last_7p), default=1)
    for day in last_7p:
        bar_len = int((day["count"] / max_p) * 25) if max_p > 0 else 0
        bar = "█" * bar_len
        label = day["date"][-5:]
        console.print(f"  [dim]{label}[/]  [bright_green]{bar}[/] [bright_white]{day['count']}[/]")

    if not last_7p:
        console.print("  [dim]No Pomodoro data yet. Start a session![/]")

    # Summary stats
    total_days = len(xp_hist) if xp_hist else 1
    total_xp = sum(h["xp"] for h in xp_hist)
    total_pomos = sum(h["count"] for h in pomo_hist)
    avg_xp = total_xp // total_days if total_days > 0 else 0
    avg_pomo = total_pomos / total_days if total_days > 0 else 0

    console.print()
    table = Table(title="📊 Summary", box=box.ROUNDED, border_style="bright_cyan")
    table.add_column("Metric", style="bright_white")
    table.add_column("Value", style="bright_yellow", justify="right")
    table.add_row("Total XP Earned", f"{user.get('total_xp', 0):,}")
    table.add_row("Avg XP/Day", f"{avg_xp:,}")
    table.add_row("Total Pomodoros", f"{user.get('pomodoros', 0)}")
    table.add_row("Avg Pomodoros/Day", f"{avg_pomo:.1f}")
    table.add_row("Current Streak", f"{user.get('streak', 0)} days")
    table.add_row("Badges Earned", f"{len(user.get('badges', []))}")
    table.add_row("Tasks Completed", f"{sum(1 for t in data['tasks'] if t['status'] == 'done')}")
    console.print(table)
    console.print()


# ── Challenges ───────────────────────────────────────────

@app.command()
def challenge():
    """🎯 View today's daily and weekly challenges."""
    data = load_data()
    daily = get_or_assign_challenge(data)
    weekly = get_or_assign_weekly(data)
    save_data(data)

    # Daily challenge
    d_prog = daily.get("progress", 0)
    d_target = daily.get("target", 1)
    d_done = daily.get("completed", False)
    d_bar_w = 20
    d_filled = int((d_prog / d_target) * d_bar_w) if d_target > 0 else 0
    d_bar = f"[bright_green]{'█' * d_filled}[/][bright_black]{'░' * (d_bar_w - d_filled)}[/]"
    d_status = "[bold bright_green]✅ COMPLETE![/]" if d_done else f"{d_bar} {d_prog}/{d_target}"

    # Weekly challenge
    w_prog = weekly.get("progress", 0)
    w_target = weekly.get("target", 1)
    w_done = weekly.get("completed", False)
    w_filled = int((w_prog / w_target) * d_bar_w) if w_target > 0 else 0
    w_bar = f"[bright_cyan]{'█' * w_filled}[/][bright_black]{'░' * (d_bar_w - w_filled)}[/]"
    w_status = "[bold bright_cyan]✅ COMPLETE![/]" if w_done else f"{w_bar} {w_prog}/{w_target}"

    content = (
        f"  [bold bright_yellow]📅 Daily Challenge[/]  [dim]+{daily.get('xp', 0)} XP[/]\n"
        f"  {daily.get('desc', '...')}\n"
        f"  {d_status}\n\n"
        f"  [bold bright_cyan]📆 Weekly Challenge[/]  [dim]+{weekly.get('xp', 0)} XP[/]\n"
        f"  {weekly.get('desc', '...')}\n"
        f"  {w_status}"
    )

    panel = Panel(
        content,
        title="[bold bright_yellow]🎯 CHALLENGES[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Achievements ─────────────────────────────────────────

@app.command()
def achievements():
    """🏆 View all badge progress with progress bars."""
    data = load_data()
    progress = get_badge_progress(data)

    table = Table(
        title="🏆 Achievement Progress",
        box=box.ROUNDED,
        border_style="bright_yellow",
        header_style="bold bright_magenta",
        show_lines=True,
    )
    table.add_column("Badge", style="bright_white", min_width=20)
    table.add_column("Progress", min_width=25)
    table.add_column("Status", justify="center", width=10)

    for p in progress:
        bar_w = 15
        filled = int((p["current"] / p["target"]) * bar_w) if p["target"] > 0 else 0
        bar = f"[bright_cyan]{'█' * filled}[/][bright_black]{'░' * (bar_w - filled)}[/]"
        status = "[bold bright_green]✅[/]" if p["unlocked"] else f"[dim]{p['current']}/{p['target']}[/]"
        name = f"{p['emoji']} {p['name']}"
        table.add_row(name, bar if not p["unlocked"] else "[bright_green]████████████████[/]", status)

    console.print()
    console.print(table)
    console.print()


# ── Git Sync ─────────────────────────────────────────────

@app.command("git-sync")
def git_sync(
    path: str = typer.Option(None, "--path", "-p", help="Path to a Git repository (or use config)"),
):
    """💻 Scan Git commits and earn XP for real work!"""
    data = load_data()
    _run_passive_checks(data)

    if path:
        # Single repo mode
        commits = scan_today_commits(path)
        all_commits = {path: commits} if commits else {}
    else:
        # Multi-repo mode from config
        all_commits = scan_all_repos()

    total_commits = sum(len(c) for c in all_commits.values())
    xp_earned = 0

    if total_commits > 0:
        total_commit_xp = total_commits * XP_PER_COMMIT
        actual_xp, leveled_up = add_xp(data, total_commit_xp, source="pomodoro")
        xp_earned = actual_xp
        record_xp_history(data, actual_xp)
        new_badges = check_and_award_badges(data)
        save_data(data)

        # Show results per repo
        flat_commits = []
        for repo, commits in all_commits.items():
            for c in commits:
                flat_commits.append(c)
        show_git_sync_results(flat_commits, xp_earned)

        if leveled_up:
            play_sound("level_up")
            show_level_up(data["user"]["level"])
        show_new_badges(new_badges)
    else:
        save_data(data)
        show_git_sync_results([], 0)


# ── Pet Commands ─────────────────────────────────────────

@pet_app.command("name")
def pet_name_cmd(new_name: str = typer.Argument(..., help="New name for your pet")):
    """✏️ Give your pet a custom name."""
    data = load_data()
    msg = name_pet(data, new_name)
    save_data(data)
    panel = Panel(
        f"[bold bright_green]{msg}[/]",
        title="[bold bright_cyan]🐾 PET RENAMED[/]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


@pet_app.command("feed")
def pet_feed_cmd():
    """🍖 Feed your pet to restore HP."""
    data = load_data()
    hp_gain, msg = feed_pet(data)
    save_data(data)
    play_sound("pet_feed")
    panel = Panel(
        f"[bold bright_green]{msg}[/]",
        title="[bold bright_green]🍖 PET FED[/]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


@pet_app.command("species")
def pet_species_cmd(
    species: str = typer.Argument(..., help="Species: dragon, phoenix, wolf, cat"),
):
    """🔄 Switch your pet's species."""
    data = load_data()
    success, msg = switch_species(data, species.lower())
    if success:
        save_data(data)
        pet_art = get_pet_art(data)
        panel = Panel(
            Group(Text(msg, style="bold bright_green"), pet_art),
            title="[bold bright_cyan]🔄 SPECIES CHANGED[/]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    else:
        panel = Panel(
            f"[bold red]{msg}[/]",
            title="[bold bright_red]❌ ERROR[/]",
            border_style="bright_red",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    console.print()
    console.print(panel)
    console.print()


# ── Config Commands ──────────────────────────────────────

@config_app.command("show")
def config_show():
    """📋 Display current configuration."""
    config = load_config()
    table = Table(title="⚙️ Configuration", box=box.ROUNDED, border_style="bright_cyan")
    table.add_column("Setting", style="bright_white")
    table.add_column("Value", style="bright_yellow")

    table.add_row("Pomodoro Duration", f"{config.get('pomodoro_duration', 25)} min")
    table.add_row("Short Break", f"{config.get('short_break', 5)} min")
    table.add_row("Long Break", f"{config.get('long_break', 15)} min")
    table.add_row("Theme", config.get("theme", "default"))
    table.add_row("Pet Species", config.get("pet_species", "dragon"))
    table.add_row("Notifications", "✅ On" if config.get("notifications", True) else "❌ Off")
    table.add_row("Sound", "✅ On" if config.get("sound_enabled", True) else "❌ Off")
    table.add_row("Git Repos", ", ".join(config.get("git_repos", ["."])))
    table.add_row("Blocked Sites", f"{len(config.get('blocked_sites', []))} sites")

    console.print()
    console.print(table)
    console.print()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Setting name"),
    value: str = typer.Argument(..., help="New value"),
):
    """✏️ Update a configuration setting."""
    config = load_config()
    valid_keys = {
        "pomodoro_duration": int,
        "short_break": int,
        "long_break": int,
        "theme": str,
        "pet_species": str,
        "notifications": bool,
        "sound_enabled": bool,
    }

    if key not in valid_keys:
        console.print(f"\n[bold red]❌ Unknown setting: {key}[/]")
        console.print(f"[dim]Valid settings: {', '.join(valid_keys.keys())}[/]\n")
        raise typer.Exit(code=1)

    cast = valid_keys[key]
    if cast == bool:
        config[key] = value.lower() in ("true", "1", "yes", "on")
    elif cast == int:
        config[key] = int(value)
    else:
        if key == "theme" and value not in THEMES:
            console.print(f"\n[bold red]❌ Unknown theme. Available: {', '.join(THEMES.keys())}[/]\n")
            raise typer.Exit(code=1)
        if key == "pet_species" and value not in ALL_SPECIES:
            console.print(f"\n[bold red]❌ Unknown species. Available: {', '.join(ALL_SPECIES.keys())}[/]\n")
            raise typer.Exit(code=1)
        config[key] = value

    save_config(config)
    console.print(f"\n  [bold bright_green]✅ {key} = {value}[/]\n")


@config_app.command("reset")
def config_reset_cmd():
    """🔄 Reset all settings to defaults."""
    reset_config()
    console.print("\n  [bold bright_green]✅ Configuration reset to defaults.[/]\n")


@config_app.command("repo-add")
def config_repo_add(path: str = typer.Argument(..., help="Path to Git repository")):
    """➕ Add a Git repository for multi-repo sync."""
    config = load_config()
    repos = config.get("git_repos", ["."])
    if path not in repos:
        repos.append(path)
        config["git_repos"] = repos
        save_config(config)
        console.print(f"\n  [bold bright_green]✅ Added repo: {path}[/]\n")
    else:
        console.print(f"\n  [bold yellow]⚠  {path} already in repos list.[/]\n")


@config_app.command("repo-remove")
def config_repo_remove(path: str = typer.Argument(..., help="Path to remove")):
    """➖ Remove a Git repository from sync."""
    config = load_config()
    repos = config.get("git_repos", ["."])
    if path in repos:
        repos.remove(path)
        config["git_repos"] = repos
        save_config(config)
        console.print(f"\n  [bold bright_green]✅ Removed repo: {path}[/]\n")
    else:
        console.print(f"\n  [bold yellow]⚠  {path} not in repos list.[/]\n")


# ── Strict Mode Commands ─────────────────────────────────

@strict_app.command("add")
def strict_add(site: str = typer.Argument(..., help="Site to block (e.g. discord.com)")):
    """➕ Add a site to the block list."""
    msg = add_blocked_site(site)
    console.print(f"\n  [bold bright_green]✅ {msg}[/]\n")


@strict_app.command("remove")
def strict_remove(site: str = typer.Argument(..., help="Site to unblock")):
    """➖ Remove a site from the block list."""
    msg = remove_blocked_site(site)
    console.print(f"\n  [bold bright_green]✅ {msg}[/]\n")


@strict_app.command("list")
def strict_list():
    """📋 Show all blocked sites."""
    from strict_mode import get_blocked_sites
    sites = get_blocked_sites()
    if not sites:
        console.print("\n  [dim]No blocked sites configured.[/]\n")
        return
    console.print("\n  [bold bright_red]🛑 Blocked Sites[/]")
    for s in sites:
        console.print(f"  [dim]•[/] {s}")
    console.print()


# ── Data Commands ────────────────────────────────────────

@data_app.command("export")
def data_export(
    path: str = typer.Argument("levelup_backup.json", help="Export file path"),
):
    """💾 Export your data to a backup file."""
    result = export_data(path)
    if result:
        console.print(f"\n  [bold bright_green]✅ Data exported to: {result}[/]\n")
    else:
        console.print("\n  [bold red]❌ No data file found to export.[/]\n")


@data_app.command("import")
def data_import_cmd(
    path: str = typer.Argument(..., help="Backup file to import"),
):
    """📥 Import data from a backup file."""
    success = import_data(path)
    if success:
        console.print(f"\n  [bold bright_green]✅ Data imported from: {path}[/]\n")
    else:
        console.print(f"\n  [bold red]❌ Failed to import. File missing or invalid.[/]\n")


# ── Boss Commands ────────────────────────────────────────

@boss_app.command("spawn")
def boss_spawn_cmd(name: str = typer.Argument(None, help="Boss name (random if omitted)")):
    """👹 Spawn a new boss to fight! Defeat it with Pomodoro sessions."""
    data = load_data()
    ensure_boss_data(data)

    if is_boss_active(data):
        console.print("\n[bold yellow]⚠  A boss is already active![/]")
        show_boss_status(data["active_boss"])
        save_data(data)
        raise typer.Exit()

    boss = spawn_boss(data, name)
    save_data(data)
    show_boss_spawn(boss)


@boss_app.command("attack")
def boss_attack_cmd():
    """⚔️ Attack the active boss (also auto-triggered after Pomodoros)."""
    data = load_data()
    ensure_boss_data(data)

    if not is_boss_active(data):
        console.print("\n[dim]No active boss. Spawn one with:[/]")
        console.print("  [cyan]python levelup.py boss spawn[/]\n")
        raise typer.Exit()

    defeated, dmg = animate_attack(data)
    if defeated:
        boss_name = data["active_boss"]["name"]
        animate_victory(boss_name)
        boss_loot = roll_boss_loot(data)
        victory_xp, victory_leveled = add_xp(data, VICTORY_XP, source="pomodoro")
        show_xp_gain(victory_xp, f"Defeated {boss_name}!")
        console.print(f"  [bold bright_yellow]🎁 Boss Loot: {boss_loot['name']}[/]\n")
        if victory_leveled:
            play_sound("level_up")
            show_level_up(data["user"]["level"])
    save_data(data)


@boss_app.command("status")
def boss_status_cmd():
    """📊 Check the current boss HP and status."""
    data = load_data()
    ensure_boss_data(data)
    show_boss_status(data["active_boss"])


# ── Easter Eggs ──────────────────────────────────────────

@app.command(hidden=True)
def coffee():
    """☕ Secret coffee break — shhh!"""
    data = load_data()
    add_xp(data, 5, source="pomodoro")
    save_data(data)
    play_sound("coffee")
    show_coffee_easter_egg()


# ── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    app()
