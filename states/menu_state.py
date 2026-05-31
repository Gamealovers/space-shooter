"""menu_state.py — The main menu screen."""

from __future__ import annotations

import pygame

from src import settings
from src.states.base_state import State


class MenuState(State):
    """Title screen: prompts the player to start or quit."""

    def on_enter(self) -> None:
        """Cache the starfield background when the menu becomes active."""
        self._background: pygame.Surface = self.game.images["background"]

    def handle_event(self, event: pygame.event.Event) -> None:
        """Start the game on Enter/Space, quit on Escape."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.change_state("play")
        elif event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: int) -> None:
        """The menu is static; nothing to advance."""

    def draw(self, surface: pygame.Surface) -> None:
        """Render the title, prompt and control hints."""
        surface.blit(self._background, (0, 0))
        self._draw_centered(surface, settings.TITLE, "large", settings.CYAN, 200)
        self._draw_centered(
            surface, "Press ENTER to Start", "medium", settings.WHITE, 320
        )
        self._draw_centered(
            surface, "Arrows / WASD to move - SPACE to shoot", "small", settings.GREY, 400
        )
        self._draw_centered(surface, "ESC to quit", "small", settings.GREY, 430)

    def _draw_centered(
        self, surface: pygame.Surface, text: str, font_key: str, color, y: int
    ) -> None:
        """Helper: blit horizontally-centred text at vertical position ``y``."""
        rendered = self.game.fonts[font_key].render(text, True, color)
        rect = rendered.get_rect(center=(settings.SCREEN_WIDTH // 2, y))
        surface.blit(rendered, rect)
