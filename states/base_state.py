"""base_state.py — Abstract base class for every game state.

The State Machine pattern: GameManager owns one "current state" and delegates
input, update and draw to it. Each concrete screen (menu, play, game over)
subclasses State and overrides the hooks it needs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:  # avoid a circular import at runtime
    from src.game import GameManager


class State:
    """Base class defining the lifecycle every state shares."""

    def __init__(self, game: "GameManager") -> None:
        """Store a back-reference to the owning GameManager."""
        self.game: "GameManager" = game

    def on_enter(self) -> None:
        """Called once each time this state becomes the active state."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single input event (key press, quit, etc.)."""

    def update(self, dt: int) -> None:
        """Advance the state by ``dt`` milliseconds."""

    def draw(self, surface: pygame.Surface) -> None:
        """Render the state onto ``surface``."""
