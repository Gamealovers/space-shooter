"""main.py — Entry point.

By project rule this file contains ONLY the launch glue. All game logic lives
under src/. Run with:  python main.py
"""

from __future__ import annotations

from src.game import GameManager


def main() -> None:
    """Create the GameManager and run the main loop."""
    GameManager().run()


if __name__ == "__main__":
    main()
