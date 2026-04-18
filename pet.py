"""
pet.py — ASCII Tamagotchi Pet System for LevelUp CLI v2.1

4 species (Dragon, Phoenix, Wolf, Cat) × 5 evolution stages each.
Pet becomes "sick" after 3 days of inactivity.
Pet can be named, fed, and switched species.
"""

from datetime import datetime
from rich.text import Text


# ── Species: Dragon ──────────────────────────────────────

DRAGON_STAGES = {
    0: {"name": "Dragon Egg", "art": r"""
      ╭───╮
     ╱ ◌◌◌ ╲
    │ ◌◌◌◌◌ │
    │ ◌◌◌◌◌ │
     ╲ ◌◌◌ ╱
      ╰───╯
    """, "color": "bright_yellow"},
    1: {"name": "Baby Dragon", "art": r"""
        /\_/\
       ( o.o )
        > ~ <
       /|   |\
      (_|   |_)
    """, "color": "bright_green"},
    2: {"name": "Young Dragon", "art": r"""
       __====-_  _-====___
     _--^^^####//      \\###^^^--_
      _/######//   (@::@)   \\######\_
     /#####//      |\\^^/|     \\#####\
    """, "color": "bright_cyan"},
    3: {"name": "Elder Dragon", "art": r"""
             ______________
      ,===:'.,            `-._
            `:.`---.__         `-._
              `:.     `--.         `.
                \.        `.         `.
        (,,(,    \.         `.   ____,-`.,
     (,'     `/   \.   ,--.___`.'
         `{D, {    \  :    \;
           V,,'    /  /    //
    """, "color": "bright_magenta"},
    4: {"name": "Legendary Dragon", "art": r"""
                ___====-_  _-====___
           _--^^^#####//      \\#####^^^--_
        _-^##########// (    ) \\##########^-_
       -############//  |\^^/|  \\############-
      _/############//   (@::@)   \\############\_
     /#############((     \\//     ))#############\
      ⚡ LEGENDARY ⚡
    """, "color": "bold bright_yellow"},
}

# ── Species: Phoenix ─────────────────────────────────────

PHOENIX_STAGES = {
    0: {"name": "Phoenix Egg", "art": r"""
      ╭───╮
     ╱ 🔥🔥 ╲
    │ 🔥🔥🔥 │
    │ 🔥🔥🔥 │
     ╲ 🔥🔥 ╱
      ╰───╯
    """, "color": "bright_red"},
    1: {"name": "Phoenix Chick", "art": r"""
        ,  ,
       /(  )\
       \ \/ /
       /`  `\
      (_/||\_)
    """, "color": "bright_red"},
    2: {"name": "Young Phoenix", "art": r"""
         .  .
        |\\/|
        |  |
       /|  |\
      /_|__|_\
       //  \\
      (/    \)
    """, "color": "bright_yellow"},
    3: {"name": "Elder Phoenix", "art": r"""
          __     __
         /  \~~~/ .\
        (     ..    )
         \___(  )__/
           / () \
          /  /\  \
         (__/  \__)
    """, "color": "bold bright_red"},
    4: {"name": "Eternal Phoenix", "art": r"""
      .    *    .   *  .
        \  🔥  /  🔥
     *   \\|//   *
        --🔥--
     *   //|\\   *
        /  🔥  \  🔥
      .    *    .   *  .
       ✨ ETERNAL ✨
    """, "color": "bold bright_yellow"},
}

# ── Species: Wolf ────────────────────────────────────────

WOLF_STAGES = {
    0: {"name": "Wolf Pup Egg", "art": r"""
      ╭───╮
     ╱ 🐾🐾 ╲
    │ 🐾🐾🐾 │
    │ 🐾🐾🐾 │
     ╲ 🐾🐾 ╱
      ╰───╯
    """, "color": "bright_white"},
    1: {"name": "Wolf Pup", "art": r"""
       /^ ^\
      / 0 0 \
      V\ Y /V
       / - \
      /    |
     V__) ||
    """, "color": "bright_white"},
    2: {"name": "Young Wolf", "art": r"""
          /\
     /\  / /
    / /-/ /
    \/  \/
     \  /\
      \/  \
       \   \
    """, "color": "bright_cyan"},
    3: {"name": "Alpha Wolf", "art": r"""
       __
      /  \  _
     / /\ \//
    / /  \/
    \/   /\
     \  /  \
      \/    \
       \____/  AWOOO!
    """, "color": "bright_magenta"},
    4: {"name": "Dire Wolf", "art": r"""
           ___
       ___/   \___
      /   '---'   \
     /  /|     |\  \
     \_/ |  o  | \_/
         \ ___ /
    ⚡ DIRE WOLF ⚡
    """, "color": "bold bright_cyan"},
}

# ── Species: Cat ─────────────────────────────────────────

