"""wave_manager.py — Wave spawning and the win condition.

Each wave queues a set of formation slots and spawns the enemies one at a time
(``WAVE_SPAWN_DELAY`` apart) so they stream in rather than popping in at once.
A wave is "cleared" when its queue is empty and no enemies remain. Clearing all
``TOTAL_WAVES`` waves sets ``won`` — the player's victory condition.
"""

from __future__ import annotations

import pygame

from src import settings
from src.entities.enemy import Enemy


class WaveManager:
    """Spawns enemies wave by wave and tracks overall progress / victory."""

    def __init__(self, enemy_sheet: pygame.Surface) -> None:
        """Store the shared enemy sprite sheet and reset progress counters.

        Args:
            enemy_sheet: Pre-loaded 2-frame sprite sheet shared by every enemy.
        """
        self._enemy_sheet: pygame.Surface = enemy_sheet
        self.wave: int = 0  # number of the wave currently in progress (1-based)
        self.won: bool = False
        self._queue: list[tuple[int, int]] = []  # remaining (row, col) slots
        self._last_spawn: int = 0
        self._wave_active: bool = False

    def _build_queue(self) -> list[tuple[int, int]]:
        """Return the (row, col) slots to fill for the upcoming wave."""
        slots: list[tuple[int, int]] = []
        for i in range(settings.WAVE_ENEMY_COUNT):
            slots.append((i // settings.FORMATION_COLS, i % settings.FORMATION_COLS))
        return slots

    def _start_next_wave(self, now: int) -> None:
        """Begin the next wave, or flag victory once all waves are done."""
        if self.wave >= settings.TOTAL_WAVES:
            self.won = True
            return
        self.wave += 1
        self._queue = self._build_queue()
        self._wave_active = True
        self._last_spawn = now

    def update(self, now: int, enemies: pygame.sprite.Group) -> None:
        """Advance wave logic: start waves, drip-spawn enemies, detect clears."""
        if self.won:
            return
        if not self._wave_active:
            self._start_next_wave(now)
            return
        self._spawn_due_enemy(now, enemies)
        if not self._queue and len(enemies) == 0:
            self._wave_active = False  # cleared; next update starts the next wave

    def _spawn_due_enemy(self, now: int, enemies: pygame.sprite.Group) -> None:
        """Pop one queued enemy into the group when the spawn delay elapses."""
        if not self._queue or now - self._last_spawn < settings.WAVE_SPAWN_DELAY:
            return
        row, col = self._queue.pop(0)
        enemies.add(Enemy(self._enemy_sheet, row, col))
        self._last_spawn = now

    def reset(self) -> None:
        """Reset all progress for a brand-new game."""
        self.wave = 0
        self.won = False
        self._queue = []
        self._wave_active = False
        self._last_spawn = 0
