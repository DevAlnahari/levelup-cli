# 🎮 LevelUp CLI v2.1

**Gamified Productivity for Developers** — Transform your terminal into an RPG!

Earn XP, level up, raise pets, fight bosses, track stats, and crush daily challenges — all from the command line.

## ⚡ Installation

```bash
pip install typer rich
python levelup.py setup "YourName"
```

**Optional extras:**
```bash
pip install playsound    # 8-bit retro sound effects
pip install plyer        # Desktop notifications
```

**PyPI install (global):**
```bash
pip install .
levelup --help
```

## 🚀 Quick Start

```bash
python levelup.py setup "YourName"        # Create your profile
python levelup.py task add "Fix bug"  # Add a task
python levelup.py task complete 1     # Complete it (+5 XP)
python levelup.py start              # 25-min Pomodoro (+100 XP)
python levelup.py profile            # View your stats
```

## 📋 All Commands

### Core
| Command | Description |
|---|---|
| `setup "NAME"` | Initialize your player profile |
| `profile` | View your stats, pet, badges, XP |
| `start` | Start a Pomodoro session (+100 XP) |
| `start --strict` | Pomodoro + block distracting sites |
| `stats` | 📊 Statistics dashboard with charts |
| `challenge` | 🎯 View daily & weekly challenges |
| `achievements` | 🏆 Badge progress bars |
| `coffee` | ☕ Secret easter egg |

### Tasks (`task`)
| Command | Description |
|---|---|
| `task add "title"` | Add a new task |
| `task list` | View all tasks |
| `task complete ID` | Mark task as done (+5 XP) |
| `task undo ID` | Revert a completed task |
| `task remove ID` | Delete a task |

### Pet (`pet`)
| Command | Description |
|---|---|
| `pet name "Blaze"` | Name your pet |
| `pet feed` | Feed your pet (+20 HP) |
| `pet species dragon` | Switch species: dragon, phoenix, wolf, cat |

### Boss Fights (`boss`)
| Command | Description |
|---|---|
| `boss spawn` | Spawn a random boss (1000 HP) |
| `boss attack` | Attack the active boss |
| `boss status` | Check boss HP |

### Configuration (`config`)
| Command | Description |
|---|---|
| `config show` | View all settings |
| `config set KEY VALUE` | Update a setting |
| `config reset` | Reset to defaults |
| `config repo-add PATH` | Add a Git repo for sync |
| `config repo-remove PATH` | Remove a Git repo |

**Configurable settings:** `pomodoro_duration`, `short_break`, `long_break`, `theme`, `pet_species`, `notifications`, `sound_enabled`

### Strict Mode (`strict`)
| Command | Description |
|---|---|
| `strict add SITE` | Add a site to block list |
| `strict remove SITE` | Remove a site |
| `strict list` | Show all blocked sites |

### Data (`data`)
| Command | Description |
|---|---|
| `data export FILE` | Backup your data |
| `data import FILE` | Restore from backup |

### Git Sync
| Command | Description |
|---|---|
| `git-sync` | Scan all configured repos (+10 XP/commit) |
| `git-sync --path ./repo` | Scan a specific repo |

## 🎨 Themes

Switch your visual theme: `default`, `cyberpunk`, `forest`, `ocean`

```bash
python levelup.py config set theme cyberpunk
```

## 🐾 Pet System

4 species × 5 evolution stages (Egg → Baby → Teen → Adult → Legendary):
- 🐉 **Dragon** — Classic fire-breathing companion
- 🔥 **Phoenix** — Reborn from the ashes
- 🐺 **Wolf** — Pack leader
- 🐱 **Cat** — Mysterious mystic

Pets evolve automatically as you level up. Feed them to restore HP!

## 🎯 Challenges

- **Daily Challenge:** Random objective refreshed every day (+20–100 XP)
- **Weekly Challenge:** Bigger goal refreshed every Monday (+150–500 XP)
- Progress tracked automatically as you complete tasks and Pomodoros

## 👹 Boss Fights

Bosses have 1000 HP. Attack them by completing Pomodoros (auto-attacks after each session). Defeating a boss earns:
- **+500 XP**
- **Boss-specific loot** (Legendary badges, power boosts)

## 🔊 Sound Effects

**Note:** This repository includes a few basic sounds (`task_complete.wav`, `pomodoro_done.wav`, `level_up.wav`), but is **missing several other audio files!** 

You can add your own custom `.wav` files into the `sounds/` directory to get the full experience. If a file is missing, the CLI will automatically generate a basic 8-bit placeholder sound for it on the first run.

## � Data Files

| File | Location |
|---|---|
| User data | `~/.levelup/data.json` |
| Config | `~/.levelup/config.json` |
| Sounds | `./sounds/*.wav` |

## 🛡️ Anti-Cheat

- 10-minute cooldown between manual task completions
- 500 XP daily cap for manual tasks
- Pomodoro XP bypasses the cap

## 📦 Dependencies

- `typer` — CLI framework
- `rich` — Beautiful terminal output
- `playsound` — Sound effects (optional)
- `plyer` — Desktop notifications (optional)
