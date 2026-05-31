"""enemy.py — Enemy ship entity.

The enemy owns its own coordinate maths (formation snapping and the sinusoidal
dive path). The *policy* deciding when to dive or shoot lives in
``systems/enemy_ai.py``; this class only knows how to execute the chosen
movement, keeping raw coordinate math out of the game loop.
"""

from __future__ import annotations

import math

import pygame

from src import settings

# Behaviour phases.
STATE_FORMATION = "formation"
STATE_DIVING = "diving"


class Enemy(pygame.sprite.Sprite):
    """A single invader that holds a formation slot and can dive at the player."""

    def __init__(self, sheet: pygame.Surface, row: int, col: int) -> None:
        """Create an enemy bound to grid slot (row, col).

        Args:
            sheet: Pre-loaded 2-frame horizontal sprite sheet (loaded once).
            row: Formation row index (0 at the top).
            col: Formation column index (0 at the left).
        """
        super().__init__()
        self._frames: list[pygame.Surface] = self._slice_sheet(sheet)
        self._frame_index: int = 0
        self._frame_elapsed: float = 0.0
        self.image: pygame.Surface = self._frames[0]
        self.row: int = row
        self.col: int = col
        self.rect: pygame.Rect = self.image.get_rect()
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)
        self.health: int = settings.ENEMY_HEALTH
        self.state: str = STATE_FORMATION
        self._dive_phase: float = 0.0
        self._dive_origin_x: int = 0

    @staticmethod
    def _slice_sheet(sheet: pygame.Surface) -> list[pygame.Surface]:
        """Cut the horizontal sheet into individual frame surfaces."""
        size = settings.ENEMY_FRAME_SIZE
        count = sheet.get_width() // size
        return [
            sheet.subsurface(pygame.Rect(i * size, 0, size, size)).copy()
            for i in range(count)
        ]

    def update(self, dt: int) -> None:
        """Step the wing-pulse animation frame."""
        self._frame_elapsed += dt
        frame_ms = 1000.0 / settings.ENEMY_ANIMATION_FPS
        if self._frame_elapsed >= frame_ms:
            self._frame_elapsed -= frame_ms
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            self.image = self._frames[self._frame_index]
            self.mask = pygame.mask.from_surface(self.image)

    def snap_to_slot(self, x: int, y: int) -> None:
        """Place the enemy at its formation slot centre (called while in formation)."""
        if self.state == STATE_FORMATION:
            self.rect.center = (x, y)

    def start_dive(self) -> None:
        """Switch into the diving phase, anchoring the sine path to current x."""
        self.state = STATE_DIVING
        self._dive_phase = 0.0
        self._dive_origin_x = self.rect.centerx

    def update_dive(self) -> bool:
        """Advance one diving step; return True once the enemy exits the bottom.

        The path descends at a constant rate while swinging horizontally on a
        sine wave, producing the classic Galaga-style swoop.
        """
        self._dive_phase += settings.DIVE_FREQUENCY
        offset = math.sin(self._dive_phase) * settings.DIVE_AMPLITUDE
        self.rect.centerx = int(self._dive_origin_x + offset)
        self.rect.y += settings.DIVE_SPEED
        return self.rect.top > settings.SCREEN_HEIGHT

    def return_to_formation(self) -> None:
        """Reset a finished diver back to its formation slot from the top edge."""
        self.state = STATE_FORMATION
        self.rect.bottom = 0

    def hit(self) -> bool:
        """Apply one point of damage; return True if the enemy is destroyed."""
        self.health -= 1
        return self.health <= 0
