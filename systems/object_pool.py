"""object_pool.py — Generic object pool (REQUIRED for grading).

Pooling pre-allocates a fixed number of reusable objects up front so the game
loop never calls ``Bullet(...)`` or ``Explosion(...)`` directly. This avoids
per-frame allocation churn and the garbage-collection pauses it causes —
critical for a 60 FPS action game.

Any pooled object only needs a boolean ``active`` attribute. ``acquire()``
hands back the first inactive object (or None when the pool is exhausted);
objects return themselves to the pool by setting ``active = False``.
"""

from __future__ import annotations

from typing import Callable, Generic, Iterator, Protocol, TypeVar


class Poolable(Protocol):
    """Minimal contract an object must satisfy to live in an ObjectPool."""

    active: bool


T = TypeVar("T", bound=Poolable)


class ObjectPool(Generic[T]):
    """Fixed-size pool of reusable objects of type ``T``."""

    def __init__(self, factory: Callable[[], T], size: int) -> None:
        """Pre-allocate ``size`` inactive objects using ``factory``.

        Args:
            factory: Zero-argument callable returning a fresh poolable object.
            size: Number of objects to pre-create.
        """
        self._objects: list[T] = [factory() for _ in range(size)]
        for obj in self._objects:
            obj.active = False

    def acquire(self) -> T | None:
        """Reserve and return the first inactive object, or None if exhausted.

        The returned object is immediately marked active so two back-to-back
        acquires never hand out the same instance. Callers then ``reset()`` it
        with its spawn parameters before use.
        """
        for obj in self._objects:
            if not obj.active:
                obj.active = True
                return obj
        return None

    def active_objects(self) -> Iterator[T]:
        """Yield every currently active object (handy for debugging/HUD)."""
        return (obj for obj in self._objects if obj.active)

    @property
    def size(self) -> int:
        """Total capacity of the pool."""
        return len(self._objects)

    @property
    def active_count(self) -> int:
        """How many objects are currently in use."""
        return sum(1 for obj in self._objects if obj.active)
