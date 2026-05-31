"""generate_assets.py — Procedurally create placeholder art and audio.

The project spec references PNG sprites and WAV sound effects under assets/.
Rather than ship binary art, this one-off helper draws simple but readable
placeholders with pygame and synthesises short SFX with the stdlib `wave`
module (no numpy dependency). Run it once before playing:

    python tools/generate_assets.py

It is a build-time tool, NOT part of the game runtime, so it deliberately
ignores the "no asset loading outside setup" rules that apply to the game.
"""

from __future__ import annotations

import math
import os
import struct
import sys
import wave
from pathlib import Path

# Allow running both as `python tools/generate_assets.py` and as a module.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402  (import after env setup is intentional)

from src import settings  # noqa: E402

SAMPLE_RATE = 22050


def _draw_player() -> pygame.Surface:
    """Return a 48x48 player ship sprite (cyan arrowhead with engine glow)."""
    size = 48
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    hull = [(size // 2, 2), (size - 6, size - 8), (size // 2, size - 16), (6, size - 8)]
    pygame.draw.polygon(surf, settings.CYAN, hull)
    pygame.draw.polygon(surf, settings.WHITE, hull, 2)
    pygame.draw.circle(surf, settings.YELLOW, (size // 2, 12), 5)
    pygame.draw.rect(surf, settings.RED, (size // 2 - 4, size - 14, 8, 6))
    return surf


def _draw_enemy_sheet() -> pygame.Surface:
    """Return a 2-frame horizontal sprite sheet (80x40) for the pulsing enemy.

    Frame 0: wings spread, neutral red body.
    Frame 1: wings tucked, yellow-outlined body (glow phase).
    The alternation at ENEMY_ANIMATION_FPS creates the classic Galaga wing-flap.
    """
    size = settings.ENEMY_FRAME_SIZE  # 40
    sheet = pygame.Surface((size * 2, size), pygame.SRCALPHA)

    for frame in range(2):
        glow = frame == 1
        ox = frame * size
        body = pygame.Rect(ox + 6, 10, size - 12, size - 18)
        body_color = (255, 90, 90) if glow else settings.RED
        outline_color = settings.YELLOW if glow else settings.WHITE
        pygame.draw.ellipse(sheet, body_color, body)
        pygame.draw.ellipse(sheet, outline_color, body, 2)
        pygame.draw.circle(sheet, settings.WHITE, (ox + 15, 20), 4)
        pygame.draw.circle(sheet, settings.WHITE, (ox + 25, 20), 4)
        pygame.draw.circle(sheet, settings.BLACK, (ox + 15, 20), 2)
        pygame.draw.circle(sheet, settings.BLACK, (ox + 25, 20), 2)
        claw_offsets = (-14, -4, 6, 16) if not glow else (-10, -2, 4, 12)
        claw_y = 38 if not glow else 35
        for dx in claw_offsets:
            pygame.draw.line(sheet, body_color, (ox + size // 2, 28), (ox + size // 2 + dx, claw_y), 3)

    return sheet


def _draw_bullet(color: tuple[int, int, int]) -> pygame.Surface:
    """Return a small 6x16 glowing bolt in the given color."""
    surf = pygame.Surface((6, 16), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (1, 0, 4, 16), border_radius=2)
    pygame.draw.rect(surf, settings.WHITE, (2, 2, 2, 6))
    return surf


def _draw_explosion_sheet() -> pygame.Surface:
    """Return a horizontal sprite sheet of expanding explosion rings."""
    frame = settings.EXPLOSION_FRAME_SIZE
    frames = 6
    sheet = pygame.Surface((frame * frames, frame), pygame.SRCALPHA)
    center = frame // 2
    palette = [settings.WHITE, settings.YELLOW, (255, 160, 40), settings.RED]
    for i in range(frames):
        ox = i * frame
        radius = int((i + 1) / frames * (center - 4))
        for ring, color in enumerate(palette):
            r = max(1, radius - ring * 5)
            alpha = max(0, 255 - i * 35)
            tmp = pygame.Surface((frame, frame), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*color, alpha), (center, center), r)
            sheet.blit(tmp, (ox, 0))
    return sheet


def _draw_background() -> pygame.Surface:
    """Return a dark starfield background sized to the screen."""
    import random

    rng = random.Random(42)
    surf = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    surf.fill(settings.DARK_BLUE)
    for _ in range(220):
        x = rng.randrange(settings.SCREEN_WIDTH)
        y = rng.randrange(settings.SCREEN_HEIGHT)
        shade = rng.randint(90, 255)
        size = rng.choice((1, 1, 1, 2))
        pygame.draw.circle(surf, (shade, shade, shade), (x, y), size)
    return surf


def _write_wave(path: Path, samples: list[float]) -> None:
    """Write mono 16-bit PCM samples (range -1..1) to a .wav file."""
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
        )
        wav.writeframes(frames)


def _make_shoot_sfx() -> list[float]:
    """A short descending laser blip."""
    duration = 0.18
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 900 - 1800 * t  # sweep down
        env = max(0.0, 1.0 - i / n)
        out.append(0.4 * env * math.sin(2 * math.pi * freq * t))
    return out


def _make_music_wav() -> list[float]:
    """Synthesize a 4-second looping space-shooter chiptune background.

    Three layers:
      Bass pulse  — A2 (110 Hz) sine, one hit per beat, exponential decay.
      Lead arpeggio — Am pentatonic square-wave, 16th-note pattern.
      Pad drone   — A2 + E2 sustained sines at very low volume.

    A 20 ms fade-in/out prevents click artefacts at the loop point.
    Replace assets/sounds/music.wav with any real OGG/WAV for better audio.
    """
    duration = 4.0
    n = int(SAMPLE_RATE * duration)
    out = [0.0] * n

    bpm = 120
    beat_s = int(SAMPLE_RATE * 60.0 / bpm)   # 11 025 samples / beat
    sixteenth_s = beat_s // 4                  # 2 756 samples / 16th note

    # Bass pulse (A2 = 110 Hz), one hit per beat
    total_beats = int(duration * bpm / 60)
    for b in range(total_beats):
        onset = b * beat_s
        note_dur = beat_s * 3 // 4
        for i in range(min(note_dur, n - onset)):
            t = i / SAMPLE_RATE
            env = math.exp(-8.0 * i / note_dur)
            out[onset + i] += 0.40 * env * math.sin(2 * math.pi * 110.0 * t)

    # Lead arpeggio — Am pentatonic square wave, 16th notes
    arp = [220.0, 261.63, 329.63, 440.0, 329.63, 261.63, 220.0, 329.63]
    total_steps = n // sixteenth_s
    for step in range(total_steps):
        freq = arp[step % len(arp)]
        onset = step * sixteenth_s
        note_dur = max(1, sixteenth_s - 300)
        for i in range(min(note_dur, n - onset)):
            t = i / SAMPLE_RATE
            env = max(0.0, 1.0 - i / note_dur) ** 0.5
            square = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            out[onset + i] += 0.10 * env * square

    # Pad drone — A2 (110 Hz) + E2 (82.41 Hz), very soft
    for i in range(n):
        t = i / SAMPLE_RATE
        out[i] += 0.05 * math.sin(2 * math.pi * 110.0 * t)
        out[i] += 0.03 * math.sin(2 * math.pi * 82.41 * t)

    # 20 ms fade-in and fade-out for seamless looping
    fade = int(SAMPLE_RATE * 0.02)
    for i in range(fade):
        out[i] *= i / fade
        out[n - fade + i] *= (fade - i) / fade

    # Normalise to avoid clipping
    peak = max(abs(v) for v in out) or 1.0
    if peak > 0.88:
        scale = 0.88 / peak
        out = [v * scale for v in out]

    return out


def _make_explosion_sfx() -> list[float]:
    """A noisy decaying burst."""
    import random

    rng = random.Random(7)
    duration = 0.45
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        env = max(0.0, 1.0 - i / n) ** 2
        noise = rng.uniform(-1.0, 1.0)
        rumble = math.sin(2 * math.pi * 70 * i / SAMPLE_RATE)
        out.append(0.5 * env * (0.7 * noise + 0.3 * rumble))
    return out


def main() -> None:
    """Generate every placeholder asset referenced by the game."""
    pygame.init()
    settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    settings.SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

    pygame.image.save(_draw_player(), settings.IMAGES_DIR / "player.png")
    pygame.image.save(_draw_enemy_sheet(), settings.IMAGES_DIR / "enemy_sheet.png")
    pygame.image.save(_draw_bullet(settings.YELLOW), settings.IMAGES_DIR / "bullet.png")
    pygame.image.save(
        _draw_bullet(settings.GREEN), settings.IMAGES_DIR / "enemy_bullet.png"
    )
    pygame.image.save(
        _draw_explosion_sheet(), settings.IMAGES_DIR / "explosion_sheet.png"
    )
    pygame.image.save(_draw_background(), settings.IMAGES_DIR / "background.png")

    _write_wave(settings.SOUNDS_DIR / "shoot.wav", _make_shoot_sfx())
    _write_wave(settings.SOUNDS_DIR / "explosion.wav", _make_explosion_sfx())
    _write_wave(settings.SOUNDS_DIR / settings.MUSIC_FILE, _make_music_wav())

    pygame.quit()
    print("Assets generated under", settings.ASSETS_DIR)


if __name__ == "__main__":
    main()
