# Space Shooter

A Galaga-style 2D arcade shooter built in **Python / Pygame** for the BMI4242
Game Programming course. Survive five waves of formation-flying, dive-bombing
enemies.

![status](https://img.shields.io/badge/build-runnable-success)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
#    (On Python 3.13+: if PNGs fail to load, use the drop-in community edition)
#    pip install "pygame-ce>=2.5"

# 2. Generate placeholder art & sound (one time)
python tools/generate_assets.py

# 3. Play
python main.py
```

## Controls

| Action | Keys |
|--------|------|
| Move   | Arrow keys or `WASD` |
| Shoot  | `Space` |
| Back to menu | `Esc` |
| Start / Replay | `Enter` |

**Goal:** clear all 5 waves to win. Lose all 3 health points and it's game over.

## Architecture

State-machine driven, OOP entities, with the engineering requirements the course
grades on:

```
main.py                 # entry point only
src/
  settings.py           # single source of truth for every constant
  game.py               # GameManager: state machine + asset owner + main loop
  assets.py             # load-once, cached image/sound helpers
  states/               # menu / play / gameover  (State subclasses)
  entities/             # Player, Enemy, Bullet, AnimatedSprite/Explosion
  systems/
    object_pool.py      # generic ObjectPool[T]  (bullets & explosions)
    collision.py        # AABB broad phase + pixel-perfect mask refinement
    enemy_ai.py         # formation march → sinusoidal dive → downward fire
    wave_manager.py     # wave spawning + win condition
  ui/hud.py             # score, health, wave counter
tools/
  generate_assets.py    # procedural placeholder art + SFX
  build_tdd_pdf.py      # renders docs/TDD_report.md → .pdf
docs/TDD_report.{md,pdf}
```

Design details are in [`docs/TDD_report.md`](docs/TDD_report.md) and the project
rules in [`CLAUDE.md`](CLAUDE.md).

## Feature Checklist (grading)

| Feature | Location | ✓ |
|---------|----------|---|
| Player movement (keyboard) | `entities/player.py` | ✅ |
| Bullet shooting (spacebar) | `entities/bullet.py` + `object_pool.py` | ✅ |
| Enemy spawning in waves | `systems/wave_manager.py` | ✅ |
| Enemy AI movement | `systems/enemy_ai.py` | ✅ |
| Sprite animation (explosion) | `entities/animated_sprite.py` | ✅ |
| Collision detection | `systems/collision.py` | ✅ |
| Object pooling | `systems/object_pool.py` | ✅ |
| HUD (score, health, wave) | `ui/hud.py` | ✅ |
| Sound effects | `states/play_state.py` | ✅ |
| Win condition (survive N waves) | `systems/wave_manager.py` | ✅ |
| Lose condition (health = 0) | `states/play_state.py` | ✅ |
| Main menu screen | `states/menu_state.py` | ✅ |
| Game over screen | `states/gameover_state.py` | ✅ |

## Standalone Build

```bash
pip install pyinstaller
# macOS / Linux:
pyinstaller --onefile --windowed --add-data "assets:assets" main.py
# Windows:
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```
