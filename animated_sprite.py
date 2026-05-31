"""animated_sprite.py — Sprite-sheet animation base class.

AnimatedSprite slices a horizontal sprite sheet into equal frames and steps
through them on a fixed timeline. The explosion effect subclasses it as a
one-shot animation that deactivates itself when the final frame is reached
(so it can live inside an ObjectPool).
"""

from __future__ import annotations

import pygame

from src import settings


class AnimatedSprite(pygame.sprite.Sprite):
    """A sprite that animates frames sliced from a sprite sheet."""

    def __init__(
        self,
        sheet: pygame.Surface,
        frame_width: int,
        frame_height: int,
        fps: int = 12,
        loop: bool = True,
    ) -> None:
        """Slice `sheet` into frames and prepare the animation timeline.

        Args:
            sheet: Horizontal strip of equally sized frames.
            frame_width: Width of a single frame in pixels.
            frame_height: Height of a single frame in pixels.
            fps: Playback speed in frames per second.
            loop: When False the animation runs once then deactivates.
        """
        super().__init__()
        self.frames: list[pygame.Surface] = self._slice_sheet(
            sheet, frame_width, frame_height
        )
        self.loop: bool = loop
        self.active: bool = False
        self.current_frame: int = 0
        self.animation_speed: float = 1000.0 / fps  # ms per frame
        self._elapsed: float = 0.0  # ms accumulated toward the next frame
        self.image: pygame.Surface = self.frames[0]
        self.rect: pygame.Rect = self.image.get_rect()

    @staticmethod
    def _slice_sheet(
        sheet: pygame.Surface, frame_width: int, frame_height: int
    ) -> list[pygame.Surface]:
        """Cut the sheet into a list of frame surfaces, left to right."""
        count = sheet.get_width() // frame_width
        frames: list[pygame.Surface] = []
        for i in range(count):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frames.append(sheet.subsurface(rect).copy())
        return frames

    def update(self, dt: int) -> None:
        """Advance the animation by ``dt`` ms (frame-rate independent)."""
        if not self.active:
            return
        self._elapsed += dt
        while self._elapsed >= self.animation_speed:
            self._elapsed -= self.animation_speed
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.deactivate()
                    return
            self.image = self.frames[self.current_frame]

    def deactivate(self) -> None:
        """Mark inactive and remove from all sprite groups (pool keeps it)."""
        self.active = False
        self.kill()


class Explosion(AnimatedSprite):
    """One-shot explosion effect driven by the explosion sprite sheet."""

    def __init__(self, sheet: pygame.Surface) -> None:
        """Build a non-looping explosion from the shared sheet surface."""
        super().__init__(
            sheet,
            settings.EXPLOSION_FRAME_SIZE,
            settings.EXPLOSION_FRAME_SIZE,
            fps=settings.EXPLOSION_FPS,
            loop=False,
        )

    def reset(self, center: tuple[int, int]) -> None:
        """Restart the animation centred on `center` (pool re-use entry point)."""
        self.active = True
        self.current_frame = 0
        self._elapsed = 0.0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
