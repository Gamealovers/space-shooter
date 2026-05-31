"""settings.py — Single source of truth for all game constants.

Per the project rules, NO magic numbers live anywhere else in the code base.
Every tunable value (resolution, speeds, colors, gameplay balance, asset paths)
is declared here and imported where needed.
"""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
# Project root = the `space_shooter/` directory (this file lives in src/).
ROOT_DIR: Path = Path(__file__).resolve().parent.parent
ASSETS_DIR: Path = ROOT_DIR / "assets"
IMAGES_DIR: Path = ASSETS_DIR / "images"
SOUNDS_DIR: Path = ASSETS_DIR / "sounds"

# --------------------------------------------------------------------------- #
# Display
# --------------------------------------------------------------------------- #
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60
TITLE: str = "Space Shooter"

# Toggle developer overlays / verbose logging. Must be False in final build.
DEBUG: bool = False

# --------------------------------------------------------------------------- #
# Colors (R, G, B)
# --------------------------------------------------------------------------- #
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 100)
YELLOW = (255, 220, 0)
CYAN = (80, 200, 255)
GREY = (120, 120, 140)
DARK_BLUE = (8, 10, 28)

# --------------------------------------------------------------------------- #
# Player
# --------------------------------------------------------------------------- #
PLAYER_SPEED: int = 5
PLAYER_MAX_HEALTH: int = 3
PLAYER_SHOOT_DELAY: int = 300  # milliseconds between shots
PLAYER_INVULN_TIME: int = 1200  # ms of i-frames after taking a hit

# --------------------------------------------------------------------------- #
# Enemy
# --------------------------------------------------------------------------- #
ENEMY_SPEED: int = 2
ENEMY_HEALTH: int = 1
ENEMY_SCORE_VALUE: int = 10
ENEMY_SHOOT_CHANCE: float = 0.002  # per-frame probability a firing enemy shoots
ENEMY_DIVE_CHANCE: float = 0.0015  # per-frame probability a formation enemy dives

# --------------------------------------------------------------------------- #
# Bullet
# --------------------------------------------------------------------------- #
BULLET_SPEED: int = 8
BULLET_POOL_SIZE: int = 30
ENEMY_BULLET_SPEED: int = 5
ENEMY_BULLET_POOL_SIZE: int = 30

# --------------------------------------------------------------------------- #
# Explosion (sprite-sheet animation)
# --------------------------------------------------------------------------- #
EXPLOSION_POOL_SIZE: int = 16
EXPLOSION_FRAME_SIZE: int = 64  # width == height of one frame in the sheet
EXPLOSION_FPS: int = 18

# --------------------------------------------------------------------------- #
# Enemy animation (sprite-sheet pulse)
# --------------------------------------------------------------------------- #
ENEMY_FRAME_SIZE: int = 40   # width == height of one enemy frame
ENEMY_ANIMATION_FPS: int = 6  # wing-pulse cycles per second

# --------------------------------------------------------------------------- #
# Waves
# --------------------------------------------------------------------------- #
WAVE_ENEMY_COUNT: int = 8
WAVE_SPAWN_DELAY: int = 500  # ms between individual enemy spawns
TOTAL_WAVES: int = 5

# Formation grid geometry.
FORMATION_COLS: int = 8
FORMATION_ROWS: int = 4
FORMATION_CELL_W: int = 64
FORMATION_CELL_H: int = 50
FORMATION_TOP_MARGIN: int = 60
FORMATION_SIDE_MARGIN: int = 40
FORMATION_SPEED: int = 1  # horizontal block speed (px/frame at base FPS)
FORMATION_STEP_DOWN: int = 12  # px the block drops when it hits an edge

# Dive (sinusoidal) path tuning.
DIVE_SPEED: int = 4  # vertical descent speed while diving
DIVE_AMPLITUDE: int = 90  # horizontal swing of the sine path (px)
DIVE_FREQUENCY: float = 0.05  # radians of phase added per frame
MAX_CONCURRENT_DIVERS: int = 3  # cap simultaneous divers so a wave stays fair

# --------------------------------------------------------------------------- #
# Audio
# --------------------------------------------------------------------------- #
SFX_VOLUME: float = 0.5
MUSIC_VOLUME: float = 0.35
MUSIC_FILE: str = "music.wav"
