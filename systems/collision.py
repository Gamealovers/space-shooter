"""collision.py — AABB and pixel-perfect collision helpers.

The broad phase uses Axis-Aligned Bounding Boxes (pygame.Rect overlap). Where
precision matters we refine with pygame.mask for pixel-perfect hits. These thin
wrappers keep all collision logic in one place so gameplay code stays readable.
"""

from __future__ import annotations

import pygame


def aabb_collide(a: pygame.sprite.Sprite, b: pygame.sprite.Sprite) -> bool:
    """Return True if the two sprites' bounding boxes overlap (broad phase)."""
    return a.rect.colliderect(b.rect)


def mask_collide(a: pygame.sprite.Sprite, b: pygame.sprite.Sprite) -> bool:
    """Return True for a pixel-perfect overlap, falling back to AABB if needed."""
    if not aabb_collide(a, b):
        return False
    if getattr(a, "mask", None) and getattr(b, "mask", None):
        return pygame.sprite.collide_mask(a, b) is not None
    return True


def collide_group(
    sprite: pygame.sprite.Sprite, group: pygame.sprite.Group
) -> list[pygame.sprite.Sprite]:
    """Return every sprite in ``group`` that collides with ``sprite``.

    Uses AABB then mask refinement; nothing is killed (the pool owns lifetimes).
    """
    return pygame.sprite.spritecollide(
        sprite, group, dokill=False, collided=pygame.sprite.collide_mask
    )


def collide_groups(
    group_a: pygame.sprite.Group, group_b: pygame.sprite.Group
) -> dict[pygame.sprite.Sprite, list[pygame.sprite.Sprite]]:
    """Return a map of each ``group_a`` sprite to the ``group_b`` sprites it hit.

    Wraps ``pygame.sprite.groupcollide`` with pixel-perfect masks and no auto
    kill, so the caller decides how to retire pooled objects.
    """
    return pygame.sprite.groupcollide(
        group_a, group_b, dokilla=False, dokillb=False, collided=pygame.sprite.collide_mask
    )
