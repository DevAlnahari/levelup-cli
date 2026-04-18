"""
boss.py — Epic Boss Fight System for LevelUp CLI v2.0

Features:
- Spawn bosses with 1000 HP
- Live Rich animations for attack sequences (hit flash, damage, recovery)
- Victory explosion with 1000 XP + Dragon Slayer badge
"""

import os
import time
import random
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.progress import BarColumn, Progress, TextColumn
from rich import box

console = Console()

# ── Boss ASCII Art ───────────────────────────────────────

BOSS_ART_NORMAL = r"""
         ___
        /   \
       | O O |
       |  ^  |
       | \_/ |
    ___/     \___
   /  |       |  \
  /   |  |||  |   \
 /    | /   \ |    \
|  /\ |/ BUG \| /\  |
| /  \|___|___\|/  \ |
|/    |       |    \|
 \    |  / \  |    /
  \   | /   \ |   /
   \__|/_____\|__/
      |       |
     _|       |_
    / |_______| \
   /  /       \  \
  /__/         \__\
"""

BOSS_ART_HIT = r"""
         ___
        /   \
       | > < |
       |  ~  |
       | === |
    ___/     \___
   / *|  !!!  |* \
  / * | *|||* | * \
 / *  |*/   \*|  * \
|  /\ |/* X *\| /\  |
| /  \|*__|__*\|/  \ |
|/  * |   *   | *  \|
 \ *  |  / \  |  * /
  \ * | / * \ | * /
   \*_|/__ __\|_*/
      |   *   |
     _|  ***  |_
    / |_______| \
   /  /       \  \
  /__/         \__\
"""

BOSS_ART_DEAD = r"""
         ___
        /   \
       | x x |
       |  .  |
       | --- |
    ___/     \___
   /  |       |  \
  /   |  ...  |   \
 /    |       |    \
|     |  R.I.P |     |
|     |________|     |
 \    |       |    /
  \   |       |   /
   \__|_______|__/
"""

VICTORY_ART = r"""
    ██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗██╗
    ██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██║
    ██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ ██║
    ╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  ╚═╝
     ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   ██╗
      ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝
"""

# ── Default Boss Templates ──────────────────────────────

DEFAULT_BOSSES = [
    "The Legacy Code Monster",
    "The Spaghetti Daemon",
    "The Infinite Loop Hydra",
    "The Null Pointer Phantom",
    "The Memory Leak Kraken",
]

BOSS_MAX_HP = 1000
ATTACK_DAMAGE = 100
VICTORY_XP = 1000
DRAGON_SLAYER_BADGE = "🐉 Dragon Slayer"


# ── Boss Data Helpers ────────────────────────────────────

def get_default_boss() -> dict:
    """Return the default boss structure."""
    return {
        "name": None,
        "max_hp": BOSS_MAX_HP,
        "current_hp": BOSS_MAX_HP,
        "is_active": False,
    }


def ensure_boss_data(data: dict) -> None:
    """Ensure boss data exists in the data structure."""
    if "active_boss" not in data:
        data["active_boss"] = get_default_boss()


def spawn_boss(data: dict, name: str | None = None) -> dict:
    """Spawn a new boss. Returns the boss dict."""
    ensure_boss_data(data)

    if data["active_boss"].get("is_active"):
        return data["active_boss"]  # Boss already active

    boss_name = name or random.choice(DEFAULT_BOSSES)
    data["active_boss"] = {
        "name": boss_name,
        "max_hp": BOSS_MAX_HP,
        "current_hp": BOSS_MAX_HP,
        "is_active": True,
    }
    return data["active_boss"]


def is_boss_active(data: dict) -> bool:
    """Check if there is an active boss."""
    ensure_boss_data(data)
    return data["active_boss"].get("is_active", False)


# ── Boss HP Bar Builder ──────────────────────────────────

def _build_hp_bar(current_hp: int, max_hp: int, width: int = 40) -> str:
    """Build a colored HP bar string."""
    ratio = max(0, current_hp / max_hp)
    filled = int(ratio * width)
    empty = width - filled

    if ratio > 0.5:
        color = "bright_green"
    elif ratio > 0.25:
        color = "bright_yellow"
    else:
        color = "bright_red"

    bar = f"[{color}]{'█' * filled}[/][bright_black]{'░' * empty}[/]"
    return f"  ❤️ {bar}  [{color}]{current_hp}/{max_hp} HP[/]"


