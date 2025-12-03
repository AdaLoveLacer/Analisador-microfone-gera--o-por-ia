"""Main analyzer orchestrating audio capture, transcription, detection and playback."""

import threading
import queue
import logging
import time
import numpy as np
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from core.config_manager import ConfigManager
from core.event_logger import get_logger
from audio.processor import AudioProcessor
from audio.transcriber import TranscriberThread
from ai.keyword_detector import KeywordDetector
from ai.context_analyzer import ContextAnalyzer
from sound.player import SoundManager
from database.db_manager import DatabaseManager

logger = get_logger(__name__)


class MicrophoneAnalyzer:
    """Main analyzer that orchestrates everything."""

    def __init__(
        self,
        config_dir: str = ".",
        database_dir: str = ".",
    ):
        """
        Initialize MicrophoneAnalyzer.

        Args:
            config_dir: Configuration directory
            database_dir: Database directory
        """
        # Initialize components
        self.config = ConfigManager(config_dir)
        self.database = DatabaseManager(database_dir)

        # Audio components
        self.audio_processor: Optional[AudioProcessor] = None
        self.transcriber: Optional[TranscriberThread] = None

        # AI components
        self.keyword_detector = KeywordDetector(self.config.get_keywords())
        self.context_analyzer = ContextAnalyzer()

        # Sound component
        self.sound_manager = SoundManager(self.config.get_sounds())

        # State
        self.is_running = False
        self.is_capturing = False
        self.current_transcript = ""
        self.last_detected_keyword = None

        # Queues
        self.event_queue = queue.Queue()

        # Callbacks
        self._transcription_callbacks = []
        self._detection_callbacks = []
        self._status_callbacks = []
        self._audio_level_callbacks = []

        # Threads
        self._processor_thread: Optional[threading.Thread] = None
        self._event_thread: Optional[threading.Thread] = None

        # Thread synchronization (CORREÇÃO: race conditions)
        self._state_lock = threading.Lock()
        self._callback_lock = threading.Lock()

        logger.info("MicrophoneAnalyzer initialized")

    def start(self) -> None:
        """Start the analyzer."""
        try:
            with self._state_lock:
                if self.is_running:
                    logger.warning("Analyzer already running")
                    return

                self.is_running = True

            # CORREÇÃO: Limpeza automática de registros antigos (libera espaço em disco)
            # Limpar registros com mais de 7 dias a cada inicialização
            try:
                self.database.clear_old_records(days=7)
            except Exception as e:
                logger.warning(f"Failed to clear old database records: {e}")

            # CORREÇÃO: Reutilizar AudioProcessor ao invés de recriar
            if not self.audio_processor:
                audio_config = self.config.get("audio")
                self.audio_processor = AudioProcessor(
                    device_id=audio_config.get("device_id", -1),
                    sample_rate=audio_config.get("sample_rate", 16000),
                    chunk_size=audio_config.get("chunk_size", 2048),
                    channels=audio_config.get("channels", 1),
                    silence_threshold=audio_config.get("silence_threshold", 0.02),
                )

            # Start audio capture
            if not self.audio_processor.is_recording:
                self.audio_processor.start()

            # CORREÇÃO: Reutilizar Transcriber ao invés de recriar
            if not self.transcriber:
                whisper_config = self.config.get("whisper")
                self.transcriber = TranscriberThread(
                    model_name=whisper_config.get("model", "base"),
                    language=whisper_config.get("language", "pt"),
                    device=whisper_config.get("device", "cpu"),
                )
            
            if hasattr(self.transcriber, 'is_running') and not self.transcriber.is_running:
                self.transcriber.start()

            # Start processing thread
            self._processor_thread = threading.Thread(
                target=self._processing_loop, daemon=True
            )
            self._processor_thread.start()

            # Start event thread
            self._event_thread = threading.Thread(
                target=self._event_loop, daemon=True
            )
            self._event_thread.start()

            self.is_capturing = True
            self._notify_status()

            logger.info("Analyzer started")
            self.database.add_event("analyzer_started")

        except Exception as e:
            logger.error(f"Failed to start analyzer: {e}")
            self.is_running = False
            raise

    def stop(self) -> None:
        """Stop the analyzer."""
        try:
            with self._state_lock:
                self.is_running = False
                self.is_capturing = False

            # Stop components
            if self.audio_processor and self.audio_processor.is_recording:
                self.audio_processor.stop()

            if self.transcriber and hasattr(self.transcriber, 'is_running') and self.transcriber.is_running:
                self.transcriber.stop()

            if self.sound_manager:
                self.sound_manager.stop_sound()

            logger.info("Analyzer stopped")
            self.database.add_event("analyzer_stopped")
            self._notify_status()

        except Exception as e:
            logger.error(f"Error stopping analyzer: {e}")

    def _processing_loop(self) -> None:
        """Main processing loop."""
        try:
            audio_buffer = []
            min_duration = self.config.get("audio.min_duration_seconds", 0.5)
            sample_rate = self.config.get("audio.sample_rate", 16000)
            min_samples = int(min_duration * sample_rate)

            while self.is_running:
                try:
                    # Get audio chunk
                    chunk = self.audio_processor.get_chunk(timeout=0.5)
                    if chunk is None:
                        continue

                    # Calcular e enviar o nível de áudio
                    energy = np.sqrt(np.mean(chunk ** 2))
                    max_energy = np.max(np.abs(chunk))
                    
                    # CORREÇÃO: Usar log scale para melhor distribuição de valores
                    # O áudio já está normalizado em 0-1 pelo Whisper
                    # Usar escala logarítmica: dB = 20 * log10(amplitude)
                    # Normalizar para 0-1 com range de -60dB a 0dB
                    db = 20 * np.log10(max(max_energy, 1e-6))  # Evitar log(0)
                    normalized_level = max(0.0, min(1.0, (db + 60) / 60))  # Map -60dB a 0dB para 0-1
                    
                    with self._callback_lock:
                        for callback in self._audio_level_callbacks:
                            try:
                                callback({"level": float(normalized_level), "energy": float(energy)})
                            except Exception as e:
                                logger.error(f"Error in audio level callback: {e}")

                    # Add to buffer
                    audio_buffer.append(chunk)

                    # Check if we have enough audio
                    total_samples = sum(len(c) for c in audio_buffer)
                    if total_samples >= min_samples:
                        # Combine chunks
                        audio_data = np.concatenate(audio_buffer)

                        # Submit for transcription
                        self.transcriber.submit_audio(audio_data, sample_rate)

                        # Clear buffer
                        audio_buffer = []

                        # Get transcription result
                        result = self.transcriber.get_result(timeout=10.0)
                        if result:
                            self._handle_transcription(result)

                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    time.sleep(0.1)

        except Exception as e:
            logger.error(f"Processing loop crashed: {e}")
            self.is_running = False

    def _handle_transcription(self, result: Dict[str, Any]) -> None:
        """
        Handle transcription result.

        Args:
            result: Transcription result from Whisper
        """
        try:
            text = result.get("text", "").strip()
            confidence = result.get("confidence", 0.0)

            if not text:
                return

            self.current_transcript = text

            # Log transcription
            self.database.add_transcription(text, confidence, 0.0)

            # Notify callbacks
            for callback in self._transcription_callbacks:
                try:
                    callback(text, confidence)
                except Exception as e:
                    logger.error(f"Error in transcription callback: {e}")

            # Detect keywords
            self._detect_keywords(text)

        except Exception as e:
            logger.error(f"Error handling transcription: {e}")

    def _detect_keywords(self, text: str) -> None:
        """
        Detect keywords in text.

        Args:
            text: Text to analyze
        """
        try:
            keyword_id, confidence = self.keyword_detector.detect(text)

            if not keyword_id:
                return

            logger.info(f"Keyword detected: {keyword_id} (confidence={confidence})")

            # Perform context analysis if enabled
            context_score = 0.0
            if self.config.get("ai.context_analysis_enabled", True):
                keyword_data = self.config.get_keyword(keyword_id)
                if keyword_data:
                    context_keywords = keyword_data.get("context_keywords", [])
                    context_score = self.context_analyzer.analyze(
                        text, context_keywords
                    )

            # Check threshold
            min_context = self.config.get("ai.min_context_confidence", 0.6)
            if context_score < min_context and context_score > 0:
                logger.info(f"Context score below threshold: {context_score}")
                return

            # Play sound
            keyword_data = self.config.get_keyword(keyword_id)
            if keyword_data:
                sound_id = keyword_data.get("sound_id")
                if sound_id:
                    self.sound_manager.play_sound(sound_id)
                    self.last_detected_keyword = keyword_id

            # Log detection
            self.database.add_detection(
                text=text,
                keyword_matched=keyword_id,
                confidence=confidence,
                context_score=context_score,
                sound_played=keyword_data.get("sound_id") if keyword_data else None,
            )

            # Notify callbacks
            for callback in self._detection_callbacks:
                try:
                    callback(keyword_id, text, confidence, context_score)
                except Exception as e:
                    logger.error(f"Error in detection callback: {e}")

        except Exception as e:
            logger.error(f"Error detecting keywords: {e}")

    def _event_loop(self) -> None:
        """Process events from queue."""
        while self.is_running:
            try:
                event = self.event_queue.get(timeout=1.0)
                logger.debug(f"Processing event: {event}")
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in event loop: {e}")

    def register_transcription_callback(self, callback: Callable) -> None:
        """Register callback for transcriptions."""
        with self._callback_lock:
            self._transcription_callbacks.append(callback)

    def register_detection_callback(self, callback: Callable) -> None:
        """Register callback for detections."""
        with self._callback_lock:
            self._detection_callbacks.append(callback)

    def register_status_callback(self, callback: Callable) -> None:
        """Register callback for status updates."""
        with self._callback_lock:
            self._status_callbacks.append(callback)

    def register_audio_level_callback(self, callback: Callable) -> None:
        """Register callback for audio level updates."""
        with self._callback_lock:
            self._audio_level_callbacks.append(callback)

    def _notify_status(self) -> None:
        """Notify status callbacks."""
        status = {
            "is_running": self.is_running,
            "is_capturing": self.is_capturing,
            "timestamp": datetime.now().isoformat(),
        }
        with self._callback_lock:
            for callback in self._status_callbacks:
                try:
                    callback(status)
                except Exception as e:
                    logger.error(f"Error in status callback: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        with self._state_lock:
            return {
                "is_running": self.is_running,
                "is_capturing": self.is_capturing,
                "current_transcript": self.current_transcript,
                "last_detected_keyword": self.last_detected_keyword,
                "audio_queue_size": (
                    self.audio_processor.get_queue_size()
                    if self.audio_processor
                    else 0
                ),
                "timestamp": datetime.now().isoformat(),
            }

    def reload_config(self) -> None:
        """Reload configuration from file."""
        try:
            self.config.load_config()
            self.keyword_detector.update_keywords(self.config.get_keywords())
            self.sound_manager.update_sounds_config(self.config.get_sounds())
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")

    def get_devices(self) -> list:
        """Get list of available audio devices."""
        try:
            # Se audio_processor já existe, usar dele
            if self.audio_processor:
                return self.audio_processor.list_devices()
            
            # Caso contrário, criar um temporário só para listar dispositivos
            temp_processor = AudioProcessor()
            devices = temp_processor.list_devices()
            # Limpar recursos temporários
            if hasattr(temp_processor, 'pa') and temp_processor.pa:
                temp_processor.pa.terminate()
            return devices
        except Exception as e:
            logger.warning(f"Error getting audio devices: {e}")
            return []
