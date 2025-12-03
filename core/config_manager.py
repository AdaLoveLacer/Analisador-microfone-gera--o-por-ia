"""Configuration manager for persistent config management."""

import json
import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
from utils.exceptions import ConfigException, ConfigValidationException
from utils.validators import Validator, validate_or_raise

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration with persistence and hot-reload."""

    DEFAULT_CONFIG_FILE = "config_default.json"
    USER_CONFIG_FILE = "config.json"
    CONFIG_BACKUP_SUFFIX = ".backup"

    def __init__(self, config_dir: str = "."):
        """
        Initialize ConfigManager.

        Args:
            config_dir: Directory to store config files (default: current directory)
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.default_config_path = self.config_dir / self.DEFAULT_CONFIG_FILE
        self.user_config_path = self.config_dir / self.USER_CONFIG_FILE

        self._config: Dict[str, Any] = {}
        self._last_modified: float = 0
        self._change_callbacks = []

        # Load configuration
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from files."""
        try:
            # Load default config
            default_config = self._load_json_file(self.default_config_path)
            if default_config is None:
                raise ConfigException(
                    f"Default config file not found: {self.default_config_path}"
                )

            # Validar estrutura mínima (CORREÇÃO)
            self._validate_config_structure(default_config)

            # Load user config if exists
            user_config = {}
            if self.user_config_path.exists():
                user_config = self._load_json_file(self.user_config_path) or {}
                self._validate_config_structure(user_config)

            # Merge configs (user config overrides defaults)
            self._config = self._deep_merge(default_config, user_config)
            self._last_modified = os.path.getmtime(self.user_config_path) if self.user_config_path.exists() else 0

            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigException(f"Failed to load configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Key in dot notation (e.g., 'audio.sample_rate')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """
        Set configuration value by dot-notation key.

        Args:
            key: Key in dot notation (e.g., 'audio.sample_rate')
            value: Value to set
            persist: Whether to save to file
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        if persist:
            self.save_config()

        # Trigger callbacks
        self._notify_changes(key, value)

    def get_keywords(self) -> list:
        """Get all keywords."""
        return self.get("keywords", [])

    def get_keyword(self, keyword_id: str) -> Optional[Dict]:
        """Get keyword by ID."""
        keywords = self.get_keywords()
        for kw in keywords:
            if kw.get("id") == keyword_id:
                return kw
        return None

    def add_keyword(self, keyword: Dict[str, Any]) -> None:
        """Add a new keyword."""
        validate_or_raise(
            Validator.validate_keyword(keyword),
            "Invalid keyword structure"
        )

        keywords = self.get_keywords()
        
        # Check for duplicate ID
        if any(kw.get("id") == keyword["id"] for kw in keywords):
            raise ConfigValidationException(f"Keyword with ID '{keyword['id']}' already exists")

        keywords.append(keyword)
        self.set("keywords", keywords)

    def update_keyword(self, keyword_id: str, keyword: Dict[str, Any]) -> None:
        """Update an existing keyword."""
        validate_or_raise(
            Validator.validate_keyword(keyword),
            "Invalid keyword structure"
        )

        keywords = self.get_keywords()
        index = next((i for i, kw in enumerate(keywords) if kw.get("id") == keyword_id), -1)

        if index == -1:
            raise ConfigValidationException(f"Keyword with ID '{keyword_id}' not found")

        keywords[index] = keyword
        self.set("keywords", keywords)

    def delete_keyword(self, keyword_id: str) -> None:
        """Delete a keyword."""
        keywords = self.get_keywords()
        keywords = [kw for kw in keywords if kw.get("id") != keyword_id]
        self.set("keywords", keywords)

    def get_sounds(self) -> list:
        """Get all sounds."""
        return self.get("sounds", [])

    def get_sound(self, sound_id: str) -> Optional[Dict]:
        """Get sound by ID."""
        sounds = self.get_sounds()
        for sound in sounds:
            if sound.get("id") == sound_id:
                return sound
        return None

    def add_sound(self, sound: Dict[str, Any]) -> None:
        """Add a new sound."""
        validate_or_raise(
            Validator.validate_sound(sound),
            "Invalid sound structure"
        )

        sounds = self.get_sounds()

        # Check for duplicate ID
        if any(s.get("id") == sound["id"] for s in sounds):
            raise ConfigValidationException(f"Sound with ID '{sound['id']}' already exists")

        sounds.append(sound)
        self.set("sounds", sounds)

    def update_sound(self, sound_id: str, sound: Dict[str, Any]) -> None:
        """Update an existing sound."""
        validate_or_raise(
            Validator.validate_sound(sound),
            "Invalid sound structure"
        )

        sounds = self.get_sounds()
        index = next((i for i, s in enumerate(sounds) if s.get("id") == sound_id), -1)

        if index == -1:
            raise ConfigValidationException(f"Sound with ID '{sound_id}' not found")

        sounds[index] = sound
        self.set("sounds", sounds)

    def delete_sound(self, sound_id: str) -> None:
        """Delete a sound."""
        sounds = self.get_sounds()
        sounds = [s for s in sounds if s.get("id") != sound_id]
        self.set("sounds", sounds)

    def save_config(self) -> None:
        """Save current configuration to user config file."""
        try:
            # Create backup
            if self.user_config_path.exists():
                backup_path = self.user_config_path.with_suffix(
                    f"{self.CONFIG_BACKUP_SUFFIX}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                self.user_config_path.rename(backup_path)

            # Write config
            with open(self.user_config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration saved to {self.user_config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigException(f"Failed to save configuration: {e}")

    def export_config(self, file_path: str) -> None:
        """Export current configuration to a file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise ConfigException(f"Failed to export configuration: {e}")

    def import_config(self, file_path: str) -> None:
        """Import configuration from a file."""
        try:
            imported_config = self._load_json_file(Path(file_path))
            if imported_config is None:
                raise ConfigException(f"Invalid config file: {file_path}")

            self._config = imported_config
            self.save_config()
            logger.info(f"Configuration imported from {file_path}")
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            raise ConfigException(f"Failed to import configuration: {e}")

    def check_for_updates(self) -> bool:
        """Check if config file has been modified externally."""
        if not self.user_config_path.exists():
            return False

        current_modified = os.path.getmtime(self.user_config_path)
        if current_modified > self._last_modified:
            self._last_modified = current_modified
            return True
        return False

    def register_change_callback(self, callback) -> None:
        """Register a callback to be called when config changes."""
        self._change_callbacks.append(callback)

    def _notify_changes(self, key: str, value: Any) -> None:
        """Notify all registered callbacks of changes."""
        for callback in self._change_callbacks:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Error in change callback: {e}")

    @staticmethod
    def _load_json_file(file_path: Path) -> Optional[Dict]:
        """Load JSON file safely."""
        try:
            if not file_path.exists():
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """Deep merge override into base dictionary."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self._config.copy()

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        try:
            default_config = self._load_json_file(self.default_config_path)
            if default_config is None:
                raise ConfigException("Default config file not found")

            self._config = default_config
            self.save_config()
            logger.info("Configuration reset to defaults")
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            raise

    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """
        Validate that config has required sections.
        
        Args:
            config: Configuration dict to validate
            
        Raises:
            ConfigValidationException: If validation fails
        """
        required_sections = ["audio", "whisper", "ai", "app"]
        
        if not isinstance(config, dict):
            raise ConfigValidationException("Configuration must be a dictionary")
        
        for section in required_sections:
            if section not in config:
                logger.warning(f"Missing required config section: {section}")
                # Não falhar se estiver faltando - usar valores padrão ConfigException(f"Failed to reset configuration: {e}")
