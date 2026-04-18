"""
audio.py — 8-bit retro sound effects for LevelUp CLI v2.1

Plays .wav files from the sounds/ directory on game events.
Can generate basic sine-wave sounds if no .wav files exist.
"""

import struct
import wave
import math
from pathlib import Path
from config import load_config

SOUNDS_DIR = Path(__file__).parent / "sounds"

# Event-to-file mapping
SOUND_FILES = {
    "task_complete": "task_complete.wav",
    "pomodoro_done": "pomodoro_done.wav",
    "level_up": "level_up.wav",
    "loot_drop": "loot_drop.wav",
    "level_down": "level_down.wav",
    "badge": "badge.wav",
    "coffee": "coffee.wav",
    "boss_hit": "boss_hit.wav",
    "boss_victory": "boss_victory.wav",
    "pet_feed": "pet_feed.wav",
    "challenge_complete": "challenge_complete.wav",
}

# Sound definitions: (frequency_hz, duration_ms, volume 0-1)
SOUND_DEFS = {
    "task_complete": [(523, 100, 0.5), (659, 100, 0.5), (784, 200, 0.6)],
    "pomodoro_done": [(440, 200, 0.6), (554, 200, 0.6), (659, 300, 0.7)],
    "level_up": [(440, 100, 0.5), (554, 100, 0.5), (659, 100, 0.6), (880, 300, 0.7)],
    "loot_drop": [(880, 80, 0.4), (660, 80, 0.4), (880, 80, 0.5), (1100, 200, 0.6)],
    "level_down": [(440, 200, 0.5), (350, 200, 0.5), (260, 400, 0.4)],
    "badge": [(784, 150, 0.5), (988, 150, 0.5), (1175, 300, 0.6)],
    "coffee": [(600, 100, 0.3), (700, 100, 0.3), (800, 200, 0.4)],
    "boss_hit": [(200, 80, 0.7), (150, 80, 0.7), (100, 200, 0.6)],
    "boss_victory": [(523, 100, 0.6), (659, 100, 0.6), (784, 100, 0.6), (1047, 400, 0.8)],
    "pet_feed": [(500, 100, 0.3), (600, 100, 0.3), (700, 150, 0.4)],
    "challenge_complete": [(660, 100, 0.5), (880, 100, 0.5), (1100, 100, 0.6), (1320, 300, 0.7)],
}


def _generate_tone(freq: float, duration_ms: int, volume: float, sample_rate: int = 22050) -> bytes:
    """Generate a sine wave tone as raw PCM bytes."""
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Apply envelope (fade in/out)
        envelope = 1.0
        fade = int(num_samples * 0.1)
        if i < fade:
            envelope = i / fade
        elif i > num_samples - fade:
            envelope = (num_samples - i) / fade
        value = volume * envelope * math.sin(2 * math.pi * freq * t)
        samples.append(int(value * 32767))
    return struct.pack(f"<{len(samples)}h", *samples)


def generate_sounds() -> int:
    """Generate all missing sound files. Returns count of files generated."""
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for event, notes in SOUND_DEFS.items():
        filepath = SOUNDS_DIR / SOUND_FILES[event]
        if filepath.exists():
            continue
        sample_rate = 22050
        all_samples = b""
        for freq, dur, vol in notes:
            all_samples += _generate_tone(freq, dur, vol, sample_rate)
        with wave.open(str(filepath), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(all_samples)
        count += 1
    return count


def play_sound(event: str) -> None:
    """Play a sound effect for the given event. Silently does nothing if unavailable."""
    config = load_config()
    if not config.get("sound_enabled", True):
        return

    filename = SOUND_FILES.get(event)
    if not filename:
        return

    filepath = SOUNDS_DIR / filename
    if not filepath.exists():
        return

    try:
        from playsound import playsound
        playsound(str(filepath), block=False)
    except Exception:
        pass
