"""gameover_state.py — Win / lose results screen."""

from __future__ import annotations

import pygame

from src import settings
from src.states.base_state import State


class GameOverState(State):
    """Shows victory or defeat plus the final score, and offers a restart."""

    def on_enter(self) -> None:
        """Read the result data the PlayState recorded on the GameManager."""
        self._background: pygame.Surface = self.game.images["background"]
        self._victory: bool = self.game.victory
        self._score: int = self.game.final_score

    def handle_event(self, event: pygame.event.Event) -> None:
        """Replay on Enter/Space, return to the menu on Escape."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.change_state("play")
        elif event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

    def update(self, dt: int) -> None:
        """Static results screen; nothing to advance."""

    def draw(self, surface: pygame.Surface) -> None:
        """Render the outcome banner, score, and prompts."""
        surface.blit(self._background, (0, 0))
        heading = "YOU WIN!" if self._victory else "GAME OVER"
        color = settings.GREEN if self._victory else settings.RED
        self._draw_centered(surface, heading, "large", color, 210)
        self._draw_centered(
            surface, f"Final Score: {self._score}", "medium", settings.WHITE, 320
        )
        self._draw_centered(
            surface, "ENTER to play again - ESC for menu", "small", settings.GREY, 400
        )

    def _draw_centered(
        self, surface: pygame.Surface, text: str, font_key: str, color, y: int
    ) -> None:
        """Helper: blit horizontally-centred text at vertical position ``y``."""
        rendered = self.game.fonts[font_key].render(text, True, color)
        rect = rendered.get_rect(center=(settings.SCREEN_WIDTH // 2, y))
        surface.blit(rendered, rect)
