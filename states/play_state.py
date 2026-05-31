"""play_state.py — Core gameplay state.

Owns the player, all sprite groups, the bullet/explosion object pools, the
formation AI and the wave manager. Every frame it gathers input, advances the
world, resolves collisions and checks the win/lose conditions. State is rebuilt
in ``on_enter`` so the player can replay cleanly.
"""

from __future__ import annotations

import pygame

from src import settings
from src.entities.animated_sprite import Explosion
from src.entities.bullet import Bullet
from src.entities.enemy import Enemy
from src.entities.player import Player
from src.states.base_state import State
from src.systems import collision
from src.systems.enemy_ai import FormationManager
from src.systems.object_pool import ObjectPool
from src.systems.wave_manager import WaveManager
from src.ui.hud import HUD


class PlayState(State):
    """The playable round: movement, shooting, waves, collisions, scoring."""

    def on_enter(self) -> None:
        """Build a fresh game world for a new (or replayed) round."""
        images = self.game.images
        self._background: pygame.Surface = images["background"]
        self._player: Player = Player(images["player"])

        self._enemies: pygame.sprite.Group = pygame.sprite.Group()
        self._player_bullets: pygame.sprite.Group = pygame.sprite.Group()
        self._enemy_bullets: pygame.sprite.Group = pygame.sprite.Group()
        self._explosions: pygame.sprite.Group = pygame.sprite.Group()

        self._bullet_pool: ObjectPool[Bullet] = ObjectPool(
            lambda: Bullet(images["bullet"]), settings.BULLET_POOL_SIZE
        )
        self._enemy_bullet_pool: ObjectPool[Bullet] = ObjectPool(
            lambda: Bullet(images["enemy_bullet"]), settings.ENEMY_BULLET_POOL_SIZE
        )
        self._explosion_pool: ObjectPool[Explosion] = ObjectPool(
            lambda: Explosion(images["explosion_sheet"]), settings.EXPLOSION_POOL_SIZE
        )

        self._formation: FormationManager = FormationManager()
        self._waves: WaveManager = WaveManager(images["enemy_sheet"])
        self._hud: HUD = HUD(self.game.fonts["small"])
        self._score: int = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Allow bailing out to the menu with Escape."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("menu")

    def update(self, dt: int) -> None:
        """Advance input, AI, projectiles, collisions and end conditions."""
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self._player.handle_input(keys)
        self._player.update(dt)
        if keys[pygame.K_SPACE]:
            self._player_shoot(now)

        self._waves.update(now, self._enemies)
        for muzzle in self._formation.update(self._enemies):
            self._enemy_shoot(muzzle)
        self._enemies.update(dt)

        self._player_bullets.update(dt)
        self._enemy_bullets.update(dt)
        self._explosions.update(dt)

        self._handle_collisions(now)
        self._check_end_conditions()

    def _player_shoot(self, now: int) -> None:
        """Fire an upward bullet from the pool, respecting the cooldown."""
        if not self._player.can_shoot(now):
            return
        bullet = self._bullet_pool.acquire()
        if bullet is None:
            return
        bullet.reset(self._player.rect.centerx, self._player.rect.top, -1, settings.BULLET_SPEED)
        self._player_bullets.add(bullet)
        self._play("shoot")

    def _enemy_shoot(self, muzzle: tuple[int, int]) -> None:
        """Fire a downward bullet from the enemy pool at ``muzzle``."""
        bullet = self._enemy_bullet_pool.acquire()
        if bullet is None:
            return
        bullet.reset(muzzle[0], muzzle[1], 1, settings.ENEMY_BULLET_SPEED)
        self._enemy_bullets.add(bullet)

    def _handle_collisions(self, now: int) -> None:
        """Resolve all collision pairs for this frame."""
        self._resolve_player_bullets_vs_enemies()
        self._resolve_enemy_fire_vs_player(now)

    def _resolve_player_bullets_vs_enemies(self) -> None:
        """Destroy enemies struck by player bullets and award score."""
        hits = collision.collide_groups(self._player_bullets, self._enemies)
        for bullet, struck in hits.items():
            bullet.deactivate()
            for enemy in struck:
                if isinstance(enemy, Enemy) and enemy.hit():
                    self._destroy_enemy(enemy)

    def _resolve_enemy_fire_vs_player(self, now: int) -> None:
        """Damage the player from enemy bullets or body contact."""
        incoming = collision.collide_group(self._player, self._enemy_bullets)
        for bullet in incoming:
            bullet.deactivate()
        rammers = collision.collide_group(self._player, self._enemies)
        if (incoming or rammers) and self._player.take_damage(now):
            self._spawn_explosion(self._player.rect.center)
        for enemy in rammers:
            if isinstance(enemy, Enemy):
                self._destroy_enemy(enemy)

    def _destroy_enemy(self, enemy: Enemy) -> None:
        """Blow up an enemy, score it, and remove it from play."""
        self._spawn_explosion(enemy.rect.center)
        enemy.kill()
        self._score += settings.ENEMY_SCORE_VALUE

    def _spawn_explosion(self, center: tuple[int, int]) -> None:
        """Pull an explosion from the pool and play the boom SFX."""
        explosion = self._explosion_pool.acquire()
        if explosion is not None:
            explosion.reset(center)
            self._explosions.add(explosion)
        self._play("explosion")

    def _check_end_conditions(self) -> None:
        """Transition to game over on death (lose) or final clear (win)."""
        if not self._player.is_alive():
            self._end_game(victory=False)
        elif self._waves.won and len(self._enemies) == 0:
            self._end_game(victory=True)

    def _end_game(self, victory: bool) -> None:
        """Record the result on the GameManager and switch to game over."""
        self.game.final_score = self._score
        self.game.victory = victory
        self.game.change_state("gameover")

    def _play(self, name: str) -> None:
        """Play a named sound effect if audio is available."""
        sound = self.game.sounds.get(name)
        if sound is not None:
            sound.play()

    def draw(self, surface: pygame.Surface) -> None:
        """Render the world bottom-up: background, projectiles, actors, HUD."""
        surface.blit(self._background, (0, 0))
        self._player_bullets.draw(surface)
        self._enemy_bullets.draw(surface)
        self._enemies.draw(surface)
        self._explosions.draw(surface)
        self._player.draw(surface)
        self._hud.draw(surface, self._score, self._player.health, self._waves.wave)
