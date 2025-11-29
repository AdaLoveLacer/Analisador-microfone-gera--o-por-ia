"""Audio utilities for processing and validation."""

import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_audio(
    audio_data: np.ndarray, target_db: float = -20.0
) -> np.ndarray:
    """
    Normalize audio to target dB level.

    Args:
        audio_data: Audio samples as numpy array
        target_db: Target dB level (-20.0 is typical)

    Returns:
        Normalized audio data
    """
    try:
        # Avoid division by zero
        if np.max(np.abs(audio_data)) == 0:
            return audio_data

        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data**2))

        # Avoid log of zero
        if rms <= 0:
            return audio_data

        # Current dB level
        current_db = 20 * np.log10(rms)

        # Calculate gain needed
        gain_db = target_db - current_db
        gain_linear = 10 ** (gain_db / 20)

        return audio_data * gain_linear
    except Exception as e:
        logger.error(f"Error normalizing audio: {e}")
        return audio_data


def detect_silence(
    audio_data: np.ndarray,
    sample_rate: int,
    threshold: float = 0.02,
    duration_ms: int = 300,
) -> Tuple[bool, float]:
    """
    Detect if audio contains silence.

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        threshold: Silence threshold (0.0 to 1.0)
        duration_ms: Duration of silence to detect (milliseconds)

    Returns:
        Tuple of (is_silent, energy_level)
    """
    try:
        if len(audio_data) == 0:
            return True, 0.0

        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio_data**2))

        # Check if below threshold
        is_silent = energy < threshold

        return is_silent, float(energy)
    except Exception as e:
        logger.error(f"Error detecting silence: {e}")
        return False, 0.0


def get_audio_energy(audio_data: np.ndarray) -> float:
    """
    Calculate audio energy level (0.0 to 1.0).

    Args:
        audio_data: Audio samples as numpy array

    Returns:
        Energy level
    """
    try:
        if len(audio_data) == 0:
            return 0.0

        energy = np.sqrt(np.mean(audio_data**2))
        return min(float(energy), 1.0)
    except Exception as e:
        logger.error(f"Error calculating energy: {e}")
        return 0.0


def resample_audio(
    audio_data: np.ndarray,
    original_sr: int,
    target_sr: int,
) -> np.ndarray:
    """
    Resample audio to target sample rate.

    Args:
        audio_data: Audio samples
        original_sr: Original sample rate
        target_sr: Target sample rate

    Returns:
        Resampled audio data
    """
    try:
        if original_sr == target_sr:
            return audio_data

        # Simple linear interpolation
        num_samples = int(len(audio_data) * target_sr / original_sr)
        indices = np.linspace(0, len(audio_data) - 1, num_samples)
        resampled = np.interp(indices, np.arange(len(audio_data)), audio_data)

        return resampled
    except Exception as e:
        logger.error(f"Error resampling audio: {e}")
        return audio_data


def convert_bytes_to_numpy(
    audio_bytes: bytes, sample_width: int, num_channels: int
) -> np.ndarray:
    """
    Convert audio bytes to numpy array.

    Args:
        audio_bytes: Audio data as bytes
        sample_width: Sample width in bytes (1, 2, or 4)
        num_channels: Number of audio channels

    Returns:
        Audio data as numpy array
    """
    try:
        # Convert bytes to numpy array
        if sample_width == 1:
            dtype = np.uint8
        elif sample_width == 2:
            dtype = np.int16
        elif sample_width == 4:
            dtype = np.int32
        else:
            raise ValueError(f"Invalid sample width: {sample_width}")

        audio_data = np.frombuffer(audio_bytes, dtype=dtype).astype(np.float32)

        # Normalize to -1.0 to 1.0
        max_value = np.iinfo(dtype).max
        audio_data = audio_data / max_value

        # Convert stereo to mono if needed
        if num_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
            audio_data = np.mean(audio_data, axis=1)

        return audio_data
    except Exception as e:
        logger.error(f"Error converting audio bytes: {e}")
        return np.array([])


def validate_audio_chunk(
    audio_data: np.ndarray,
    min_duration_seconds: float,
    sample_rate: int,
) -> bool:
    """
    Validate audio chunk.

    Args:
        audio_data: Audio samples
        min_duration_seconds: Minimum duration required
        sample_rate: Sample rate in Hz

    Returns:
        True if valid
    """
    try:
        min_samples = int(min_duration_seconds * sample_rate)
        return len(audio_data) >= min_samples
    except Exception as e:
        logger.error(f"Error validating audio chunk: {e}")
        return False


def apply_gain(audio_data: np.ndarray, gain_db: float) -> np.ndarray:
    """
    Apply gain to audio.

    Args:
        audio_data: Audio samples
        gain_db: Gain in dB

    Returns:
        Audio with gain applied
    """
    try:
        gain_linear = 10 ** (gain_db / 20)
        return np.clip(audio_data * gain_linear, -1.0, 1.0)
    except Exception as e:
        logger.error(f"Error applying gain: {e}")
        return audio_data
