"""Whisper transcriber for real-time speech-to-text."""

import whisper
import numpy as np
import threading
import queue
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from utils.exceptions import WhisperException

logger = logging.getLogger(__name__)


class Transcriber:
    """Transcribes audio using OpenAI Whisper."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "pt",
        device: str = "cpu",
        fp16: bool = False,
    ):
        """
        Initialize Transcriber.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            language: Language code (e.g., 'pt' for Portuguese)
            device: Device to use (cpu or cuda)
            fp16: Use FP16 precision
        """
        self.model_name = model_name
        self.language = language
        self.device = device
        self.fp16 = fp16

        logger.info(f"Loading Whisper model: {model_name}")
        try:
            self.model = whisper.load_model(model_name, device=device)
            logger.info(f"Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise WhisperException(f"Failed to load Whisper model: {e}")

    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
    ) -> Dict[str, Any]:
        """
        Transcribe audio data.

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with transcription result
        """
        try:
            if len(audio_data) == 0:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": self.language,
                }

            # Ensure audio is in correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Normalize audio
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val

            result = self.model.transcribe(
                audio_data,
                language=self.language,
                task="transcribe",
                fp16=self.fp16,
                verbose=False,
            )

            return {
                "text": result.get("text", "").strip(),
                "confidence": self._calculate_confidence(result),
                "language": result.get("language", self.language),
                "segments": result.get("segments", []),
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise WhisperException(f"Transcription failed: {e}")

    def _calculate_confidence(self, result: Dict) -> float:
        """
        Calculate average confidence from segments.

        Args:
            result: Whisper result dictionary

        Returns:
            Average confidence score
        """
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.0

            # Use probability from segments if available
            probs = []
            for segment in segments:
                if "confidence" in segment:
                    probs.append(segment["confidence"])

            return sum(probs) / len(probs) if probs else 0.8  # Default confidence
        except Exception:
            return 0.8

    def __del__(self):
        """Cleanup on deletion."""
        try:
            del self.model
        except Exception:
            pass


class TranscriberThread:
    """Threaded transcriber for non-blocking transcription."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "pt",
        device: str = "cpu",
    ):
        """
        Initialize TranscriberThread.

        Args:
            model_name: Whisper model name
            language: Language code
            device: Device to use
        """
        self.transcriber = Transcriber(model_name, language, device)
        self.input_queue: queue.Queue = queue.Queue(maxsize=10)
        self.output_queue: queue.Queue = queue.Queue(maxsize=10)
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start transcriber thread."""
        if self.is_running:
            logger.warning("Transcriber thread already running")
            return

        self.is_running = True
        self._thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        self._thread.start()
        logger.info("Transcriber thread started")

    def stop(self) -> None:
        """Stop transcriber thread."""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Transcriber thread stopped")

    def submit_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> None:
        """
        Submit audio for transcription.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
        """
        try:
            self.input_queue.put_nowait((audio_data, sample_rate))
        except queue.Full:
            logger.warning("Transcriber input queue full")

    def get_result(self, timeout: float = 1.0) -> Optional[Dict]:
        """
        Get transcription result.

        Args:
            timeout: Timeout in seconds

        Returns:
            Transcription result or None
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _transcribe_loop(self) -> None:
        """Main transcription loop."""
        try:
            while self.is_running:
                try:
                    # Get audio from queue
                    audio_data, sample_rate = self.input_queue.get(timeout=0.5)

                    # Transcribe
                    result = self.transcriber.transcribe(audio_data, sample_rate)

                    # Put result in output queue
                    try:
                        self.output_queue.put_nowait(result)
                    except queue.Full:
                        try:
                            self.output_queue.get_nowait()  # Discard oldest
                            self.output_queue.put_nowait(result)
                        except queue.Empty:
                            pass

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in transcribe loop: {e}")

        except Exception as e:
            logger.error(f"Transcriber thread error: {e}")
            self.is_running = False

    def get_queue_size(self) -> tuple:
        """Get input and output queue sizes."""
        return (self.input_queue.qsize(), self.output_queue.qsize())
