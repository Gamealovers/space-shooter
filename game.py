"""game.py — GameManager, the top-level state machine and resource owner.

GameManager initialises pygame, loads every asset exactly once, and runs the
main loop, delegating update()/draw() to whichever State is current. Shared,
cross-state data (final score, victory flag) also lives here.
"""

from __future__ import annotations

import pygame

from src import assets, settings
from src.states.gameover_state import GameOverState
from src.states.menu_state import MenuState
from src.states.play_state import PlayState


class GameManager:
    """Owns the window, the shared assets, and the active game state."""

    def __init__(self) -> None:
        """Boot pygame, load assets once, and enter the menu state."""
        pygame.init()
        self._init_mixer()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        self.fonts: dict[str, pygame.font.Font] = {
            "small": pygame.font.Font(None, 28),
            "medium": pygame.font.Font(None, 48),
            "large": pygame.font.Font(None, 84),
        }
        self.images: dict[str, pygame.Surface] = self._load_images()
        self.sounds: dict[str, pygame.mixer.Sound | None] = self._load_sounds()
        self._load_music()

        # Cross-state result data filled in by PlayState, read by GameOverState.
        self.final_score: int = 0
        self.victory: bool = False

        self.states: dict[str, object] = {
            "menu": MenuState(self),
            "play": PlayState(self),
            "gameover": GameOverState(self),
        }
        self.current_state = self.states["menu"]
        self.current_state.on_enter()

    @staticmethod
    def _init_mixer() -> None:
        """Initialise the audio mixer, tolerating headless/no-audio setups."""
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except pygame.error:
            pass  # No audio device — the game runs silently.

    @staticmethod
    def _load_images() -> dict[str, pygame.Surface]:
        """Load every sprite once and return them keyed by short name."""
        return {
            "player": assets.load_image("player.png"),
            "enemy_sheet": assets.load_image("enemy_sheet.png"),
            "bullet": assets.load_image("bullet.png"),
            "enemy_bullet": assets.load_image("enemy_bullet.png"),
            "explosion_sheet": assets.load_image("explosion_sheet.png"),
            "background": assets.load_image("background.png", alpha=False),
        }

    @staticmethod
    def _load_sounds() -> dict[str, pygame.mixer.Sound | None]:
        """Load every SFX once (returns None values when audio is disabled)."""
        return {
            "shoot": assets.load_sound("shoot.wav"),
            "explosion": assets.load_sound("explosion.wav"),
        }

    def _load_music(self) -> None:
        """Pre-load the background music track into the streaming mixer."""
        if not pygame.mixer.get_init():
            return
        path = settings.SOUNDS_DIR / settings.MUSIC_FILE
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
        except pygame.error:
            pass

    def _start_music(self) -> None:
        """Begin looping background music (silently ignores missing audio)."""
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _stop_music(self) -> None:
        """Stop background music gracefully."""
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    def change_state(self, name: str) -> None:
        """Switch the active state, fire its on_enter hook, and manage music."""
        if name == "play":
            self._start_music()
        else:
            self._stop_music()
        self.current_state = self.states[name]
        self.current_state.on_enter()

    def quit(self) -> None:
        """Request a clean shutdown of the main loop."""
        self.running = False

    def run(self) -> None:
        """Run the main loop until the player quits."""
        while self.running:
            dt = self.clock.tick(settings.FPS)
            self._process_events()
            self.current_state.update(dt)
            self.current_state.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def _process_events(self) -> None:
        """Pump the event queue, handling quit and delegating the rest."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            else:
                self.current_state.handle_event(event)
