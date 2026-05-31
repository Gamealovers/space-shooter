"""player.py — The player-controlled ship entity."""

from __future__ import annotations

import pygame

from src import settings


class Player(pygame.sprite.Sprite):
    """Keyboard-driven ship: moves, shoots on a cooldown, and takes damage."""

    def __init__(self, image: pygame.Surface) -> None:
        """Spawn the ship centred near the bottom of the screen.

        Args:
            image: Pre-loaded ship surface (loaded once at start-up).
        """
        super().__init__()
        self.image: pygame.Surface = image
        start_x = settings.SCREEN_WIDTH // 2
        start_y = settings.SCREEN_HEIGHT - 60
        self.rect: pygame.Rect = self.image.get_rect(center=(start_x, start_y))
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)
        self.health: int = settings.PLAYER_MAX_HEALTH
        self._last_shot: int = 0
        self._invuln_until: int = 0
        self._visible: bool = True

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Move the ship from the current key state, clamped to the screen."""
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (
            keys[pygame.K_UP] or keys[pygame.K_w]
        )
        self.rect.x += dx * settings.PLAYER_SPEED
        self.rect.y += dy * settings.PLAYER_SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    def can_shoot(self, now: int) -> bool:
        """Return True if the shoot cooldown has elapsed, recording the shot."""
        if now - self._last_shot < settings.PLAYER_SHOOT_DELAY:
            return False
        self._last_shot = now
        return True

    def take_damage(self, now: int) -> bool:
        """Apply one point of damage unless in i-frames; return True if hit landed."""
        if now < self._invuln_until:
            return False
        self.health -= 1
        self._invuln_until = now + settings.PLAYER_INVULN_TIME
        return True

    def is_alive(self) -> bool:
        """Return True while the ship still has health remaining."""
        return self.health > 0

    def update(self, dt: int) -> None:
        """Flicker the sprite while invulnerable to signal the i-frame window."""
        now = pygame.time.get_ticks()
        self._visible = now >= self._invuln_until or (now // 100) % 2 == 0

    def draw(self, surface: pygame.Surface) -> None:
        """Blit the ship, honouring the invulnerability flicker."""
        if self._visible:
            surface.blit(self.image, self.rect)
