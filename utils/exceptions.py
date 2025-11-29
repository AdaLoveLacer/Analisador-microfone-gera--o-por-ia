"""Custom exceptions for the application."""


class AppException(Exception):
    """Base exception for the application."""
    pass


class AudioException(AppException):
    """Exception raised for audio-related errors."""
    pass


class AudioDeviceException(AudioException):
    """Exception raised when audio device is not found or unavailable."""
    pass


class AudioCaptureException(AudioException):
    """Exception raised during audio capture."""
    pass


class TranscriptionException(AppException):
    """Exception raised for transcription errors."""
    pass


class WhisperException(TranscriptionException):
    """Exception raised for Whisper-related errors."""
    pass


class AIException(AppException):
    """Exception raised for AI-related errors."""
    pass


class KeywordDetectionException(AIException):
    """Exception raised for keyword detection errors."""
    pass


class ContextAnalysisException(AIException):
    """Exception raised for context analysis errors."""
    pass


class SoundException(AppException):
    """Exception raised for sound playback errors."""
    pass


class SoundFileException(SoundException):
    """Exception raised when sound file is not found or invalid."""
    pass


class ConfigException(AppException):
    """Exception raised for configuration errors."""
    pass


class ConfigValidationException(ConfigException):
    """Exception raised when configuration validation fails."""
    pass


class DatabaseException(AppException):
    """Exception raised for database errors."""
    pass


class WebException(AppException):
    """Exception raised for web/API errors."""
    pass


class ValidationException(AppException):
    """Exception raised for validation errors."""
    pass
