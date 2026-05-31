"""bullet.py — Poolable projectile entity.

Bullets are NEVER instantiated in the game loop. The ObjectPool pre-creates a
fixed number of them; gameplay code calls ``pool.acquire()`` then ``reset()``.
When a bullet leaves the screen or hits something it deactivates itself, which
removes it from all sprite groups while the pool retains the instance.
"""

from __future__ import annotations

import pygame

from src import settings


class Bullet(pygame.sprite.Sprite):
    """A straight-moving projectile reused via the object pool."""

    def __init__(self, image: pygame.Surface) -> None:
        """Create an inactive bullet holding its sprite image.

        Args:
            image: The pre-loaded bullet surface (shared, loaded once).
        """
        super().__init__()
        self.image: pygame.Surface = image
        self.rect: pygame.Rect = self.image.get_rect()
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)
        self.active: bool = False
        self.direction: int = -1  # -1 = up (player), +1 = down (enemy)
        self.speed: int = settings.BULLET_SPEED

    def reset(self, x: int, y: int, direction: int, speed: int) -> None:
        """Position and arm the bullet for re-use from the pool.

        Args:
            x: Spawn centre x (typically the shooter's centre).
            y: Spawn centre y.
            direction: -1 to travel up, +1 to travel down.
            speed: Pixels travelled per frame.
        """
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = speed
        self.active = True

    def update(self, dt: int) -> None:
        """Move along the vertical axis and self-deactivate when off screen."""
        if not self.active:
            return
        self.rect.y += self.direction * self.speed
        if self.rect.bottom < 0 or self.rect.top > settings.SCREEN_HEIGHT:
            self.deactivate()

    def deactivate(self) -> None:
        """Mark inactive and drop out of all sprite groups (pool keeps ref)."""
        self.active = False
        self.kill()