# ── Boss Display Panels ─────────────────────────────────

def _build_boss_panel(
    boss: dict,
    art: str,
    art_style: str = "bright_green",
    subtitle: str = "",
    hp_override: int | None = None,
) -> Panel:
    """Build a Rich Panel showing the boss art + HP bar."""
    hp = hp_override if hp_override is not None else boss["current_hp"]
    max_hp = boss["max_hp"]

    boss_text = Text(art, style=art_style)
    hp_bar = _build_hp_bar(hp, max_hp)

    content = Group(
        Align.center(boss_text),
        Text.from_markup(f"\n{hp_bar}\n"),
    )

    return Panel(
        content,
        title=f"[bold bright_red]👹 {boss['name']} 👹[/]",
        subtitle=f"[dim]{subtitle}[/]" if subtitle else None,
        border_style="bright_red",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    )


# ── Live Attack Animation ───────────────────────────────

def animate_attack(data: dict) -> tuple[bool, int]:
    """
    Play the boss attack animation sequence using Rich Live.
    Returns (boss_defeated, damage_dealt).
    """
    ensure_boss_data(data)
    boss = data["active_boss"]

    if not boss.get("is_active"):
        return False, 0

    old_hp = boss["current_hp"]
    new_hp = max(0, old_hp - ATTACK_DAMAGE)
    damage = old_hp - new_hp
    defeated = new_hp <= 0

    console.print()

    # ── Frame 1: Normal (show the boss) ──────────────
    with Live(
        _build_boss_panel(boss, BOSS_ART_NORMAL, "bright_green", "Preparing attack..."),
        console=console,
        refresh_per_second=10,
        transient=True,
    ) as live:
        time.sleep(0.8)

        # ── Frame 2: THE HIT (flash red) ────────────
        live.update(
            _build_boss_panel(boss, BOSS_ART_HIT, "bold bright_red", "💥 SMASH!")
        )
        time.sleep(0.5)

        # ── Frame 3: Animate HP decrease ─────────────
        steps = 20
        hp_step = damage / steps
        for i in range(steps):
            current = int(old_hp - hp_step * (i + 1))
            current = max(new_hp, current)
            live.update(
                _build_boss_panel(
                    boss, BOSS_ART_HIT, "bright_yellow",
                    f"💥 -{damage} DAMAGE!",
                    hp_override=current,
                )
            )
            time.sleep(0.05)

        # ── Frame 4: Recovery ────────────────────────
        if not defeated:
            live.update(
                _build_boss_panel(
                    boss, BOSS_ART_NORMAL, "bright_green",
                    "The boss staggers...",
                    hp_override=new_hp,
                )
            )
            time.sleep(0.8)
        else:
            # Death sequence
            live.update(
                _build_boss_panel(
                    boss, BOSS_ART_DEAD, "dim bright_red",
                    "💀 DEFEATED!",
                    hp_override=0,
                )
            )
            time.sleep(1.0)

    # Update boss data
    boss["current_hp"] = new_hp
    if defeated:
        boss["is_active"] = False

    # Damage panel
    panel = Panel(
        f"[bold bright_red]💥 CRITICAL HIT![/]\n\n"
        f"  You dealt [bold bright_yellow]{damage}[/] damage to [bold]{boss['name']}[/]!\n"
        f"  [dim]Boss HP: {new_hp}/{boss['max_hp']}[/]",
        title="[bold bright_yellow]⚔️  ATTACK RESULT  ⚔️[/]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)
    console.print()

    return defeated, damage


# ── Victory Animation ───────────────────────────────────

def animate_victory(boss_name: str) -> None:
    """Play the victory explosion animation."""
    os.system("cls" if os.name == "nt" else "clear")

    explosions = ["💥", "🔥", "✨", "⚡", "💫", "🌟", "🎆", "🎇", "☄️", "💎"]

    # Multi-frame explosion
    with Live(
        Text("", style="bold"),
        console=console,
        refresh_per_second=10,
        transient=True,
    ) as live:
        # Frame 1–6: Explosion frames
        for i in range(6):
            boom_line = " ".join(random.choices(explosions, k=15))
            content = Text()
            content.append(f"\n{boom_line}\n", style="bold bright_yellow")
            if i % 2 == 0:
                content.append(VICTORY_ART, style="bold bright_yellow")
            else:
                content.append(VICTORY_ART, style="bold bright_magenta")
            content.append(f"\n{boom_line}\n", style="bold bright_cyan")

            panel = Panel(
                Align.center(content),
                title="[bold bright_yellow]🐉 BOSS DEFEATED 🐉[/]",
                border_style="bright_yellow" if i % 2 == 0 else "bright_magenta",
                box=box.DOUBLE_EDGE,
                padding=(1, 4),
            )
            live.update(panel)
            time.sleep(0.4)

    # Final static victory panel
    final_boom = " ".join(random.choices(explosions, k=15))
    victory_text = Text()
    victory_text.append(VICTORY_ART, style="bold bright_yellow")
    victory_text.append(f"\n  You slayed [bold]{boss_name}[/]!\n\n", style="bright_white")
    victory_text.append(f"  🏆 +{VICTORY_XP} XP\n", style="bold bright_yellow")
    victory_text.append(f"  {DRAGON_SLAYER_BADGE}\n", style="bold bright_cyan")
    victory_text.append(f"\n{final_boom}\n", style="bright_magenta")

    panel = Panel(
        Align.center(victory_text),
        title="[bold bright_yellow]⚔️  GLORIOUS VICTORY  ⚔️[/]",
        subtitle="[bold bright_cyan]The server is safe... for now.[/]",
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Spawn Display ────────────────────────────────────────

def show_boss_spawn(boss: dict) -> None:
    """Display the boss spawn announcement."""
    os.system("cls" if os.name == "nt" else "clear")

    warning_emojis = "⚠️ 🚨 ☠️ 👹 🔥 ⚠️ 🚨 ☠️ 👹 🔥"

    with Live(
        Text("", style="bold"),
        console=console,
        refresh_per_second=10,
        transient=True,
    ) as live:
        # Dramatic entrance: 3 flash frames
        for i in range(4):
            if i % 2 == 0:
                content = Text("\n\n  ⚠️  A BOSS APPROACHES...  ⚠️\n\n", style="bold bright_red")
            else:
                content = Text("\n\n  🚨  PREPARE FOR BATTLE!  🚨\n\n", style="bold bright_yellow")
            panel = Panel(
                Align.center(content),
                border_style="bright_red" if i % 2 == 0 else "bright_yellow",
                box=box.HEAVY,
                padding=(2, 4),
            )
            live.update(panel)
            time.sleep(0.5)

    # Final spawn panel with boss art
    boss_text = Text(BOSS_ART_NORMAL, style="bold bright_red")
    hp_bar = _build_hp_bar(boss["max_hp"], boss["max_hp"])

    info = Text()
    info.append(f"\n  {warning_emojis}\n\n", style="bright_red")
    info.append(f"  A wild [bold]{boss['name']}[/] has appeared!\n\n", style="bright_white")
    info.append(f"  HP: {boss['max_hp']}\n", style="bright_red")
    info.append(f"  Complete Pomodoro sessions to deal 100 damage!\n\n", style="dim")
    info.append(f"  [dim]Defeat the boss for +{VICTORY_XP} XP and a legendary badge![/]\n", style="dim")

    panel = Panel(
        Group(
            Align.center(boss_text),
            Text.from_markup(f"\n{hp_bar}\n"),
            info,
        ),
        title=f"[bold bright_red]👹 BOSS SPAWNED: {boss['name']} 👹[/]",
        border_style="bright_red",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    console.print()


def show_boss_status(boss: dict) -> None:
    """Show current boss status panel."""
    if not boss.get("is_active"):
        console.print("\n[dim]No active boss. Spawn one with:[/]")
        console.print("  [cyan]python levelup.py boss spawn[/]\n")
        return

    panel = _build_boss_panel(
        boss, BOSS_ART_NORMAL, "bright_green",
        f"Deal {ATTACK_DAMAGE} damage per Pomodoro!"
    )
    console.print()
    console.print(panel)
    console.print()
