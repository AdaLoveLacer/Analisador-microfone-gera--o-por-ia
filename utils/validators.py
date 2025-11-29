"""Input validation utilities."""

import re
import os
from typing import Any, Dict, List
from .exceptions import ValidationException


class Validator:
    """Utility class for input validation."""

    @staticmethod
    def is_valid_keyword_id(keyword_id: str) -> bool:
        """Validate keyword ID format."""
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, keyword_id)) and len(keyword_id) <= 50

    @staticmethod
    def is_valid_keyword_pattern(pattern: str) -> bool:
        """Validate keyword pattern."""
        if not pattern or not isinstance(pattern, str):
            return False
        if len(pattern) < 2 or len(pattern) > 100:
            return False
        return True

    @staticmethod
    def is_valid_sound_id(sound_id: str) -> bool:
        """Validate sound ID format."""
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, sound_id)) and len(sound_id) <= 50

    @staticmethod
    def is_valid_file_path(file_path: str) -> bool:
        """Validate file path exists and is readable."""
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Handle both absolute and relative paths
        if os.path.isabs(file_path):
            return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
        else:
            # For relative paths, just check format
            return len(file_path) > 0 and len(file_path) < 500

    @staticmethod
    def is_valid_volume(volume: float) -> bool:
        """Validate volume (0.0 to 1.0)."""
        try:
            v = float(volume)
            return 0.0 <= v <= 1.0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_confidence_score(score: float) -> bool:
        """Validate confidence score (0.0 to 1.0)."""
        try:
            s = float(score)
            return 0.0 <= s <= 1.0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_sample_rate(sample_rate: int) -> bool:
        """Validate audio sample rate."""
        valid_rates = [8000, 16000, 22050, 44100, 48000]
        return sample_rate in valid_rates

    @staticmethod
    def is_valid_chunk_size(chunk_size: int) -> bool:
        """Validate audio chunk size."""
        return chunk_size > 0 and chunk_size <= 65536 and chunk_size % 256 == 0

    @staticmethod
    def is_valid_channels(channels: int) -> bool:
        """Validate number of audio channels."""
        return channels in [1, 2]

    @staticmethod
    def is_valid_language_code(lang: str) -> bool:
        """Validate language code."""
        valid_langs = ["pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh"]
        return lang in valid_langs

    @staticmethod
    def is_valid_whisper_model(model: str) -> bool:
        """Validate Whisper model name."""
        valid_models = ["tiny", "base", "small", "medium", "large"]
        return model in valid_models

    @staticmethod
    def is_valid_device_id(device_id: int) -> bool:
        """Validate audio device ID."""
        return isinstance(device_id, int) and device_id >= -1

    @staticmethod
    def validate_keyword(keyword: Dict[str, Any]) -> bool:
        """Validate keyword structure."""
        required_fields = ["id", "name", "pattern", "enabled", "sound_id"]
        
        # Check required fields
        if not all(field in keyword for field in required_fields):
            return False
        
        # Validate ID
        if not Validator.is_valid_keyword_id(keyword["id"]):
            return False
        
        # Validate pattern
        if not Validator.is_valid_keyword_pattern(keyword["pattern"]):
            return False
        
        # Validate name
        if not isinstance(keyword["name"], str) or len(keyword["name"]) == 0:
            return False
        
        # Validate enabled
        if not isinstance(keyword["enabled"], bool):
            return False
        
        # Validate sound_id
        if not Validator.is_valid_sound_id(keyword["sound_id"]):
            return False
        
        # Validate variations (optional)
        if "variations" in keyword:
            if not isinstance(keyword["variations"], list):
                return False
            if not all(isinstance(v, str) for v in keyword["variations"]):
                return False
        
        # Validate weight (optional)
        if "weight" in keyword:
            if not isinstance(keyword["weight"], (int, float)) or not (0 <= keyword["weight"] <= 1):
                return False
        
        return True

    @staticmethod
    def validate_sound(sound: Dict[str, Any]) -> bool:
        """Validate sound structure."""
        required_fields = ["id", "name", "file_path", "volume", "enabled", "category"]
        
        # Check required fields
        if not all(field in sound for field in required_fields):
            return False
        
        # Validate ID
        if not Validator.is_valid_sound_id(sound["id"]):
            return False
        
        # Validate name
        if not isinstance(sound["name"], str) or len(sound["name"]) == 0:
            return False
        
        # Validate file_path
        if not isinstance(sound["file_path"], str):
            return False
        
        # Validate volume
        if not Validator.is_valid_volume(sound["volume"]):
            return False
        
        # Validate enabled
        if not isinstance(sound["enabled"], bool):
            return False
        
        # Validate category
        valid_categories = ["meme", "notification", "effect", "custom"]
        if sound["category"] not in valid_categories:
            return False
        
        return True


def validate_or_raise(condition: bool, message: str) -> None:
    """Raise ValidationException if condition is False."""
    if not condition:
        raise ValidationException(message)
