"""assets.py — Centralised, cached asset loading.

Every image and sound is loaded exactly once here and cached. GameManager
calls these helpers during start-up and hands the resulting surfaces / Sound
objects to the rest of the game. Nothing in an update() loop ever touches disk.
"""

from __future__ import annotations

import pygame

from src import settings

# Internal caches keyed by file name so a second request is free.
_image_cache: dict[str, pygame.Surface] = {}
_sound_cache: dict[str, pygame.mixer.Sound] = {}


def load_image(name: str, alpha: bool = True) -> pygame.Surface:
    """Load `assets/images/<name>` once and return the cached surface.

    Args:
        name: File name (e.g. ``"player.png"``).
        alpha: Convert with per-pixel alpha when True, else plain convert().
    """
    if name not in _image_cache:
        surface = pygame.image.load(str(settings.IMAGES_DIR / name))
        surface = surface.convert_alpha() if alpha else surface.convert()
        _image_cache[name] = surface
    return _image_cache[name]


def load_sound(name: str) -> pygame.mixer.Sound | None:
    """Load `assets/sounds/<name>` once, returning None if audio is disabled.

    The mixer may be unavailable (e.g. dummy audio driver in CI). In that case
    we return None and callers simply skip playback.
    """
    if not pygame.mixer.get_init():
        return None
    if name not in _sound_cache:
        sound = pygame.mixer.Sound(str(settings.SOUNDS_DIR / name))
        sound.set_volume(settings.SFX_VOLUME)
        _sound_cache[name] = sound
    return _sound_cache[name]
