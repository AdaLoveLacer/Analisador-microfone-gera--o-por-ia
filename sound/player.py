"""Sound playback and management."""

import pygame
import logging
from pathlib import Path
from typing import Optional, Dict, List
from utils.exceptions import SoundException, SoundFileException

logger = logging.getLogger(__name__)

# Initialize pygame mixer
try:
    pygame.mixer.init()
except Exception as e:
    logger.warning(f"Failed to initialize pygame mixer: {e}")


class SoundPlayer:
    """Plays sound files."""

    def __init__(self, volume: float = 0.8):
        """
        Initialize SoundPlayer.

        Args:
            volume: Default volume (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.current_sound: Optional[pygame.mixer.Sound] = None
        self.is_playing = False

    def play(self, file_path: str, volume: Optional[float] = None) -> bool:
        """
        Play a sound file.

        Args:
            file_path: Path to sound file
            volume: Volume override (0.0 to 1.0)

        Returns:
            True if sound played successfully
        """
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                raise SoundFileException(f"Sound file not found: {file_path}")

            # Load sound
            sound = pygame.mixer.Sound(str(path))

            # Set volume
            vol = volume if volume is not None else self.volume
            vol = max(0.0, min(1.0, vol))
            sound.set_volume(vol)

            # Play
            sound.play()
            self.current_sound = sound
            self.is_playing = True

            logger.info(f"Playing sound: {file_path} (volume={vol})")
            return True

        except pygame.error as e:
            logger.error(f"Pygame error playing sound: {e}")
            raise SoundException(f"Error playing sound: {e}")
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            raise SoundException(f"Error playing sound: {e}")

    def stop(self) -> None:
        """Stop current sound."""
        try:
            if self.current_sound:
                self.current_sound.stop()
                self.is_playing = False
            pygame.mixer.stop()
            logger.info("Sound stopped")
        except Exception as e:
            logger.error(f"Error stopping sound: {e}")

    def set_volume(self, volume: float) -> None:
        """
        Set volume level.

        Args:
            volume: Volume (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.current_sound:
            self.current_sound.set_volume(self.volume)

    def is_playing_sound(self) -> bool:
        """Check if a sound is currently playing."""
        return pygame.mixer.get_busy()

    def wait(self) -> None:
        """Wait for current sound to finish."""
        try:
            if self.current_sound:
                while pygame.mixer.get_busy():
                    import time
                    time.sleep(0.01)
                self.is_playing = False
        except Exception as e:
            logger.error(f"Error waiting for sound: {e}")


class SoundManager:
    """Manages sound library and playback."""

    def __init__(self, sounds_config: List[Dict]):
        """
        Initialize SoundManager.

        Args:
            sounds_config: List of sound configurations
        """
        self.sounds_config = {s["id"]: s for s in sounds_config}
        self.player = SoundPlayer()
        self._validate_sounds()

    def _validate_sounds(self) -> None:
        """Validate all configured sounds."""
        for sound_id, sound_data in self.sounds_config.items():
            file_path = sound_data.get("file_path")
            if file_path and not Path(file_path).exists():
                logger.warning(f"Sound file not found: {file_path} (ID: {sound_id})")

    def play_sound(self, sound_id: str) -> bool:
        """
        Play a sound by ID.

        Args:
            sound_id: Sound ID from configuration

        Returns:
            True if sound played
        """
        try:
            if sound_id not in self.sounds_config:
                logger.warning(f"Sound ID not found: {sound_id}")
                return False

            sound_data = self.sounds_config[sound_id]

            # Check if enabled
            if not sound_data.get("enabled", True):
                logger.info(f"Sound disabled: {sound_id}")
                return False

            file_path = sound_data.get("file_path")
            if not file_path:
                logger.error(f"No file path for sound: {sound_id}")
                return False

            volume = sound_data.get("volume", 0.8)

            return self.player.play(file_path, volume)

        except Exception as e:
            logger.error(f"Error playing sound {sound_id}: {e}")
            return False

    def preview_sound(self, sound_id: str) -> bool:
        """
        Preview a sound (same as play_sound).

        Args:
            sound_id: Sound ID

        Returns:
            True if preview played
        """
        return self.play_sound(sound_id)

    def stop_sound(self) -> None:
        """Stop current sound playback."""
        self.player.stop()

    def set_volume(self, volume: float) -> None:
        """
        Set global volume.

        Args:
            volume: Volume (0.0 to 1.0)
        """
        self.player.set_volume(volume)

    def update_sounds_config(self, sounds_config: List[Dict]) -> None:
        """Update sound configurations."""
        self.sounds_config = {s["id"]: s for s in sounds_config}
        self._validate_sounds()

    def get_sound_info(self, sound_id: str) -> Optional[Dict]:
        """Get sound information."""
        return self.sounds_config.get(sound_id)

    def list_sounds(self) -> List[Dict]:
        """List all configured sounds."""
        return list(self.sounds_config.values())

    def is_sound_playing(self) -> bool:
        """Check if any sound is playing."""
        return self.player.is_playing_sound()
