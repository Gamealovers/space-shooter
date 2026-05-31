"""hud.py — Heads-up display: score, health and wave counter."""

from __future__ import annotations

import pygame

from src import settings


class HUD:
    """Draws the in-game overlay (score, remaining health, current wave)."""

    def __init__(self, font: pygame.font.Font) -> None:
        """Store the font used for all HUD text."""
        self._font: pygame.font.Font = font

    def draw(self, surface: pygame.Surface, score: int, health: int, wave: int) -> None:
        """Render the full HUD for the current frame."""
        self._draw_score(surface, score)
        self._draw_wave(surface, wave)
        self._draw_health(surface, health)

    def _draw_score(self, surface: pygame.Surface, score: int) -> None:
        """Top-left score readout."""
        text = self._font.render(f"SCORE {score}", True, settings.WHITE)
        surface.blit(text, (12, 10))

    def _draw_wave(self, surface: pygame.Surface, wave: int) -> None:
        """Top-centre wave counter."""
        label = f"WAVE {wave}/{settings.TOTAL_WAVES}"
        text = self._font.render(label, True, settings.YELLOW)
        rect = text.get_rect(midtop=(settings.SCREEN_WIDTH // 2, 10))
        surface.blit(text, rect)

    def _draw_health(self, surface: pygame.Surface, health: int) -> None:
        """Top-right row of heart icons representing remaining health."""
        radius = 9
        gap = 26
        right = settings.SCREEN_WIDTH - 14
        for i in range(settings.PLAYER_MAX_HEALTH):
            cx = right - i * gap
            filled = (settings.PLAYER_MAX_HEALTH - 1 - i) < health
            color = settings.RED if filled else settings.GREY
            pygame.draw.circle(surface, color, (cx, 22), radius)
