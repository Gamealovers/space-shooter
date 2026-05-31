"""enemy_ai.py — Enemy behaviour policy (formation, dive, shoot phases).

This module is the "algorithmic engineering" centrepiece. It implements the
classic Space Invaders / Galaga behaviour as three clearly separated phases:

1. Formation phase — every non-diving enemy is snapped to its grid slot while
   the whole block marches left/right, dropping a step each time it hits a wall.
2. Dive phase — a capped number of randomly chosen enemies break formation and
   swoop toward the player along a sinusoidal path (maths lives on the Enemy).
3. Shooting phase — enemies occasionally fire downward; this manager only
   *reports* muzzle positions so play_state can pull bullets from the pool and
   trigger the shoot sound, keeping pooling/audio out of the AI.
"""

from __future__ import annotations

import random

import pygame

from src import settings
from src.entities.enemy import STATE_DIVING, STATE_FORMATION, Enemy


class FormationManager:
    """Drives the marching grid and per-enemy dive/shoot decisions."""

    def __init__(self) -> None:
        """Start the block at the left, moving right, with no vertical drop."""
        self._direction: int = 1
        self._offset_x: int = 0
        self._offset_y: int = 0

    def _max_offset_x(self) -> int:
        """Horizontal travel room before the block must bounce off a wall."""
        block_w = settings.FORMATION_COLS * settings.FORMATION_CELL_W
        return settings.SCREEN_WIDTH - 2 * settings.FORMATION_SIDE_MARGIN - block_w

    def _slot_position(self, row: int, col: int) -> tuple[int, int]:
        """Return the on-screen centre of formation slot (row, col)."""
        x = (
            settings.FORMATION_SIDE_MARGIN
            + col * settings.FORMATION_CELL_W
            + settings.FORMATION_CELL_W // 2
            + self._offset_x
        )
        y = (
            settings.FORMATION_TOP_MARGIN
            + row * settings.FORMATION_CELL_H
            + settings.FORMATION_CELL_H // 2
            + self._offset_y
        )
        return x, y

    def _advance_block(self) -> None:
        """Move the block horizontally; bounce and drop when it hits a wall."""
        self._offset_x += self._direction * settings.FORMATION_SPEED
        if self._offset_x <= 0 or self._offset_x >= self._max_offset_x():
            self._offset_x = max(0, min(self._offset_x, self._max_offset_x()))
            self._direction *= -1
            self._offset_y += settings.FORMATION_STEP_DOWN

    def update(self, enemies: pygame.sprite.Group) -> list[tuple[int, int]]:
        """Run all three phases for one frame.

        Returns:
            A list of (x, y) muzzle positions for enemies that fired this frame.
        """
        self._advance_block()
        divers = self._update_formation_enemies(enemies)
        self._maybe_start_dives(enemies, active_divers=divers)
        self._update_divers(enemies)
        return self._collect_shots(enemies)

    def _update_formation_enemies(self, enemies: pygame.sprite.Group) -> int:
        """Snap formation enemies to their slots; return the diver count."""
        divers = 0
        for enemy in enemies:  # type: Enemy
            if enemy.state == STATE_FORMATION:
                enemy.snap_to_slot(*self._slot_position(enemy.row, enemy.col))
            else:
                divers += 1
        return divers

    def _maybe_start_dives(self, enemies: pygame.sprite.Group, active_divers: int) -> None:
        """Randomly promote formation enemies to divers, respecting the cap."""
        room = settings.MAX_CONCURRENT_DIVERS - active_divers
        if room <= 0:
            return
        for enemy in enemies:  # type: Enemy
            if room <= 0:
                break
            if enemy.state == STATE_FORMATION and random.random() < settings.ENEMY_DIVE_CHANCE:
                enemy.start_dive()
                room -= 1

    def _update_divers(self, enemies: pygame.sprite.Group) -> None:
        """Advance every diving enemy; recycle it to formation past the bottom."""
        for enemy in enemies:  # type: Enemy
            if enemy.state == STATE_DIVING and enemy.update_dive():
                enemy.return_to_formation()

    def _collect_shots(self, enemies: pygame.sprite.Group) -> list[tuple[int, int]]:
        """Return muzzle positions for enemies that randomly chose to fire."""
        shots: list[tuple[int, int]] = []
        for enemy in enemies:  # type: Enemy
            if random.random() < settings.ENEMY_SHOOT_CHANCE:
                shots.append((enemy.rect.centerx, enemy.rect.bottom))
        return shots

    def reset(self) -> None:
        """Recentre the block for a fresh game."""
        self._direction = 1
        self._offset_x = 0
        self._offset_y = 0