CAT_STAGES = {
    0: {"name": "Kitten Egg", "art": r"""
      ╭───╮
     ╱ 🐱🐱 ╲
    │ 🐱🐱🐱 │
    │ 🐱🐱🐱 │
     ╲ 🐱🐱 ╱
      ╰───╯
    """, "color": "bright_yellow"},
    1: {"name": "Kitten", "art": r"""
       /\_/\
      ( o.o )
       > ^ <
      /|   |\
     (_|   |_)
    """, "color": "bright_yellow"},
    2: {"name": "Young Cat", "art": r"""
       /\_/\
      ( =.= )
      (")_(")
       \   /
    """, "color": "bright_green"},
    3: {"name": "Shadow Cat", "art": r"""
        /\_____/\
       /  o   o  \
      ( ==  ^  == )
       )         (
      (           )
     ( (  )   (  ) )
    (__(__)___(__)__)
    """, "color": "bright_magenta"},
    4: {"name": "Mystic Cat", "art": r"""
       |\      _,,,---,,_
 ZZZzz /,`.-'`'    -.  ;-;;,_
      |,4-  ) )-,_. ,\ (  `'-'
     '---''(_/--'  `-'\_)
    ✨ MYSTIC ✨
    """, "color": "bold bright_cyan"},
}


# ── Species Registry ────────────────────────────────────

ALL_SPECIES = {
    "dragon": DRAGON_STAGES,
    "phoenix": PHOENIX_STAGES,
    "wolf": WOLF_STAGES,
    "cat": CAT_STAGES,
}

PET_SICK_ART = r"""
      ╭───╮
     ( x_x )  zzZ
      > _ <
     /|   |\
    (_|   |_)
   💀 Feeling sick...
"""


# ── Pet Functions ────────────────────────────────────────

def get_species_stages(data: dict) -> dict:
    """Get the stage dict for the user's chosen species."""
    species = data["user"].get("pet_species", "dragon")
    return ALL_SPECIES.get(species, DRAGON_STAGES)


def get_pet_info(data: dict) -> dict:
    """Get current pet stage info."""
    stage = data["user"].get("pet_stage", 0)
    stages = get_species_stages(data)
    return stages.get(stage, stages[0])


def get_pet_art(data: dict) -> Text:
    """Return styled pet ASCII art based on stage and health."""
    is_sick = data["user"].get("pet_sick", False)
    if is_sick:
        return Text(PET_SICK_ART, style="dim bright_red")
    info = get_pet_info(data)
    return Text(info["art"], style=info["color"])


def get_pet_name(data: dict) -> str:
    """Return the pet's custom name, or evolution name, or sick name."""
    if data["user"].get("pet_sick", False):
        return "Sick Pet 💀"
    custom = data["user"].get("pet_name")
    if custom:
        return custom
    info = get_pet_info(data)
    return info["name"]


def name_pet(data: dict, name: str) -> str:
    """Set a custom pet name. Returns confirmation message."""
    old = data["user"].get("pet_name") or get_pet_info(data)["name"]
    data["user"]["pet_name"] = name
    return f"{old} is now named '{name}'!"


def feed_pet(data: dict) -> tuple[int, str]:
    """
    Feed the pet, restoring 20 HP and increasing hunger satisfaction.
    Returns (hp_restored, message).
    """
    hunger = data["user"].get("pet_hunger", 100)
    hp = data["user"].get("hp", 100)
    max_hp = data["user"].get("max_hp", 100)

    if hunger >= 100:
        return 0, "Your pet isn't hungry right now! 😊"

    hp_gain = min(20, max_hp - hp)
    data["user"]["hp"] = min(max_hp, hp + hp_gain)
    data["user"]["pet_hunger"] = min(100, hunger + 30)

    pet_name = get_pet_name(data)
    return hp_gain, f"{pet_name} ate happily! +{hp_gain} HP ❤️"


def switch_species(data: dict, species: str) -> tuple[bool, str]:
    """Switch pet species. Returns (success, message)."""
    if species not in ALL_SPECIES:
        available = ", ".join(ALL_SPECIES.keys())
        return False, f"Unknown species. Available: {available}"
    data["user"]["pet_species"] = species
    data["user"]["pet_name"] = None  # Reset custom name
    info = ALL_SPECIES[species].get(data["user"].get("pet_stage", 0), ALL_SPECIES[species][0])
    return True, f"Your pet is now a {info['name']}! 🎉"


def check_pet_sickness(data: dict) -> bool:
    """If inactive for 3+ days, pet becomes sick. Returns True if pet just got sick."""
    last = data["user"].get("last_active_date")
    if last is None:
        return False
    last_date = datetime.strptime(last, "%Y-%m-%d").date()
    today = datetime.now().date()
    inactive_days = (today - last_date).days

    if inactive_days >= 3 and not data["user"].get("pet_sick", False):
        data["user"]["pet_sick"] = True
        return True
    return False


def cure_pet(data: dict) -> bool:
    """Cure the pet after completing a Pomodoro. Returns True if cured."""
    if data["user"].get("pet_sick", False):
        data["user"]["pet_sick"] = False
        return True
    return False


def decay_hunger(data: dict) -> None:
    """Decrease pet hunger over time (call daily)."""
    data["user"]["pet_hunger"] = max(0, data["user"].get("pet_hunger", 100) - 10)
